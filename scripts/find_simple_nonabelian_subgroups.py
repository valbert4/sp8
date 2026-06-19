#!/usr/bin/env python3
"""Find nonabelian simple subgroup representatives in the Sp(8,2) run."""

from __future__ import annotations

import argparse
import csv
import json
import shutil
import subprocess
import tempfile
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_RUN_DIR = SCRIPT_DIR / "work_sp8" / "run_20260527_130624"
DEFAULT_GAP = Path("/home/valbert/gap-4.15.1/gap")
DEFAULT_OUT_MD = REPO_ROOT / "results" / "simple_nonabelian_groups.md"
DEFAULT_SIMPLE_TSV = REPO_ROOT / "results" / "simple_nonabelian_representatives.tsv"
DEFAULT_SCAN_TSV = REPO_ROOT / "results" / "non_solvable_simple_scan.tsv"
DEFAULT_NORMALIZER_TSV = REPO_ROOT / "results" / "subgroup_count_normalizers.tsv"

ALIASES = {
    "O(5,3)": "PSp(4,3)",
    "O(5,4)": "Sp(4,4)",
    "O(7,2)": "Sp(6,2)",
    "O+(8,2)": "Omega+(8,2)",
    "O-(8,2)": "Omega-(8,2)",
    "O(9,2)": "Sp(8,2)",
}


def gap_string(value: str | Path) -> str:
    text = str(value)
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'


def read_json(path: Path) -> dict:
    return json.loads(path.read_text())


def rep_id_from_path(path: Path) -> int:
    return int(path.name.removeprefix("rep_").removesuffix(".json"))


def find_nonsolvable_jsons(reps_dir: Path) -> list[Path]:
    rg = shutil.which("rg")
    if rg:
        result = subprocess.run(
            [rg, "-l", "solvable=false", str(reps_dir), "-g", "rep_*.json"],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
        )
        return sorted((Path(line) for line in result.stdout.splitlines()), key=rep_id_from_path)

    paths = []
    for path in reps_dir.glob("rep_*.json"):
        if "solvable=false" in path.read_text():
            paths.append(path)
    return sorted(paths, key=rep_id_from_path)


def load_candidates(run_dir: Path, limit: int | None) -> list[dict[str, int]]:
    paths = find_nonsolvable_jsons(run_dir / "reps")
    if limit is not None:
        paths = paths[:limit]
    candidates = []
    for path in paths:
        data = json.loads(path.read_text())
        candidates.append({"id": int(data["id"]), "order": int(data["order"])})
    return candidates


def write_gap_config(path: Path, candidates: list[dict[str, int]]) -> None:
    lines = ["SP8_SIMPLE_SCAN_CANDIDATES := [\n"]
    for item in candidates:
        lines.append(f"  [ {item['id']}, {item['order']} ],\n")
    lines.append("];;\n")
    path.write_text("".join(lines))


def run_gap_scan(args: argparse.Namespace, candidates: list[dict[str, int]]) -> None:
    args.scan_tsv.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="sp8_simple_scan.") as tmp:
        config_path = Path(tmp) / "candidates.g"
        write_gap_config(config_path, candidates)
        expr = (
            f"SCRIPT_DIR:={gap_string(SCRIPT_DIR)};;"
            f"RUN_DIR:={gap_string(args.run_dir.resolve())};;"
            f"SP8_SIMPLE_SCAN_CONFIG:={gap_string(config_path)};;"
            f"SP8_SIMPLE_SCAN_OUT_TSV:={gap_string(args.scan_tsv.resolve())};;"
        )
        cmd = [
            str(args.gap),
            "-q",
            "--quitonbreak",
            "-K",
            args.gap_workspace,
            "-c",
            expr,
            str(SCRIPT_DIR / "sp8_scan_simple_nonabelian.g"),
        ]
        subprocess.run(cmd, check=True, text=True)


def read_scan_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def read_normalizer_rows(path: Path) -> dict[int, dict[str, int]]:
    if not path.exists():
        return {}
    with path.open(newline="") as f:
        return {
            int(row["rep_id"]): {
                "normalizer_order": int(row["normalizer_order"]),
                "actual_subgroups": int(row["conjugacy_class_size"]),
            }
            for row in csv.DictReader(f, delimiter="\t")
        }


def orbit_pattern_from_fingerprint(value: str) -> str:
    prefix = "orbits=["
    start = value.find(prefix)
    if start < 0:
        return ""
    start += len(prefix)
    end = value.find("]", start)
    if end < 0:
        return ""
    return ",".join(item.strip() for item in value[start:end].split(",") if item.strip())


