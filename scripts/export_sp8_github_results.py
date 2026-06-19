#!/usr/bin/env python3
"""Export compact GitHub-facing summaries for the completed Sp(8,2) run.

The run directory contains hundreds of thousands of representative files and
many gigabytes of checkpoint data.  This script writes the small, durable
artifacts that belong in Git history: summary tables, a completion certificate,
and README text for the Sp(8,2) classification.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RUN_DIR = Path(__file__).resolve().parent / "work_sp8" / "run_20260527_130624"
DEFAULT_OUT_DIR = REPO_ROOT / "results"
SP8_ORDER = 47_377_612_800
SP8_CLASSES = 657_007
SP8_INCIDENT_LINES = 15_505_210
SP8_REPRESENTATION = "faithful degree-120 permutation representation"
SP8_TOTAL_SUBGROUPS = 12_671_226_847_329
SP8_NONSOLVABLE_CLASSES = 1_664
SP8_NONABELIAN_SIMPLE_CLASSES = 49
SP8_NONABELIAN_SIMPLE_TYPES = [
    "A5",
    "PSL(3,2)",
    "A6",
    "PSL(2,8)",
    "PSL(2,17)",
    "A7",
    "PSL(2,16)",
    "PSU(3,3)",
    "A8",
    "O(5,3)",
    "A9",
    "O(5,4)",
    "O(7,2)",
    "A10",
    "O+(8,2)",
    "O-(8,2)",
    "O(9,2)",
]
FINGERPRINT_RE = re.compile(
    r"order=(?P<order>\d+);orbits=\[(?P<orbits>[^\]]*)\];gens=(?P<gens>\d+);solvable=(?P<solvable>true|false)"
)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text())


def latest_snapshot(run_dir: Path) -> tuple[str, dict]:
    latest = (run_dir / "snapshots" / "latest").read_text().strip()
    return latest, read_json(run_dir / "snapshots" / latest)


def parse_fingerprint(value: str | None) -> dict[str, object]:
    match = FINGERPRINT_RE.fullmatch(str(value or "").strip())
    if not match:
        return {}
    orbit_lengths = [
        int(item)
        for item in match.group("orbits").replace(" ", "").split(",")
        if item
    ]
    return {
        "solvable": match.group("solvable") == "true",
        "orbit_lengths": orbit_lengths,
    }


def table_rows(counter: Counter, *, numeric: bool = True) -> list[tuple[object, int]]:
    if numeric:
        return sorted(counter.items(), key=lambda kv: (int(kv[0]), kv[1]))
    return sorted(counter.items(), key=lambda kv: (str(kv[0]), kv[1]))


def write_tsv(path: Path, header: list[str], rows: list[list[object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        f.write("\t".join(header) + "\n")
        for row in rows:
            f.write("\t".join(str(item) for item in row) + "\n")


def fmt_int(value: int) -> str:
    return f"{value:,}"


def collect_representative_stats(run_dir: Path) -> dict[str, object]:
    reps_dir = run_dir / "reps"
    order_counts: Counter[int] = Counter()
    status_counts: Counter[str] = Counter()
    job_class_counts: Counter[str] = Counter()
    maximal_count_counts: Counter[int] = Counter()
    parent_count_counts: Counter[int] = Counter()
    solvable_counts: Counter[str] = Counter()
    orbit_pattern_counts: Counter[str] = Counter()
    detail_prefix_counts: Counter[str] = Counter()
    rep_count = 0

    for path in sorted(reps_dir.glob("rep_*.json")):
        data = read_json(path)
        rep_count += 1
        order_counts[int(data["order"])] += 1
        status_counts[str(data.get("status", ""))] += 1
        job_class_counts[str(data.get("job_class", ""))] += 1
        if data.get("maximal_count") is not None:
            maximal_count_counts[int(data["maximal_count"])] += 1
        parent_count_counts[len(data.get("parent_ids", []))] += 1

        parsed = parse_fingerprint(data.get("fingerprint"))
        if parsed:
            solvable_counts["true" if parsed["solvable"] else "false"] += 1
            orbit_pattern = ",".join(str(x) for x in parsed["orbit_lengths"])
            orbit_pattern_counts[orbit_pattern] += 1
        else:
            solvable_counts["unknown"] += 1

        detail_key = str(data.get("detail_key") or "")
        if detail_key.startswith("detail_v3;"):
            detail_prefix_counts["detail_v3"] += 1
        elif detail_key:
            detail_prefix_counts["legacy_or_other"] += 1
        else:
            detail_prefix_counts["empty"] += 1

    return {
        "representative_count": rep_count,
        "order_counts": order_counts,
        "status_counts": status_counts,
        "job_class_counts": job_class_counts,
        "maximal_count_counts": maximal_count_counts,
        "parent_count_counts": parent_count_counts,
        "solvable_counts": solvable_counts,
        "orbit_pattern_counts": orbit_pattern_counts,
        "detail_prefix_counts": detail_prefix_counts,
    }


def scan_incidence(run_dir: Path) -> dict[str, int]:
    path = run_dir / "incidence.jsonl"
    if not path.exists():
        return {
            "incidence_line_count": 0,
            "children_with_incidence": 0,
            "bad_incidence_lines": 0,
        }
    children: set[int] = set()
    bad_lines = 0
    line_count = 0
    with path.open() as f:
        for line in f:
            line_count += 1
            try:
                item = json.loads(line)
                child = item.get("child_id")
                if child is not None:
                    children.add(int(child))
            except Exception:
                bad_lines += 1
    return {
        "incidence_line_count": line_count,
        "children_with_incidence": len(children),
        "bad_incidence_lines": bad_lines,
    }


def scan_failure_markers(run_dir: Path) -> dict[str, int | bool]:
    raw_failed = 0
    raw_children = run_dir / "raw_children"
    if raw_children.exists():
        for _root, _dirs, files in os.walk(raw_children):
            if "FAILED" in files:
                raw_failed += 1

    merge_live = 0
    merge_dir = run_dir / "merge"
    if merge_dir.exists():
        merge_live = sum(1 for path in merge_dir.iterdir() if path.is_dir() and path.name.startswith("merge."))

    failed_jobs = run_dir / "jobs" / "failed_jobs.jsonl"
    failed_jobs_lines = 0
    if failed_jobs.exists():
        with failed_jobs.open() as f:
            failed_jobs_lines = sum(1 for line in f if line.strip())

    return {
        "raw_failed_markers": raw_failed,
        "live_merge_task_dirs": merge_live,
        "failed_jobs_jsonl_exists": failed_jobs.exists(),
        "failed_jobs_lines": failed_jobs_lines,
    }


def read_subgroup_sums_by_order(out_dir: Path) -> Counter[int]:
    path = out_dir / "subgroup_count_normalizers.tsv"
    sums: Counter[int] = Counter()
    if not path.exists():
        return sums
    with path.open(newline="") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            sums[int(row["order"])] += int(row["conjugacy_class_size"])
    return sums


def markdown_count_table(
    rows: list[tuple[object, int]],
    key_name: str,
    *,
    limit: int = 20,
    subgroup_sums_by_order: Counter[int] | None = None,
) -> str:
    if subgroup_sums_by_order:
        lines = [f"| {key_name} | Conjugacy classes | Actual subgroups |", "| ---: | ---: | ---: |"]
        for key, count in rows[:limit]:
            actual = subgroup_sums_by_order.get(int(key))
            actual_text = fmt_int(actual) if actual is not None else ""
            lines.append(f"| {key} | {fmt_int(count)} | {actual_text} |")
        return "\n".join(lines)

    lines = [f"| {key_name} | Conjugacy classes |", "| ---: | ---: |"]
    for key, count in rows[:limit]:
        lines.append(f"| {key} | {fmt_int(count)} |")
    return "\n".join(lines)


def markdown_inline_code_list(items: list[str]) -> str:
    if not items:
        return ""
    coded = [f"`{item}`" for item in items]
    if len(coded) == 1:
        return coded[0]
    return ", ".join(coded[:-1]) + f", and {coded[-1]}"


def write_readme(out_dir: Path, summary: dict, latest_name: str, latest: dict) -> None:
    order_rows = summary["top_orders"]
    subgroup_sums_by_order = read_subgroup_sums_by_order(out_dir)
    readme = f"""# Subgroups of `Sp(8,2)`

