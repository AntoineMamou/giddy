import subprocess


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
    """Prépare le terrain en créant une nouvelle branche propre."""

    print("\n🔄 Bascule sur la branche principale (main)...")
    # On utilise subprocess.run directement ici pour ne pas planter si la branche s'appelle "master"
    # ou si on y est déjà.
    subprocess.run(["git", "checkout", "main"], capture_output=True)

    print("⬇️  Mise à jour locale depuis GitHub (pull)...")
    # C'est crucial pour être sûr de partir du code le plus récent
    run_git_command(["git", "pull"])

    # Nettoyage du nom entré par l'utilisateur (ex: "Ajout Login" -> "ajout-login")
    clean_name = feature_name.strip().lower().replace(" ", "-").replace("_", "-")
    branch_name = f"feat/{clean_name}"

    print(f"🌱 Création de la branche '{branch_name}'...")
    if run_git_command(["git", "checkout", "-b", branch_name]):
        print(
            f"\n✅ C'est parti ! Tu peux commencer à coder sur \033[96m{branch_name}\033[0m."
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