def enrich_simple_rows(
    rows: list[dict[str, str]],
    *,
    run_dir: Path,
    normalizer_tsv: Path,
) -> list[dict[str, object]]:
    normalizers = read_normalizer_rows(normalizer_tsv)
    simple_rows = []
    for row in rows:
        if row["is_nonabelian_simple"] != "true":
            continue
        rep_id = int(row["rep_id"])
        rep_json = read_json(run_dir / "reps" / f"rep_{rep_id}.json")
        normalizer = normalizers.get(rep_id, {})
        structure = row["structure"]
        simple_rows.append(
            {
                "rep_id": rep_id,
                "order": int(row["order"]),
                "structure": structure,
                "alias": ALIASES.get(structure, "-"),
                "composition_factor_count": int(row["composition_factor_count"]),
                "normalizer_order": normalizer.get("normalizer_order"),
                "actual_subgroups": normalizer.get("actual_subgroups"),
                "orbit_lengths": orbit_pattern_from_fingerprint(rep_json.get("fingerprint", "")),
                "parent_count": len(rep_json.get("parent_ids", [])),
                "maximal_count": rep_json.get("maximal_count"),
            }
        )
    return sorted(simple_rows, key=lambda item: (int(item["order"]), str(item["structure"]), int(item["rep_id"])))


def summarize_simple_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, int], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        key = (str(row["structure"]), int(row["order"]))
        grouped[key].append(row)

    summary = []
    for (structure, order), items in grouped.items():
        rep_ids = sorted(int(item["rep_id"]) for item in items)
        normalizer_orders = [
            int(item["normalizer_order"])
            for item in items
            if item.get("normalizer_order") is not None
        ]
        actual_subgroups = [
            int(item["actual_subgroups"])
            for item in items
            if item.get("actual_subgroups") is not None
        ]
        summary.append(
            {
                "structure": structure,
                "alias": ALIASES.get(structure, "-"),
                "order": order,
                "classes": len(rep_ids),
                "rep_ids": rep_ids,
                "normalizer_orders": normalizer_orders,
                "actual_subgroups": sum(actual_subgroups) if actual_subgroups else None,
                "orbit_patterns": [str(item["orbit_lengths"]) for item in items],
            }
        )
    return sorted(summary, key=lambda item: (int(item["order"]), str(item["structure"])))


def fmt_int(value: int) -> str:
    return f"{value:,}"


def display_path(path: Path) -> str:
    path = path.resolve()
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def rep_id_preview(rep_ids: list[int], limit: int = 12) -> str:
    shown = ", ".join(str(rep_id) for rep_id in rep_ids[:limit])
    remaining = len(rep_ids) - limit
    if remaining > 0:
        return f"{shown}, ... (+{remaining} more)"
    return shown


def format_cell(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, int):
        return str(value)
    return str(value)


def format_collected(values: list[object], *, numeric: bool = False, separator: str = "<br>") -> str:
    counts = defaultdict(int)
    for value in values:
        counts[value] += 1
    if numeric:
        keys = sorted(counts, key=lambda item: int(item))
        labels = [fmt_int(int(key)) for key in keys]
    else:
        keys = sorted(counts, key=str)
        labels = [str(key) for key in keys]
    parts = []
    for key, label in zip(keys, labels):
        count = counts[key]
        if count == 1:
            parts.append(label)
        else:
            parts.append(f"{label} x {count}")
    return separator.join(parts)


def write_simple_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    fieldnames = [
        "rep_id",
        "structure",
        "alias",
        "order",
        "normalizer_order",
        "actual_subgroups",
        "orbit_lengths",
        "parent_count",
        "maximal_count",
        "composition_factor_count",
    ]
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, delimiter="\t", fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: format_cell(row.get(key)) for key in fieldnames})


