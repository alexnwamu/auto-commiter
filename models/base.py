from abc import ABC, abstractmethod


class BaseCommitModel(ABC):
    @abstractmethod
    def generate_commit_message(self, diff: str) -> str:
        pass
