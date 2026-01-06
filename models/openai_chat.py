"""OpenAI-based commit message generator."""

from openai import OpenAI
from .base import BaseCommitModel


class OpenAIModel(BaseCommitModel):
    """Uses OpenAI API to generate commit messages."""
    
    def __init__(self, style: str = "conventional"):
        self.style = style
        self._client = None
    
    @property
    def client(self) -> OpenAI:
        """Lazy initialization of OpenAI client."""
        if self._client is None:
            from config import get_openai_api_key
            api_key = get_openai_api_key()
            self._client = OpenAI(api_key=api_key)
        return self._client

    def generate_commit_message(self, diff: str) -> str:
        """Generate a commit message using OpenAI.
        
        Args:
            diff: The git diff content
            
        Returns:
            Generated commit message
        """
        style_instructions = {
            "conventional": "Use the Conventional Commits format: <type>(<optional-scope>): <description>. Types include: feat, fix, docs, style, refactor, perf, test, build, ci, chore.",
            "short": "Create a brief, single-line commit message that describes the change concisely.",
            "verbose": "Create a detailed commit message with a summary line followed by a blank line and a body explaining what and why.",
        }
        
        style_hint = style_instructions.get(self.style, style_instructions["conventional"])
        
        system_prompt = f"""You are an expert at writing clear, concise git commit messages.

Rules:
1. {style_hint}
2. Be specific about what changed
3. Use present tense ("add" not "added")
4. Don't end with a period
5. Keep the summary under 72 characters
6. Only output the commit message, no explanations

Analyze the diff and generate an appropriate commit message."""

        user_prompt = f"Generate a commit message for this diff:\n\n{diff}"
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=200,
                temperature=0.3,
            )
            
            message = response.choices[0].message.content.strip()
            
            # Clean up any markdown formatting
            if message.startswith("```"):
                lines = message.split("\n")
                message = "\n".join(lines[1:-1]) if len(lines) > 2 else message
            
            return message
            
        except Exception as e:
            print(f"[openai] Error generating message: {e}")
            return ""
