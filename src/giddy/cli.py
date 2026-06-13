from InquirerPy import inquirer
from InquirerPy.validator import EmptyInputValidator
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from giddy.git import get_current_branch, get_modified_files


def ask_commit_details() -> str:
    """Affiche le menu interactif et retourne le message de commit formaté."""

    commit_type_full = inquirer.select(
        message="Quel type de changement viens-tu de faire ?",
        choices=[
            "feat     ✨ (Nouvelle fonctionnalité)",
            "fix      🐛 (Correction de bug)",
            "refactor 🔨 (Amélioration du code)",
            "docs     📚 (Documentation)",
            "chore    🧹 (Tâches ménagères, dépendances)",
        ],
        pointer="👉",
    ).execute()

    commit_type = commit_type_full.split()[0]

    scope = inquirer.text(
        message="Sur quelle partie du projet ? (ex: api, ui - Entrée pour ignorer) :"
    ).execute()

    description = inquirer.text(
        message="Décris ton changement (sans majuscule à la fin) :",
        validate=EmptyInputValidator("La description est obligatoire !"),
    ).execute()

    # Formatage de la chaîne finale
    scope_str = f"({scope.strip()})" if scope.strip() else ""
    return f"{commit_type}{scope_str}: {description.strip()}"


def show_dashboard():
    """Affiche un magnifique tableau de bord de l'état actuel."""
    console = Console()
    branch = get_current_branch()
    files = get_modified_files()

    # Si tout est propre
    if not files:
        message = Text(
            "\n✨ Ton arbre de travail est impeccable sur la branche '", style="green"
        )
        message.append(branch, style="bold cyan")
        message.append("'.\nRien à commiter !", style="green")
        console.print(
            Panel(
                message,
                title="[bold green]🐎 Giddy Status[/bold green]",
                border_style="green",
            )
        )
        return

    # Si on a des modifications
    content = Text("Tu es actuellement sur la branche : ", style="white")
    content.append(f"{branch}\n\n", style="bold cyan")
    content.append("📝 Fichiers modifiés :\n", style="bold yellow")

    for file_line in files:
        # Le format '--porcelain' de Git donne " M fichier.py" ou "?? nouveau.txt"
        state = file_line[:2]
        file_name = file_line[3:]

        if "??" in state:
            content.append("  🆕 Non suivi  ", style="blue")
        elif "M" in state:
            content.append("  🛠️  Modifié    ", style="yellow")
        elif "D" in state:
            content.append("  ❌ Supprimé   ", style="red")
        elif "A" in state:
            content.append("  ✅ Ajouté     ", style="green")
        else:
            content.append(f"  📄 {state.strip()}      ", style="white")

        content.append(f"{file_name}\n", style="white")

    content.append("\n👉 Tape ", style="dim")
    content.append("giddy done", style="bold green")
    content.append(" pour sauvegarder tout ça.", style="dim")

    console.print(
        Panel(
            content,
            title="[bold yellow]🐎 Giddy Status[/bold yellow]",
            border_style="yellow",
        )
    )
