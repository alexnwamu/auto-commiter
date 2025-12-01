"""Simple rule-based commit message generator (placeholder).

This file is useful for:
- Having a fallback when no AI model is available.
- Quickly testing your CLI end-to-end without hitting external APIs.
- Encoding small, deterministic heuristics for certain types of changes.
"""

# Hints:
# - You can analyze the diff text for patterns, e.g.:
#   - Filenames ("README", "tests", specific modules).
#   - Whether lines are mostly additions vs. deletions.
# - Based on these patterns, return messages such as:
#   - "Update documentation"
#   - "Add tests for <module>"
#   - "Refactor <component>"
# - Keeping this very simple makes it a good starting point for tests and
#   for running in environments without network access.
