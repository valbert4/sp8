#!/usr/bin/env python3
"""Export Sp(8,2) subgroup representatives as packed 8x8 GF(2) matrices."""

from __future__ import annotations

import argparse
import csv
import json
import os
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_GAP = Path("/home/valbert/gap-4.15.1/gap")
DEFAULT_RUN_DIR = SCRIPT_DIR / "work_sp8" / "run_20260527_130624"
DEFAULT_OUT_DIR = REPO_ROOT / "results" / "matrix_generators"
MATRIX_BYTES = 8


def gap_string(value: str | Path) -> str:
    s = str(value)
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def read_json(path: Path) -> dict:
    return json.loads(path.read_text())


def latest_representative_count(run_dir: Path) -> int:
    latest_path = run_dir / "snapshots" / "latest"
    if latest_path.exists():
        latest_name = latest_path.read_text().strip()
        latest = read_json(run_dir / "snapshots" / latest_name)
        if "representative_count" in latest:
            return int(latest["representative_count"])
    seq = run_dir / ".next_rep_id"
    if seq.exists():
        return int(seq.read_text().strip()) - 1
    raise SystemExit(f"cannot determine representative count for {run_dir}")


def write_format_docs(out_dir: Path) -> None:
    text = """# Packed Matrix Generator Format

This directory stores generators for representatives of subgroup conjugacy
classes of `Sp(8,2)` as compact 8x8 matrices over GF(2).

Each matrix is stored in exactly 8 bytes.  The packing is row-major and
most-significant-bit first:

- byte 0 stores row 1, columns 1 through 8;
- byte 1 stores row 2, columns 1 through 8;
- within a byte, column 1 is bit 7 and column 8 is bit 0.

For each shard, `shard_*.bin` is the concatenated matrix payload and
`shard_*.index.tsv` maps each representative id to its offset and generator
count.  Offsets are measured in matrices, not bytes.  The byte offset is
`matrix_offset * 8`.

The matrices are preimages under the faithful GAP map
`phi : Sp(8,2) -> P`, where `P` is the degree-120 permutation representation
used by the classification.  The verifier recomputes those preimages from the
archived permutation representatives and checks that the generated matrix
subgroup maps back onto the stored permutation subgroup.
"""
    (out_dir / "FORMAT.md").write_text(text)


def write_manifest(out_dir: Path, payload: dict) -> None:
    (out_dir / "manifest.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def run_gap_batch(
    *,
    gap: Path,
    run_dir: Path,
    start_id: int,
    end_id: int,
    temp_tsv: Path,
    use_small_generating_set: bool,
    gap_workspace: str,
) -> None:
    expr = (
        f"SCRIPT_DIR:={gap_string(SCRIPT_DIR)};;"
        f"RUN_DIR:={gap_string(run_dir)};;"
        f"START_ID:={start_id};;"
        f"END_ID:={end_id};;"
        f"OUT_PATH:={gap_string(temp_tsv)};;"
        f"DIM:=8;;"
        f"USE_SMALL_GENERATING_SET:={'true' if use_small_generating_set else 'false'};;"
    )
    cmd = [
        str(gap),
        "-q",
        "--quitonbreak",
        "-K",
        gap_workspace,
        "-c",
        expr,
        str(SCRIPT_DIR / "sp8_export_matrix_batch.g"),
    ]
    subprocess.run(cmd, check=True, text=True)


def convert_tsv_to_shard(temp_tsv: Path, bin_path: Path, index_path: Path) -> dict:
    total_reps = 0
    total_matrices = 0
    bin_tmp = bin_path.with_suffix(bin_path.suffix + ".tmp")
    index_tmp = index_path.with_suffix(index_path.suffix + ".tmp")
    with temp_tsv.open(newline="") as src, bin_tmp.open("wb") as bout, index_tmp.open("w", newline="") as iout:
        reader = csv.DictReader(src, delimiter="\t")
        writer = csv.writer(iout, delimiter="\t", lineterminator="\n")
        writer.writerow([
            "rep_id",
            "order",
            "matrix_offset",
            "generator_count",
            "generator_orders",
            "matrix_bytes",
        ])
        for row in reader:
            rep_id = int(row["rep_id"])
            order = int(row["order"])
            generator_count = int(row["generator_count"])
            matrix_hex = row["matrix_hex"]
            expected_len = 16 * generator_count
            if len(matrix_hex) != expected_len:
                raise ValueError(f"rep {rep_id}: expected {expected_len} hex chars, got {len(matrix_hex)}")
            offset = total_matrices
            if matrix_hex:
                bout.write(bytes.fromhex(matrix_hex))
            writer.writerow([
                rep_id,
                order,
                offset,
                generator_count,
                row["generator_orders"],
                generator_count * MATRIX_BYTES,
            ])
            total_reps += 1
            total_matrices += generator_count
    os.replace(bin_tmp, bin_path)
    os.replace(index_tmp, index_path)
    return {
        "representatives": total_reps,
        "matrices": total_matrices,
        "bytes": total_matrices * MATRIX_BYTES,
    }


