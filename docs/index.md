# appfx.configuration documentation

`appfx.configuration` provides a small, explicit configuration-loading layer for
Python applications. It supports local `.env` files, Azure App Configuration, and
optional population of `os.environ` for frameworks and libraries that expect
settings in process environment variables.

## Naming

| Purpose | Name |
| --- | --- |
| PyPI distribution | `appfx-configuration` |
| Python package | `appfx.configuration` |
| Environment module | `appfx.configuration.env` |
| Azure module | `appfx.configuration.azure` |

## Configuration model

The package separates configuration loading into two layers:

1. `appfx.configuration.env` loads local `.env` values.
2. `appfx.configuration.azure` loads `.env`, reads Azure App Configuration, and
   returns or applies the merged values.

This keeps local development, cloud-hosted configuration, and process-level
environment mutation explicit.

## Required Azure endpoint setting

Azure helpers need the Azure App Configuration endpoint URL before they can
connect to Azure. Set it in `.env` or `os.environ` using this exact key:

```dotenv
AZURE_APPCONFIG_ENDPOINT=https://<your-app-configuration-name>.azconfig.io
```

If `AZURE_APPCONFIG_ENDPOINT` is missing or blank, Azure helpers raise
`AzureAppConfigurationEndpointError` with a setup-focused message.

## Authentication

Azure helpers authenticate with `DefaultAzureCredential` from `azure-identity`.
Use any Azure Identity-supported mechanism, such as:

- Azure CLI sign-in for local development.
- Managed identity in Azure-hosted environments.
- Environment-based credentials in CI or containerized workloads.

The package does not read Azure connection strings or secrets from code. The only
required Azure App Configuration locator is the endpoint URL.

## API reference

### `load_environment_variables()`

Module: `appfx.configuration.env`

```python
load_environment_variables(
    env_file: str | Path = ".env",
    *,
    override: bool = False,
) -> dict[str, str]
```

Loads variables from a `.env` file into `os.environ` and returns the effective
values for keys declared in that file.

Behavior:

- Returns `{}` when the `.env` file does not exist.
- Existing process environment values win by default.
- Set `override=True` to let `.env` values replace existing process environment
  values.
- Does not include unrelated process environment variables in the returned
  dictionary.

Example:

```python
from appfx.configuration.env import load_environment_variables

settings = load_environment_variables()
```

### `load_app_configuration_settings()`

Module: `appfx.configuration.azure`

```python
load_app_configuration_settings(
    *,
    env_file: str | Path = ".env",
    credential: TokenCredential | None = None,
    endpoint_env_var: str = "AZURE_APPCONFIG_ENDPOINT",
    override: bool = False,
) -> dict[str, str]
```

Loads `.env`, reads Azure App Configuration, and returns merged settings as a
dictionary.

Use this function when your application wants explicit control over the returned
configuration values and does not want Azure-only values written into
`os.environ`.

Behavior:

- Loads `.env` first so the endpoint can come from local development settings.
- Uses `DefaultAzureCredential` unless a custom credential is provided.
- Reads all Azure App Configuration key-values where both key and value are set.
- Returns merged values as `dict[str, str]`.
- Does not write Azure-only values into `os.environ`.
- Existing process environment values win by default.

Example:

```python
from appfx.configuration.azure import load_app_configuration_settings

settings = load_app_configuration_settings()
connection_name = settings["CONNECTION_NAME"]
```

### `load_app_configuration_environment()`

Module: `appfx.configuration.azure`

```python
load_app_configuration_environment(
    *,
    env_file: str | Path = ".env",
    credential: TokenCredential | None = None,
    endpoint_env_var: str = "AZURE_APPCONFIG_ENDPOINT",
    override: bool = False,
) -> dict[str, str]
```

Loads `.env`, reads Azure App Configuration, writes merged values into
`os.environ`, and returns the merged dictionary.

Use this function when downstream libraries read settings from environment
variables.

Behavior:

- Calls `load_app_configuration_settings()` internally.
- Writes each merged key-value pair into `os.environ`.
- Existing process environment values win by default.
- Set `override=True` to replace existing environment variables.

Example:

```python
from appfx.configuration.azure import load_app_configuration_environment

settings = load_app_configuration_environment()
```

## Precedence rules

By default, configuration precedence is:

1. Azure App Configuration values are read first.
2. `.env` values override Azure values with the same key.
3. Existing process environment values may override matching `.env` or Azure
   keys.

This default favors local and platform-provided overrides over centralized
configuration defaults.

Use `override=True` when you intentionally want loaded values to replace existing
process environment values.

## Common usage patterns

### Local development only

```python
from appfx.configuration.env import load_environment_variables

load_environment_variables()
```

### Local plus Azure, explicit dictionary

```python
from appfx.configuration.azure import load_app_configuration_settings

settings = load_app_configuration_settings()
```

### Local plus Azure, environment-first applications

```python
from appfx.configuration.azure import load_app_configuration_environment

load_app_configuration_environment()
```

### Custom Azure credential

```python
from azure.identity import DefaultAzureCredential
from appfx.configuration.azure import load_app_configuration_settings

credential = DefaultAzureCredential(exclude_interactive_browser_credential=True)
settings = load_app_configuration_settings(credential=credential)
```

## Error handling

Catch `AzureAppConfigurationEndpointError` when you want to provide a custom setup
message to users:

```python
from appfx.configuration.azure import (
    AzureAppConfigurationEndpointError,
    load_app_configuration_settings,
)

try:
    settings = load_app_configuration_settings()
except AzureAppConfigurationEndpointError as error:
    raise RuntimeError("Configure AZURE_APPCONFIG_ENDPOINT before startup") from error
```
