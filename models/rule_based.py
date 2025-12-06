import os

from .base import BaseCommitModel


class RuleBasedModel(BaseCommitModel):
    def __init__(self, style: str | None = None):
        self.style = style or "conventional"

    def generate_commit_message(self, diff: str) -> str:
        commit_type, scope, summary = self._analyze(diff)

        if self.style == "conventional":
            header = commit_type
            if scope:
                header += f"({scope})"
            return f"{header}: {summary}"

        if scope:
            return f"{summary} in {scope}"
        return summary

    def _analyze(self, diff: str) -> tuple[str, str, str]:
        lines = diff.splitlines()
        lower = diff.lower()
        added = 0
        removed = 0
        files_set: set[str] = set()

        for line in lines:
            if line.startswith("diff --git"):
                parts = line.split()
                if len(parts) >= 4:
                    path = parts[2]
                    if path.startswith("a/"):
                        path = path[2:]
                    files_set.add(path)
            elif line.startswith("+++ ") or line.startswith("--- "):
                parts = line.split()
                if len(parts) >= 2:
                    path = parts[1]
                    if path not in ("a/dev/null", "b/dev/null"):
                        if path.startswith("a/") or path.startswith("b/"):
                            path = path[2:]
                        files_set.add(path)
            elif line.startswith("+") and not line.startswith("+++"):
                added += 1
            elif line.startswith("-") and not line.startswith("---"):
                removed += 1

        files = sorted(files_set)
        commit_type = self._infer_type(lower, files, added, removed)
        scope = self._infer_scope(files)
        primary = files[0] if files else ""
        summary = self._build_summary(
            commit_type,
            scope,
            primary,
            len(files),
            added,
            removed,
            lower,
        )
        return commit_type, scope, summary

    def _infer_type(
        self, lower: str, files: list[str], added: int, removed: int
    ) -> str:
        keywords = {
            "config": [
                ".json",
                "config",
                "settings",
                ".env",
                "dockerfile",
                "makefile",
                ".yaml",
                ".yml",
            ],
            "test": ["test", "spec", "__test__", ".test.", "_test.", "tests/"],
            "docs": ["readme", "doc", "docs", ".md", "changelog"],
            "fix": ["fix", "bug", "error", "issue"],
            "feat": ["add", "new", "create", "implement", "feature"],
            "refactor": ["refactor", "cleanup", "organize", "restructure"],
            "style": ["format", "lint", "style", "prettier"],
            "deps": ["package.json", "requirements.txt", "pip", "npm", "poetry.lock"],
        }

        files_str = " ".join(files).lower()
        for key, tokens in keywords.items():
            if any(token in files_str for token in tokens):
                return self._map_keyword_to_type(key)

        if ".json" in files_str and any(
            word in lower for word in ("config", "setting")
        ):
            return "chore"
        if any(word in lower for word in ("fix", "bug", "error", "issue", "hotfix")):
            return "fix"
        if any(
            ".test." in f or "_test." in f or "/test/" in f or "tests/" in f
            for f in files
        ):
            return "test"

        if added > removed * 2:
            return "feat"
        if removed > added * 2:
            return "chore"
        return "chore"

    def _map_keyword_to_type(self, keyword: str) -> str:
        if keyword == "docs":
            return "docs"
        if keyword == "test":
            return "test"
        if keyword == "fix":
            return "fix"
        if keyword == "feat":
            return "feat"
        if keyword == "refactor":
            return "refactor"
        if keyword == "style":
            return "style"
        if keyword in {"config", "deps"}:
            return "chore"
        return "chore"

    def _infer_scope(self, files: list[str]) -> str:
        if not files:
            return ""
        raw = files[0]
        name = os.path.basename(raw)
        if not name:
            return ""
        base = name.split(".")[0]
        if base in {"index", "main", "app"}:
            parent = os.path.basename(os.path.dirname(raw))
            if parent:
                base = parent
        base = base.replace("_", "-").replace(" ", "-")
        if len(base) > 30:
            base = base[:30]
        return base

    def _build_summary(
        self,
        commit_type: str,
        scope: str,
        primary_file: str,
        file_count: int,
        added: int,
        removed: int,
        lower: str,
    ) -> str:
        if primary_file:
            base_name = os.path.basename(primary_file)
            base_without_ext = base_name.split(".")[0]
        else:
            base_without_ext = ""

        if scope:
            target = scope
        elif base_without_ext:
            target = base_without_ext
        else:
            target = "code"

        if added > 0 and removed == 0:
            change_kind = "add"
        elif removed > 0 and added == 0:
            change_kind = "remove"
        else:
            change_kind = "update"

        if commit_type == "docs":
            if change_kind == "add":
                return f"add documentation for {target}"
            return f"update documentation for {target}"

        if commit_type == "test":
            if file_count == 1:
                cleaned = target.replace(".test", "").replace("_test", "")
                if change_kind == "add":
                    return f"add tests for {cleaned}"
                return f"update tests for {cleaned}"
            if change_kind == "add":
                return f"add tests for {file_count} modules"
            return f"update tests for {file_count} modules"

        if commit_type == "fix":
            if file_count == 1:
                return f"fix issue in {target}"
            return "fix multiple issues"

        if commit_type == "feat":
            if file_count == 1:
                if change_kind == "add":
                    return f"add feature to {target}"
                return f"update feature in {target}"
            if change_kind == "add":
                return f"add new features ({file_count} files)"
            return f"update features ({file_count} files)"

        if commit_type == "refactor":
            if file_count == 1:
                return f"refactor {target}"
            return f"refactor codebase ({file_count} files)"

        if commit_type == "style":
            return "format code"

        if (
            "dependency" in lower
            or "requirements" in lower
            or "package.json" in lower
            or "pyproject" in lower
        ):
            return "update dependencies"

        if "config" in lower or "settings" in lower or "env" in lower:
            return f"update configuration for {target}"

        if file_count > 1:
            if change_kind == "add":
                return f"add content to {file_count} files"
            if change_kind == "remove":
                return f"remove content from {file_count} files"
            return f"update {file_count} files"

        if change_kind == "add":
            return f"add {target}"
        if change_kind == "remove":
            return f"remove {target}"
        return f"update {target}"
