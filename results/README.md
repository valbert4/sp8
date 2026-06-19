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
| Total actual subgroups | 12,671,226,847,329 |
| Nonsolvable classes scanned for simple groups | 1,664 |
| Nonabelian simple subgroup classes | 49 |
| Nonabelian simple isomorphism types | 17 |

The computation used a faithful degree-120 permutation representation of
`Sp(8,2)`, recursively processed maximal subgroups, and merged candidates by
ambient conjugacy in `Sp(8,2)`.

## Nonabelian Simple Subgroups

A GAP scan of the 1,664 nonsolvable representatives found 49 nonabelian
simple `Sp(8,2)`-conjugacy classes, spanning 17 abstract isomorphism types.
The table gives the number of `Sp(8,2)`-classes of each type and the total
number of actual subgroups in those classes, computed from the normalizer pass;
together these classes account for 1,670,895,105 actual subgroups. The
`O(9,2)` / `Sp(8,2)` row is the ambient group itself.

| Simple group | Alias | Order | `Sp(8,2)`-classes | Actual subgroups | Representative ids |
| --- | --- | ---: | ---: | ---: | --- |
| A5 | - | 60 | 10 | 838,430,208 | `1871, 1872, 1873, 2094, 6810, 6811, 9452, 18865, 19195, 52578` |
| PSL(3,2) | - | 168 | 6 | 564,019,200 | `3097, 3485, 3486, 3488, 9055, 656971` |
| A6 | - | 360 | 5 | 78,231,552 | `576, 577, 3519, 7919, 20941` |
| PSL(2,8) | - | 504 | 5 | 146,227,200 | `2581, 3270, 4538, 4539, 4845` |
| PSL(2,17) | - | 2,448 | 1 | 19,353,600 | `11` |
| A7 | - | 2,520 | 2 | 10,967,040 | `1047, 3006` |
| PSL(2,16) | - | 4,080 | 2 | 5,806,080 | `809, 810` |
| PSU(3,3) | - | 6,048 | 2 | 2,611,200 | `4127, 5427` |
| A8 | - | 20,160 | 4 | 4,308,480 | `247, 248, 1251, 4835` |
| O(5,3) | PSp(4,3) | 25,920 | 2 | 456,960 | `4891, 656999` |
| A9 | - | 181,440 | 2 | 391,680 | `316, 656976` |
| O(5,4) | Sp(4,4) | 979,200 | 1 | 24,192 | `59` |
| O(7,2) | Sp(6,2) | 1,451,520 | 3 | 54,400 | `399, 400, 656977` |
| A10 | - | 1,814,400 | 1 | 13,056 | `66` |
| O+(8,2) | Omega+(8,2) | 174,182,400 | 1 | 136 | `656969` |
| O-(8,2) | Omega-(8,2) | 197,406,720 | 1 | 120 | `656970` |
| O(9,2) | Sp(8,2) | 47,377,612,800 | 1 | 1 | `1` |

## Tables

- [`order_counts.tsv`](order_counts.tsv): number of conjugacy classes for each subgroup order.
- [`maximal_count_counts.tsv`](maximal_count_counts.tsv): distribution of the number of maximal-subgroup classes recorded for a representative.
- [`parent_count_counts.tsv`](parent_count_counts.tsv): distribution of the number of known incidence parents per representative.
- [`solvable_counts.tsv`](solvable_counts.tsv): solvability split from the stored fingerprints.
- [`orbit_pattern_counts.tsv`](orbit_pattern_counts.tsv): orbit-length patterns in the degree-120 action.
- [`completion_certificate.json`](completion_certificate.json): machine-readable final snapshot and health checks.
- [`subgroup_count_summary.md`](subgroup_count_summary.md): normalizer-pass summary for the total actual subgroup count.
- [`subgroup_count_normalizers.tsv`](subgroup_count_normalizers.tsv): normalizer order and conjugacy-class size for every representative.
- [`simple_nonabelian_groups.md`](simple_nonabelian_groups.md): GAP-certified table of nonabelian simple subgroup types.
- [`simple_nonabelian_representatives.tsv`](simple_nonabelian_representatives.tsv): per-representative normalizer, orbit, and incidence data for the 49 nonabelian simple classes.
- [`non_solvable_simple_scan.tsv`](non_solvable_simple_scan.tsv): full GAP scan over the 1,664 nonsolvable classes.

## Matrix Generators

The permutation representatives can be converted to faithful 8x8 GF(2)
symplectic matrix generators with:

```sh
python3 scripts/export_matrix_generators.py \
  --run-dir /path/to/restored-or-local-run \
  --out-dir results/matrix_generators
```

The compact export uses binary matrix shards plus TSV indexes. It is designed to
be publishable in this repository while the original representative files remain
in the external run archive. The companion reader and verifier are:

```sh
python3 scripts/read_matrix_generators.py --matrix-dir results/matrix_generators info
python3 scripts/read_matrix_generators.py --matrix-dir results/matrix_generators verify \
  --run-dir /path/to/restored-or-local-run --sample 25
```

## Largest Order Buckets

| Order | Conjugacy classes | Actual subgroups |
| ---: | ---: | ---: |
| 128 | 152,415 | 3,004,665,044,115 |
| 256 | 135,501 | 1,782,372,214,035 |
| 64 | 117,527 | 3,158,917,342,995 |
| 512 | 83,862 | 730,255,008,915 |
| 32 | 49,818 | 1,753,056,973,395 |
| 1024 | 37,185 | 209,761,983,315 |
| 2048 | 14,084 | 48,795,065,235 |
| 16 | 10,843 | 465,757,201,395 |
| 384 | 7,345 | 155,454,206,700 |
| 192 | 7,111 | 238,056,581,100 |
| 768 | 5,744 | 71,361,222,660 |
| 4096 | 4,853 | 10,149,492,915 |
| 96 | 4,610 | 255,780,182,700 |
| 1536 | 4,450 | 28,066,444,695 |
| 3072 | 3,254 | 11,964,355,965 |
| 48 | 2,367 | 229,444,883,280 |
| 6144 | 1,400 | 3,309,315,030 |
| 8 | 1,231 | 46,472,586,435 |
| 8192 | 1,195 | 1,725,851,475 |
| 576 | 893 | 18,090,760,800 |

## Total Subgroup Count

The actual subgroup count is computed from the conjugacy-class representatives
by summing `|Sp(8,2)| / |N_{Sp(8,2)}(H)|` over all 657,007 representatives
`H`. The completed normalizer pass gives 12,671,226,847,329 actual subgroups.

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
