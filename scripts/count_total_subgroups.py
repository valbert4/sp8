#!/usr/bin/env python3
"""Count actual subgroups of Sp(8,2) from conjugacy-class representatives.

For each representative H, the number of actual subgroups in its ambient
conjugacy class is |Sp(8,2)| / |N_{Sp(8,2)}(H)|.  This driver is resumable:
it writes one TSV row per representative after GAP computes the normalizer.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import csv
import json
import random
import statistics
import subprocess
import tempfile
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_RUN_DIR = SCRIPT_DIR / "work_sp8" / "run_20260527_130624"
DEFAULT_GAP = Path("/home/valbert/gap-4.15.1/gap")
DEFAULT_MATRIX_DIR = REPO_ROOT / "results" / "matrix_generators"
DEFAULT_SIMPLE_TSV = REPO_ROOT / "results" / "simple_nonabelian_representatives.tsv"
DEFAULT_PILOT_TSV = REPO_ROOT / "results" / "subgroup_count_pilot.tsv"
DEFAULT_PILOT_MD = REPO_ROOT / "results" / "subgroup_count_pilot_summary.md"
DEFAULT_FULL_TSV = REPO_ROOT / "results" / "subgroup_count_normalizers.tsv"
DEFAULT_FULL_MD = REPO_ROOT / "results" / "subgroup_count_summary.md"
SP8_ORDER = 47_377_612_800
TSV_HEADER = [
    "rep_id",
    "order",
    "normalizer_order",
    "conjugacy_class_size",
    "elapsed_ms",
]


def gap_string(value: str | Path) -> str:
    text = str(value)
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'


def display_path(path: Path) -> str:
    path = path.resolve()
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def fmt_int(value: int) -> str:
    return f"{value:,}"


def load_rep_index(matrix_dir: Path) -> list[dict[str, int]]:
    rows: list[dict[str, int]] = []
    for index_path in sorted(matrix_dir.glob("shard_*.index.tsv")):
        with index_path.open(newline="") as f:
            reader = csv.DictReader(f, delimiter="\t")
            for row in reader:
                rows.append({"rep_id": int(row["rep_id"]), "order": int(row["order"])})
    if not rows:
        raise FileNotFoundError(f"no shard_*.index.tsv files found under {matrix_dir}")
    return sorted(rows, key=lambda item: item["rep_id"])


def load_simple_ids(path: Path) -> set[int]:
    if not path.exists():
        return set()
    with path.open(newline="") as f:
        return {int(row["rep_id"]) for row in csv.DictReader(f, delimiter="\t")}


def choose_evenly(items: list[dict[str, int]], count: int) -> list[dict[str, int]]:
    if count <= 0 or not items:
        return []
    if len(items) <= count:
        return list(items)
    if count == 1:
        return [items[0]]
    step = (len(items) - 1) / (count - 1)
    return [items[round(i * step)] for i in range(count)]


def select_pilot_reps(
    rows: list[dict[str, int]],
    *,
    simple_ids: set[int],
    top_orders: int,
    per_order: int,
    random_count: int,
    seed: int,
    include_simple: bool,
) -> list[dict[str, int]]:
    by_order: dict[int, list[dict[str, int]]] = defaultdict(list)
    for row in rows:
        by_order[row["order"]].append(row)

    selected: dict[int, dict[str, int]] = {}
    selected[rows[0]["rep_id"]] = rows[0]

    if include_simple:
        for row in rows:
            if row["rep_id"] in simple_ids:
                selected[row["rep_id"]] = row

    largest_buckets = [
        order
        for order, _count in Counter({order: len(items) for order, items in by_order.items()}).most_common(top_orders)
    ]
    for order in largest_buckets:
        for row in choose_evenly(by_order[order], per_order):
            selected[row["rep_id"]] = row

    rng = random.Random(seed)
    remaining = [row for row in rows if row["rep_id"] not in selected]
    if random_count > 0 and remaining:
        for row in rng.sample(remaining, min(random_count, len(remaining))):
            selected[row["rep_id"]] = row

    return [selected[rep_id] for rep_id in sorted(selected)]


def read_completed(path: Path) -> set[int]:
    if not path.exists():
        return set()
    with path.open(newline="") as f:
        return {int(row["rep_id"]) for row in csv.DictReader(f, delimiter="\t") if row.get("rep_id")}


def initialize_output(path: Path, *, force: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if force or not path.exists():
        with path.open("w", newline="") as f:
            writer = csv.writer(f, delimiter="\t", lineterminator="\n")
            writer.writerow(TSV_HEADER)


def write_gap_config(path: Path, reps: list[dict[str, int]]) -> None:
    lines = ["SP8_NORMALIZER_COUNT_REPS := [\n"]
    for row in reps:
        lines.append(f"  [ {row['rep_id']}, {row['order']} ],\n")
    lines.append("];;\n")
    path.write_text("".join(lines))


def chunked(items: list[dict[str, int]], size: int):
    for start in range(0, len(items), size):
        yield items[start : start + size]


def run_gap_chunk(args: argparse.Namespace, reps: list[dict[str, int]], out_tsv: Path) -> Path:
    with tempfile.TemporaryDirectory(prefix="sp8_normalizer_count.") as tmp:
        config_path = Path(tmp) / "normalizer_count_reps.g"
        write_gap_config(config_path, reps)
        expr = (
            f"SCRIPT_DIR:={gap_string(SCRIPT_DIR)};;"
            f"RUN_DIR:={gap_string(args.run_dir.resolve())};;"
            f"SP8_NORMALIZER_COUNT_CONFIG:={gap_string(config_path)};;"
            f"SP8_NORMALIZER_COUNT_OUT_TSV:={gap_string(out_tsv.resolve())};;"
        )
        cmd = [
            str(args.gap),
            "-q",
            "--quitonbreak",
            "-K",
            args.gap_workspace,
            "-c",
            expr,
            str(SCRIPT_DIR / "sp8_count_normalizers.g"),
        ]
        try:
            subprocess.run(
                cmd,
                check=True,
                text=True,
                timeout=args.chunk_timeout,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
        except subprocess.CalledProcessError as exc:
            if exc.stdout:
                print(exc.stdout)
            raise
        except subprocess.TimeoutExpired as exc:
            if exc.stdout:
                print(exc.stdout)
            raise
    return out_tsv


def append_chunk_output(master_tsv: Path, chunk_tsv: Path) -> int:
    lines = chunk_tsv.read_text().splitlines()
    if not lines:
        return 0
    with master_tsv.open("a") as f:
        for line in lines:
            f.write(line)
            f.write("\n")
    return len(lines)


def run_gap_chunks(args: argparse.Namespace, chunks: list[list[dict[str, int]]]) -> None:
    if not chunks:
        return
    with tempfile.TemporaryDirectory(prefix="sp8_normalizer_chunks.") as tmp:
        tmp_dir = Path(tmp)
        if args.workers <= 1:
            for idx, chunk in enumerate(chunks, start=1):
                chunk_out = tmp_dir / f"chunk_{idx:06d}.tsv"
                print(f"chunk {idx}: reps {chunk[0]['rep_id']}..{chunk[-1]['rep_id']} ({len(chunk)})")
                run_gap_chunk(args, chunk, chunk_out)
                rows = append_chunk_output(args.out_tsv, chunk_out)
                print(f"merged chunk {idx}: {rows} rows")
            return

        with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
            futures = {}
            for idx, chunk in enumerate(chunks, start=1):
                chunk_out = tmp_dir / f"chunk_{idx:06d}.tsv"
                print(f"submit chunk {idx}: reps {chunk[0]['rep_id']}..{chunk[-1]['rep_id']} ({len(chunk)})")
                futures[executor.submit(run_gap_chunk, args, chunk, chunk_out)] = (idx, chunk_out)

            for future in concurrent.futures.as_completed(futures):
                idx, chunk_out = futures[future]
                future.result()
                rows = append_chunk_output(args.out_tsv, chunk_out)
                print(f"merged chunk {idx}: {rows} rows")


def read_count_rows(path: Path) -> list[dict[str, int]]:
    with path.open(newline="") as f:
        return [
            {key: int(value) for key, value in row.items()}
            for row in csv.DictReader(f, delimiter="\t")
        ]


def percentile(values: list[int], pct: float) -> int:
    if not values:
        return 0
    if len(values) == 1:
        return values[0]
    values = sorted(values)
    pos = (len(values) - 1) * pct
    lo = int(pos)
    hi = min(lo + 1, len(values) - 1)
    if lo == hi:
        return values[lo]
    return round(values[lo] + (values[hi] - values[lo]) * (pos - lo))


def summarize_rows(rows: list[dict[str, int]]) -> dict[str, object]:
    elapsed = [row["elapsed_ms"] for row in rows]
    slowest = sorted(rows, key=lambda row: (-row["elapsed_ms"], row["rep_id"]))[:12]
    by_order: dict[int, list[dict[str, int]]] = defaultdict(list)
    for row in rows:
        by_order[row["order"]].append(row)
    order_rows = []
    for order, order_items in by_order.items():
        times = [row["elapsed_ms"] for row in order_items]
        order_rows.append(
            {
                "order": order,
                "samples": len(order_items),
                "median_ms": round(statistics.median(times)),
                "max_ms": max(times),
                "sum_conjugacy_class_size": sum(row["conjugacy_class_size"] for row in order_items),
            }
        )
    return {
        "rows": len(rows),
        "partial_subgroup_sum": sum(row["conjugacy_class_size"] for row in rows),
        "elapsed_min_ms": min(elapsed) if elapsed else 0,
        "elapsed_median_ms": round(statistics.median(elapsed)) if elapsed else 0,
        "elapsed_p90_ms": percentile(elapsed, 0.90),
        "elapsed_max_ms": max(elapsed) if elapsed else 0,
        "slowest": slowest,
        "by_order": sorted(order_rows, key=lambda row: (-row["samples"], row["order"]))[:20],
    }


def write_summary(path: Path, *, out_tsv: Path, selected_count: int, summary: dict[str, object], mode: str) -> None:
    generated_at = datetime.now(timezone.utc).isoformat()
    sum_label = "Total subgroup count" if mode == "all" else "Partial subgroup sum for completed rows"
    order_heading = "Order Buckets" if mode == "all" else "Sampled Order Buckets"
    order_count_label = "Representatives" if mode == "all" else "Samples"
    order_sum_label = "Subgroup sum" if mode == "all" else "Partial subgroup sum"
    lines = [
        "# Sp(8,2) Subgroup Count Normalizer Pass",
        "",
        f"Generated at `{generated_at}` by `scripts/count_total_subgroups.py --mode {mode}`.",
        "",
        "For a representative `H`, the row contribution is",
        "`|Sp(8,2)| / |N_{Sp(8,2)}(H)|`. The TSV records one completed",
        "normalizer computation per representative and is safe to resume.",
        "",
        "## Summary",
        "",
        "| Quantity | Value |",
        "| --- | ---: |",
        f"| Selected representatives | {fmt_int(selected_count)} |",
        f"| Completed representatives | {fmt_int(int(summary['rows']))} |",
        f"| {sum_label} | {fmt_int(int(summary['partial_subgroup_sum']))} |",
        f"| Median normalizer time | {fmt_int(int(summary['elapsed_median_ms']))} ms |",
        f"| 90th percentile normalizer time | {fmt_int(int(summary['elapsed_p90_ms']))} ms |",
        f"| Slowest normalizer time | {fmt_int(int(summary['elapsed_max_ms']))} ms |",
        f"| Row data | `{display_path(out_tsv)}` |",
        "",
        "## Slowest Rows",
        "",
        "| Rep id | Order | Normalizer order | Class size | Time |",
        "| ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in summary["slowest"]:  # type: ignore[index]
        lines.append(
            f"| {row['rep_id']} | {fmt_int(row['order'])} | "
            f"{fmt_int(row['normalizer_order'])} | {fmt_int(row['conjugacy_class_size'])} | "
            f"{fmt_int(row['elapsed_ms'])} ms |"
        )

    lines.extend(
        [
            "",
            f"## {order_heading}",
            "",
            f"| Order | {order_count_label} | Median time | Max time | {order_sum_label} |",
            "| ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in summary["by_order"]:  # type: ignore[index]
        lines.append(
            f"| {fmt_int(row['order'])} | {fmt_int(row['samples'])} | "
            f"{fmt_int(row['median_ms'])} ms | {fmt_int(row['max_ms'])} ms | "
            f"{fmt_int(row['sum_conjugacy_class_size'])} |"
        )
    path.write_text("\n".join(lines) + "\n")


def default_output_paths(mode: str) -> tuple[Path, Path]:
    if mode == "all":
        return DEFAULT_FULL_TSV, DEFAULT_FULL_MD
    return DEFAULT_PILOT_TSV, DEFAULT_PILOT_MD


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=["pilot", "all", "ids"], default="pilot")
    parser.add_argument("--run-dir", type=Path, default=DEFAULT_RUN_DIR)
    parser.add_argument("--matrix-dir", type=Path, default=DEFAULT_MATRIX_DIR)
    parser.add_argument("--simple-tsv", type=Path, default=DEFAULT_SIMPLE_TSV)
    parser.add_argument("--gap", type=Path, default=DEFAULT_GAP)
    parser.add_argument("--gap-workspace", default="2g")
    parser.add_argument("--out-tsv", type=Path)
    parser.add_argument("--summary-md", type=Path)
    parser.add_argument("--rep-id", type=int, action="append", default=[])
    parser.add_argument("--pilot-top-orders", type=int, default=8)
    parser.add_argument("--pilot-per-order", type=int, default=5)
    parser.add_argument("--pilot-random", type=int, default=50)
    parser.add_argument("--no-pilot-simple", action="store_true")
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--chunk-size", type=int, default=25)
    parser.add_argument("--chunk-timeout", type=int, default=300)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    default_tsv, default_md = default_output_paths(args.mode)
    args.out_tsv = args.out_tsv or default_tsv
    args.summary_md = args.summary_md or default_md

    rows = load_rep_index(args.matrix_dir)
    by_id = {row["rep_id"]: row for row in rows}
    if args.mode == "all":
        selected = rows
    elif args.mode == "ids":
        if not args.rep_id:
            raise SystemExit("--mode ids requires at least one --rep-id")
        selected = [by_id[rep_id] for rep_id in sorted(set(args.rep_id))]
    else:
        selected = select_pilot_reps(
            rows,
            simple_ids=load_simple_ids(args.simple_tsv),
            top_orders=args.pilot_top_orders,
            per_order=args.pilot_per_order,
            random_count=args.pilot_random,
            seed=args.seed,
            include_simple=not args.no_pilot_simple,
        )

    if args.limit is not None:
        selected = selected[: args.limit]

    initialize_output(args.out_tsv, force=args.force)
    completed = read_completed(args.out_tsv)
    remaining = [row for row in selected if row["rep_id"] not in completed]

    print(f"Selected representatives: {len(selected)}")
    print(f"Already completed: {len(completed.intersection({row['rep_id'] for row in selected}))}")
    print(f"Remaining: {len(remaining)}")
    print(f"Output TSV: {args.out_tsv}")

    if not args.dry_run:
        chunks = list(chunked(remaining, args.chunk_size))
        print(f"Chunks: {len(chunks)}")
        print(f"Workers: {args.workers}")
        run_gap_chunks(args, chunks)

    selected_ids = {item["rep_id"] for item in selected}
    result_rows = [row for row in read_count_rows(args.out_tsv) if row["rep_id"] in selected_ids]
    summary = summarize_rows(result_rows)
    write_summary(
        args.summary_md,
        out_tsv=args.out_tsv,
        selected_count=len(selected),
        summary=summary,
        mode=args.mode,
    )
    print(f"Completed representatives in selection: {summary['rows']}")
    if args.mode == "all":
        print(f"Total subgroup count: {summary['partial_subgroup_sum']}")
    else:
        print(f"Partial subgroup sum: {summary['partial_subgroup_sum']}")
    print(f"Median normalizer time: {summary['elapsed_median_ms']} ms")
    print(f"Slowest normalizer time: {summary['elapsed_max_ms']} ms")
    print(f"Wrote {args.summary_md}")


if __name__ == "__main__":
    main()
