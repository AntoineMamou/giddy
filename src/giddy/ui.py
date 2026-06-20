from InquirerPy import inquirer
from InquirerPy.validator import EmptyInputValidator
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

# Initialize Rich console
console = Console()

# -------------------------------------------------------------------
# 1. GENERIC MESSAGES (Standardizing colors and emojis!)
# -------------------------------------------------------------------


def show_success(message: str) -> None:
    """Display a success message in green."""
    print(f"\n✅ \033[92m{message}\033[0m")


def show_error(message: str) -> None:
    """Display a fatal error message in red."""
    print(f"\n🛑 \033[91mError: {message}\033[0m")


def show_warning(message: str) -> None:
    """Display a warning message in yellow."""
    print(f"\n⚠️  \033[93mWarning: {message}\033[0m")


def show_step(message: str, icon: str = "🐎") -> None:
    """Display a main step in the process."""
    print(f"\n{icon} {message}")


def show_info(message: str) -> None:
    """Display a standard indented info message."""
    print(f"   {message}")


def show_pr_link(pr_url: str, pr_type: str) -> None:
    """Display the pull/merge request link beautifully."""
    print(f"\n🌐 Want to merge this? Create a {pr_type} here:")
    print(f"   \033[94m\033[4m{pr_url}\033[0m")


# -------------------------------------------------------------------
# 2. RICH DASHBOARDS
# -------------------------------------------------------------------


def show_dashboard(branch: str, files: list[str]) -> None:
    """Display repository status dashboard using Rich."""
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


# -------------------------------------------------------------------
# 3. INTERACTIVE PROMPTS (InquirerPy)
# -------------------------------------------------------------------


def ask_commit_details(defined_scopes: list[str]) -> str:
    """Interactively prompt for commit details. Returns the formatted message."""
    commit_type_full = inquirer.select(
        message="What type of change did you make?",
        choices=[
            "feat     ✨ (New feature)",
            "fix      🐛 (Bug fix)",
            "refactor 🔨 (Code improvement)",
            "docs     📚 (Documentation)",
            "test     🧪 (Add/Update tests)",
            "chore    🧹 (Dependencies, configuration)",
        ],
        pointer="👉",
    ).execute()

    commit_type = commit_type_full.split()[0]

    if defined_scopes:
        choices = ["(none)"] + defined_scopes
        scope_choice = inquirer.select(
            message="Select the scope of this change:", choices=choices, pointer="👉"
        ).execute()
        scope = "" if scope_choice == "(none)" else scope_choice
    else:
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


def ask_files_to_stage(raw_files: list[str]) -> list[str]:
    """Prompts the user to select specific files to stage."""
    if not raw_files:
        return []

    choices = [{"name": line, "value": line[3:].strip()} for line in raw_files]

    return inquirer.checkbox(
        message="Which files do you want to commit?",
        choices=choices,
        instruction="(Press <Space> to select, <Alt+a> to toggle all, <Enter> to confirm)",
    ).execute()


def ask_branch_to_switch(branches: list[str], current_branch: str) -> str:
    """Prompt the user to fuzzy-search and select a branch."""
    available_branches = [b for b in branches if b != current_branch]

    if not available_branches:
        show_warning("No other branches found!")
        return ""

    return inquirer.fuzzy(
        message="Which branch do you want to switch to?",
        choices=available_branches,
        instruction="(Start typing to search, Enter to select)",
    ).execute()


def ask_stash_preference(current_branch: str, file_count: int) -> str:
    """Prompt the user to handle uncommitted changes."""
    show_step(
        f"You have {file_count} modified file(s) on branch '{current_branch}'.",
        icon="📦",
    )

    return inquirer.select(
        message="What would you like to do with these changes?",
        choices=[
            "🧳 Take them with me to the new branch",
            "🧊 Leave them here (stash) and switch with clean state",
            "❌ Cancel and stay on current branch",
        ],
        pointer="👉",
    ).execute()


def ask_undo_confirmation() -> bool:
    """Prompt the user to confirm the undo action."""
    return inquirer.confirm(
        message="Are you sure you want to undo your last commit? (Your files will be kept)",
        default=False,
    ).execute()


def ask_file_to_untrack(tracked_files: list[str]) -> str:
    """Prompt the user to fuzzy-search a tracked file to untrack."""
    if not tracked_files:
        show_warning("No tracked files found in this repository.")
        return ""

    return inquirer.fuzzy(
        message="Which file or folder do you want Git to forget? (It won't be deleted from your PC)",
        choices=tracked_files,
        instruction="(Start typing to search, Enter to select)",
    ).execute()


def ask_gitignore_append_confirmation(file_path: str) -> bool:
    """Prompt the user to confirm if they want to add the file to .gitignore."""
    return inquirer.confirm(
        message=f"Would you like Giddy to automatically add '{file_path}' to your .gitignore?",
        default=True,
    ).execute()


def ask_branch_type() -> str:
    """Interactively prompt for the branch type."""
    branch_type_full = inquirer.select(
        message="What type of branch are you starting?",
        choices=[
            "feat     ✨ (New feature)",
            "fix      🐛 (Bug fix)",
            "refactor 🔨 (Code improvement)",
            "docs     📚 (Documentation)",
            "test     🧪 (Add/Update tests)",
            "chore    🧹 (Dependencies, configuration)",
        ],
        pointer="👉",
    ).execute()

    # take only the first word (ex: "fix" instead of "fix 🐛 (Bug fix)")
    return branch_type_full.split()[0]


def ask_branch_name() -> str:
    """Interactively prompt for the branch name."""
    return inquirer.text(
        message="What is the name of your branch?",
        validate=EmptyInputValidator("A branch name is required!"),
    ).execute()
