# FABulous bit_gen

Bitstream generation utilities for FABulous FPGA fabrics.

This package provides functionality for generating bitstreams from FASM (FPGA Assembly)
files for FABulous FPGA fabrics. It handles the conversion of place-and-route results
into configuration bitstreams that can be loaded onto the FPGA fabric.

## Features

- Parse FASM files containing FPGA configuration features
- Process configuration bits according to bitstream specifications
- Generate bitstream output in multiple formats:
  - Binary (.bin)
  - CSV (.csv)
  - Verilog header (.vh)
  - VHDL package (.vhd)

## Installation

```bash
pip install FABulous-bit-gen
```

## Usage

### Command Line

```bash
bit_gen -genBitstream input.fasm spec.pkl output.bin
```

### Python API

```python
from fabulous_bit_gen import gen_bitstream

gen_bitstream("input.fasm", "spec.pkl", "output.bin")
```

## License

Apache Software License 2.0
# Encoded frame strobes

Specifications may include `ArchSpecs.FrameStrobeEncoding` with
`{"kind": "q_of_n", "q": 2, "n": 6}` and an ordered
`ArchSpecs.FrameStrobeMasks` list exported by FABulous. `MaxFramesPerCol` remains
the physical width (20); the table length determines the logical frame count
(29 in this example). The writer validates the table and uses its masks in
frame-address words, leaving column selection and desynchronization unchanged.

The encoded group uses the highest n physical strobes. Lower strobes remain
direct; q-wire combinations follow in lexicographic order. Values must satisfy
`1 <= q <= n <= min(20, MaxFramesPerCol)` and produce at most 256 logical frames.
Missing or inconsistent encoding metadata is rejected. Without either encoding
field, the writer retains the legacy direct-strobe format and output bytes.

## Current limits and wider interfaces

The matching FABulous implementation currently supports 20 physical frame
strobes and 32 data bits per frame. The q-out-of-n algorithm itself is not tied
to those widths. With `M = MaxFramesPerCol` and `B = FrameBitsPerRow`, capacity
is `(M - n + binomial(n, q)) * B` configuration bits per tile.

The writer already uses the supplied widths for masks, frame storage and
packing. Remaining validation limits are explicit:

- `_resolve_frame_masks` restricts the encoded group to
  `1 <= q <= n <= min(20, MaxFramesPerCol)`.
- Its logical-frame check uses the actual physical width and caps the result
  at 256 frames to bound decoder size.
- FABulous's `FrameStrobeEncoding` also caps `q` and `n` at 20, but its capacity
  check still uses the literal `20 - n + binomial(n, q)`.

When wider interfaces are supported, generalize the validation in both
repositories together. Existing 2-of-6 encoding can scale within the current
limits; groups larger than 20 require lifting the group-size restriction.
The mask-table and AND-decoder approach can remain the same.

Removing the guards alone is insufficient: the configuration controller,
frame data transport and binary word layout must support the new widths.
Frame strobes must not overlap the column-address or desynchronization fields;
the writer checks these boundaries in `_resolve_bitstream_format`. Add
end-to-end tests against the matching configuration RTL before claiming wider
support. This note does not change the current limits or supported interface.
