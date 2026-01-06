"""Core logic for generating commit messages.

This module orchestrates the commit message generation process,
selecting the appropriate model and handling caching.
"""

from git_utils import get_staged_diff, get_branch_name
from models.rule_based import RuleBasedModel
from cache import get_cached_message, cache_message
from settings import get_setting


MAX_RULE_BASED_DIFF_CHARS = 5000


def generate_commit_message(
    style: str | None = None,
    use_cache: bool | None = None,
    model_override: str | None = None,
) -> str:
    """Generate a commit message for staged changes.
    
    Args:
        style: Commit message style ('conventional', 'short', 'verbose')
        use_cache: Whether to use caching (defaults to setting)
        model_override: Force a specific model ('rule-based', 'openai', 'auto')
        
    Returns:
        Generated commit message string
    """
    print("[core] Fetching staged diff...")
    diff = get_staged_diff()
    branch_name = get_branch_name()
    diff_length = len(diff)
    
    print(f"[core] Diff length: {diff_length} characters")
    print(f"[core] Branch name: {branch_name}")
    
    if not diff:
        print("[core] No staged changes detected. Stage some files and try again.")
        return ""

    # Resolve settings
    effective_style = style or get_setting("style", "conventional")
    should_use_cache = use_cache if use_cache is not None else get_setting("use_cache", True)
    model_choice = model_override or get_setting("model", "auto")
    
    # Check cache first
    if should_use_cache:
        cached = get_cached_message(diff, effective_style)
        if cached:
            return cached
    
    # Select model
    max_diff = get_setting("max_diff_for_rules", MAX_RULE_BASED_DIFF_CHARS)
    
    if model_choice == "auto":
        if diff_length <= max_diff:
            print("[core] Using RuleBasedModel...")
            model = RuleBasedModel(style=effective_style)
        else:
            print(
                f"[core] Diff too large for RuleBasedModel "
                f"({diff_length} > {max_diff}). Using OpenAIModel..."
            )
            # Lazy import to avoid requiring API key when not needed
            from models.openai_chat import OpenAIModel
            model = OpenAIModel(style=effective_style)
    elif model_choice == "rule-based":
        print("[core] Using RuleBasedModel (forced)...")
        model = RuleBasedModel(style=effective_style)
    else:  # openai
        print("[core] Using OpenAIModel (forced)...")
        from models.openai_chat import OpenAIModel
        model = OpenAIModel(style=effective_style)

    # Generate message
    context = f"\n\nBranch: {branch_name}" if branch_name else ""
    message = model.generate_commit_message(diff + context)
    
    print("[core] Model returned a commit message.")
    
    # Cache the result
    if should_use_cache and message:
        cache_message(diff, effective_style, message)
    
    return message


if __name__ == "__main__":
    print("[core] Running core.py as a script.")
    commit_message = generate_commit_message(style="conventional")
    print("[core] Final commit message:")
    print(commit_message)
