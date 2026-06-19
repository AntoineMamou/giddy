from giddy.git import handle_uncommitted_changes
from giddy.main import switch_branch


def test_handle_uncommitted_changes_no_files():
    """Test that if there are no modified files, it returns immediately."""
    should_continue, bring_changes, stashed = handle_uncommitted_changes("main", [])

    assert should_continue is True
    assert bring_changes is False
    assert stashed is False


def test_handle_uncommitted_changes_cancel(mocker):
    """Test that if the user cancels, the operation stops."""
    # Mock InquirerPy to simulate the user choosing 'Cancel'
    mock_prompt = mocker.patch("giddy.git.inquirer.select")
    mock_prompt.return_value.execute.return_value = (
        "❌ Cancel and stay on current branch"
    )

    should_continue, bring_changes, stashed = handle_uncommitted_changes(
        "main", ["file1.txt"]
    )

    assert should_continue is False
    assert bring_changes is False
    assert stashed is False


def test_switch_branch_success(mocker):
    """Test the happy path of switching branches with no uncommitted changes."""
    # 1. Setup all the mocks for the external dependencies
    mocker.patch("giddy.main.get_current_branch", return_value="main")
    mocker.patch("giddy.main.get_modified_files", return_value=[])

    # Mock our newly extracted safeguard
    mocker.patch(
        "giddy.main.handle_uncommitted_changes", return_value=(True, False, False)
    )

    # Mock the branch list and the user selection
    mocker.patch(
        "giddy.main.get_local_branches", return_value=["main", "feat/awesome-feature"]
    )
    mocker.patch("giddy.main.ask_branch_to_switch", return_value="feat/awesome-feature")

    # Mock the Git command and the restore logic
    mock_run_git = mocker.patch("giddy.git.run_git_command", return_value=True)
    mock_restore = mocker.patch("giddy.main.restore_stashed_changes")

    # 2. Execute the function
    switch_branch()

    # 3. Assertions: verify that the right Git commands were called!
    mock_run_git.assert_called_once_with(["git", "checkout", "feat/awesome-feature"])
    mock_restore.assert_called_once_with(False, False, "main")


def test_switch_branch_aborted_by_safeguard(mocker):
    """
    Test that switching stops if the user cancels at the uncommitted changes prompt.
    """
    mocker.patch("giddy.main.get_current_branch", return_value="main")
    mocker.patch("giddy.main.get_modified_files", return_value=["file.txt"])

    # Simulate the user aborting the operation (should_continue = False)
    mocker.patch(
        "giddy.main.handle_uncommitted_changes", return_value=(False, False, False)
    )

    mock_get_branches = mocker.patch("giddy.main.get_local_branches")

    # Execute
    switch_branch()

    # Ensure that it stopped immediately and never tried to fetch branches
    mock_get_branches.assert_not_called()
