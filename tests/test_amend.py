from giddy.workflows import amend_workflow


def test_commit_amend_success(mocker):
    """Test that commit_amend calls the correct git command."""
    mock_run = mocker.patch("giddy.git.subprocess.run")
    from giddy.git import commit_amend

    result = commit_amend()

    mock_run.assert_called_once_with(
        ["git", "commit", "--amend", "--no-edit"], check=True, capture_output=True
    )
    assert result is True


def test_push_force_success(mocker):
    """Test that push_force uses the safe --force-with-lease option."""
    mock_run = mocker.patch("giddy.git.subprocess.run")
    from giddy.git import push_force

    result = push_force()

    mock_run.assert_called_once_with(
        ["git", "push", "--force-with-lease", "origin", "HEAD"],
        check=True,
        capture_output=True,
    )
    assert result is True


def test_amend_workflow_blocked_on_main(mocker):
    """Test that the safety feature prevents amending on the base branch."""
    # Simulate being on 'main'
    mocker.patch("giddy.workflows.get_current_branch", return_value="main")
    mocker.patch("giddy.workflows.load_config", return_value={})

    mock_error = mocker.patch("giddy.workflows.show_error")

    amend_workflow()

    # Assert it stopped immediately with an error
    mock_error.assert_called_once_with(
        "Safety first! You cannot amend and force-push on 'main'."
    )


def test_amend_workflow_clean_tree(mocker):
    """Test that the workflow stops if there are no modified files."""
    mocker.patch("giddy.workflows.get_current_branch", return_value="feat/awesome")
    mocker.patch("giddy.workflows.load_config", return_value={})
    mocker.patch("giddy.workflows.get_modified_files", return_value=[])

    mock_success = mocker.patch("giddy.workflows.show_success")

    amend_workflow()

    mock_success.assert_called_once_with("Working tree is clean. Nothing to amend!")


def test_amend_workflow_no_files_selected(mocker):
    """Test that the workflow stops if the user cancels file selection."""
    mocker.patch("giddy.workflows.get_current_branch", return_value="feat/awesome")
    mocker.patch("giddy.workflows.load_config", return_value={})
    mocker.patch("giddy.workflows.get_modified_files", return_value=[" M config.py"])

    # User selects nothing
    mocker.patch("giddy.workflows.ask_files_to_stage", return_value=[])

    mocker.patch("giddy.workflows.show_step")
    mock_warning = mocker.patch("giddy.workflows.show_warning")

    amend_workflow()

    mock_warning.assert_called_once_with("No files selected. Operation aborted.")


def test_amend_workflow_happy_path(mocker):
    """Test the complete successful flow of amending and force-pushing."""
    mocker.patch("giddy.workflows.get_current_branch", return_value="feat/awesome")
    mocker.patch("giddy.workflows.load_config", return_value={})
    mocker.patch("giddy.workflows.get_modified_files", return_value=[" M config.py"])

    # User selects a file
    mocker.patch("giddy.workflows.ask_files_to_stage", return_value=["config.py"])

    # Mock all Git operations returning True
    mock_stage = mocker.patch("giddy.workflows.stage_files", return_value=True)
    mock_amend = mocker.patch("giddy.workflows.commit_amend", return_value=True)
    mock_push = mocker.patch("giddy.workflows.push_force", return_value=True)

    # Silence UI
    mocker.patch("giddy.workflows.show_step")
    mock_success = mocker.patch("giddy.workflows.show_success")

    amend_workflow()

    # Assert the correct sequence of Git calls was made
    mock_stage.assert_called_once_with(["config.py"])
    mock_amend.assert_called_once()
    mock_push.assert_called_once()
    mock_success.assert_called_once_with(
        "Done! Your last commit has been perfectly updated."
    )
