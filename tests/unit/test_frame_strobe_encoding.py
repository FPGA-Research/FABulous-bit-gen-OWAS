"""Encoded frame addresses retain the legacy wire format and validate metadata."""

import copy
from itertools import combinations

import pytest

from fabulous_bit_gen.bit_gen import _build_binary_bitstream, _resolve_bitstream_format


def encoded_spec(q=2, n=6):
    """Build the address table exported by the FABulous generator."""
    masks = [1 << bit for bit in range(20 - n)]
    masks += [
        sum(1 << bit for bit in group) for group in combinations(range(20 - n, 20), q)
    ]
    return {
        "ArchSpecs": {
            "FrameStrobeEncoding": {"kind": "q_of_n", "q": q, "n": n},
            "FrameStrobeMasks": masks,
        }
    }


@pytest.mark.parametrize(
    ("q", "n", "frames"), [(1, 20, 20), (2, 6, 29), (2, 7, 34), (3, 6, 34)]
)
def test_encoded_addresses(q, n, frames):
    """Every frame uses its physical mask, with column/desync bits unchanged."""
    spec = encoded_spec(q, n)
    fmt = _resolve_bitstream_format(spec)
    assert fmt.max_frames_per_col == 20
    assert fmt.logical_frames_per_col == frames
    data = [[bytes([frame]) * 4 for frame in range(frames)] for _ in range(2)]
    binary = _build_binary_bitstream(data, 2, fmt)
    offset = len(bytes.fromhex(fmt.sync_header_hex))
    for col in range(2):
        for frame, mask in enumerate(spec["ArchSpecs"]["FrameStrobeMasks"]):
            assert (
                int.from_bytes(binary[offset : offset + 4], "big") == (col << 27) | mask
            )
            assert binary[offset + 4 : offset + 8] == data[col][frame]
            offset += 8
    assert binary[offset:] == b"\x00\x10\x00\x00"


def test_identity_bytes_match_legacy():
    """Explicit 1-of-20 encoding produces exactly the legacy binary bytes."""
    legacy = _resolve_bitstream_format({})
    encoded = _resolve_bitstream_format(encoded_spec(1, 20))
    data = [[frame.to_bytes(4, "big") for frame in range(20)]]
    assert _build_binary_bitstream(data, 1, legacy) == _build_binary_bitstream(
        data, 1, encoded
    )


@pytest.mark.parametrize(
    "change",
    [
        "missing_masks",
        "missing_encoding",
        "wrong_mask",
        "duplicate_mask",
        "reordered_masks",
        "reserved_bit",
        "boolean_mask",
        "q_zero",
        "q_exceeds_n",
        "too_large",
        "n_exceeds_width",
        "unknown_kind",
    ],
)
def test_reject_invalid_metadata(change):
    """Malformed specs fail before any binary output is produced."""
    spec = copy.deepcopy(encoded_spec())
    arch = spec["ArchSpecs"]
    if change == "missing_masks":
        del arch["FrameStrobeMasks"]
    elif change == "missing_encoding":
        del arch["FrameStrobeEncoding"]
    elif change == "wrong_mask":
        arch["FrameStrobeMasks"][14] = 1 << 14
    elif change == "duplicate_mask":
        arch["FrameStrobeMasks"][15] = arch["FrameStrobeMasks"][14]
    elif change == "reordered_masks":
        arch["FrameStrobeMasks"].reverse()
    elif change == "reserved_bit":
        arch["FrameStrobeMasks"][-1] |= 1 << 20
    elif change == "boolean_mask":
        arch["FrameStrobeMasks"][0] = True
    elif change == "q_zero":
        arch["FrameStrobeEncoding"]["q"] = 0
    elif change == "q_exceeds_n":
        arch["FrameStrobeEncoding"]["q"] = 7
    elif change == "too_large":
        arch["FrameStrobeEncoding"].update(q=10, n=20)
    elif change == "n_exceeds_width":
        arch["FrameStrobeEncoding"]["n"] = 21
    else:
        arch["FrameStrobeEncoding"]["kind"] = "binary"
    with pytest.raises(ValueError, match="FrameStrobe"):
        _resolve_bitstream_format(spec)
