"""Azure App Configuration loading helpers."""

from __future__ import annotations

import os
from pathlib import Path

from azure.appconfiguration import AzureAppConfigurationClient
from azure.core.credentials import TokenCredential
from azure.identity import DefaultAzureCredential

from appfx.configuration.env import load_environment_variables

AzureCredential = DefaultAzureCredential
AZURE_APPCONFIG_ENDPOINT_ENV_VAR = "AZURE_APPCONFIG_ENDPOINT"


class AzureAppConfigurationEndpointError(ValueError):
    """Raised when the Azure App Configuration endpoint is not configured."""


def create_default_credential() -> DefaultAzureCredential:
    """Create the default Azure credential chain."""
    return DefaultAzureCredential()


def load_app_configuration_settings(
    *,
    env_file: str | Path = ".env",
    credential: TokenCredential | None = None,
    endpoint_env_var: str = AZURE_APPCONFIG_ENDPOINT_ENV_VAR,
    override: bool = False,
) -> dict[str, str]:
    """Load .env and Azure App Configuration values into a dictionary.

    The .env file is loaded into ``os.environ`` first. Azure App Configuration
    values are returned with local .env values applied as overrides, but Azure
    values are not written to ``os.environ`` by this function.
    """
    local_settings = load_environment_variables(env_file, override=override)
    endpoint = os.environ.get(
        endpoint_env_var, local_settings.get(endpoint_env_var, "")
    )
    endpoint = endpoint.strip()

    if not endpoint:
        raise AzureAppConfigurationEndpointError(
            "Azure App Configuration endpoint URL is required. Set it in .env as "
            f"{AZURE_APPCONFIG_ENDPOINT_ENV_VAR}."
        )

    app_config_client = AzureAppConfigurationClient(
        base_url=endpoint,
        credential=credential or create_default_credential(),
    )

    settings: dict[str, str] = {}
    for setting in app_config_client.list_configuration_settings():
        if setting.key and setting.value is not None:
            settings[setting.key] = (
                setting.value
                if override
                else os.environ.get(setting.key, setting.value)
            )

    settings.update(local_settings)
    return settings


def load_app_configuration_environment(
    *,
    env_file: str | Path = ".env",
    credential: TokenCredential | None = None,
    endpoint_env_var: str = AZURE_APPCONFIG_ENDPOINT_ENV_VAR,
    override: bool = False,
) -> dict[str, str]:
    """Load .env and Azure App Configuration values into ``os.environ``.

    Existing process environment values win by default. Set ``override=True``
    to replace existing values with the merged configuration values.
    """
    settings = load_app_configuration_settings(
        env_file=env_file,
        credential=credential,
        endpoint_env_var=endpoint_env_var,
        override=override,
    )

    for key, value in settings.items():
        if override or key not in os.environ:
            os.environ[key] = value

    return settings
