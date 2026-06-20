import pytest

from giddy.utils import clean_branch_name


@pytest.mark.parametrize(
    "branch_type, input_name, expected_branch",
    [
        # Standard cases
        ("feat", "add login", "feat/add-login"),
        ("feat", "Fix UI bug", "feat/fix-ui-bug"),
        ("fix", "crash on startup", "fix/crash-on-startup"),
        ("docs", "Update README", "docs/update-readme"),
        ("refactor", "Core API", "refactor/core-api"),
        # Extra spaces and underscores
        ("feat", "  spaces  around  ", "feat/spaces-around"),
        ("feat", "underscores_and_spaces", "feat/underscores-and-spaces"),
        # Special characters that should be removed
        ("feat", "API v2 (new)!", "feat/api-v2-new"),
        ("feat", "what about ? and *", "feat/what-about-and"),
        # Multiple dashes prevention
        (
            "feat",
            "multiple---dashes___and_underscores",
            "feat/multiple-dashes-and-underscores",
        ),
        # Edge cases (should return empty string if no valid chars left)
        ("feat", "-start with dash", "feat/start-with-dash"),
        ("feat", "end with dash-", "feat/end-with-dash"),
        ("feat", "crazy?!*chars", "feat/crazychars"),
        ("feat", "", ""),
        ("fix", "   ", ""),
        ("docs", "?!*", ""),
        ("feat", "---", ""),
        ("feat", "___", ""),
        ("feat", "-_-", ""),
        # Mixed case and numbers
        ("feat", "Feature 123", "feat/feature-123"),
        ("feat", "MiXeD CaSe", "feat/mixed-case"),
        # Leading and trailing dashes after cleaning
        ("feat", "--leading and trailing--", "feat/leading-and-trailing"),
    ],
)
def test_clean_branch_name(branch_type: str, input_name: str, expected_branch: str):
    """Test that feature names are correctly converted to valid git branch names."""
    assert clean_branch_name(branch_type, input_name) == expected_branch
