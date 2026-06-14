import os

import tomllib

DEFAULT_CONFIG = {
    "core": {
        "base_branch": "main",
    },
    "commits": {"scopes": []},
}


def load_config() -> dict:
    """Load the local config or return the default."""
    if not os.path.exists(".giddy.toml"):
        return DEFAULT_CONFIG

    try:
        with open(".giddy.toml", "rb") as f:
            user_config = tomllib.load(f)

            merged = DEFAULT_CONFIG.copy()
            if "core" in user_config:
                merged["core"].update(user_config["core"])
            if "commits" in user_config:
                merged["commits"].update(user_config["commits"])
            return merged

    except Exception as e:
        print(f"⚠️ Error reading .giddy.toml : {e}. Using default values.")
        return DEFAULT_CONFIG


CONFIG_TEMPLATE = """# ==========================================
# Giddy Configuration
# ==========================================

[core]
# The main branch of your repository where PRs are merged.
# Default: "main"
base_branch = "main"

[commits]
# Define a list here to transform the 'scope' question into a dropdown menu.
# Example: scopes = ["api", "ui", "database", "docs"]
# Default: [] (Leaves a free text input)
scopes = []
"""


def init_config() -> None:
    """
    Generates a default .giddy.toml configuration file.

    Checks if the configuration file already exists in the current working
    directory to prevent accidental overwrites. If it does not exist, it
    creates the file with a pre-filled template containing default settings
    and explanatory comments.

    Returns:
        None
    """
    config_path = ".giddy.toml"

    if os.path.exists(config_path):
        print(f"\n⚠️  The file \033[93m{config_path}\033[0m already exists.")
        print(
            "   If you want to start fresh, delete it first and run 'giddy init' again."
        )
        return

    with open(config_path, "w", encoding="utf-8") as f:
        f.write(CONFIG_TEMPLATE)

    print(f"\n🎉 Success! A \033[92m{config_path}\033[0m file has been generated.")
    print("   You can open it and customize Giddy's behavior for this repository.")