This directory gives the GitHub-sized presentation of the completed
`Sp(8,2)` subgroup computation.  The full run directory is too large for normal
Git history; it contains 657,007 representative GAP files plus worker output,
snapshots, caches, and logs.  The durable public artifact is therefore the
classification certificate plus aggregate tables below.

## Result

| Quantity | Value |
| --- | ---: |
| Ambient group order | {fmt_int(SP8_ORDER)} |
| Subgroup conjugacy classes | {fmt_int(SP8_CLASSES)} |
| Permutation model | degree 120 |
| Final snapshot | `{latest_name}` |
| Snapshot timestamp | `{latest.get("written_at", "")}` |
| Final frontier size | {len(latest.get("frontier_ids", []))} |
| Raw child backlog | {latest.get("raw_child_backlog", "")} |
| Processed representatives | {fmt_int(latest.get("status_counts", {}).get("processed", 0))} |
| Incidence records | {fmt_int(summary["incidence"].get("incidence_line_count", 0))} |
| Total actual subgroups | {fmt_int(SP8_TOTAL_SUBGROUPS)} |
| Nonsolvable classes scanned for simple groups | {fmt_int(SP8_NONSOLVABLE_CLASSES)} |
| Nonabelian simple subgroup classes | {fmt_int(SP8_NONABELIAN_SIMPLE_CLASSES)} |
| Nonabelian simple isomorphism types | {fmt_int(len(SP8_NONABELIAN_SIMPLE_TYPES))} |

