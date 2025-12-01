import subprocess


def get_staged_diff():
    try:
        result = subprocess.run(
            ["git", "diff", "--cached"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return ""


def get_branch_name():
    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"], capture_output=True, text=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return "unknown"


def add_staged_diff():
    try:
        subprocess.run(
            ["git", "add", "--all"],
            capture_output=True,
            text=True,
            check=True,
        )
        return True
    except subprocess.CalledProcessError:
        return False


def commit_diff(commit_message: str):
    try:
        subprocess.run(
            ["git", "commit", "-m", commit_message],
            capture_output=True,
            text=True,
            check=True,
        )
        return True
    except subprocess.CalledProcessError:
        return False
