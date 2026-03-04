# Git-Player

Git-Player is a tiny command-line dashboard for exploring git history.

## New features

- **Recent commit stream** with SHA, date, author, and subject.
- **Top contributor leaderboard** from git shortlog data.
- **Hot file tracking** showing which files changed most in recent commits.
- **View selector** so you can print one report (`commits`, `contributors`, `files`) or all at once.

## Usage

```bash
python3 git_player.py --repo /path/to/repo --limit 30 --view all --top-files 8
```

### Examples

```bash
# Show only recent commits in the current repo
python3 git_player.py --view commits

# Show top contributors from the last 100 commits
python3 git_player.py --view contributors --limit 100

# Show hottest files from last 50 commits
python3 git_player.py --view files --limit 50 --top-files 15
```
