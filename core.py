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
