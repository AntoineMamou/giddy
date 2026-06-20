import subprocess


def run_git_command(command: list[str]) -> bool:
    """Execute a Git command silently. Returns True if successful."""
    try:
        subprocess.run(command, check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError:
        # 🧹 REFRACTOR: No more prints here! The caller handles the error.
        return False


def get_current_branch() -> str:
    """Get the current Git branch name."""
    result = subprocess.run(
        ["git", "branch", "--show-current"], capture_output=True, text=True
    )
    return result.stdout.strip()


def get_modified_files() -> list[str]:
    """Get list of modified files using Git's porcelain format."""
    result = subprocess.run(
        ["git", "status", "--porcelain", "-uall"], capture_output=True, text=True
    )
    return result.stdout.splitlines()


def get_local_branches() -> list[str]:
    """Get a list of local branches sorted by recent commit date."""
    try:
        result = subprocess.run(
            [
                "git",
                "for-each-ref",
                "--sort=-committerdate",
                "--format=%(refname:short)",
                "refs/heads/",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        output = result.stdout.strip()
        if not output:
            return []
        return [branch.strip() for branch in output.split("\n") if branch.strip()]
    except subprocess.CalledProcessError:
        return []


def switch_to_branch(branch_name: str) -> bool:
    """Switch to an existing branch."""
    return run_git_command(["git", "checkout", branch_name])


def get_remote_repo_info() -> tuple[str, str]:
    """Extracts the repository URL and provider."""
    result = subprocess.run(
        ["git", "config", "--get", "remote.origin.url"], capture_output=True, text=True
    )
    url = result.stdout.strip()

    if not url:
        return "", ""

    if "github.com" in url:
        clean_path = (
            url.replace("git@github.com:", "")
            .replace("https://github.com/", "")
            .replace(".git", "")
        )
        return f"https://github.com/{clean_path}", "github"

    if "gitlab.com" in url:
        clean_path = (
            url.replace("git@gitlab.com:", "")
            .replace("https://gitlab.com/", "")
            .replace(".git", "")
        )
        return f"https://gitlab.com/{clean_path}", "gitlab"

    return "", ""


# -------------------------------------------------------------------
# 🧩 NEW EXTRACTED ACTIONS (Previously mixed in your commands)
# -------------------------------------------------------------------


def create_and_checkout_branch(branch_name: str) -> bool:
    """Create a new branch and switch to it."""
    return run_git_command(["git", "checkout", "-b", branch_name])


def fetch_and_prune() -> bool:
    """Fetch from origin and prune deleted remote branches."""
    return run_git_command(["git", "fetch", "-p"])


def pull_changes() -> bool:
    """Pull the latest changes from the remote repository."""
    return run_git_command(["git", "pull"])


def stage_files(files: list[str]) -> bool:
    """Stage specific files for commit."""
    return run_git_command(["git", "add"] + files)


def commit_changes(message: str) -> bool:
    """Create a commit with the staged files."""
    return run_git_command(["git", "commit", "-m", message])


def push_head() -> bool:
    """Push the current branch to origin."""
    return run_git_command(["git", "push", "origin", "HEAD"])


def stash_push(message: str) -> bool:
    """Stash modifications and untracked files with a message."""
    return run_git_command(["git", "stash", "push", "-u", "-m", message])


def stash_pop() -> bool:
    """Pop the latest stashed changes. Returns True if no conflicts."""
    try:
        subprocess.run(
            ["git", "stash", "pop"], capture_output=True, text=True, check=True
        )
        return True
    except subprocess.CalledProcessError:
        return False


def get_merged_branches() -> list[str]:
    """Get a list of branches that have already been merged into the current branch."""
    result = subprocess.run(
        ["git", "branch", "--merged"], capture_output=True, text=True
    )
    return [
        b.strip().replace("* ", "") for b in result.stdout.splitlines() if b.strip()
    ]


def delete_local_branch(branch_name: str) -> bool:
    """Delete a local branch."""
    # Using lowercase -d is safe: Git will refuse to delete if it's not merged!
    return run_git_command(["git", "branch", "-d", branch_name])
