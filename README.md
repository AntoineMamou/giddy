# Giddy

An interactive Git assistant that simplifies your workflow and helps you follow best practices.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)]([https://www.python.org/downloads/](https://www.python.org/downloads/))
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

Giddy is a command-line tool that makes Git workflows smoother and more intuitive. Whether you're starting a new feature, committing changes, or syncing with your team, Giddy guides you through the process with interactive prompts and clear feedback.

### Why Giddy?

- **Enforce Best Practices**: Follow conventional commits automatically
- **Interactive Workflow**: Intuitive prompts guide you through each step
- **Smart Defaults**: Handles branch naming, stashing, and cleanup intelligently
- **Minimal Dependencies**: Lightweight and fast
- **Beautiful Output**: Rich, colorful terminal UI for better readability

## Installation

### Requirements
- Python 3.11 or higher
- Git 2.0 or higher

### To use giddy globally

```bash
git clone https://github.com/AntoineMamou/giddy/
cd giddy
pipx install -e .
```

## Quick Start

### 1. Initialize configuration (Optional)

```bash
giddy init
```

Generates a `.giddy.toml` file to customize your base branch and commit scopes.

### 2. Start a New Feature

```bash
giddy start
```

Giddy will interactively ask for the branch type and name, then:
- Switch to the base branch (e.g., `main`)
- Pull the latest changes from remote
- Create a new formatted branch: `feat/add-user-authentication`
- Optionally carry or stash your current uncommitted changes

### 3. Check Status

```bash
giddy status
```

View:
- Current branch
- Modified files and their status
- Next steps

### 4. Commit Changes

```bash
giddy done
```

Giddy will:
- Show your modified files and let you select which to stage
- Guide you through creating a conventional commit message
- Push changes to your remote repository
- Show you the Pull Request / Merge Request link if needed (GitHub & GitLab supported!)

### 5. Sync with Main

```bash
giddy sync
```

Giddy will:
- Switch back to the base branch
- Pull latest changes from remote
- Clean up deleted remote branches

## Commands

### `giddy init`

Generate a default `.giddy.toml` configuration file in your current directory.

**Features:**
- Safely checks if a configuration already exists to prevent overwriting
- Generates a commented template
- Allows you to define your custom `base_branch` (e.g., `develop`, `master`)
- Allows you to define predefined `scopes` (transforms the text input into a dropdown menu during `giddy done`)

---

### `giddy start`

Start an interactive wizard to create and checkout a new branch.

**Features:**
- Interactive prompts for branch type (`feat`, `fix`, `docs`, etc.) and name
- Automatic branch naming: `type/clean-feature-name`
- Interactive stash handling if you have uncommitted changes
- Pulls latest code from remote before creating the branch

**Example:**
```bash
giddy start
# Prompts: What type of branch? -> feat
# Prompts: What is the name? -> implement dark mode
# Creates: feat/implement-dark-mode
```

---

### `giddy switch`

Switch to a different branch interactively.

**Features:**
- Fuzzy search to quickly find the branch you need
- Branches are sorted by recent commit date
- Safety guard: handles uncommitted changes before switching

---

### `giddy done`

Create a commit and push changes to remote.

**Features:**
- Interactive file selection (choose which files to stage)
- Conventional commits format with auto-formatting
- Automatic push to current branch
- Clear feedback on success or failure

**Commit Types:**
- `feat` ✨ - New feature
- `fix` 🐛 - Bug fix
- `refactor` 🔨 - Code improvement
- `docs` 📚 - Documentation
- `test` 🧪 - Add/Update tests
- `chore` 🧹 - Dependencies, configuration

**Example:**
```bash
giddy done
# Follow the interactive prompts:
# 1. Select files with Spacebar
# 2. Select commit type: feat
# 3. Add scope (optional): auth
# 4. Describe change: add password reset functionality
# 5. Commit and push!
```

---

### `giddy amend`

Quickly fix your last commit by adding forgotten files.

**Features:**
- Perfect for the classic "oops, I forgot to save this file before committing"
- Interactively select forgotten files to stage
- Amends the last commit silently without changing its message
- Safe force-push (`--force-with-lease`)
- Safety guard: blocked on main/base branch to protect project history

---

### `giddy undo`

Undo the last commit without losing your changes.

**Features:**
- Uses `git reset --soft HEAD~1` safely
- Your code is kept exactly as it is in your working directory
- Perfect for reverting a `giddy done` to change the commit message

---

### `giddy untrack`

Stop tracking a file in Git without deleting it locally.

**Features:**
- Fuzzy search through all tracked files
- Safely removes the file from Git's index (`--cached`)
- Optionally appends the file automatically to your `.gitignore`

---

### `giddy status`

Display repository status dashboard.

**Shows:**
- Current branch name
- List of modified files with status indicators:
  - 🆕 Untracked (new files)
  - 🛠️ Modified (changed files)
  - ✅ Added (staged files)
  - ❌ Deleted (removed files)
- Next action suggestion

**Example:**
```bash
giddy status
# Displays a rich panel with current state
```

---

### `giddy sync`

Switch back to the base branch, pull updates, and clean up dead branches.

**Features:**
- Safe switch to base branch
- Pulls latest changes from remote
- Removes local branches that no longer exist on remote
- Ideal after merging pull requests

**Example:**
```bash
giddy sync
# Clean up after your PR is merged
```

## Conventional Commits Format

Giddy uses the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <description>
```

### Examples

```
feat(api): add user authentication endpoint
fix(ui): resolve button alignment issue
refactor(db): optimize query performance
docs: update installation instructions
chore(deps): upgrade Flask to 2.0.0
```

### Why Conventional Commits?

- Automatically generate changelogs
- Enable semantic versioning
- Provide clear project history
- Link commits to issues
- Enable automation workflows

## Workflow Example

### Complete Feature Development

```bash
# 1. Start new feature
giddy start
# You're now on: feat/add-email-notifications

# 2. Make your changes
# ... edit files ...

# 3. Check what changed
giddy status

# 4. Commit and push
giddy done
# Select files → Choose type → Add description → Push!

# 5. Open a pull/merge request on GitHub/GitLab

# 6. After PR is merged, sync back to main
giddy sync
```

## Tips & Tricks

### 1. Branch Naming
Giddy automatically converts your branch type and feature name to a valid Git branch:
```bash
# User inputs "feat" and "Add User Login" -> feat/add-user-login
# User inputs "fix" and "bug_in API"      -> fix/bug-in-api
# User inputs "docs" and "REFACTOR  docs" -> docs/refactor-docs
```

### 2. Stashing Changes
When starting or switching a branch with uncommitted changes:
- **Take them**: Moves modifications to the new branch
- **Leave them (Stash)**: Safely stores them, retrieve later with `git stash pop`
- **Cancel**: Stay on current branch

### 3. File Selection
When running `giddy done` or `giddy amend`, select specific files instead of staging everything:
- Choose files you want to commit
- Leave others for the next commit
- Keeps commits focused and organized

### 4. Multiple Commits
Make focused commits on related changes:
```bash
# Commit set 1
giddy done  # Select files A, B
# Commit set 2
giddy done  # Select files C, D
```

## Troubleshooting

### "main branch not found"
Make sure your repository has a `main` branch. If using `master`, initialize Giddy to set your custom base branch:
```bash
giddy init
# Then edit .giddy.toml and set base_branch = "master"
```

### Changes not staged after stash pop
Conflicts may occur when popping a stash. Check status:
```bash
giddy status
```

### Accidental commit on wrong branch?
Reset and try again using the built-in undo tool:
```bash
giddy undo
giddy switch
giddy done
```

## Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/AntoineMamou/giddy.git
cd giddy

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode
pip install -e .
```

### Project Structure

```
giddy/
├── src/giddy/
│   ├── __init__.py          # Package metadata
│   ├── main.py              # CLI entry point & router
│   ├── workflows.py         # Main command logic and workflows
│   ├── ui.py                # InquirerPy prompts and Rich UI
│   ├── git.py               # Pure Git command wrappers
│   └── utils.py             # Helper functions and config loading
├── pyproject.toml           # Project configuration
└── README.md                # This file
```

### Code Style

This project uses:
- **Ruff** for linting
- **Type hints** for static typing
- **Google-style docstrings** for documentation

```bash
# Check code style
ruff check src/

# Format code
ruff format src/
```

## Contributing

Contributions are welcome! Here's how to help:

1. **Fork** the repository
2. **Create** a feature branch: `giddy start`
3. **Make** your changes and add tests if possible
4. **Commit** using `giddy done`
5. **Push** to your fork
6. **Open** a pull request

### Development Guidelines

- Follow PEP 8 style guide
- Write clear, descriptive commit messages
- Add docstrings to functions
- Test your changes locally (`pytest tests/`)

## Roadmap

- [ ] Commit templates
- [x] Integration with GitHub/GitLab APIs
- [x] Undo/rollback functionality
- [x] Branch switching helpers
- [ ] Automated changelog generation

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## Author

Created by **Antoine** ([GitHub](https://github.com/AntoineMamou))