from giddy.git import (
    commit_changes,
    create_and_checkout_branch,
    delete_local_branch,
    fetch_and_prune,
    get_current_branch,
    get_local_branches,
    get_merged_branches,
    get_modified_files,
    get_remote_repo_info,
    pull_changes,
    push_head,
    stage_files,
    stash_pop,
    stash_push,
    switch_to_branch,
)
from giddy.ui import (
    ask_branch_to_switch,
    ask_commit_details,
    ask_files_to_stage,
    ask_stash_preference,
    show_error,
    show_info,
    show_pr_link,
    show_step,
    show_success,
    show_warning,
)

# Nous créerons ces deux petites fonctions dans utils.py juste après !
from giddy.utils import clean_branch_name, load_config

# -------------------------------------------------------------------
# SHARED SUB-WORKFLOWS (Stash management)
# -------------------------------------------------------------------


def handle_uncommitted_changes(
    current_branch: str, files: list[str]
) -> tuple[bool, bool, bool]:
    """Prompt user to handle changes. Returns (should_continue, bring_changes, stashed)"""
    if not files:
        return True, False, False

    action = ask_stash_preference(current_branch, len(files))

    if "Cancel" in action:
        show_warning("Operation cancelled. You are still on your current branch.")
        return False, False, False

    bring_changes = "Take them" in action

    show_info("Stashing changes (git stash)...")
    stash_push(f"Giddy auto-stash from {current_branch}")

    return True, bring_changes, True


def restore_stashed_changes(
    stashed: bool, bring_changes: bool, original_branch: str
) -> None:
    """Restore stashed changes if needed."""
    if stashed and bring_changes:
        show_step("Restoring your changes (git stash pop)...", icon="✨")
        if stash_pop():
            show_success("Changes restored successfully!")
        else:
            show_warning(
                "Potential conflict during restoration!\n   Your files are here, but run 'giddy status' to verify."
            )

    elif stashed and not bring_changes:
        show_info("Your previous changes are safely stored in the stash.")
        show_info(
            f"You can retrieve them later by returning to '{original_branch}' and running 'git stash pop'."
        )


# -------------------------------------------------------------------
# MAIN COMMAND WORKFLOWS
# -------------------------------------------------------------------


def switch_workflow() -> None:
    """Workflow for 'giddy switch'"""
    current_branch = get_current_branch()
    files = get_modified_files()

    should_continue, bring_changes, stashed = handle_uncommitted_changes(
        current_branch, files
    )
    if not should_continue:
        return

    branches = get_local_branches()
    target_branch = ask_branch_to_switch(branches, current_branch)

    if not target_branch:
        return

    show_step(f"Switching to {target_branch}...", icon="🔄")
    if switch_to_branch(target_branch):
        show_success(f"Switched to {target_branch}!")
        restore_stashed_changes(stashed, bring_changes, current_branch)
    else:
        show_error("Failed to switch branch. Please check for conflicts.")


def start_workflow(feature_name: str) -> None:
    """Workflow for 'giddy start'"""
    branch_name = clean_branch_name(feature_name)
    if not branch_name:
        show_error(
            "The feature name is invalid. Please provide a name with letters or numbers."
        )
        return

    config = load_config()
    base_branch = config.get("core", {}).get("base_branch", "main")
    current_branch = get_current_branch()
    files = get_modified_files()

    should_continue, bring_changes, stashed = handle_uncommitted_changes(
        current_branch, files
    )
    if not should_continue:
        return

    show_step(f"Switching to the base branch ('{base_branch}')...", icon="🔄")
    if not switch_to_branch(base_branch):
        show_error("Impossible to switch branches. Check your workspace.")
        return

    show_step("Updating from remote repository...", icon="⬇️")
    if not pull_changes():
        show_warning("Failed to update from remote repository. Process stopped.")
        return

    show_step(f"Creating branch '{branch_name}'...", icon="🌱")
    if create_and_checkout_branch(branch_name):
        show_success(f"Branch created! You are now on {branch_name}.")
        restore_stashed_changes(stashed, bring_changes, current_branch)
    else:
        show_error("Failed to create branch. Does it already exist?")


def commit_workflow() -> None:
    """Workflow for 'giddy done'"""
    files = get_modified_files()
    if not files:
        show_success("Working tree is clean. Nothing to commit!")
        return

    show_step("Giddy up! Let's prepare this commit.", icon="🐎")
    files_to_stage = ask_files_to_stage(files)

    if not files_to_stage:
        show_error("You didn't select any files. Operation aborted.")
        return

    config = load_config()
    defined_scopes = config.get("commits", {}).get("scopes", [])
    commit_message = ask_commit_details(defined_scopes)

    show_step(f"Staging {len(files_to_stage)} selected file(s)...", icon="📦")
    if not stage_files(files_to_stage):
        show_error("Failed to stage files.")
        return

    show_step("Saving local commit...", icon="📝")
    if not commit_changes(commit_message):
        show_error("Failed to commit changes.")
        return

    show_step("Pushing to remote...", icon="🚀")
    if push_head():
        show_success("Done! Your code is safely pushed.")

        # Display PR Link if not on main
        branch = get_current_branch()
        if branch not in ["main", "master"]:
            repo_url, provider = get_remote_repo_info()
            if repo_url:
                if provider == "github":
                    pr_url = f"{repo_url}/compare/main...{branch}?expand=1"
                    show_pr_link(pr_url, "Pull Request")
                elif provider == "gitlab":
                    pr_url = f"{repo_url}/-/merge_requests/new?merge_request[source_branch]={branch}"
                    show_pr_link(pr_url, "Merge Request")
    else:
        show_error("Failed to push changes.")


def sync_workflow() -> None:
    """Workflow for 'giddy sync'"""
    config = load_config()
    base_branch = config.get("core", {}).get("base_branch", "main")

    show_step(f"Switching to the base branch ('{base_branch}')...", icon="🔄")
    if not switch_to_branch(base_branch):
        show_error("Impossible to come back to the main branch.")
        return

    show_step(" Updating and syncing from remote...", icon="⬇️")
    fetch_and_prune()

    if not pull_changes():
        show_error("Impossible to fetch the latest changes. Cleanup aborted.")
        return

    show_step("Scanning for old local branches...", icon="🧹")
    merged_branches = get_merged_branches()

    cleaned_count = 0
    for branch in merged_branches:
        if branch not in ["main", "master", base_branch]:
            if delete_local_branch(branch):
                show_info(f"🗑️  Deleted local branch: {branch}")
                cleaned_count += 1

    if cleaned_count == 0:
        show_info("✨ Everything is clean, no dead branches found.")
    else:
        show_success(f"Successfully cleaned {cleaned_count} branch(es)!")

    show_success("Your repository is pristine. You are ready for a new 'giddy start'!")
