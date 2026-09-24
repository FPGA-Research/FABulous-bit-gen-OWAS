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
