import argparse
import subprocess
import sys

from giddy.cli import (
    ask_branch_to_switch,
    ask_commit_details,
    ask_files_to_stage,
    show_dashboard,
)
from giddy.config import init_config
from giddy.git import (
    do_commit_and_push,
    get_current_branch,
    get_local_branches,
    get_modified_files,
    handle_uncommitted_changes,
    restore_stashed_changes,
    start_new_branch,
    switch_to_branch,
    sync_main_and_clean,
)


def check_git_environment(command: str) -> None:
    """Check if Git is installed and if the current directory is a Git repository."""
    if command == "init":
        return

    # 1. Check if Git is installed
    try:
        subprocess.run(["git", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("\n🛑 Fatal Error : Git is not installed or not accessible in your PATH.")
        sys.exit(1)

    # 2. Check if we are inside a Git repository
    try:
        subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            capture_output=True,
            check=True,
        )
    except subprocess.CalledProcessError:
        print(
            "\n🛑 Error : This directory is not a Git repository. Run 'git init' first."
        )
        sys.exit(1)


def switch_branch():
    """Handle the interactive branch switching workflow."""
    current_branch = get_current_branch()
    files = get_modified_files()

    # 1. Check for uncommitted changes
    should_continue, bring_changes, stashed = handle_uncommitted_changes(
        current_branch, files
    )

    if not should_continue:
        return  # The user selected "Cancel"

    # 2. Get branches and ask user
    branches = get_local_branches()
    target_branch = ask_branch_to_switch(branches, current_branch)

    if not target_branch:
        return  # User cancelled or no branches

    # 3. Perform the switch
    print(f"🔄 Switching to {target_branch}...")
    if switch_to_branch(target_branch):
        print(f"✅ Switched to \033[96m{target_branch}\033[0m!")

        restore_stashed_changes(stashed, bring_changes, current_branch)
    else:
        print("❌ Failed to switch branch. Please check for conflicts.")


def app() -> None:
    """Main entry point for the Giddy Git assistant CLI."""
    try:
        if sys.platform == "win32":
            import os

            os.system("")

        parser = argparse.ArgumentParser(
            description="Interactive Git assistant to simplify your workflow."
        )
        subparsers = parser.add_subparsers(dest="command", required=True)

        parser_start = subparsers.add_parser(
            "start", help="Create and checkout a new feature branch."
        )
        parser_start.add_argument("name", type=str, help="Name of the feature.")

        parser_done = subparsers.add_parser(
            "done", help="Create a commit and push changes to remote."
        )

        parser_status = subparsers.add_parser(
            "status", help="Display repository status and modified files."
        )

        parser_sync = subparsers.add_parser(
            "sync",
            help="Switch back to main, pull updates, and clean up dead branches.",
        )

        parser_init = subparsers.add_parser(
            "init", help="Generate a default .giddy.toml configuration file."
        )

        parser_switch = subparsers.add_parser(
            "switch", help="Switch to a different branch."
        )

        args = parser.parse_args()

        # Check environment before proceeding
        check_git_environment(args.command)

        if args.command == "done":
            if not get_modified_files():
                print("\n✨ Working tree is clean. Nothing to commit!")
                return

            print("\n🐎 Giddy up! Let's prepare this commit.\n")
            files_to_stage = ask_files_to_stage()

            if not files_to_stage:
                print("\n🛑 You didn't select any files. Operation aborted.")
                return

            commit_message = ask_commit_details()

            do_commit_and_push(commit_message, files_to_stage)

        elif args.command == "start":
            print(f"\n🐎 Giddy is preparing a branch for: {args.name}")
            start_new_branch(args.name)

        elif args.command == "status":
            show_dashboard()

        elif args.command == "sync":
            sync_main_and_clean()

        elif args.command == "init":
            init_config()

        elif args.command == "switch":
            switch_branch()

    except KeyboardInterrupt:
        # Gracefully handle Ctrl+C to prevent ugly tracebacks
        print("\n\n🛑 Operation cancelled. No changes were made.\n")
        sys.exit(0)


if __name__ == "__main__":
    app()
