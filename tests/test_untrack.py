def test_untrack_workflow_with_gitignore_approved(mocker):
    """Test that .gitignore is updated if the user approves."""
    mocker.patch("giddy.workflows.get_tracked_files", return_value=["secret.json"])
    mocker.patch("giddy.workflows.ask_file_to_untrack", return_value="secret.json")
    mocker.patch("giddy.workflows.untrack_file", return_value=True)

    # L'utilisateur accepte l'écriture dans le .gitignore
    mocker.patch("giddy.workflows.ask_gitignore_append_confirmation", return_value=True)
    mock_append = mocker.patch("giddy.workflows.append_to_gitignore")

    # Silence UI
    mocker.patch("giddy.workflows.show_step")
    mocker.patch("giddy.workflows.show_success")
    mocker.patch("giddy.workflows.show_info")

    from giddy.workflows import untrack_workflow

    untrack_workflow()

    # On vérifie que la fonction d'écriture a bien été appelée !
    mock_append.assert_called_once_with("secret.json")
