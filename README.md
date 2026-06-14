# Giddy

An interactive Git assistant that simplifies your workflow and helps you follow best practices.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
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

Generates a .giddy.toml file to customize your base branch and commit scopes.

### 2. Start a New Feature

```bash
giddy start "add user authentication"
```

Giddy will:
- Switch to the `main` branch
- Pull the latest changes from remote
- Create a new feature branch: `feat/add-user-authentication`
- Optionally carry or stash your current changes

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
- Show you the Pull Request link if needed

### 5. Sync with Main

```bash
giddy sync
```

Giddy will:
- Switch back to `main`
- Pull latest changes from remote
- Clean up deleted remote branches

## Commands

### giddy init

Generate a default .giddy.toml configuration file in your current directory.

**Features:**

- Safely checks if a configuration already exists to prevent overwriting
- Generates a commented template
- Allows you to define your custom base_branch (e.g., develop, master)
- Allows you to define predefined scopes (transforms the text input into a dropdown menu during giddy done)

---

### `giddy start <feature-name>`

Create and checkout a new feature branch.

**Features:**
- Automatic branch naming: `feat/feature-name`
- Interactive stash handling if you have uncommitted changes
- Pulls latest code from remote before creating branch

**Options:**
- `--name`: Feature name (supports spaces and special characters)

**Example:**
```bash
giddy start "implement dark mode"
# Creates: feat/implement-dark-mode
```

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
- `chore` 🧹 - Dependencies, configuration

**Example:**
```bash
giddy done
# Follow the interactive prompts:
# 1. Select commit type: feat
# 2. Add scope (optional): auth
# 3. Describe change: add password reset functionality
# 4. Commit and push!
```

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

Switch back to main, pull updates, and clean up dead branches.

**Features:**
- Safe switch to main branch
- Pulls latest changes from remote
- Removes local branches that no longer exist on remote
- Ideal after merging pull requests

**Example:**
```bash
giddy sync
# Clean up after your PR is merged
```

---

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
giddy start "add email notifications"
# You're now on: feat/add-email-notifications

# 2. Make your changes
# ... edit files ...

# 3. Check what changed
giddy status

# 4. Commit and push
giddy done
# Select files → Choose type → Add description → Push!

# 5. Open a pull request on GitHub

# 6. After PR is merged, sync back to main
giddy sync
```

## Tips & Tricks

### 1. Branch Naming
Giddy automatically converts your feature name to a valid Git branch:
```bash
giddy start "Add User Login"     # → feat/add-user-login
giddy start "fix bug_in API"     # → feat/fix-bug-in-api
giddy start "REFACTOR  helpers"  # → feat/refactor-helpers
```

### 2. Stashing Changes
When starting a new branch with uncommitted changes:
- **Carry Changes**: Moves modifications to the new branch
- **Stash**: Safely stores them, retrieve later with `git stash pop`
- **Cancel**: Stay on current branch

### 3. File Selection
When running `giddy done`, select specific files instead of staging everything:
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
Make sure your repository has a `main` branch. If using `master`:
```bash
git branch -m master main
```

### Changes not staged after stash pop
Conflicts may occur when popping a stash. Check status:
```bash
giddy status
```

### Accidental commit on wrong branch?
Reset and try again:
```bash
git reset --soft HEAD~1
giddy start "correct-feature-name"
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
│   ├── main.py              # CLI entry point
│   ├── cli.py               # User prompts and UI
│   └── git.py               # Git command wrappers
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
2. **Create** a feature branch: `git checkout -b feat/your-feature`
3. **Make** your changes and add tests if possible
4. **Commit** using `giddy done` (eating our own dog food!)
5. **Push** to your fork
6. **Open** a pull request

### Development Guidelines

- Follow PEP 8 style guide
- Write clear, descriptive commit messages
- Add docstrings to functions
- Test your changes locally

## Roadmap

- [ ] Commit templates
- [ ] Integration with GitHub/GitLab APIs
- [ ] Undo/rollback functionality
- [ ] Branch switching helpers
- [ ] Automated changelog generation

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## Author

Created by **Antoine** ([GitHub](https://github.com/AntoineMamou))

---

