from InquirerPy import inquirer
from InquirerPy.validator import EmptyInputValidator
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from giddy.git import get_current_branch, get_modified_files


def ask_commit_details() -> str:
    """Interactively prompt for commit details using conventional commits format.

    Returns:
        A formatted commit message following conventional commits format.
    """

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

    scope = inquirer.text(
        message="Which part of the project? (e.g., api, ui - leave blank to skip):"
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
