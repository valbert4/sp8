# Sp(8,2) Subgroup Count Normalizer Pass

Generated at `2026-06-19T02:36:46.781587+00:00` by `scripts/count_total_subgroups.py --mode pilot`.

For a representative `H`, the row contribution is
`|Sp(8,2)| / |N_{Sp(8,2)}(H)|`. The TSV records one completed
normalizer computation per representative and is safe to resume.

## Summary

| Quantity | Value |
| --- | ---: |
| Selected representatives | 139 |
| Completed representatives | 139 |
| Partial subgroup sum for completed rows | 4,742,501,685 |
| Median normalizer time | 4 ms |
| 90th percentile normalizer time | 8 ms |
| Slowest normalizer time | 69 ms |
| Row data | `results/subgroup_count_pilot.tsv` |

## Slowest Rows

| Rep id | Order | Normalizer order | Class size | Time |
| ---: | ---: | ---: | ---: | ---: |
| 656976 | 181,440 | 181,440 | 261,120 | 69 ms |
| 656966 | 64 | 512 | 92,534,400 | 39 ms |
| 32126 | 256 | 2,048 | 23,133,600 | 38 ms |
| 471395 | 256 | 4,096 | 11,566,800 | 37 ms |
| 254147 | 1,024 | 8,192 | 5,783,400 | 36 ms |
| 3488 | 168 | 336 | 141,004,800 | 35 ms |
| 316 | 181,440 | 362,880 | 130,560 | 34 ms |
| 247 | 20,160 | 20,160 | 2,350,080 | 13 ms |
| 194995 | 128 | 2,048 | 23,133,600 | 12 ms |
| 4127 | 6,048 | 72,576 | 652,800 | 10 ms |
| 3097 | 168 | 672 | 70,502,400 | 9 ms |
| 519574 | 128 | 2,048 | 23,133,600 | 9 ms |

## Sampled Order Buckets

| Order | Samples | Median time | Max time | Partial subgroup sum |
| ---: | ---: | ---: | ---: | ---: |
| 64 | 14 | 4 ms | 39 ms | 412,549,200 |
| 128 | 14 | 4 ms | 12 ms | 370,137,600 |
| 256 | 14 | 4 ms | 38 ms | 185,068,800 |
| 512 | 13 | 4 ms | 8 ms | 156,151,800 |
| 60 | 10 | 4 ms | 5 ms | 838,430,208 |
| 32 | 9 | 5 ms | 8 ms | 740,275,200 |
| 1,024 | 7 | 3 ms | 36 ms | 70,846,650 |
| 2,048 | 7 | 3 ms | 7 ms | 30,362,850 |
| 168 | 6 | 6 ms | 35 ms | 564,019,200 |
| 16 | 5 | 5 ms | 8 ms | 821,242,800 |
| 360 | 5 | 4 ms | 6 ms | 78,231,552 |
| 504 | 5 | 2 ms | 3 ms | 146,227,200 |
| 20,160 | 4 | 6 ms | 13 ms | 4,308,480 |
| 1,451,520 | 3 | 2 ms | 9 ms | 54,400 |
| 192 | 2 | 4 ms | 4 ms | 185,068,800 |
| 1,536 | 2 | 4 ms | 6 ms | 7,711,200 |
| 2,520 | 2 | 4 ms | 5 ms | 10,967,040 |
| 4,080 | 2 | 3 ms | 4 ms | 5,806,080 |
| 6,048 | 2 | 6 ms | 10 ms | 2,611,200 |
| 25,920 | 2 | 2 ms | 2 ms | 456,960 |