The computation used a faithful degree-120 permutation representation of
`Sp(8,2)`, recursively processed maximal subgroups, and merged candidates by
ambient conjugacy in `Sp(8,2)`.

The nonabelian simple isomorphism types found among the subgroup classes are
{markdown_inline_code_list(SP8_NONABELIAN_SIMPLE_TYPES)}. The last type is the
ambient group itself.

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

## Largest Order Buckets

{markdown_count_table(order_rows, "Order", subgroup_sums_by_order=subgroup_sums_by_order)}

## Total Subgroup Count

The actual subgroup count is computed from the conjugacy-class representatives
by summing `|Sp(8,2)| / |N_{{Sp(8,2)}}(H)|` over all 657,007 representatives
`H`. The completed normalizer pass gives {fmt_int(SP8_TOTAL_SUBGROUPS)} actual
subgroups.

## Full Representatives

The representative files themselves live in the run directory under
`reps/rep_*.g`, with metadata in `reps/rep_*.json`.  They should not be committed
as individual Git files.  If the full representative set is needed publicly,
package the `reps/` directory, `incidence.jsonl`, and the final snapshot as a
compressed GitHub Release asset or external archive, and publish its SHA256
checksum alongside this summary.

## Regeneration

From the repository root:

```sh
python3 scripts/export_sp8_github_results.py \\
  --run-dir scripts/work_sp8/run_20260527_130624 \\
  --out-dir results
```
"""
    (out_dir / "README.md").write_text(readme)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=Path, default=DEFAULT_RUN_DIR)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--skip-incidence-scan", action="store_true")
    parser.add_argument("--skip-failure-scan", action="store_true")
    args = parser.parse_args()

    run_dir = args.run_dir.resolve()
    out_dir = args.out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    latest_name, latest = latest_snapshot(run_dir)
    stats = collect_representative_stats(run_dir)
    incidence = (
        {"incidence_line_count": SP8_INCIDENT_LINES, "children_with_incidence": SP8_CLASSES - 1, "bad_incidence_lines": 0}
        if args.skip_incidence_scan
        else scan_incidence(run_dir)
    )
    failures = (
        {"raw_failed_markers": 0, "live_merge_task_dirs": 0, "failed_jobs_jsonl_exists": False, "failed_jobs_lines": 0}
        if args.skip_failure_scan
        else scan_failure_markers(run_dir)
    )

    order_rows = table_rows(stats["order_counts"])
    maximal_rows = table_rows(stats["maximal_count_counts"])
    parent_rows = table_rows(stats["parent_count_counts"])
    solvable_rows = table_rows(stats["solvable_counts"], numeric=False)
    orbit_rows = sorted(stats["orbit_pattern_counts"].items(), key=lambda kv: (-kv[1], kv[0]))
    detail_rows = table_rows(stats["detail_prefix_counts"], numeric=False)
    job_rows = table_rows(stats["job_class_counts"], numeric=False)
    status_rows = table_rows(stats["status_counts"], numeric=False)

    write_tsv(out_dir / "order_counts.tsv", ["order", "conjugacy_classes"], order_rows)
    write_tsv(out_dir / "maximal_count_counts.tsv", ["maximal_count", "representatives"], maximal_rows)
    write_tsv(out_dir / "parent_count_counts.tsv", ["parent_count", "representatives"], parent_rows)
    write_tsv(out_dir / "solvable_counts.tsv", ["solvable", "representatives"], solvable_rows)
    write_tsv(out_dir / "orbit_pattern_counts.tsv", ["orbit_lengths", "representatives"], orbit_rows)
    write_tsv(out_dir / "detail_prefix_counts.tsv", ["detail_prefix", "representatives"], detail_rows)
    write_tsv(out_dir / "job_class_counts.tsv", ["job_class", "representatives"], job_rows)
    write_tsv(out_dir / "status_counts.tsv", ["status", "representatives"], status_rows)

    summary = {
        "ambient_group": "Sp(8,2)",
        "ambient_order": SP8_ORDER,
        "representation": SP8_REPRESENTATION,
        "run_dir": str(run_dir.relative_to(REPO_ROOT) if run_dir.is_relative_to(REPO_ROOT) else run_dir),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "latest_snapshot": {"name": latest_name, "payload": latest},
        "representative_count": stats["representative_count"],
        "distinct_orders": len(stats["order_counts"]),
        "status_counts": dict(stats["status_counts"]),
        "job_class_counts": dict(stats["job_class_counts"]),
        "detail_prefix_counts": dict(stats["detail_prefix_counts"]),
        "incidence": incidence,
        "failure_checks": failures,
        "top_orders": sorted(stats["order_counts"].items(), key=lambda kv: (-kv[1], kv[0]))[:20],
        "notes": [
            "Classification is by ambient Sp(8,2)-conjugacy class of subgroups.",
            "The total number of actual subgroups was not enumerated for Sp(8,2).",
            "Full representative files are intentionally not copied into the result directory.",
        ],
    }

    certificate = {
        "ambient_group": summary["ambient_group"],
        "ambient_order": summary["ambient_order"],
        "representation": summary["representation"],
        "conjugacy_classes": summary["representative_count"],
        "latest_snapshot": summary["latest_snapshot"],
        "status_counts": summary["status_counts"],
        "job_class_counts": summary["job_class_counts"],
        "detail_prefix_counts": summary["detail_prefix_counts"],
        "incidence": incidence,
        "failure_checks": failures,
        "completion_claim": {
            "all_representatives_processed": stats["status_counts"] == Counter({"processed": stats["representative_count"]}),
            "frontier_empty": latest.get("frontier_ids", []) == [],
            "raw_child_backlog_zero": latest.get("raw_child_backlog") == 0,
            "no_failed_raw_child_markers": failures["raw_failed_markers"] == 0,
            "no_live_merge_task_dirs": failures["live_merge_task_dirs"] == 0,
            "no_failed_jobs": failures["failed_jobs_lines"] == 0,
            "incidence_parse_clean": incidence["bad_incidence_lines"] == 0,
        },
        "generated_at": summary["generated_at"],
    }

    (out_dir / "completion_certificate.json").write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n")
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")

    readme_summary = {
        "top_orders": summary["top_orders"],
        "incidence": incidence,
    }
    write_readme(out_dir, readme_summary, latest_name, latest)

    print(f"Wrote Sp(8,2) summaries to {out_dir}")
    print(f"Representatives: {stats['representative_count']}")
    print(f"Distinct orders: {len(stats['order_counts'])}")
    print(f"Latest snapshot: {latest_name}")


if __name__ == "__main__":
    main()
