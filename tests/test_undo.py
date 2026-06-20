import subprocess

from giddy.workflows import undo_workflow

# -------------------------------------------------------------------
# 1. TEST DU MOTEUR GIT (giddy.git)
# -------------------------------------------------------------------


def test_undo_last_commit_success(mocker):
    """Test that undo_last_commit calls the correct git reset command."""
    # We mock subprocess.run directly where it is used in git.py
    mock_run = mocker.patch("giddy.git.subprocess.run")

    from giddy.git import undo_last_commit

    result = undo_last_commit()

    # Assert the correct git command was executed
    mock_run.assert_called_once_with(
        ["git", "reset", "--soft", "HEAD~1"], check=True, capture_output=True
    )
    assert result is True


def test_undo_last_commit_failure(mocker):
    """Test that undo_last_commit returns False on Git error."""
    # Simulate Git crashing (e.g. no commits exist yet)
    mocker.patch(
        "giddy.git.subprocess.run", side_effect=subprocess.CalledProcessError(1, [])
    )

    from giddy.git import undo_last_commit

    result = undo_last_commit()

    assert result is False


# -------------------------------------------------------------------
# 2. TESTS DU WORKFLOW (giddy.workflows)
# -------------------------------------------------------------------


def test_undo_workflow_cancelled_by_user(mocker):
    """Test that the workflow stops if the user selects 'No' at confirmation."""
    # Mock UI to simulate user saying "No"
    mocker.patch("giddy.workflows.ask_undo_confirmation", return_value=False)

    # Mock the git function to ensure it is NEVER called
    mock_undo = mocker.patch("giddy.workflows.undo_last_commit")

    # Silence the UI prints during tests
    mocker.patch("giddy.workflows.show_step")
    mocker.patch("giddy.workflows.show_info")

    undo_workflow()

    # Assert Git was protected and not called
    mock_undo.assert_not_called()


def test_undo_workflow_success(mocker):
    """Test the happy path where user confirms and undo succeeds."""
    # User says "Yes"
    mocker.patch("giddy.workflows.ask_undo_confirmation", return_value=True)
    # Git command succeeds
    mock_undo = mocker.patch("giddy.workflows.undo_last_commit", return_value=True)

    # Silence UI
    mocker.patch("giddy.workflows.show_step")
    mocker.patch("giddy.workflows.show_success")
    mocker.patch("giddy.workflows.show_info")

    undo_workflow()

    # Assert Git was called once
    mock_undo.assert_called_once()


def test_undo_workflow_failure(mocker):
    """Test the error path where user confirms but git fails."""
    # User says "Yes"
    mocker.patch("giddy.workflows.ask_undo_confirmation", return_value=True)
    # Git command fails
    mock_undo = mocker.patch("giddy.workflows.undo_last_commit", return_value=False)

    # Silence UI
    mocker.patch("giddy.workflows.show_step")
    mock_error = mocker.patch("giddy.workflows.show_error")

    undo_workflow()

    # Assert Git was called but returned False, triggering the error UI
    mock_undo.assert_called_once()
    mock_error.assert_called_once_with(
        "Failed to undo commit. (Is this a brand new repository with no commits?)"
    )
