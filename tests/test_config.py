from giddy.config import DEFAULT_CONFIG, load_config


def test_load_config_no_file(mocker):
    """
    Test that the default configuration is returned
    when no .giddy.toml file exists in the directory.
    """
    # We mock 'os.path.exists' to always return False
    mocker.patch("giddy.config.os.path.exists", return_value=False)

    config = load_config()

    assert config == DEFAULT_CONFIG


def test_load_config_with_file(mocker, tmp_path):
    """
    Test that custom configuration is properly merged
    with the default configuration.
    """
    # Create a temporary fake .giddy.toml file
    fake_config_content = b"""
    [core]
    base_branch = "develop"
    """
    fake_toml = tmp_path / ".giddy.toml"
    fake_toml.write_bytes(fake_config_content)

    # Force os.path.exists to return True and mock the 'open' function
    # to read our temporary fake file
    mocker.patch("giddy.config.os.path.exists", return_value=True)
    mocker.patch("builtins.open", mocker.mock_open(read_data=fake_config_content))

    config = load_config()

    # Assert that the base_branch was overwritten, but other defaults remain
    assert config["core"]["base_branch"] == "develop"
    assert "commits" in config
