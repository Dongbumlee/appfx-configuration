# appfx.configuration

[![CI](https://github.com/Dongbumlee/appfx-configuration/actions/workflows/ci.yml/badge.svg)](https://github.com/Dongbumlee/appfx-configuration/actions/workflows/ci.yml)
[![Publish](https://github.com/Dongbumlee/appfx-configuration/actions/workflows/publish.yml/badge.svg)](https://github.com/Dongbumlee/appfx-configuration/actions/workflows/publish.yml)
[![PyPI](https://img.shields.io/pypi/v/appfx-configuration.svg)](https://pypi.org/project/appfx-configuration/)
[![Python versions](https://img.shields.io/pypi/pyversions/appfx-configuration.svg)](https://pypi.org/project/appfx-configuration/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/Dongbumlee/appfx-configuration/blob/main/LICENSE)

`appfx.configuration` is a lightweight Python configuration utility for loading
application settings from local `.env` files and Azure App Configuration.

The package is designed for applications that want predictable configuration
loading, local-development overrides, and optional population of `os.environ` for
libraries that read configuration from environment variables.

## Features

- Load `.env` values into `os.environ`.
- Read Azure App Configuration values using `DefaultAzureCredential`.
- Return merged configuration as `dict[str, str]`.
- Optionally write merged Azure and `.env` settings into `os.environ`.
- Preserve existing process environment values by default.
- Include a `py.typed` marker for typed consumers.

## Package and import names

| Purpose | Name |
| --- | --- |
| PyPI distribution | `appfx-configuration` |
| Python package | `appfx.configuration` |
| `.env` helpers | `appfx.configuration.env` |
| Azure App Configuration helpers | `appfx.configuration.azure` |

## Installation

Install from PyPI after the package is published:

```powershell
python -m pip install appfx-configuration
```

For local development, install the package in editable mode with development
tools:

```powershell
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

## Configure Azure App Configuration

Copy the example environment file and set your Azure App Configuration endpoint:

```powershell
Copy-Item .env.example .env
```

The required endpoint variable name is `AZURE_APPCONFIG_ENDPOINT`:

```dotenv
AZURE_APPCONFIG_ENDPOINT=https://<your-app-configuration-name>.azconfig.io
```

The Azure loader reads `AZURE_APPCONFIG_ENDPOINT` from `.env` or `os.environ`
before connecting to Azure App Configuration. The local `.env` file is ignored by
Git so local endpoints and secrets are not committed.

Authentication is handled by `DefaultAzureCredential`. Before loading Azure App
Configuration values, authenticate with a supported Azure Identity mechanism such
as Azure CLI sign-in, managed identity, or environment-based credentials.

## Usage

### Load `.env` values only

Use `appfx.configuration.env` when you only need local `.env` values loaded into
`os.environ`.

```python
from appfx.configuration.env import load_environment_variables

local_settings = load_environment_variables()
```

### Read Azure App Configuration as a dictionary

Use `load_app_configuration_settings()` when you want a merged dictionary without
writing Azure-only values into `os.environ`.

```python
from appfx.configuration.azure import load_app_configuration_settings

settings = load_app_configuration_settings()
value = settings["MY_SETTING"]
```

### Load Azure App Configuration into `os.environ`

Use `load_app_configuration_environment()` when downstream libraries expect
configuration in environment variables.

```python
from appfx.configuration.azure import load_app_configuration_environment

settings = load_app_configuration_environment()
```

Pass `override=True` to replace existing process environment values with loaded
configuration values:

```python
settings = load_app_configuration_environment(override=True)
```

## Loading behavior

The loaders apply configuration in this order:

1. Azure App Configuration values are read first.
2. Values from `.env` override Azure values with the same key.
3. Existing process environment values may override matching keys from `.env`.

By default, existing process environment values win. Unrelated process
environment variables are not included in returned settings dictionaries.

If `AZURE_APPCONFIG_ENDPOINT` is missing or blank, Azure helpers raise
`AzureAppConfigurationEndpointError` with a setup-focused error message.

## Public API

### `appfx.configuration.env`

| API | Description |
| --- | --- |
| `load_environment_variables(env_file=".env", override=False)` | Loads variables from a `.env` file into `os.environ` and returns the effective values for keys declared in that file. |

### `appfx.configuration.azure`

| API | Description |
| --- | --- |
| `load_app_configuration_settings(...)` | Loads `.env`, reads Azure App Configuration, and returns merged settings as `dict[str, str]`. |
| `load_app_configuration_environment(..., override=False)` | Loads merged settings and writes them into `os.environ`. |
| `create_default_credential()` | Creates the default Azure credential chain. |
| `AzureAppConfigurationEndpointError` | Raised when `AZURE_APPCONFIG_ENDPOINT` is missing or blank. |
| `AZURE_APPCONFIG_ENDPOINT_ENV_VAR` | Constant for the required endpoint environment variable name. |

## Development

Run the local validation suite:

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

This project is configured for PyPI Trusted Publishing through GitHub Actions.
Publishing does not require a PyPI API token in GitHub secrets or local terminals.

Before the first publish, create a PyPI pending publisher for
`appfx-configuration` with these values:

| PyPI Trusted Publisher field | Value |
| --- | --- |
| PyPI project name | `appfx-configuration` |
| Owner | `Dongbumlee` |
| Repository name | `appfx-configuration` |
| Workflow name | `publish.yml` |
| Environment name | `pypi` |

To publish a release, create and publish a GitHub release, or run the `Publish`
workflow manually from GitHub Actions after the pending publisher is configured.

## Project layout

```text
.
├── .github/workflows/     # CI and PyPI publish workflows
├── docs/                  # Package documentation
├── examples/              # Usage examples
├── scripts/               # Maintenance/release script notes
├── src/appfx/configuration/
│   ├── azure/             # Azure App Configuration helpers
│   ├── env.py             # .env environment loader
│   └── py.typed           # Typing marker
└── tests/                 # Automated tests
```

## License

This project is licensed under the MIT License. See `LICENSE` for details.
