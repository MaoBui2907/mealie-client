# Build & Publish Scripts

This directory contains utility scripts for building and publishing the mealie-client package.

## Scripts Overview

### 🧹 `clean.ps1`
Cleans build artifacts and cache files.

```powershell
.\scripts\clean.ps1
```

**What it does:**
- Removes `dist/` directory
- Removes `build/` directory  
- Removes `*.egg-info` directories
- Removes `__pycache__` directories
- Removes `*.pyc` files

### 🔢 `bump_version.py`
Bumps version number in `pyproject.toml` following semantic versioning.

```bash
# Bump patch version (0.1.0 → 0.1.1)
python scripts/bump_version.py patch

# Bump minor version (0.1.0 → 0.2.0)
python scripts/bump_version.py minor

# Bump major version (0.1.0 → 1.0.0)
python scripts/bump_version.py major
```

### 🚀 `upload_testpypi.ps1`
Uploads the package to TestPyPI with validation checks.

```powershell
.\scripts\upload_testpypi.ps1
```

**Prerequisites:**
- Set up TestPyPI API token (see below)
- Built package in `dist/` directory

## TestPyPI Setup

### 1. Create Account
- Register at: https://test.pypi.org/account/register/
- Verify your email address

### 2. Create API Token
- Go to: https://test.pypi.org/manage/account/token/
- Click "Add API token"
- Name: `mealie-client-upload`
- Scope: "Entire account" (for first upload)
- Copy the token (starts with `pypi-`)

### 3. Set Authentication

**Option A: Environment Variables (Recommended)**
```powershell
$env:TWINE_USERNAME = "__token__"
$env:TWINE_PASSWORD = "pypi-YOUR_ACTUAL_TOKEN_HERE"
```

**Option B: .pypirc file**
Create `~/.pypirc`:
```ini
[distutils]
index-servers =
    testpypi

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-YOUR_ACTUAL_TOKEN_HERE
```

## Complete Workflow

1. **Clean previous builds:**
   ```powershell
   .\scripts\clean.ps1
   ```

2. **Bump version (if needed):**
   ```bash
   python scripts/bump_version.py patch
   ```

3. **Build package:**
   ```bash
   pdm build
   ```

4. **Upload to TestPyPI:**
   ```powershell
   .\scripts\upload_testpypi.ps1
   ```

5. **Test installation:**
   ```bash
   pip install -i https://test.pypi.org/simple/ mealie-client
   ```

## Troubleshooting

### Package already exists
If you get "File already exists" error:
- Bump version: `python scripts/bump_version.py patch`
- Rebuild: `pdm build`
- Upload again

### Authentication errors
- Verify API token is correct
- Check token scope includes the package
- Ensure username is `__token__` (not your username)

### Network issues
- Check internet connection
- Try with `--verbose` flag: `pdm run twine upload --repository testpypi --verbose dist/*` 