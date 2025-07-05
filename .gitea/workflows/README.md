# Gitea CI/CD Workflow

This repository uses Gitea Actions for automated building, testing, and deployment.

## Workflow Overview

The main workflow (`.gitea/workflows/ci-cd.yml`) performs the following steps:

### 1. Build
- Sets up Python 3.11 environment
- Installs PDM (Python Dependency Manager)
- Installs project dependencies and test dependencies
- Builds the package using `pdm build`

### 2. Test  
- Runs unit tests with pytest
- Generates code coverage reports
- Tests are located in `tests/unit/` directory
- Coverage target: 85% (configured in `pyproject.toml`)

### 3. Deploy to PyPI Test
- **Only runs on main branch pushes**
- Uploads built package to test.pypi.org
- Uses skip-existing flag to avoid conflicts
- Requires `PYPI_TEST_TOKEN` secret to be configured

## Workflow Triggers

The workflow runs on:
- **Push** to `main` and `develop` branches
- **Pull Requests** to `main` branch

## Required Secrets

To enable PyPI Test deployment, you need to configure the following secret in your Gitea repository:

### PYPI_TEST_TOKEN
1. Go to [test.pypi.org](https://test.pypi.org)
2. Create an account or log in
3. Generate an API token in Account Settings
4. In your Gitea repository: Settings → Secrets → Add secret
5. Name: `PYPI_TEST_TOKEN`
6. Value: Your API token (including `pypi-` prefix)

## Local Development

To run the same commands locally:

```bash
# Install dependencies
pdm install
pdm add pytest pytest-asyncio pytest-cov pytest-mock factory-boy freezegun respx

# Run tests
pdm run pytest tests/unit/ -v --cov=src/mealie_client

# Build package
pdm build

# Upload to PyPI Test (optional)
pdm add twine
pdm run twine upload --repository testpypi dist/* --skip-existing
```

## Package Information

- **Package Name**: `mealie-client`
- **Module Name**: `mealie_client` 
- **Current Version**: 0.1.0
- **Build System**: PDM with pdm-backend
- **Test Framework**: pytest with asyncio support

## Workflow Status

Check the "Actions" tab in your Gitea repository to see workflow runs and their status.

## Troubleshooting

### Common Issues

1. **Test failures**: Check the test output in the workflow logs
2. **Build failures**: Ensure all dependencies are properly specified in `pyproject.toml`
3. **PyPI upload failures**: 
   - Verify `PYPI_TEST_TOKEN` secret is correctly set
   - Check if the version already exists on test.pypi.org
   - Ensure package metadata is valid

### Debugging

To debug locally, you can run individual workflow steps:

```bash
# Check Python version
python --version

# Verify PDM installation  
pdm --version

# List PDM scripts
pdm run --list

# Check package can be imported
python -c "import mealie_client; print(mealie_client.__version__)"
``` 

## Optional: Automatic Version Bump in CI

You can instruct the CI pipeline to automatically bump the project version **before** building the package.

1. Go to your repository **Settings → Secrets**.
2. Add a new secret named `CI_VERSION_BUMP` with one of the following values:
   * `patch` – increments 0.0.X
   * `minor` – increments 0.X.0
   * `major` – increments X.0.0
   * `1.2.3` – any explicit version string in `MAJOR.MINOR.PATCH` format

If the secret is **not set** or left empty, the bump step is skipped and the existing version is used.

The bump is handled by the `scripts/bump_version.py` script, which updates both `pyproject.toml` and the module's `__version__` variable. 

## Tag-Based Release Publishing
 
 When you push a git tag following the pattern `vX.Y.Z` (e.g. `v1.2.0`) a dedicated workflow `.gitea/workflows/tag-release.yml` will:
 
 1. Extract the version from the tag _(strips the leading `v`)_.
 2. Run `scripts/bump_version.py` to synchronise `pyproject.toml` & `__version__` to exactly that version (in memory – no commit necessary).
 3. Execute tests, build the package, upload to TestPyPI, then to Production PyPI.
 
 **Prerequisites**: secrets `PYPI_TEST_TOKEN` and `PYPI_TOKEN` must be configured (same as main pipeline).
 
 ```bash
 # Example release workflow
 git tag v1.2.0
 git push origin v1.2.0
 ``` 