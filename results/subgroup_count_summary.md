# Sp(8,2) Subgroup Count Normalizer Pass

Generated at `2026-06-19T02:50:38.908725+00:00` by `scripts/count_total_subgroups.py --mode all`.

For a representative `H`, the row contribution is
`|Sp(8,2)| / |N_{Sp(8,2)}(H)|`. The TSV records one completed
normalizer computation per representative and is safe to resume.

## Summary

| Quantity | Value |
| --- | ---: |
| Selected representatives | 657,007 |
| Completed representatives | 657,007 |
| Total subgroup count | 12,671,226,847,329 |
| Median normalizer time | 7 ms |
| 90th percentile normalizer time | 14 ms |
| Slowest normalizer time | 958 ms |
| Row data | `results/subgroup_count_normalizers.tsv` |

## Slowest Rows

| Rep id | Order | Normalizer order | Class size | Time |
| ---: | ---: | ---: | ---: | ---: |
| 191565 | 256 | 2,048 | 23,133,600 | 958 ms |
| 606025 | 64 | 2,048 | 23,133,600 | 876 ms |
| 191568 | 256 | 4,096 | 11,566,800 | 870 ms |
| 191553 | 256 | 4,096 | 11,566,800 | 832 ms |
| 191890 | 256 | 4,096 | 11,566,800 | 793 ms |
| 191566 | 256 | 4,096 | 11,566,800 | 772 ms |
| 191552 | 256 | 4,096 | 11,566,800 | 770 ms |
| 191647 | 256 | 4,096 | 11,566,800 | 751 ms |
| 606028 | 64 | 2,048 | 23,133,600 | 743 ms |
| 191608 | 256 | 4,096 | 11,566,800 | 741 ms |
| 191816 | 256 | 4,096 | 11,566,800 | 723 ms |
| 2268 | 240 | 960 | 49,351,680 | 704 ms |

## Order Buckets

| Order | Representatives | Median time | Max time | Subgroup sum |
| ---: | ---: | ---: | ---: | ---: |
| 128 | 152,415 | 7 ms | 571 ms | 3,004,665,044,115 |
| 256 | 135,501 | 7 ms | 958 ms | 1,782,372,214,035 |
| 64 | 117,527 | 8 ms | 876 ms | 3,158,917,342,995 |
| 512 | 83,862 | 7 ms | 490 ms | 730,255,008,915 |
| 32 | 49,818 | 9 ms | 241 ms | 1,753,056,973,395 |
| 1,024 | 37,185 | 6 ms | 285 ms | 209,761,983,315 |
| 2,048 | 14,084 | 6 ms | 138 ms | 48,795,065,235 |
| 16 | 10,843 | 10 ms | 556 ms | 465,757,201,395 |
| 384 | 7,345 | 6 ms | 222 ms | 155,454,206,700 |
| 192 | 7,111 | 6 ms | 121 ms | 238,056,581,100 |
| 768 | 5,744 | 6 ms | 117 ms | 71,361,222,660 |
| 4,096 | 4,853 | 5 ms | 100 ms | 10,149,492,915 |
| 96 | 4,610 | 7 ms | 129 ms | 255,780,182,700 |
| 1,536 | 4,450 | 6 ms | 105 ms | 28,066,444,695 |
| 3,072 | 3,254 | 5 ms | 101 ms | 11,964,355,965 |
| 48 | 2,367 | 8 ms | 134 ms | 229,444,883,280 |
| 6,144 | 1,400 | 5 ms | 79 ms | 3,309,315,030 |
| 8 | 1,231 | 13 ms | 106 ms | 46,472,586,435 |
| 8,192 | 1,195 | 5 ms | 21 ms | 1,725,851,475 |
| 576 | 893 | 6 ms | 49 ms | 18,090,760,800 |
