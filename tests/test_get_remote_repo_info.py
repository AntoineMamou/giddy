import pytest

from giddy.git import get_remote_repo_info


@pytest.mark.parametrize(
    "git_remote_output, expected_url, expected_provider",
    [
        # GitHub formats
        (
            "git@github.com:coder/awesome-tool.git\n",
            "https://github.com/coder/awesome-tool",
            "github",
        ),
        (
            "https://github.com/developer/super-repo.git\n",
            "https://github.com/developer/super-repo",
            "github",
        ),
        # GitLab formats
        (
            "git@gitlab.com:coder/awesome-tool.git\n",
            "https://gitlab.com/coder/awesome-tool",
            "gitlab",
        ),
        (
            "https://gitlab.com/developer/super-repo.git\n",
            "https://gitlab.com/developer/super-repo",
            "gitlab",
        ),
        # Empty or unsupported provider (e.g., Bitbucket)
        ("", "", ""),
        ("git@bitbucket.org:coder/awesome-tool.git\n", "", ""),
    ],
)
def test_get_remote_repo_info(
    mocker, git_remote_output: str, expected_url: str, expected_provider: str
):
    """Test that Git remote URLs are correctly parsed for both GitHub and GitLab."""

    mock_run = mocker.patch("giddy.git.subprocess.run")
    mock_run.return_value.stdout = git_remote_output

    url, provider = get_remote_repo_info()

    assert url == expected_url
    assert provider == expected_provider
