# Sp(8,2) subgroup classification

This repository publishes the `Sp(8,2)` subgroup-classification scripts together with a compact result summary from the completed classification. The full classified-group run data is archived separately outside Git.

## Layout

- `scripts/`: GAP and Python orchestration scripts.
- `results/`: compact result summary and completion certificate.

## Result

The completed run classified 657,007 conjugacy classes of subgroups of
`Sp(8,2)`, using a faithful degree-120 permutation representation.  See
`results/README.md` and `results/completion_certificate.json`.

## Regenerate the GitHub Result Summary

From this repository root:

```sh
python3 scripts/export_sp8_github_results.py
```

The exporter writes summaries to `results/`. When regenerating from archived run
data, pass `--run-dir` explicitly to point at the external restored run
directory.

## Archive a Completed Run

To archive a completed run into large, reproducible tarballs and publish them to
an external archive directory, use:

```sh
scripts/archive_sp8_run.sh \
	/path/to/restored-or-local-run \
	/path/to/archive-root
```

The archiver stages each `.tar.zst` file locally, writes SHA-256 checksums,
copies into a temporary destination filename, validates the copied checksum, and
only then publishes the final archive in the destination directory. The full
classified groups are intended to live in that external archive, not in this
repository.

To track an active archive run:

```sh
watch -n 15 'scripts/archive_sp8_status.sh /path/to/restored-or-local-run /path/to/archive-root'
```
