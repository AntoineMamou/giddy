from giddy.workflows import handle_uncommitted_changes, switch_workflow


def test_handle_uncommitted_changes_no_files():
    """Test that if there are no modified files, it returns immediately."""
    should_continue, bring_changes, stashed = handle_uncommitted_changes("main", [])

    assert should_continue is True
    assert bring_changes is False
    assert stashed is False


def test_handle_uncommitted_changes_cancel(mocker):
    """Test that if the user cancels, the operation stops."""
    mocker.patch(
        "giddy.workflows.ask_stash_preference",
        return_value="❌ Cancel and stay on current branch",
    )

    should_continue, bring_changes, stashed = handle_uncommitted_changes(
        "main", ["file1.txt"]
    )

    assert should_continue is False
    assert bring_changes is False
    assert stashed is False


def test_switch_branch_success(mocker):
    """Test the happy path of switching branches with no uncommitted changes."""
    mocker.patch("giddy.workflows.get_current_branch", return_value="main")
    mocker.patch("giddy.workflows.get_modified_files", return_value=[])
    mocker.patch(
        "giddy.workflows.handle_uncommitted_changes", return_value=(True, False, False)
    )
    mocker.patch(
        "giddy.workflows.get_local_branches",
        return_value=["main", "feat/awesome-feature"],
    )
    mocker.patch(
        "giddy.workflows.ask_branch_to_switch", return_value="feat/awesome-feature"
    )

    mock_switch = mocker.patch("giddy.workflows.switch_to_branch", return_value=True)
    mock_restore = mocker.patch("giddy.workflows.restore_stashed_changes")

    mocker.patch("giddy.workflows.show_success")
    mocker.patch("giddy.workflows.show_step")

    switch_workflow()

    mock_switch.assert_called_once_with("feat/awesome-feature")
    mock_restore.assert_called_once_with(False, False, "main")


def test_switch_branch_aborted_by_safeguard(mocker):
    """
    Test that switching stops if the user cancels at the uncommitted changes prompt.
    """
    mocker.patch("giddy.main.get_current_branch", return_value="main")
    mocker.patch("giddy.main.get_modified_files", return_value=["file.txt"])

    # Simulate the user aborting the operation (should_continue = False)
    mocker.patch(
        "giddy.workflows.handle_uncommitted_changes", return_value=(False, False, False)
    )

    mock_get_branches = mocker.patch("giddy.workflows.get_local_branches")

    # Execute
    switch_workflow()

    # Ensure that it stopped immediately and never tried to fetch branches
    mock_get_branches.assert_not_called()
