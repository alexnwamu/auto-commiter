from openai import OpenAI
from .base import BaseCommitModel
from config import OPENAI_API_KEY


client = OpenAI(api_key=OPENAI_API_KEY)


class OpenAIModel(BaseCommitModel):
    def __init__(self, style: str):
        self.style = style

    def generate_commit_message(self, diff: str) -> str:
        prompt = f"Generate a commit message for the following diff: {diff} and style: {self.style}"
        system_role = f"You are an advanced Software Engineer with a deep understanding of Git commit messages. You are also a master of the English language. Generate a commit message that is concise, descriptive, and follows the {self.style} commit format."
        response = client.responses.create(
            model="gpt-5-nano",
            input=prompt,
            instructions=system_role,
        )
        print(response.output_text or "")
        return response.output_text
