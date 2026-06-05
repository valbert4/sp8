#!/usr/bin/env python3
"""Read and verify packed Sp(8,2) matrix-generator shards."""

from __future__ import annotations

import argparse
import csv
import json
import random
import subprocess
import tempfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_MATRIX_DIR = REPO_ROOT / "results" / "matrix_generators"
DEFAULT_RUN_DIR = SCRIPT_DIR / "work_sp8" / "run_20260527_130624"
DEFAULT_GAP = Path("/home/valbert/gap-4.15.1/gap")
MATRIX_BYTES = 8


def gap_string(value: str | Path) -> str:
    s = str(value)
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def read_json(path: Path) -> dict:
    return json.loads(path.read_text())


def iter_index_rows(matrix_dir: Path):
    for index_path in sorted(matrix_dir.glob("shard_*.index.tsv")):
        shard_stem = index_path.name.removesuffix(".index.tsv")
        bin_path = matrix_dir / f"{shard_stem}.bin"
        with index_path.open(newline="") as f:
            reader = csv.DictReader(f, delimiter="\t")
            for row in reader:
                yield {
                    "rep_id": int(row["rep_id"]),
                    "order": int(row["order"]),
                    "matrix_offset": int(row["matrix_offset"]),
                    "generator_count": int(row["generator_count"]),
                    "generator_orders": row["generator_orders"],
                    "matrix_bytes": int(row["matrix_bytes"]),
                    "bin_path": bin_path,
                    "index_path": index_path,
                }


def load_index(matrix_dir: Path) -> dict[int, dict]:
    return {row["rep_id"]: row for row in iter_index_rows(matrix_dir)}


def unpack_matrix(data: bytes) -> list[list[int]]:
    if len(data) != MATRIX_BYTES:
        raise ValueError(f"expected {MATRIX_BYTES} bytes, got {len(data)}")
    rows = []
    for byte in data:
        rows.append([(byte >> shift) & 1 for shift in range(7, -1, -1)])
    return rows


def matrix_hex_for_row(row: dict) -> str:
    with row["bin_path"].open("rb") as f:
        f.seek(row["matrix_offset"] * MATRIX_BYTES)
        data = f.read(row["generator_count"] * MATRIX_BYTES)
    if len(data) != row["generator_count"] * MATRIX_BYTES:
        raise ValueError(f"short read for rep {row['rep_id']}")
    return data.hex()


def matrices_for_row(row: dict) -> list[list[list[int]]]:
    hex_data = matrix_hex_for_row(row)
    raw = bytes.fromhex(hex_data)
    return [
        unpack_matrix(raw[i : i + MATRIX_BYTES])
        for i in range(0, len(raw), MATRIX_BYTES)
    ]


def cmd_info(args: argparse.Namespace) -> None:
    matrix_dir = args.matrix_dir.resolve()
    manifest = read_json(matrix_dir / "manifest.json")
    print(json.dumps(manifest, indent=2, sort_keys=True))


def cmd_show(args: argparse.Namespace) -> None:
    rows = load_index(args.matrix_dir.resolve())
    row = rows[args.rep_id]
    payload = {
        "rep_id": row["rep_id"],
        "order": row["order"],
        "generator_count": row["generator_count"],
        "generator_orders": row["generator_orders"],
        "matrices": matrices_for_row(row),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))


def expected_gap_file(rows: list[dict], path: Path) -> None:
    lines = ["SP8_EXPECTED_MATRIX_HEX := [\n"]
    for row in rows:
        lines.append(
            f"  [ {row['rep_id']}, \"{matrix_hex_for_row(row)}\", "
            f"{row['order']}, {row['generator_count']} ],\n"
        )
    lines.append("];;\n")
    path.write_text("".join(lines))


def cmd_verify(args: argparse.Namespace) -> None:
    matrix_dir = args.matrix_dir.resolve()
    index = load_index(matrix_dir)
    if args.rep_id:
        ids = args.rep_id
    else:
        ids = sorted(index)
        if args.sample and args.sample < len(ids):
            rng = random.Random(args.seed)
            ids = sorted(rng.sample(ids, args.sample))
    rows = [index[rep_id] for rep_id in ids]
    with tempfile.TemporaryDirectory(prefix="sp8_matrix_verify.") as tmpdir:
        expected_path = Path(tmpdir) / "expected.g"
        expected_gap_file(rows, expected_path)
        expr = (
            f"SCRIPT_DIR:={gap_string(SCRIPT_DIR)};;"
            f"RUN_DIR:={gap_string(args.run_dir.resolve())};;"
            f"EXPECTED_PATH:={gap_string(expected_path)};;"
            f"DIM:=8;;"
            f"USE_SMALL_GENERATING_SET:={'true' if args.small_generating_set else 'false'};;"
        )
        cmd = [
            str(args.gap),
            "-q",
            "--quitonbreak",
            "-K",
            args.gap_workspace,
            "-c",
            expr,
            str(SCRIPT_DIR / "sp8_verify_matrix_export.g"),
        ]
        subprocess.run(cmd, check=True, text=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--matrix-dir", type=Path, default=DEFAULT_MATRIX_DIR)
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_info = sub.add_parser("info")
    p_info.set_defaults(func=cmd_info)

    p_show = sub.add_parser("show")
    p_show.add_argument("rep_id", type=int)
    p_show.set_defaults(func=cmd_show)

    p_verify = sub.add_parser("verify")
    p_verify.add_argument("--run-dir", type=Path, default=DEFAULT_RUN_DIR)
    p_verify.add_argument("--gap", type=Path, default=DEFAULT_GAP)
    p_verify.add_argument("--gap-workspace", default="2g")
    p_verify.add_argument("--rep-id", type=int, action="append")
    p_verify.add_argument("--sample", type=int, default=10)
    p_verify.add_argument("--seed", type=int, default=1)
    p_verify.add_argument("--small-generating-set", action="store_true")
    p_verify.set_defaults(func=cmd_verify)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
