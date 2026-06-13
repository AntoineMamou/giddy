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
