from InquirerPy import inquirer
from InquirerPy.validator import EmptyInputValidator
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from giddy.config import load_config
from giddy.git import get_current_branch, get_modified_files


def ask_commit_details() -> str:
    """Interactively prompt for commit details using conventional commits format.

    Returns:
        A formatted commit message following conventional commits format.
    """
    config = load_config()
    defined_scopes = config.get("commits", {}).get("scopes", [])

    commit_type_full = inquirer.select(
        message="What type of change did you make?",
        choices=[
            "feat     ✨ (New feature)",
            "fix      🐛 (Bug fix)",
            "refactor 🔨 (Code improvement)",
            "docs     📚 (Documentation)",
            "chore    🧹 (Dependencies, configuration)",
        ],
        pointer="👉",
    ).execute()

    commit_type = commit_type_full.split()[0]

    if defined_scopes:
        # If scopes are defined in config, show a dropdown menu
        choices = ["(none)"] + defined_scopes
        scope_choice = inquirer.select(
            message="Select the scope of this change:", choices=choices, pointer="👉"
        ).execute()
        scope = "" if scope_choice == "(none)" else scope_choice
    else:
        # Default behavior: free text input
        scope = inquirer.text(
            message="Scope of this change (e.g., api, ui - Enter to skip):"
        ).execute()

    description = inquirer.text(
        message="Describe your change (in lowercase without ending punctuation):",
        validate=EmptyInputValidator("Description is required!"),
    ).execute()

    # Format final commit message
    scope_str = f"({scope.strip()})" if scope.strip() else ""
    return f"{commit_type}{scope_str}: {description.strip()}"


def show_dashboard() -> None:
    """Display repository status dashboard.

    Shows current branch, modified files, and next steps.
    """
    console = Console()
    branch = get_current_branch()
    files = get_modified_files()

    # If working tree is clean
    if not files:
        message = Text(
            "\n✨ Your working directory is clean on branch '", style="green"
        )
        message.append(branch, style="bold cyan")
        message.append("'.\nNothing to commit!", style="green")
        console.print(
            Panel(
                message,
                title="[bold green]🐎 Giddy Status[/bold green]",
                border_style="green",
            )
        )
        return

    # If there are modifications
    content = Text("Current branch: ", style="white")
    content.append(f"{branch}\n\n", style="bold cyan")
    content.append("📝 Modified files:\n", style="bold yellow")

    for file_line in files:
        # Git --porcelain format: " M filename.py" or "?? newfile.txt"
        state = file_line[:2]
        file_name = file_line[3:]

        if "??" in state:
            content.append("  🆕 Untracked  ", style="blue")
        elif "M" in state:
            content.append("  🛠️  Modified   ", style="yellow")
        elif "D" in state:
            content.append("  ❌ Deleted    ", style="red")
        elif "A" in state:
            content.append("  ✅ Added      ", style="green")
        else:
            content.append(f"  📄 {state.strip()}      ", style="white")

        content.append(f"{file_name}\n", style="white")

    content.append("\n👉 Run ", style="dim")
    content.append("giddy done", style="bold green")
    content.append(" to commit and push these changes.", style="dim")

    console.print(
        Panel(
            content,
            title="[bold yellow]🐎 Giddy Status[/bold yellow]",
            border_style="yellow",
        )
    )


def ask_files_to_stage() -> list[str]:
    """
    Prompts the user to select specific files to stage for the commit.

    Retrieves the list of modified/untracked files using Git porcelain format.
    Displays an interactive checkbox menu. The user can press 'Space' to select
    individual files, or 'a' to select all.

    Returns:
        list[str]: A list of file paths selected by the user. Returns an empty
                   list if no files are modified or selected.
    """
    raw_files = get_modified_files()

    if not raw_files:
        return []

    # Prepare choices for InquirerPy:
    # 'name' is what the user sees (e.g., " M src/main.py")
    # 'value' is what the program gets (e.g., "src/main.py")
    choices = []
    for line in raw_files:
        file_path = line[3:].strip()
        choices.append({"name": line, "value": file_path})

    selected_files = inquirer.checkbox(
        message="Which files do you want to commit?",
        choices=choices,
        instruction="(Press <Space> to select, <Alt+a> to toggle all, <Enter> to confirm)",
    ).execute()

    return selected_files


def ask_branch_to_switch(branches: list[str], current_branch: str) -> str:
    """Prompt the user to fuzzy-search and select a branch."""

    # Optional: Remove the current branch from the list so they don't switch to where they already are
    available_branches = [b for b in branches if b != current_branch]

    if not available_branches:
        print("🐎 No other branches found!")
        return ""

    branch = inquirer.fuzzy(
        message="Which branch do you want to switch to?",
        choices=available_branches,
        instruction="(Start typing to search, Enter to select)",
    ).execute()

    return branch
