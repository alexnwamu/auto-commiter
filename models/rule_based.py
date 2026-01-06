"""Rule-based commit message generator.

An enhanced rule-based model that analyzes git diffs to generate
conventional commit messages without calling external APIs.
"""

import os
import re
from collections import Counter
from .base import BaseCommitModel


class RuleBasedModel(BaseCommitModel):
    """Enhanced rule-based commit message generator.
    
    Features:
    - Better pattern matching for commit types
    - Improved scope detection from directory structure
    - Smarter summary generation with context awareness
    - Support for multiple commit styles
    """
    
    COMMIT_TYPES = {
        "feat": {
            "patterns": ["add", "new", "create", "implement", "feature", "introduce"],
            "file_patterns": [],
            "priority": 5,
        },
        "fix": {
            "patterns": ["fix", "bug", "error", "issue", "hotfix", "patch", "resolve", "repair"],
            "file_patterns": [],
            "priority": 10,
        },
        "docs": {
            "patterns": ["document", "readme", "changelog", "docs", "comment", "jsdoc", "docstring"],
            "file_patterns": [".md", "readme", "docs/", "doc/", "changelog", ".rst", ".txt"],
            "priority": 8,
        },
        "style": {
            "patterns": ["format", "lint", "style", "prettier", "eslint", "whitespace", "indent"],
            "file_patterns": [".prettierrc", ".eslintrc", ".stylelintrc"],
            "priority": 3,
        },
        "refactor": {
            "patterns": ["refactor", "cleanup", "clean", "organize", "restructure", "simplify", "rename", "move"],
            "file_patterns": [],
            "priority": 4,
        },
        "perf": {
            "patterns": ["performance", "optimize", "speed", "fast", "cache", "lazy", "perf"],
            "file_patterns": [],
            "priority": 6,
        },
        "test": {
            "patterns": ["test", "spec", "coverage", "mock", "stub", "e2e", "unit"],
            "file_patterns": [".test.", "_test.", "test_", ".spec.", "_spec.", "tests/", "__tests__/", "spec/"],
            "priority": 7,
        },
        "build": {
            "patterns": ["build", "compile", "bundle", "webpack", "vite", "rollup"],
            "file_patterns": ["webpack", "vite.config", "rollup.config", "tsconfig", "babel.config"],
            "priority": 6,
        },
        "ci": {
            "patterns": ["ci", "pipeline", "workflow", "deploy", "github actions", "jenkins"],
            "file_patterns": [".github/", ".gitlab-ci", "jenkinsfile", ".travis", ".circleci", "azure-pipelines"],
            "priority": 7,
        },
        "chore": {
            "patterns": ["chore", "misc", "update", "upgrade", "maintain"],
            "file_patterns": [".gitignore", ".editorconfig", ".nvmrc", ".node-version"],
            "priority": 1,
        },
        "deps": {
            "patterns": ["dependency", "dependencies", "package", "install", "upgrade"],
            "file_patterns": ["package.json", "package-lock.json", "yarn.lock", "requirements", "pyproject.toml", "poetry.lock", "go.mod", "cargo.toml", "gemfile"],
            "priority": 6,
        },
    }
    
    def __init__(self, style: str | None = None):
        self.style = style or "conventional"

    def generate_commit_message(self, diff: str) -> str:
        """Generate a commit message from the diff."""
        analysis = self._analyze_diff(diff)
        
        commit_type = analysis["type"]
        scope = analysis["scope"]
        summary = analysis["summary"]
        
        if self.style == "conventional":
            header = commit_type
            if scope:
                header += f"({scope})"
            return f"{header}: {summary}"
        
        elif self.style == "verbose":
            header = commit_type
            if scope:
                header += f"({scope})"
            body = self._generate_body(analysis)
            return f"{header}: {summary}\n\n{body}"
        
        else:  # short style
            if scope:
                return f"{summary} in {scope}"
            return summary

    def _analyze_diff(self, diff: str) -> dict:
        """Comprehensive analysis of the diff content."""
        lines = diff.splitlines()
        lower = diff.lower()
        
        # Track file changes
        files = []
        added_lines = []
        removed_lines = []
        current_file = None
        
        for line in lines:
            if line.startswith("diff --git"):
                parts = line.split()
                if len(parts) >= 4:
                    path = parts[2]
                    if path.startswith("a/"):
                        path = path[2:]
                    current_file = path
                    files.append({
                        "path": path,
                        "added": 0,
                        "removed": 0,
                        "is_new": False,
                        "is_deleted": False,
                    })
            elif line.startswith("new file mode"):
                if files:
                    files[-1]["is_new"] = True
            elif line.startswith("deleted file mode"):
                if files:
                    files[-1]["is_deleted"] = True
            elif line.startswith("+") and not line.startswith("+++"):
                added_lines.append(line[1:])
                if files:
                    files[-1]["added"] += 1
            elif line.startswith("-") and not line.startswith("---"):
                removed_lines.append(line[1:])
                if files:
                    files[-1]["removed"] += 1
        
        total_added = len(added_lines)
        total_removed = len(removed_lines)
        added_content = "\n".join(added_lines).lower()
        removed_content = "\n".join(removed_lines).lower()
        
        # Determine commit type
        commit_type = self._infer_type(files, added_content, removed_content, lower)
        
        # Determine scope
        scope = self._infer_scope(files)
        
        # Generate summary
        summary = self._build_summary(
            commit_type=commit_type,
            scope=scope,
            files=files,
            total_added=total_added,
            total_removed=total_removed,
            added_content=added_content,
            removed_content=removed_content,
        )
        
        return {
            "type": commit_type,
            "scope": scope,
            "summary": summary,
            "files": files,
            "added_lines": total_added,
            "removed_lines": total_removed,
        }

    def _infer_type(
        self,
        files: list[dict],
        added_content: str,
        removed_content: str,
        full_diff_lower: str,
    ) -> str:
        """Infer the commit type from various signals."""
        scores = Counter()
        
        file_paths = " ".join(f["path"].lower() for f in files)
        
        # Check file patterns first (strong signals)
        for commit_type, config in self.COMMIT_TYPES.items():
            for pattern in config["file_patterns"]:
                if pattern in file_paths:
                    scores[commit_type] += config["priority"] * 2
        
        # Check content patterns
        combined_content = added_content + " " + removed_content
        for commit_type, config in self.COMMIT_TYPES.items():
            for pattern in config["patterns"]:
                if pattern in combined_content:
                    scores[commit_type] += config["priority"]
        
        # Special case detection
        new_files = sum(1 for f in files if f.get("is_new"))
        deleted_files = sum(1 for f in files if f.get("is_deleted"))
        total_added = sum(f.get("added", 0) for f in files)
        total_removed = sum(f.get("removed", 0) for f in files)
        
        # If all files are new, likely a feat
        if new_files == len(files) and len(files) > 0:
            scores["feat"] += 15
        
        # If only deletions, could be cleanup/refactor
        if deleted_files == len(files) and len(files) > 0:
            scores["chore"] += 10
        
        # Ratio analysis
        if total_added > 0 and total_removed == 0:
            scores["feat"] += 5
        elif total_removed > total_added * 2:
            scores["refactor"] += 5
        
        # Check for fix-related keywords in context
        fix_indicators = ["fix", "bug", "error", "issue", "crash", "problem", "broken"]
        if any(indicator in full_diff_lower for indicator in fix_indicators):
            scores["fix"] += 8
        
        if not scores:
            return "chore"
        
        return scores.most_common(1)[0][0]

    def _infer_scope(self, files: list[dict]) -> str:
        """Infer scope from file paths."""
        if not files:
            return ""
        
        paths = [f["path"] for f in files]
        
        # If single file, use meaningful part of filename
        if len(paths) == 1:
            path = paths[0]
            parts = path.split("/")
            
            # Get basename without extension
            filename = os.path.basename(path)
            base = filename.split(".")[0]
            
            # Skip generic names
            if base in {"index", "main", "app", "__init__", "mod", "lib"}:
                # Use parent directory instead
                if len(parts) > 1:
                    base = parts[-2]
            
            return self._sanitize_scope(base)
        
        # For multiple files, find common ancestor or pattern
        common_parts = None
        for path in paths:
            parts = path.split("/")[:-1]  # Exclude filename
            if common_parts is None:
                common_parts = parts
            else:
                # Find common prefix
                new_common = []
                for a, b in zip(common_parts, parts):
                    if a == b:
                        new_common.append(a)
                    else:
                        break
                common_parts = new_common
        
        if common_parts:
            # Use the deepest common directory
            scope = common_parts[-1] if common_parts else ""
            return self._sanitize_scope(scope)
        
        # Check for common file type patterns
        extensions = Counter(os.path.splitext(p)[1] for p in paths)
        most_common_ext = extensions.most_common(1)
        if most_common_ext and most_common_ext[0][1] == len(paths):
            ext = most_common_ext[0][0].lstrip(".")
            if ext in {"py", "js", "ts", "go", "rs", "rb", "java", "swift"}:
                return ""
        
        return ""

    def _sanitize_scope(self, scope: str) -> str:
        """Sanitize scope string."""
        if not scope:
            return ""
        
        # Replace underscores and spaces with hyphens
        scope = scope.replace("_", "-").replace(" ", "-")
        
        # Remove special characters
        scope = re.sub(r"[^a-zA-Z0-9-]", "", scope)
        
        # Limit length
        if len(scope) > 25:
            scope = scope[:25]
        
        return scope.lower()

    def _build_summary(
        self,
        commit_type: str,
        scope: str,
        files: list[dict],
        total_added: int,
        total_removed: int,
        added_content: str,
        removed_content: str,
    ) -> str:
        """Build a descriptive commit summary."""
        file_count = len(files)
        new_files = [f for f in files if f.get("is_new")]
        deleted_files = [f for f in files if f.get("is_deleted")]
        
        # Determine primary file for context
        primary_file = files[0]["path"] if files else ""
        primary_name = os.path.basename(primary_file).split(".")[0] if primary_file else ""
        
        target = scope if scope else primary_name if primary_name else "code"
        
        # Determine change nature
        if total_added > 0 and total_removed == 0:
            action = "add"
        elif total_removed > 0 and total_added == 0:
            action = "remove"
        else:
            action = "update"
        
        # Type-specific summaries
        if commit_type == "docs":
            if action == "add":
                return f"add documentation for {target}"
            return f"update documentation for {target}"
        
        if commit_type == "test":
            clean_target = target.replace("-test", "").replace("test-", "").replace("_test", "").replace("test_", "")
            if file_count == 1:
                if action == "add":
                    return f"add tests for {clean_target}"
                return f"update tests for {clean_target}"
            if action == "add":
                return f"add tests for {file_count} modules"
            return f"update test suite"
        
        if commit_type == "fix":
            if file_count == 1:
                return f"fix issue in {target}"
            return f"fix issues in {file_count} files"
        
        if commit_type == "feat":
            if len(new_files) == file_count and file_count > 0:
                if file_count == 1:
                    return f"add {target}"
                return f"add {file_count} new files"
            if file_count == 1:
                return f"add feature to {target}"
            return f"implement new features"
        
        if commit_type == "refactor":
            if len(deleted_files) > 0:
                return f"cleanup and refactor {target}"
            if file_count == 1:
                return f"refactor {target}"
            return f"refactor codebase ({file_count} files)"
        
        if commit_type == "style":
            return "format code style"
        
        if commit_type == "perf":
            return f"improve performance of {target}"
        
        if commit_type == "deps":
            return "update dependencies"
        
        if commit_type == "build":
            return f"update build configuration"
        
        if commit_type == "ci":
            return "update CI/CD configuration"
        
        # Default summaries
        if file_count > 1:
            if action == "add":
                return f"add {file_count} files"
            if action == "remove":
                return f"remove content from {file_count} files"
            return f"update {file_count} files"
        
        if action == "add":
            return f"add {target}"
        if action == "remove":
            return f"remove {target}"
        return f"update {target}"

    def _generate_body(self, analysis: dict) -> str:
        """Generate a detailed commit body for verbose style."""
        lines = []
        
        files = analysis.get("files", [])
        if files:
            lines.append("Changed files:")
            for f in files[:5]:  # Limit to 5 files
                path = f["path"]
                added = f.get("added", 0)
                removed = f.get("removed", 0)
                
                if f.get("is_new"):
                    lines.append(f"  + {path} (new)")
                elif f.get("is_deleted"):
                    lines.append(f"  - {path} (deleted)")
                else:
                    lines.append(f"  * {path} (+{added}, -{removed})")
            
            if len(files) > 5:
                lines.append(f"  ... and {len(files) - 5} more files")
        
        return "\n".join(lines)
