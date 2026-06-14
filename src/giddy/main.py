import argparse
import subprocess
import sys

from giddy.cli import ask_commit_details, ask_files_to_stage, show_dashboard
from giddy.config import init_config
from giddy.git import (
    do_commit_and_push,
    get_modified_files,
    start_new_branch,
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

    except KeyboardInterrupt:
        # Gracefully handle Ctrl+C to prevent ugly tracebacks
        print("\n\n🛑 Operation cancelled. No changes were made.\n")
        sys.exit(0)


if __name__ == "__main__":
    app()
