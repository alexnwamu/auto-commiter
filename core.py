from git_utils import get_staged_diff, get_branch_name
from models.openai_chat import OpenAIModel
from models.rule_based import RuleBasedModel


MAX_RULE_BASED_DIFF_CHARS = 7800


def generate_commit_message(style: str | None = None):
    print("[core] Fetching staged diff...")
    diff = get_staged_diff()
    branch_name = get_branch_name()
    diff_length = len(diff)
    print(f"[core] Diff length: {diff_length} characters")
    print(f"[core] Branch name: {branch_name}")
    if not diff:
        print("[core] No staged changes detected. Stage some files and try again.")
        return ""

    effective_style = style or "conventional"

    if diff_length <= MAX_RULE_BASED_DIFF_CHARS:
        print("[core] Using RuleBasedModel...")
        model = RuleBasedModel(style=effective_style)
    else:
        print(
            f"[core] Diff too large for RuleBasedModel "
            f"({diff_length} > {MAX_RULE_BASED_DIFF_CHARS}). Using OpenAIModel..."
        )
        model = OpenAIModel(style=effective_style)

    message = model.generate_commit_message(diff + f"\n\nBranch: {branch_name}")
    print("[core] Model returned a commit message.")
    return message


if __name__ == "__main__":
    print("[core] Running core.py as a script.")
    commit_message = generate_commit_message(style="conventional")
    print("[core] Final commit message:")
    print(commit_message)
