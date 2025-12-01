"""Core orchestration logic for generating commit messages.

This file should act as the glue between:
- Git utilities (for fetching the staged diff).
- Model backends (OpenAI, Hugging Face, rule-based, etc.).
- Any formatting or post-processing of the final commit message.
"""

# Hints:
# - A common pattern is to define a function like
#     generate_commit_message(style: str | None = None) -> str
#   which is called by your CLI.
# - Inside that function, you might:
#   1. Fetch the staged diff using a helper from `git_utils`.
#   2. Build a prompt using a helper from `formatting`.
#   3. Select a model/strategy (e.g. via a function from `strategies`).
#   4. Call the model to get a commit message string.
#   5. Optionally apply some final cleanup or validation.
# - Try to keep this file free of direct OpenAI/HF calls; those belong in
#   the `models/` package. This keeps your architecture clean and testable.

from git_utils import get_staged_diff, get_branch_name
from models.openai_chat import OpenAIModel


def generate_commit_message(style: str | None = None):
    print("[core] Fetching staged diff...")
    diff = get_staged_diff()
    branch_name = get_branch_name()
    print(f"[core] Diff length: {len(diff)} characters")
    print(f"[core] Branch name: {branch_name}")
    if not diff:
        print("[core] No staged changes detected. Stage some files and try again.")
        return ""

    print("[core] Initializing OpenAIModel...")
    message = OpenAIModel(style=style).generate_commit_message(diff + branch_name)
    print("[core] Model returned a commit message.")
    return message


if __name__ == "__main__":
    print("[core] Running core.py as a script.")
    commit_message = generate_commit_message(style="conventional")
    print("[core] Final commit message:")
    print(commit_message)
