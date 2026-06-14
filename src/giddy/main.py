import argparse
import sys

from giddy.cli import ask_commit_details, ask_files_to_stage, show_dashboard
from giddy.config import init_config
from giddy.git import (
    do_commit_and_push,
    get_modified_files,
    start_new_branch,
    sync_main_and_clean,
)


def app() -> None:
    """Main entry point for the Giddy Git assistant CLI."""
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
        "sync", help="Switch back to main, pull updates, and clean up dead branches."
    )

    parser_init = subparsers.add_parser(
        "init", help="Generate a default .giddy.toml configuration file."
    )

    args = parser.parse_args()

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


if __name__ == "__main__":
    app()
