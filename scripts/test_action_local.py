"""
scripts/test_action_local.py
============================
Simulates the GitHub Action locally without needing a real PR.

Requires the FastAPI server to already be running on localhost:8000:
    uvicorn src.api.app:app --reload --port 8000

Usage
-----
  # Diff against main/master (what the CI would see for a PR):
  python scripts/test_action_local.py

  # Diff against a specific base branch or commit:
  python scripts/test_action_local.py --base origin/master

  # Analyse specific files directly:
  python scripts/test_action_local.py --files src/model/train.py src/api/app.py

  # Analyse ALL Python files in src/ (stress test):
  python scripts/test_action_local.py --all
"""

import argparse
import subprocess
import sys
from pathlib import Path

# Add project root to path so run_analysis can be imported
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.run_analysis import run   # noqa: E402


def git_changed_files(base: str) -> list[str]:
    """Return .py files changed relative to base branch/commit."""
    try:
        result = subprocess.run(
            ["git", "diff", "--diff-filter=ACM", "--name-only", base, "HEAD"],
            capture_output=True, text=True, check=True, cwd=ROOT,
        )
        files = [f.strip() for f in result.stdout.splitlines() if f.strip().endswith(".py")]
        return files
    except subprocess.CalledProcessError as e:
        print(f"git diff failed: {e.stderr.strip()}")
        return []


def all_src_files() -> list[str]:
    return [str(p.relative_to(ROOT)) for p in (ROOT / "src").rglob("*.py")]


def check_server() -> bool:
    """Return True if the API server is reachable."""
    import urllib.request
    try:
        urllib.request.urlopen("http://localhost:8000/health", timeout=3)
        return True
    except Exception:
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Test the Graphault GitHub Action locally"
    )
    parser.add_argument(
        "--base", default="origin/master",
        help="Base branch/commit to diff against (default: origin/master)"
    )
    parser.add_argument(
        "--files", nargs="+",
        help="Explicit list of Python files to analyse (skips git diff)"
    )
    parser.add_argument(
        "--all", action="store_true",
        help="Analyse all .py files under src/ (ignores git diff)"
    )
    args = parser.parse_args()

    # ── Server check ─────────────────────────────────────────────────────────
    if not check_server():
        print("ERROR: FastAPI server is not running.")
        print("Start it with:  uvicorn src.api.app:app --reload --port 8000")
        sys.exit(1)
    print("Server: OK (http://localhost:8000)\n")

    # ── Resolve file list ────────────────────────────────────────────────────
    if args.files:
        file_paths = args.files
        print(f"Mode: explicit files ({len(file_paths)} provided)")
    elif args.all:
        file_paths = all_src_files()
        print(f"Mode: all src/ files ({len(file_paths)} found)")
    else:
        file_paths = git_changed_files(args.base)
        print(f"Mode: git diff vs {args.base} ({len(file_paths)} changed Python files)")
        if not file_paths:
            print("\nNo changed Python files found. Try --files or --all.")
            sys.exit(0)

    print(f"Files to analyse: {file_paths}\n")

    # ── Run analysis (same logic as the CI action) ───────────────────────────
    comment = run(file_paths)

    output = Path("analysis_comment.md")
    output.write_text(comment, encoding="utf-8")
    print(f"\n{'='*60}")
    print("PR COMMENT PREVIEW (analysis_comment.md)")
    print("="*60)
    sys.stdout.buffer.write(comment.encode("utf-8"))
    sys.stdout.buffer.write(b"\n")
    sys.stdout.buffer.flush()
    print("="*60)
    print(f"\nFull output written to: {output.resolve()}")


if __name__ == "__main__":
    main()
