import subprocess

from giddy.git import run_git_command


def test_run_git_command_success(mocker):
    """Test that run_git_command returns True when subprocess succeeds."""
    # Intercept subprocess.run so it doesn't actually run anything
    mock_run = mocker.patch("giddy.git.subprocess.run")

    # Call our function
    result = run_git_command(["git", "status"])

    # Assertions
    assert result is True
    # Verify that subprocess.run was called with the exact right arguments
    mock_run.assert_called_once_with(["git", "status"], check=True, capture_output=True)


def test_run_git_command_failure(mocker):
    """Test that run_git_command catches errors and returns False."""
    # Force subprocess.run to raise a CalledProcessError (simulating a Git error)
    mocker.patch(
        "giddy.git.subprocess.run", side_effect=subprocess.CalledProcessError(1, "git")
    )

    result = run_git_command(["git", "checkout", "non-existent-branch"])

    assert result is False