def export_shard(args: tuple) -> dict:
    (
        shard_number,
        start_id,
        end_id,
        out_dir,
        gap,
        run_dir,
        use_small_generating_set,
        gap_workspace,
        keep_temp,
    ) = args
    shard_stem = f"shard_{shard_number:06d}"
    bin_path = out_dir / f"{shard_stem}.bin"
    index_path = out_dir / f"{shard_stem}.index.tsv"
    done_path = out_dir / f"{shard_stem}.done.json"
    if done_path.exists() and bin_path.exists() and index_path.exists():
        done = read_json(done_path)
        done["skipped_existing"] = True
        return done

    with tempfile.NamedTemporaryFile(
        prefix=f"{shard_stem}.",
        suffix=".gap.tsv",
        dir=out_dir,
        delete=False,
    ) as tmp:
        temp_tsv = Path(tmp.name)

    try:
        run_gap_batch(
            gap=gap,
            run_dir=run_dir,
            start_id=start_id,
            end_id=end_id,
            temp_tsv=temp_tsv,
            use_small_generating_set=use_small_generating_set,
            gap_workspace=gap_workspace,
        )
        stats = convert_tsv_to_shard(temp_tsv, bin_path, index_path)
        done = {
            "shard": shard_number,
            "start_id": start_id,
            "end_id": end_id,
            "bin": bin_path.name,
            "index": index_path.name,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            **stats,
        }
        done_path.write_text(json.dumps(done, indent=2, sort_keys=True) + "\n")
        return done
    finally:
        if not keep_temp:
            temp_tsv.unlink(missing_ok=True)


def shard_ranges(start_id: int, end_id: int, shard_size: int) -> list[tuple[int, int, int]]:
    ranges = []
    shard = 0
    cur = start_id
    while cur <= end_id:
        stop = min(end_id, cur + shard_size - 1)
        ranges.append((shard, cur, stop))
        cur = stop + 1
        shard += 1
    return ranges


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, default=DEFAULT_RUN_DIR)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--gap", type=Path, default=DEFAULT_GAP)
    parser.add_argument("--start-id", type=int, default=1)
    parser.add_argument("--end-id", type=int)
    parser.add_argument("--shard-size", type=int, default=50_000)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--gap-workspace", default="2g")
    parser.add_argument("--small-generating-set", action="store_true")
    parser.add_argument("--keep-temp", action="store_true")
    args = parser.parse_args()

    run_dir = args.run_dir.resolve()
    out_dir = args.out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    end_id = args.end_id or latest_representative_count(run_dir)
    if args.start_id < 1 or end_id < args.start_id:
        raise SystemExit("invalid representative id range")

    ranges = shard_ranges(args.start_id, end_id, args.shard_size)
    work = [
        (
            shard,
            start,
            stop,
            out_dir,
            args.gap,
            run_dir,
            args.small_generating_set,
            args.gap_workspace,
            args.keep_temp,
        )
        for shard, start, stop in ranges
    ]

    totals = {"representatives": 0, "matrices": 0, "bytes": 0}
    results = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(export_shard, item) for item in work]
        for future in as_completed(futures):
            done = future.result()
            results.append(done)
            totals["representatives"] += int(done["representatives"])
            totals["matrices"] += int(done["matrices"])
            totals["bytes"] += int(done["bytes"])
            print(
                f"shard {done['shard']:06d}: ids {done['start_id']}-{done['end_id']} "
                f"reps={done['representatives']} matrices={done['matrices']}"
            )

    results.sort(key=lambda item: item["shard"])
    manifest = {
        "format": "sp8_matrix_generators_v1",
        "ambient_group": "Sp(8,2)",
        "matrix_dimension": 8,
        "field": "GF(2)",
        "packing": {
            "bytes_per_matrix": MATRIX_BYTES,
            "order": "row-major",
            "bit_order": "most-significant-bit first within each row byte",
        },
        "run_dir": str(run_dir.relative_to(REPO_ROOT) if run_dir.is_relative_to(REPO_ROOT) else run_dir),
        "start_id": args.start_id,
        "end_id": end_id,
        "shard_size": args.shard_size,
        "small_generating_set": args.small_generating_set,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "totals": totals,
        "shards": results,
    }
    write_format_docs(out_dir)
    write_manifest(out_dir, manifest)
    print(json.dumps({"out_dir": str(out_dir), "totals": totals}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
