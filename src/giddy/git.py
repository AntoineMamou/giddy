import subprocess

from InquirerPy import inquirer


def run_git_command(command: list[str]) -> bool:
    """Exécute une commande Git silencieusement, retourne False si ça plante."""
    try:
        # check=True fait planter proprement si Git renvoie une erreur
        subprocess.run(command, check=True)
        return True
    except subprocess.CalledProcessError:
        print(f"\n❌ Aïe, la commande '{' '.join(command)}' a échoué.")
        return False


def do_commit_and_push(commit_message: str):
    """La routine complète pour sauvegarder et envoyer."""
    print("\n📦 Ajout des fichiers modifiés...")
    if not run_git_command(["git", "add", "."]):
        return

    print("📝 Sauvegarde locale (Commit)...")
    if not run_git_command(["git", "commit", "-m", commit_message]):
        return

    print("🚀 Envoi sur GitHub (Push)...")
    # Utiliser 'origin HEAD' permet de pousser la branche actuelle, peu importe son nom
    if run_git_command(["git", "push", "origin", "HEAD"]):
        print("\n🎉 Terminé ! Ton code est propre et en sécurité.")


def start_new_branch(feature_name: str):
    """Prépare le terrain en créant une nouvelle branche propre, avec auto-stash interactif."""

    current_branch = get_current_branch()
    files = get_modified_files()

    bring_changes = False
    stashed = False

    # 1. Gestion interactive s'il y a des fichiers modifiés
    if files:
        print(
            f"\n📦 Tu as {len(files)} fichier(s) modifié(s) sur la branche '{current_branch}'."
        )

        action = inquirer.select(
            message="Que veux-tu faire de ces modifications ?",
            choices=[
                "🧳 Les emporter avec moi vers la nouvelle branche",
                "🧊 Les laisser en attente ici (Stash) et partir à vide",
                "❌ Annuler et rester ici",
            ],
            pointer="👉",
        ).execute()

        if "Annuler" in action:
            print("🛑 Opération annulée. Tu es toujours sur ta branche actuelle.")
            return

        if "emporter" in action:
            bring_changes = True

        print("   Mise de côté (git stash)...")
        # Le "-u" est notre gilet de sauvetage pour embarquer les fichiers non suivis (nouveaux)
        run_git_command(
            [
                "git",
                "stash",
                "push",
                "-u",
                "-m",
                f"Giddy auto-stash depuis {current_branch}",
            ]
        )
        stashed = True

    # 2. La routine classique (checkout main, pull, création de branche)
    print("\n🔄 Bascule sur la branche principale (main)...")
    subprocess.run(["git", "checkout", "main"], capture_output=True)

    print("⬇️  Mise à jour locale depuis GitHub (pull)...")
    run_git_command(["git", "pull"])

    clean_name = feature_name.strip().lower().replace(" ", "-").replace("_", "-")
    branch_name = f"feat/{clean_name}"

    print(f"🌱 Création de la branche '{branch_name}'...")
    if run_git_command(["git", "checkout", "-b", branch_name]):
        print(f"\n✅ C'est parti ! Tu es sur la branche \033[96m{branch_name}\033[0m.")

    # 3. Restauration conditionnelle
    if stashed and bring_changes:
        print("\n✨ Restauration de tes modifications (git stash pop)...")
        result = subprocess.run(["git", "stash", "pop"], capture_output=True, text=True)

        if result.returncode != 0:
            print("⚠️  Attention : Conflit potentiel lors de la restauration !")
            print("   Tes fichiers sont là, mais tape 'giddy status' pour vérifier.")
        else:
            print("✅ Modifications restaurées avec succès !")
    elif stashed and not bring_changes:
        print("\n🧊 Tes anciennes modifications sont bien au chaud dans le stash.")
        print(
            f"   Tu pourras les récupérer plus tard en retournant sur '{current_branch}' et en tapant 'git stash pop'."
        )


def get_current_branch() -> str:
    """Retourne le nom de la branche actuelle."""
    result = subprocess.run(
        ["git", "branch", "--show-current"], capture_output=True, text=True
    )
    return result.stdout.strip()


def get_modified_files() -> list[str]:
    """Retourne la liste des fichiers modifiés sous un format facile à lire."""
    # --porcelain est fait exprès pour que les scripts lisent le statut Git
    result = subprocess.run(
        ["git", "status", "--porcelain"], capture_output=True, text=True
    )
    return result.stdout.splitlines()
