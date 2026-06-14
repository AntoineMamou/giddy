import pytest

from giddy.git import clean_branch_name


@pytest.mark.parametrize(
    "input_name, expected_branch",
    [
        # Standard cases
        ("add login", "feat/add-login"),
        ("Fix UI bug", "feat/fix-ui-bug"),
        # Extra spaces and underscores
        ("  spaces  around  ", "feat/spaces-around"),
        ("underscores_and_spaces", "feat/underscores-and-spaces"),
        # Special characters that should be removed
        ("API v2 (new)!", "feat/api-v2-new"),
        ("what about ? and *", "feat/what-about-and"),
        # Multiple dashes prevention
        ("multiple---dashes___and_underscores", "feat/multiple-dashes-and-underscores"),
        # Edge cases
        ("-start with dash", "feat/start-with-dash"),
        ("end with dash-", "feat/end-with-dash"),
        ("crazy?!*chars", "feat/crazychars"),
        ("", ""),
        ("   ", ""),
        ("?!*", ""),
        ("---", ""),
        ("___", ""),
        ("-_-", ""),
        # Mixed case and numbers
        ("Feature 123", "feat/feature-123"),
        ("MiXeD CaSe", "feat/mixed-case"),
        # Leading and trailing dashes after cleaning
        ("--leading and trailing--", "feat/leading-and-trailing"),
    ],
)
def test_clean_branch_name(input_name: str, expected_branch: str):
    """Test that feature names are correctly converted to valid git branch names."""
    assert clean_branch_name(input_name) == expected_branch