def write_markdown(
    path: Path,
    *,
    run_dir: Path,
    scan_tsv: Path,
    simple_tsv: Path,
    candidate_count: int,
    rows: list[dict[str, object]],
    summary: list[dict[str, object]],
) -> None:
    simple_class_count = sum(int(item["classes"]) for item in summary)
    actual_simple_subgroups = sum(
        int(item["actual_subgroups"])
        for item in summary
        if item.get("actual_subgroups") is not None
    )
    generated_at = datetime.now(timezone.utc).isoformat()
    lines = [
        "# Nonabelian Simple Subgroups in `Sp(8,2)`",
        "",
        f"Generated at `{generated_at}` by `scripts/find_simple_nonabelian_subgroups.py`.",
        "",
        "The scan starts from the archived permutation representatives whose",
        "`rep_*.json` fingerprint has `solvable=false`.  GAP then reads the",
        "corresponding `rep_*.g` file and computes `CompositionSeries(H)`.",
        "A representative is recorded here exactly when that series has one",
        "nontrivial factor and `IsAbelian(H)` is false.  Normalizer orders and",
        "actual subgroup counts come from the completed normalizer pass.",
        "",
        "## Summary",
        "",
        "| Quantity | Value |",
        "| --- | ---: |",
        f"| Nonsolvable representative classes scanned | {fmt_int(candidate_count)} |",
        f"| Nonabelian simple representative classes | {fmt_int(simple_class_count)} |",
        f"| Distinct nonabelian simple isomorphism types | {fmt_int(len(summary))} |",
        f"| Actual nonabelian simple subgroups | {fmt_int(actual_simple_subgroups)} |",
        f"| Full scan rows | `{display_path(scan_tsv)}` |",
        f"| Simple representative rows | `{display_path(simple_tsv)}` |",
        f"| Run directory | `{display_path(run_dir)}` |",
        "",
        "The `O(9,2)` / `Sp(8,2)` row is the ambient group itself.",
        "",
        "## Isomorphism Types",
        "",
        "| Simple group | Alias | Order | `Sp(8,2)`-classes | Actual subgroups | Normalizer orders | Degree-120 orbit patterns | Representative ids |",
        "| --- | --- | ---: | ---: | ---: | --- | --- | --- |",
    ]
    for item in summary:
        lines.append(
            "| {structure} | {alias} | {order} | {classes} | {actual} | {normalizers} | {orbits} | `{rep_ids}` |".format(
                structure=item["structure"],
                alias=item["alias"],
                order=fmt_int(int(item["order"])),
                classes=fmt_int(int(item["classes"])),
                actual=fmt_int(int(item["actual_subgroups"])) if item.get("actual_subgroups") is not None else "",
                normalizers=format_collected(item["normalizer_orders"], numeric=True),  # type: ignore[arg-type]
                orbits=format_collected(item["orbit_patterns"]),  # type: ignore[arg-type]
                rep_ids=rep_id_preview(item["rep_ids"]),  # type: ignore[arg-type]
            )
        )

    lines.extend(
        [
            "",
            "## Representative Details",
            "",
            "| Rep id | Simple group | Order | Normalizer order | Actual subgroups | Degree-120 orbits | Parent count | Maximal-subgroup classes |",
            "| ---: | --- | ---: | ---: | ---: | --- | ---: | ---: |",
        ]
    )
    for row in rows:
        lines.append(
            "| {rep_id} | {structure} | {order} | {normalizer} | {actual} | `{orbits}` | {parents} | {maximals} |".format(
                rep_id=row["rep_id"],
                structure=row["structure"],
                order=fmt_int(int(row["order"])),
                normalizer=fmt_int(int(row["normalizer_order"])) if row.get("normalizer_order") is not None else "",
                actual=fmt_int(int(row["actual_subgroups"])) if row.get("actual_subgroups") is not None else "",
                orbits=row["orbit_lengths"],
                parents=row["parent_count"],
                maximals=row["maximal_count"],
            )
        )
    path.write_text("\n".join(lines) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, default=DEFAULT_RUN_DIR)
    parser.add_argument("--gap", type=Path, default=DEFAULT_GAP)
    parser.add_argument("--gap-workspace", default="2g")
    parser.add_argument("--out-md", type=Path, default=DEFAULT_OUT_MD)
    parser.add_argument("--simple-tsv", type=Path, default=DEFAULT_SIMPLE_TSV)
    parser.add_argument("--scan-tsv", type=Path, default=DEFAULT_SCAN_TSV)
    parser.add_argument("--normalizer-tsv", type=Path, default=DEFAULT_NORMALIZER_TSV)
    parser.add_argument("--skip-gap", action="store_true")
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()

    run_dir = args.run_dir.resolve()
    candidates = load_candidates(run_dir, args.limit)
    if not args.skip_gap:
        run_gap_scan(args, candidates)

    scan_rows = read_scan_rows(args.scan_tsv)
    rows = enrich_simple_rows(scan_rows, run_dir=run_dir, normalizer_tsv=args.normalizer_tsv)
    summary = summarize_simple_rows(rows)
    args.out_md.parent.mkdir(parents=True, exist_ok=True)
    write_simple_tsv(args.simple_tsv, rows)
    write_markdown(
        args.out_md,
        run_dir=run_dir,
        scan_tsv=args.scan_tsv,
        simple_tsv=args.simple_tsv,
        candidate_count=len(candidates),
        rows=rows,
        summary=summary,
    )
    print(f"Scanned nonsolvable representatives: {len(candidates)}")
    print(f"Nonabelian simple representative classes: {sum(item['classes'] for item in summary)}")
    print(f"Distinct nonabelian simple isomorphism types: {len(summary)}")
    print(f"Wrote {args.out_md}")


if __name__ == "__main__":
    main()
