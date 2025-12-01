"""CLI entry point for the AI commit message generator.

This file should:
- Parse command-line arguments (e.g. style/strategy flags, dry-run, etc.).
- Call into your core orchestration logic to generate a commit message.
- Print the final message or optionally run `git commit -m "<message>"`.
"""

# Hints:
# - Consider using the built-in `argparse` module for flags like:
#   - `--style` / `--strategy` to choose OpenAI vs. rule-based vs. other backends.
#   - `--dry-run` to only print the suggestion without committing.
# - Implement a `main()` function that:
#   1. Parses CLI arguments.
#   2. Calls into your core module (e.g. a `generate_commit_message` function).
#   3. Handles errors nicely (no staged changes, missing API key, etc.).
# - Wire this file up in `pyproject.toml` under `[project.scripts]`, e.g.:
#   ai-commit = "cli:main"
