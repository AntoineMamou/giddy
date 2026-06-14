import re
import subprocess

from InquirerPy import inquirer

from giddy.config import load_config


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


def do_commit_and_push(commit_message: str, files_to_stage: list[str]) -> None:
    """
    Stages selected files, creates a commit, and pushes to the remote repository.

    Args:
        commit_message (str): The formatted Conventional Commit message.
        files_to_stage (list[str]): The exact list of file paths to stage.

    Returns:
        None
    """
    if not files_to_stage:
        print("\n❌ No files selected. Commit aborted.")
        return

    print(f"\n📦 Staging {len(files_to_stage)} selected file(s)...")
    # We pass the list of files directly to the git add command
    command = ["git", "add"] + files_to_stage
    if not run_git_command(command):
        return

    print("📝 Saving local commit...")
    if not run_git_command(["git", "commit", "-m", commit_message]):
        return

    print("🚀 Pushing to GitHub...")
    if run_git_command(["git", "push", "origin", "HEAD"]):
        print("\n🎉 Done! Your code is safely pushed.")

        branch = get_current_branch()
        # We only show the PR link if we are NOT on main/master
        if branch not in ["main", "master"]:
            repo_url, provider = get_remote_repo_info()
            if repo_url:
                if provider == "github":
                    pr_url = f"{repo_url}/compare/main...{branch}?expand=1"
                    pr_type = "Pull Request"
                elif provider == "gitlab":
                    # GitLab's specific URL structure for creating a Merge Request
                    pr_url = f"{repo_url}/-/merge_requests/new?merge_request[source_branch]={branch}"
                    pr_type = "Merge Request"
                else:
                    return

                print(f"\n🌐 Want to merge this? Create a {pr_type} here:")
                print(f"   \033[94m\033[4m{pr_url}\033[0m")


def clean_branch_name(feature_name: str) -> str:
    """
    Clean the feature name to create a valid Git branch name.

    Args:
        feature_name (str): The raw input from the user.

    Returns:
        str: A clean, safe branch name starting with 'feat/',
             or an empty string if the input is invalid.
    """
    clean_name = feature_name.strip().lower().replace(" ", "-").replace("_", "-")
    clean_name = re.sub(r"[^a-z0-9-]", "", clean_name)  # Remove special characters
    clean_name = re.sub(r"-+", "-", clean_name)  # Prevent multiple consecutive dashes
    clean_name = clean_name.strip("-")  # Remove leading/trailing dashes

    if not clean_name:
        return ""

    return f"feat/{clean_name}"


def start_new_branch(feature_name: str) -> None:
    """Create and checkout a new feature branch with interactive stash handling.

    If there are modified files, prompts the user to either:
    - Carry changes to the new branch
    - Stash them and switch with a clean state
    - Cancel the operation

    Args:
        feature_name: The name of the feature to create a branch for.
    """

    # Clean branch name (e.g. "Add Login" -> "add-login")
    branch_name = clean_branch_name(feature_name)

    if not branch_name:
        print(
            "\n🛑 Error: The feature name is invalid (empty or only special characters)."
        )
        print("   Please provide a name with letters or numbers.")
        return

    config = load_config()
    base_branch = config.get("core", {}).get("base_branch", "main")

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
    print(f"\n🔄 Switching to the base branch ('{base_branch}')...")

    if not run_git_command(["git", "checkout", base_branch]):
        print("\n🛑 Error : Impossible to switch branches. Check your workspace.")
        return

    print("⬇️  Updating from remote repository...")
    if not run_git_command(["git", "pull"]):
        print("\n⚠️ Warning : Failed to update from remote repository. Process stopped.")
        return

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


def sync_main_and_clean() -> None:
    """
    Switches back to the main branch, pulls the latest changes, and cleans up dead branches.

    This function automates the post-pull-request workflow by:
    1. Checking out the 'main' branch.
    2. Fetching and pruning remote tracking branches.
    3. Pulling the latest changes from the remote repository.
    4. Deleting local branches that have already been merged into main.

    Returns:
        None
    """

    config = load_config()
    base_branch = config.get("core", {}).get("base_branch", "main")

    print(f"\n🔄 Switching to the base branch ('{base_branch}')...")
    if not run_git_command(["git", "checkout", base_branch]):
        print("\n🛑 Error : Impossible to come back to the main branch.")
        return

    print("⬇️  Updating and syncing from GitHub...")
    # 'fetch -p' (prune) tells your local Git to forget remote branches
    # that have been deleted on GitHub after the PR merge.
    run_git_command(["git", "fetch", "-p"])

    if not run_git_command(["git", "pull"]):
        print("\n🛑 Error : Impossible to fetch the latest changes. Cleanup aborted.")
        return

    print("\n🧹 Scanning for old local branches...")
    # Ask Git: "Which branches are already merged into main?"
    result = subprocess.run(
        ["git", "branch", "--merged"], capture_output=True, text=True
    )

    # Clean up the output text (Git puts a '*' in front of the active branch)
    merged_branches = [
        b.strip().replace("* ", "") for b in result.stdout.splitlines() if b.strip()
    ]

    cleaned_count = 0
    for branch in merged_branches:
        # Golden rule: NEVER delete main or master!
        if branch not in ["main", "master", base_branch]:
            # Delete the branch (lowercase -d is safe because it's already merged)
            subprocess.run(["git", "branch", "-d", branch], capture_output=True)
            print(f"  🗑️  Deleted local branch: {branch}")
            cleaned_count += 1

    if cleaned_count == 0:
        print("  ✨ Everything is clean, no dead branches found.")
    else:
        print(f"  ✅ Successfully cleaned {cleaned_count} branch(es)!")

    print("\n🏠 Your repository is pristine. You are ready for a new 'giddy start'!")


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


def get_remote_repo_info() -> tuple[str, str]:
    """
    Extracts the repository URL and provider from the local git configuration.

    Reads 'remote.origin.url' and formats it into a clean HTTPS web link,
    handling both SSH (git@...) and HTTPS (https://...) formats.

    Returns:
        tuple[str, str]: A tuple containing (repo_url, provider_name).
                         provider_name can be "github" or "gitlab".
                         Returns ("", "") if unsupported or not found.
    """
    result = subprocess.run(
        ["git", "config", "--get", "remote.origin.url"], capture_output=True, text=True
    )
    url = result.stdout.strip()

    if not url:
        return "", ""

    # Check for GitHub
    if "github.com" in url:
        if url.startswith("git@github.com:"):
            clean_path = url.replace("git@github.com:", "").replace(".git", "")
            return f"https://github.com/{clean_path}", "github"
        if url.startswith("https://github.com/"):
            clean_url = url.replace(".git", "")
            return clean_url, "github"

    # Check for GitLab
    if "gitlab.com" in url:
        if url.startswith("git@gitlab.com:"):
            clean_path = url.replace("git@gitlab.com:", "").replace(".git", "")
            return f"https://gitlab.com/{clean_path}", "gitlab"
        if url.startswith("https://gitlab.com/"):
            clean_url = url.replace(".git", "")
            return clean_url, "gitlab"

    return "", ""
