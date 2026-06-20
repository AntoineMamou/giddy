import re
from pathlib import Path

try:
    import tomllib
except ImportError:
    pass


def clean_branch_name(feature_name: str) -> str:
    """
    Clean the feature name to create a valid Git branch name.
    """
    clean_name = feature_name.strip().lower().replace(" ", "-").replace("_", "-")
    clean_name = re.sub(r"[^a-z0-9-]", "", clean_name)  # Remove special characters
    clean_name = re.sub(r"-+", "-", clean_name)  # Prevent multiple consecutive dashes
    clean_name = clean_name.strip("-")  # Remove leading/trailing dashes

    if not clean_name:
        return ""

    return f"feat/{clean_name}"


def load_config() -> dict:
    """
    Load configuration from .giddy.toml if it exists.
    Returns an empty dict if the file is missing or invalid.
    """
    config_path = Path(".giddy.toml")
    if not config_path.is_file():
        return {}

    try:
        with open(config_path, "rb") as f:
            return tomllib.load(f)
    except Exception:
        return {}


def init_config() -> None:
    """Generate a default .giddy.toml configuration file."""
    config_path = Path(".giddy.toml")
    if config_path.exists():
        print("\n⚠️  Configuration file .giddy.toml already exists!")
        return

    default_config = """[core]
base_branch = "main"

[commits]
scopes = ["api", "ui", "cli", "docs", "tests", "core"]
"""
    with open(config_path, "w") as f:
        f.write(default_config)
    print("\n✅ Created default .giddy.toml configuration file!")
