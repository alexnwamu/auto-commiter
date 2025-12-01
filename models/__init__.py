"""Model backends for generating commit messages.

This package is where you keep different ways of turning a git diff into
an actual commit message string:
- OpenAI-based models.
- Local Hugging Face models.
- Simple rule-based/heuristic approaches.
"""

# Hints:
# - You can re-export commonly used classes here (e.g. OpenAIModel) if you
#   want slightly nicer import paths in the rest of your code.
