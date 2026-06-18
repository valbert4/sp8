# Nonabelian Simple Subgroups in `Sp(8,2)`

Generated at `2026-06-18T22:33:42.796683+00:00` by `scripts/find_simple_nonabelian_subgroups.py`.

The scan starts from the archived permutation representatives whose
`rep_*.json` fingerprint has `solvable=false`.  GAP then reads the
corresponding `rep_*.g` file and computes `CompositionSeries(H)`.
A representative is recorded here exactly when that series has one
nontrivial factor and `IsAbelian(H)` is false.

## Summary

| Quantity | Value |
| --- | ---: |
| Nonsolvable representative classes scanned | 1,664 |
| Nonabelian simple representative classes | 49 |
| Distinct nonabelian simple isomorphism types | 17 |
| Full scan rows | `results/non_solvable_simple_scan.tsv` |
| Simple representative rows | `results/simple_nonabelian_representatives.tsv` |
| Run directory | `scripts/work_sp8/run_20260527_130624` |

## Isomorphism Types

| Simple group | Order | `Sp(8,2)`-conjugacy classes | Example representative ids |
| --- | ---: | ---: | --- |
| A5 | 60 | 10 | `1871, 1872, 1873, 2094, 6810, 6811, 9452, 18865, 19195, 52578` |
| PSL(3,2) | 168 | 6 | `3097, 3485, 3486, 3488, 9055, 656971` |
| A6 | 360 | 5 | `576, 577, 3519, 7919, 20941` |
| PSL(2,8) | 504 | 5 | `2581, 3270, 4538, 4539, 4845` |
| PSL(2,17) | 2,448 | 1 | `11` |
| A7 | 2,520 | 2 | `1047, 3006` |
| PSL(2,16) | 4,080 | 2 | `809, 810` |
| PSU(3,3) | 6,048 | 2 | `4127, 5427` |
| A8 | 20,160 | 4 | `247, 248, 1251, 4835` |
| O(5,3) | 25,920 | 2 | `4891, 656999` |
| A9 | 181,440 | 2 | `316, 656976` |
| O(5,4) | 979,200 | 1 | `59` |
| O(7,2) | 1,451,520 | 3 | `399, 400, 656977` |
| A10 | 1,814,400 | 1 | `66` |
| O+(8,2) | 174,182,400 | 1 | `656969` |
| O-(8,2) | 197,406,720 | 1 | `656970` |
| O(9,2) | 47,377,612,800 | 1 | `1` |
