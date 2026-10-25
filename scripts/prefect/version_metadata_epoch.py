#!/usr/bin/env python3
"""Select the reproducible version/branding metadata date, never a build date.

SOURCE_DATE_EPOCH controls CMake TIMESTAMP in libslic3r_version.h. Ordinary GUI
implementation edits must not change this shared header or invalidate every PCH.
Actual source provenance remains HEAD/GITHUB_SHA and PREFECT-COMMIT.txt.
"""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys


VERSION_INPUTS = (
    "version.inc",
    "src/libslic3r/libslic3r.h",
    "src/libslic3r/libslic3r_version.h.in",
    "src/libslic3r/CMakeLists.txt",
)


def git(root, *args, check=True):
    env = dict(os.environ, GIT_OPTIONAL_LOCKS="0", GIT_NO_LAZY_FETCH="1")
    result = subprocess.run(["git", "-C", str(root), *args], env=env,
                            capture_output=True, text=True, encoding="utf-8")
    if check and result.returncode:
        raise ValueError(f"Git {args[0]} failed while selecting version metadata epoch")
    return result


def select_epoch(workspace, *, revision=None, deepen=False):
    root = Path(workspace).resolve()
    head = git(root, "rev-parse", "HEAD").stdout.strip()
    if not re.fullmatch(r"[0-9a-f]{40}", head):
        raise ValueError("Expected a full current source commit")
    if revision is not None and revision != head:
        raise ValueError("Pinned revision differs from the checked-out source")
    if deepen and revision is None:
        raise ValueError("History deepening requires the exact checked-out revision")
    git(root, "ls-files", "--error-unmatch", "--", *VERSION_INPUTS)
    if git(root, "diff", "--quiet", "HEAD", "--", *VERSION_INPUTS, check=False).returncode:
        raise ValueError("Version metadata inputs must match the committed source")
    while True:
        row = git(root, "log", "-1", "--format=%H %ct", "--", *VERSION_INPUTS).stdout.strip()
        match = re.fullmatch(r"([0-9a-f]{40}) ([0-9]+)", row)
        if not match:
            raise ValueError("Cannot determine a committed version metadata date")
        commit, epoch = match.groups()
        shallow_file = Path(git(root, "rev-parse", "--git-path", "shallow").stdout.strip())
        if not shallow_file.is_absolute():
            shallow_file = root / shallow_file
        boundaries = shallow_file.read_text(encoding="ascii").splitlines() if shallow_file.exists() else []
        if commit not in boundaries:
            return {"source_commit": head, "version_metadata_commit": commit,
                    "version_metadata_epoch": int(epoch), "version_metadata_inputs": list(VERSION_INPUTS)}
        if not deepen:
            raise ValueError("Version metadata commit is at a shallow boundary; exact history is required")
        before = boundaries
        git(root, "fetch", "--no-tags", "--deepen=32", "origin", revision)
        after = shallow_file.read_text(encoding="ascii").splitlines() if shallow_file.exists() else []
        if after == before:
            raise ValueError("History deepening did not advance the shallow boundary")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", required=True, type=Path)
    parser.add_argument("--revision")
    parser.add_argument("--deepen", action="store_true")
    parser.add_argument("--github-env", type=Path)
    args = parser.parse_args()
    try:
        result = select_epoch(args.workspace, revision=args.revision, deepen=args.deepen)
        if args.github_env:
            with args.github_env.open("a", encoding="utf-8", newline="\n") as output:
                output.write(f"VERSION_METADATA_COMMIT={result['version_metadata_commit']}\n")
                output.write(f"VERSION_METADATA_EPOCH={result['version_metadata_epoch']}\n")
                output.write(f"SOURCE_DATE_EPOCH={result['version_metadata_epoch']}\n")
        print(json.dumps(result, sort_keys=True))
    except (ValueError, OSError) as error:
        print(f"Version metadata epoch: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
