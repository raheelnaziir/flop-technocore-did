#!/usr/bin/env python3
"""
prove_commit.py — optional step for Git-based contributions.

Signs a message that ties your DID to one exact, already-pushed public
commit, and publishes it to Technocore. This is only meaningful for a
commit that is actually public (pushed to GitHub) — signing a local-only
commit hash proves nothing to anyone else.

Usage:
    python src/prove_commit.py --room lobby \
        --repo-url https://github.com/<you>/<repo> \
        --commit <full-commit-sha>
"""

import argparse
import subprocess
import sys

from publish import publish, DEFAULT_BASE_URL


def get_head_sha() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()


def main() -> None:
    parser = argparse.ArgumentParser(description="Publish a signed proof tying your DID to a public commit.")
    parser.add_argument("--room", required=True)
    parser.add_argument("--repo-url", required=True, help="Public GitHub repo URL")
    parser.add_argument("--commit", default=None, help="Full commit SHA (defaults to current HEAD)")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    args = parser.parse_args()

    commit = args.commit or get_head_sha()
    if len(commit) < 40:
        print("Warning: that doesn't look like a full 40-char commit SHA.")

    text = f"proof: contribution at {args.repo_url} commit {commit}"
    publish(args.base_url, args.room, text)
    print()
    print("Make sure this commit is actually pushed and public before (or right after) running this,")
    print("so anyone reading the room can independently check it.")


if __name__ == "__main__":
    sys.exit(main())
