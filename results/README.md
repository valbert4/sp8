# Subgroups of `Sp(8,2)`

This directory gives the GitHub-sized presentation of the completed
`Sp(8,2)` subgroup computation. The full classified-group run data is archived
outside this repository; it is too large for normal Git history and includes
657,007 representative GAP files plus worker output, snapshots, caches, and
logs. The published repository artifact is therefore the classification
certificate plus the aggregate tables below.

## Result

| Quantity | Value |
| --- | ---: |
| Ambient group order | 47,377,612,800 |
| Subgroup conjugacy classes | 657,007 |
| Permutation model | degree 120 |
| Final snapshot | `progress_003498.json` |
| Snapshot timestamp | `2026-06-03T19:08:21.460128+00:00` |
| Final frontier size | 0 |
| Raw child backlog | 0 |
| Processed representatives | 657,007 |
| Incidence records | 15,505,210 |

The computation used a faithful degree-120 permutation representation of
`Sp(8,2)`, recursively processed maximal subgroups, and merged candidates by
ambient conjugacy in `Sp(8,2)`.

## Tables

- [`order_counts.tsv`](order_counts.tsv): number of conjugacy classes for each subgroup order.
- [`maximal_count_counts.tsv`](maximal_count_counts.tsv): distribution of the number of maximal-subgroup classes recorded for a representative.
- [`parent_count_counts.tsv`](parent_count_counts.tsv): distribution of the number of known incidence parents per representative.
- [`solvable_counts.tsv`](solvable_counts.tsv): solvability split from the stored fingerprints.
- [`orbit_pattern_counts.tsv`](orbit_pattern_counts.tsv): orbit-length patterns in the degree-120 action.
- [`completion_certificate.json`](completion_certificate.json): machine-readable final snapshot and health checks.

## Largest Order Buckets

| Order | Conjugacy classes |
| ---: | ---: |
| 128 | 152,415 |
| 256 | 135,501 |
| 64 | 117,527 |
| 512 | 83,862 |
| 32 | 49,818 |
| 1024 | 37,185 |
| 2048 | 14,084 |
| 16 | 10,843 |
| 384 | 7,345 |
| 192 | 7,111 |
| 768 | 5,744 |
| 4096 | 4,853 |
| 96 | 4,610 |
| 1536 | 4,450 |
| 3072 | 3,254 |
| 48 | 2,367 |
| 6144 | 1,400 |
| 8 | 1,231 |
| 8192 | 1,195 |
| 576 | 893 |

## Caveat

The total number of actual subgroups of `Sp(8,2)` is not reported here.  The
classification recorded one representative for each ambient conjugacy class.
The total subgroup count would require a separate pass computing
`|N_{Sp(8,2)}(H)|` for every representative `H` and summing
`|Sp(8,2)| / |N_{Sp(8,2)}(H)|`.

## Full Representatives

The representative files themselves are archived separately from this published
repository. They should not be committed as individual Git files. If the full
representative set is needed publicly, publish the archived `reps/` directory,
`incidence.jsonl`, and the final snapshot as an external archive together with a
SHA256 checksum.

## Regeneration

From the repository root:

```sh
python3 scripts/export_sp8_github_results.py \
  --run-dir /path/to/restored-or-local-run \
  --out-dir results
```
