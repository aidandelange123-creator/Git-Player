#!/usr/bin/env python3
"""Git-Player: a tiny CLI for exploring repository activity."""

from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Commit:
    sha: str
    author: str
    date: str
    subject: str


def run_git_command(repo: Path, args: list[str]) -> str:
    """Run a git command and return stdout or fail with a friendly message."""
    command = ["git", "-C", str(repo), *args]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        message = result.stderr.strip() or "Unknown git error"
        raise RuntimeError(f"git command failed ({' '.join(args)}): {message}")
    return result.stdout


def recent_commits(repo: Path, limit: int) -> list[Commit]:
    raw = run_git_command(
        repo,
        [
            "log",
            f"--max-count={limit}",
            "--date=short",
            "--pretty=format:%h%x1f%an%x1f%ad%x1f%s",
        ],
    )
    commits: list[Commit] = []
    for line in raw.splitlines():
        if not line.strip():
            continue
        sha, author, date, subject = line.split("\x1f")
        commits.append(Commit(sha=sha, author=author, date=date, subject=subject))
    return commits


def contributor_stats(repo: Path, limit: int) -> list[tuple[str, int]]:
    raw = run_git_command(repo, ["shortlog", "-s", "-n", f"--all", f"--max-count={limit}"])
    stats: list[tuple[str, int]] = []
    for line in raw.splitlines():
        parts = line.strip().split("\t")
        if len(parts) == 2 and parts[0].strip().isdigit():
            stats.append((parts[1].strip(), int(parts[0].strip())))
    return stats


def hot_files(repo: Path, limit: int) -> list[tuple[int, str]]:
    raw = run_git_command(repo, ["log", f"--max-count={limit}", "--name-only", "--pretty=format:"])
    counts: dict[str, int] = {}
    for line in raw.splitlines():
        filename = line.strip()
        if not filename:
            continue
        counts[filename] = counts.get(filename, 0) + 1
    return sorted(((count, name) for name, count in counts.items()), reverse=True)


def print_commits(commits: list[Commit]) -> None:
    if not commits:
        print("No commits found.")
        return

    print("Recent commits:")
    for commit in commits:
        print(f"  {commit.sha:<8} {commit.date}  {commit.author:<18} {commit.subject}")


def print_contributors(stats: list[tuple[str, int]]) -> None:
    if not stats:
        print("No contributors found.")
        return

    print("Top contributors:")
    for author, count in stats:
        print(f"  {count:>4}  {author}")


def print_hot_files(files: list[tuple[int, str]], top: int) -> None:
    if not files:
        print("No file activity found.")
        return

    print(f"Hot files (top {top}):")
    for count, name in files[:top]:
        print(f"  {count:>4}  {name}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="git-player",
        description="Explore commit history as a quick activity dashboard.",
    )
    parser.add_argument("--repo", type=Path, default=Path.cwd(), help="Repository path (default: current directory)")
    parser.add_argument("--limit", type=int, default=20, help="How many recent commits to inspect")
    parser.add_argument(
        "--view",
        choices=["commits", "contributors", "files", "all"],
        default="all",
        help="Which report to show",
    )
    parser.add_argument("--top-files", type=int, default=10, help="How many hot files to print")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.limit <= 0:
        print("--limit must be greater than zero", file=sys.stderr)
        return 2
    if args.top_files <= 0:
        print("--top-files must be greater than zero", file=sys.stderr)
        return 2

    repo = args.repo.resolve()
    if not (repo / ".git").exists():
        print(f"Not a git repository: {repo}", file=sys.stderr)
        return 2

    try:
        if args.view in ("commits", "all"):
            print_commits(recent_commits(repo, args.limit))
            if args.view == "all":
                print()

        if args.view in ("contributors", "all"):
            print_contributors(contributor_stats(repo, args.limit))
            if args.view == "all":
                print()

        if args.view in ("files", "all"):
            print_hot_files(hot_files(repo, args.limit), args.top_files)
    except RuntimeError as error:
        print(str(error), file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
