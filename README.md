# appfx.configuration

`appfx.configuration` is a typed Python configuration component with Azure App
Configuration support. It can load `.env` values into environment variables,
read settings from Azure App Configuration using `DefaultAzureCredential`, and
optionally write Azure settings into `os.environ` for libraries that read from
environment variables.

## Package names

- PyPI / distribution name: `appfx-configuration`
- Python import namespace: `appfx.configuration`
- Environment namespace: `appfx.configuration.env`
- Azure configuration namespace: `appfx.configuration.azure`

## Installation

Install the package from PyPI once published:

```powershell
python -m pip install appfx-configuration
```

For local development, install the package in editable mode with developer tools:

```powershell
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

## Configuration

Copy `.env.example` to `.env`, then replace the sample endpoint with your
Azure App Configuration endpoint URL:

```powershell
Copy-Item .env.example .env
```

```dotenv
AZURE_APPCONFIG_ENDPOINT=https://<your-app-configuration-name>.azconfig.io
```

The endpoint key name must be exactly `AZURE_APPCONFIG_ENDPOINT`. The Azure
loader reads this value from `.env` / `os.environ` before connecting to Azure App
Configuration.

`.env` is intentionally ignored by Git so local endpoints and secrets are not
committed.

## Usage

Load only `.env` values into `os.environ`:

```python
from appfx.configuration.env import load_environment_variables

local_settings = load_environment_variables()
```

Read settings from Azure App Configuration and local `.env` values as a
dictionary:

```python
from appfx.configuration.azure import load_app_configuration_settings

settings = load_app_configuration_settings()
value = settings["MY_SETTING"]
```

Load `.env` and Azure App Configuration values into `os.environ`:

```python
from appfx.configuration.azure import load_app_configuration_environment

settings = load_app_configuration_environment()
```

The loader uses `DefaultAzureCredential`, so authenticate with one of the Azure
Identity-supported mechanisms before running code that contacts Azure, such as
Azure CLI sign-in, managed identity, or environment-based credentials.

### Loading behavior

`load_app_configuration_settings()` returns a dictionary and does not write Azure
App Configuration values into `os.environ`. Use
`load_app_configuration_environment()` when you want Azure values added to the
process environment. Existing process environment values win by default; pass
`override=True` to replace them with loaded configuration values.

The loaders use this precedence order:

1. Azure App Configuration values load first.
2. Values from `.env` override Azure values with the same key.
3. Existing process environment values may override matching keys from `.env`.

Unrelated process environment variables are not included in the returned settings
dictionary. If `AZURE_APPCONFIG_ENDPOINT` is missing or blank, the loader raises
`AzureAppConfigurationEndpointError` with a clear setup message.

## Validate locally

```powershell
python -m pytest
python -m pytest --cov
python -m ruff check .
python -m ruff format --check .
python -m mypy
python -m build
python -m twine check dist/*
```

## Publishing

This project is configured for PyPI Trusted Publishing through GitHub Actions,
so releases do not require a PyPI API token in GitHub secrets or local terminals.

Before the first publish, create a PyPI pending publisher for
`appfx-configuration` with these values:

- PyPI project name: `appfx-configuration`
- Owner: `Dongbumlee`
- Repository name: `appfx-configuration`
- Workflow name: `publish.yml`
- Environment name: `pypi`

To publish a release, create and publish a GitHub release, or run the `Publish`
workflow manually from GitHub Actions after the pending publisher is configured.

## Project layout

- `src/appfx/configuration/` - package source
- `src/appfx/configuration/env.py` - `.env` environment loader
- `src/appfx/configuration/azure/` - Azure App Configuration helpers
- `tests/` - automated tests
- `docs/` - package documentation
- `examples/` - runnable usage examples
- `scripts/` - maintenance/release script notes

## Next steps

- Add full public API documentation.
