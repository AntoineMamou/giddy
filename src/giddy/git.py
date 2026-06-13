import subprocess

from InquirerPy import inquirer


def run_git_command(command: list[str]) -> bool:
    """Execute a Git command silently.

    Args:
        command: List of command and arguments to execute.

    Returns:
        True if command succeeded, False otherwise.
    """
    try:
        # check=True raises exception if Git returns an error
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
    """Create and checkout a new feature branch with interactive stash handling.

    If there are modified files, prompts the user to either:
    - Carry changes to the new branch
    - Stash them and switch with a clean state
    - Cancel the operation

    Args:
        feature_name: The name of the feature to create a branch for.
    """
    current_branch = get_current_branch()
    files = get_modified_files()

    bring_changes = False
    stashed = False

    # 1. Interactive file handling if there are modifications
    if files:
        print(
            f"\n📦 You have {len(files)} modified file(s) on branch '{current_branch}'."
        )

        action = inquirer.select(
            message="What would you like to do with these changes?",
            choices=[
                "🧳 Take them with me to the new branch",
                "🧊 Leave them here (stash) and switch with clean state",
                "❌ Cancel and stay on current branch",
            ],
            pointer="👉",
        ).execute()

        if "Cancel" in action:
            print("🛑 Operation cancelled. You are still on your current branch.")
            return

        if "Take them" in action:
            bring_changes = True

        print("   Stashing changes (git stash)...")
        # The "-u" flag ensures untracked files are also stashed
        run_git_command(
            [
                "git",
                "stash",
                "push",
                "-u",
                "-m",
                f"Giddy auto-stash from {current_branch}",
            ]
        )
        stashed = True

    # 2. Standard branch creation workflow
    print("\n🔄 Switching to main branch...")
    subprocess.run(["git", "checkout", "main"], capture_output=True)

    print("⬇️  Updating from remote repository...")
    run_git_command(["git", "pull"])

    # Clean branch name (e.g. "Add Login" -> "add-login")
    clean_name = feature_name.strip().lower().replace(" ", "-").replace("_", "-")
    branch_name = f"feat/{clean_name}"

    print(f"🌱 Creating branch '{branch_name}'...")
    if run_git_command(["git", "checkout", "-b", branch_name]):
        print(f"\n✅ Branch created! You are now on \033[96m{branch_name}\033[0m.")

    # 3. Conditional restoration of changes
    if stashed and bring_changes:
        print("\n✨ Restoring your changes (git stash pop)...")
        result = subprocess.run(["git", "stash", "pop"], capture_output=True, text=True)

        if result.returncode != 0:
            print("⚠️  Warning: Potential conflict during restoration!")
            print("   Your files are here, but run 'giddy status' to verify.")
        else:
            print("✅ Changes restored successfully!")
    elif stashed and not bring_changes:
        print("\n🧊 Your previous changes are safely stored in the stash.")
        print(
            f"   You can retrieve them later by returning to '{current_branch}' and running 'git stash pop'."
        )


def get_current_branch() -> str:
    """Get the current Git branch name.

    Returns:
        The name of the current branch.
    """
    result = subprocess.run(
        ["git", "branch", "--show-current"], capture_output=True, text=True
    )
    return result.stdout.strip()


def get_modified_files() -> list[str]:
    """Get list of modified files in the repository.

    Returns:
        List of files with their status codes in format: 'XY filename',
        using Git's porcelain format for easy script parsing.
    """
    # --porcelain format is designed for scripts to easily parse Git status
    result = subprocess.run(
        ["git", "status", "--porcelain"], capture_output=True, text=True
    )
    return result.stdout.splitlines()
