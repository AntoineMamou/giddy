from InquirerPy import inquirer
from InquirerPy.validator import EmptyInputValidator


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
