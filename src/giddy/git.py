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
