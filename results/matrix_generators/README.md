# Matrix Generators

This directory is reserved for compact 8x8 GF(2) symplectic matrix-generator
exports for the classified subgroup representatives of `Sp(8,2)`.

Run:

```sh
python3 scripts/export_matrix_generators.py \
  --run-dir /path/to/restored-or-local-run \
  --out-dir results/matrix_generators
```

The exporter creates:

- `manifest.json`: export metadata and shard totals;
- `FORMAT.md`: packing convention;
- `shard_*.bin`: packed 8-byte matrices;
- `shard_*.index.tsv`: representative id, order, offset, and generator count.

Use `scripts/read_matrix_generators.py` to inspect representatives and verify
sampled shards against the archived permutation representatives.
