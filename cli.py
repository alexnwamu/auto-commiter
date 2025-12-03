import argparse
import sys

from core import generate_commit_message
from git_utils import add_staged_diff, commit_diff, push_branch


def _choose_message(options: list[str]) -> str:
    print("\nSelect a commit message:\n")
    for idx, msg in enumerate(options, start=1):
        print(f"Option {idx}:")
        print(msg)
        print("-" * 40)

    while True:
        choice = input("Enter 1 or 2 (or 'q' to cancel): ").strip()
        if choice in {"1", "2"}:
            return options[int(choice) - 1]
        if choice.lower() in {"q", "quit"}:
            return ""
        print("Invalid choice. Please enter 1, 2, or 'q'.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Auto-commiter: generate, commit, and push with AI messages.",
    )
    parser.add_argument(
        "--style",
        default="conventional",
        help="Commit message style (e.g. conventional).",
    )

    args = parser.parse_args(argv)

    print("[cli] Staging all changes (git add --all)...")
    if not add_staged_diff():
        print("[cli] Failed to stage changes. Aborting.")
        return 1

    print("[cli] Generating two commit message options...")
    msg1 = generate_commit_message(style=args.style)
    msg2 = generate_commit_message(style=args.style)

    if not msg1 or not msg2:
        print("[cli] Failed to generate commit messages. Aborting.")
        return 1

    chosen = _choose_message([msg1, msg2])
    if not chosen:
        print("[cli] Commit cancelled by user.")
        return 0

    print("[cli] Committing with selected message...")
    if not commit_diff(chosen):
        print("[cli] git commit failed. Aborting before push.")
        return 1

    print("[cli] Pushing current branch...")
    if not push_branch():
        print("[cli] git push failed. Please check your remote configuration.")
        return 1

    print("[cli] Commit and push completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
