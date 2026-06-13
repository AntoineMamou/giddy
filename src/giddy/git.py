import subprocess


def run_git_command(command: list[str]) -> bool:
    """Execute a Git command silently.

    Args:
        command: List of command and arguments to execute.

    Returns:
        True if command succeeded, False otherwise.
    """
    try:
        subprocess.run(command, check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError:
        print(f"\n❌ Error: Command '{' '.join(command)}' failed.")
        return False


def do_commit_and_push(commit_message: str) -> None:
    """Commit and push changes to remote repository.

    Args:
        commit_message: The commit message to use.
    """
    print("\n📦 Staging modified files...")
    if not run_git_command(["git", "add", "."]):
        return

    print("📝 Creating commit...")
    if not run_git_command(["git", "commit", "-m", commit_message]):
        return

    print("🚀 Pushing to remote repository...")
    # Using 'origin HEAD' pushes the current branch regardless of its name
    if run_git_command(["git", "push", "origin", "HEAD"]):
        print("\n✅ Success! Your changes have been saved and pushed.")


def start_new_branch(feature_name: str) -> None:
    """Create and checkout a new feature branch.

    Args:
        feature_name: The name of the feature to create a branch for.
    """
    print("\n🔄 Switching to main branch...")
    # Using subprocess.run directly to handle case where main doesn't exist
    subprocess.run(["git", "checkout", "main"], capture_output=True)

    print("⬇️  Updating from remote repository...")
    # Ensure we have the latest code before creating branch
    run_git_command(["git", "pull"])

    # Clean branch name (e.g. "Add Login" -> "add-login")
    clean_name = feature_name.strip().lower().replace(" ", "-").replace("_", "-")
    branch_name = f"feat/{clean_name}"

    print(f"🌱 Creating branch '{branch_name}'...")
    if run_git_command(["git", "checkout", "-b", branch_name]):
        print(
            f"\n✅ Branch created! You can now start coding on \033[96m{branch_name}\033[0m."
        )


def get_current_branch() -> str:
    """Get the current branch name.

    Returns:
        The name of the current Git branch.
    """
    result = subprocess.run(
        ["git", "branch", "--show-current"], capture_output=True, text=True
    )
    return result.stdout.strip()


def get_modified_files() -> list[str]:
    """Get list of modified files in the repository.

    Returns:
        List of files with their status codes (format: 'XY filename').
    """
    # Using --porcelain format for easy script parsing
    result = subprocess.run(
        ["git", "status", "--porcelain"], capture_output=True, text=True
    )
    return result.stdout.splitlines()
