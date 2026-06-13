import argparse
import sys

from giddy.cli import ask_commit_details, show_dashboard
from giddy.git import do_commit_and_push, start_new_branch


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

    args = parser.parse_args()

    if args.command == "done":
        print("\n🐎 Giddy up! Let's prepare this commit.\n")
        commit_message = ask_commit_details()
        do_commit_and_push(commit_message)

    elif args.command == "start":
        print(f"\n🐎 Giddy is preparing a branch for: {args.name}")
        start_new_branch(args.name)

    elif args.command == "status":
        show_dashboard()


if __name__ == "__main__":
    app()
