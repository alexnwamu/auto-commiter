"""Tests for model backends (OpenAI, HF local, rule-based).

These tests should check that each backend producing commit messages
conforms to the same simple interface and basic expectations.
"""

# Hints:
# - Start by testing the simplest backend (e.g. the rule-based model)
#   since it does not require network access.
# - For OpenAI or HF-based models, you can:
#   - Use mock objects or monkeypatching to avoid real API calls.
#   - Assert that prompt-building and parameter-passing behave as expected.
# - It can be helpful to enforce that `generate_commit_message` always
#   returns a non-empty string and never raises for normal input.
