# Distribution Guide

## Publishing to PyPI

### First-time setup

1. Create PyPI account at https://pypi.org/account/register/

2. Create API token at https://pypi.org/manage/account/token/
   - Token name: "agent-arcade"
   - Scope: "Entire account" (or specific to agent-arcade later)

3. Configure Poetry with your token:
   ```bash
   poetry config pypi-token.pypi YOUR_TOKEN_HERE
   ```

### Publishing a new version

1. Update version in `pyproject.toml`:
   ```bash
   # Edit version number manually, or use:
   poetry version patch  # 1.0.0 -> 1.0.1
   poetry version minor  # 1.0.0 -> 1.1.0
   poetry version major  # 1.0.0 -> 2.0.0
   ```

2. Commit the version change:
   ```bash
   git add pyproject.toml
   git commit -m "Bump version to $(poetry version -s)"
   ```

3. Build and publish:
   ```bash
   poetry build
   poetry publish
   ```

4. Create GitHub release:
   ```bash
   VERSION=$(poetry version -s)
   git tag -a "v$VERSION" -m "Release v$VERSION"
   git push origin "v$VERSION"
   ```

## User Installation

### Recommended: pipx (isolated installation)

```bash
# Install pipx if needed
brew install pipx
pipx ensurepath

# Install agent-arcade
pipx install agent-arcade

# Update to latest
pipx upgrade agent-arcade
```

### Alternative: pip (global installation)

```bash
pip install agent-arcade

# Update to latest
pip install --upgrade agent-arcade
```

## Testing Before Publishing

Test the package locally:

```bash
# Build the package
poetry build

# Install in a test environment
pip install dist/agent_arcade-*.whl

# Test it works
agent-arcade --help

# Uninstall test version
pip uninstall agent-arcade
```

## Notes

- Version check on startup ensures users have latest games
- Set `SKIP_VERSION_CHECK=1` during development
- PyPI packages are immediately available after publishing
- pipx creates isolated environments (recommended for CLI tools)
