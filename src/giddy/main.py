import argparse
import sys

from giddy.cli import ask_commit_details
from giddy.git import do_commit_and_push, start_new_branch


def app():
    if sys.platform == "win32":
        import os

        os.system("")

    parser = argparse.ArgumentParser(
        description="Giddy : Ton assistant Git interactif."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    parser_start = subparsers.add_parser(
        "start", help="Démarre une nouvelle fonctionnalité proprement."
    )
    parser_start.add_argument("name", type=str, help="Le nom de ta fonctionnalité.")

    parser_done = subparsers.add_parser(
        "done", help="Valide et envoie tes changements avec un beau commit."
    )

    args = parser.parse_args()

    if args.command == "done":
        print("\n🐎 Giddy up! Préparons ce commit.\n")
        commit_message = ask_commit_details()

        # On remplace les anciens 'print' par la vraie fonction Git !
        do_commit_and_push(commit_message)

    elif args.command == "start":
        print(f"\n🐎 Giddy prépare la branche pour : {args.name}")
        start_new_branch(args.name)


if __name__ == "__main__":
    app()
