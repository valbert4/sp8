# Packed Matrix Generator Format

This directory stores generators for representatives of subgroup conjugacy
classes of `Sp(8,2)` as compact 8x8 matrices over GF(2).

Each matrix is stored in exactly 8 bytes.  The packing is row-major and
most-significant-bit first:

- byte 0 stores row 1, columns 1 through 8;
- byte 1 stores row 2, columns 1 through 8;
- within a byte, column 1 is bit 7 and column 8 is bit 0.

For each shard, `shard_*.bin` is the concatenated matrix payload and
`shard_*.index.tsv` maps each representative id to its offset and generator
count.  Offsets are measured in matrices, not bytes.  The byte offset is
`matrix_offset * 8`.

The matrices are preimages under the faithful GAP map
`phi : Sp(8,2) -> P`, where `P` is the degree-120 permutation representation
used by the classification.  The verifier recomputes those preimages from the
archived permutation representatives and checks that the generated matrix
subgroup maps back onto the stored permutation subgroup.
