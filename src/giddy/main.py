import argparse
import subprocess
import sys

# On importe nos belles briques !
from giddy.git import get_current_branch, get_modified_files
from giddy.ui import show_dashboard, show_error
from giddy.utils import init_config
from giddy.workflows import (
    amend_workflow,
    commit_workflow,
    start_workflow,
    switch_workflow,
    sync_workflow,
    undo_workflow,
    untrack_workflow,
)


def check_git_environment(command: str) -> None:
    """Check if Git is installed and if the current directory is a Git repository."""
    if command == "init":
        return

    # 1. Check if Git is installed
    try:
        subprocess.run(["git", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        show_error("Git is not installed or not accessible in your PATH.")
        sys.exit(1)

    # 2. Check if we are inside a Git repository
    try:
        subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            capture_output=True,
            check=True,
        )
    except subprocess.CalledProcessError:
        show_error("This directory is not a Git repository. Run 'git init' first.")
        sys.exit(1)


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

        subparsers.add_parser("start", help="Create and checkout a new feature branch.")

        subparsers.add_parser(
            "done", help="Create a commit and push changes to remote."
        )
        subparsers.add_parser(
            "status", help="Display repository status and modified files."
        )
        subparsers.add_parser(
            "sync",
            help="Switch back to main, pull updates, and clean up dead branches.",
        )
        subparsers.add_parser(
            "init", help="Generate a default .giddy.toml configuration file."
        )
        subparsers.add_parser("switch", help="Switch to a different branch.")
        subparsers.add_parser(
            "undo", help="Undo the last commit without losing your changes."
        )
        subparsers.add_parser(
            "untrack", help="Stop tracking a file in Git without deleting it locally."
        )
        subparsers.add_parser(
            "amend", help="Quickly add forgotten files to your last commit."
        )

        args = parser.parse_args()

        # Check environment before proceeding
        check_git_environment(args.command)

        # Dispatch to the right workflow!
        if args.command == "start":
            start_workflow()

        elif args.command == "done":
            commit_workflow()

        elif args.command == "status":
            branch = get_current_branch()
            files = get_modified_files()
            show_dashboard(branch, files)

        elif args.command == "sync":
            sync_workflow()

        elif args.command == "init":
            init_config()

        elif args.command == "switch":
            switch_workflow()

        elif args.command == "undo":
            undo_workflow()

        elif args.command == "untrack":
            untrack_workflow()

        elif args.command == "amend":
            amend_workflow()

    except KeyboardInterrupt:
        # Gracefully handle Ctrl+C
        print("\n\n🛑 Operation cancelled. No changes were made.\n")
        sys.exit(0)


if __name__ == "__main__":
    app()
