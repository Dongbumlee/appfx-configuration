import os
from types import SimpleNamespace

import pytest

import appfx.configuration as configuration
from appfx.configuration.azure import (
    AZURE_APPCONFIG_ENDPOINT_ENV_VAR,
    AzureAppConfigurationEndpointError,
    AzureCredential,
    create_default_credential,
    helper,
    load_app_configuration_environment,
    load_app_configuration_settings,
)
from appfx.configuration.env import load_environment_variables


def test_package_imports() -> None:
    assert configuration.__version__ == "0.1.0"
    assert configuration.__all__ == ["__version__"]


def test_azure_helper_imports() -> None:
    assert AZURE_APPCONFIG_ENDPOINT_ENV_VAR == "AZURE_APPCONFIG_ENDPOINT"
    assert AzureAppConfigurationEndpointError.__name__ == (
        "AzureAppConfigurationEndpointError"
    )
    assert AzureCredential.__name__ == "DefaultAzureCredential"
    assert callable(create_default_credential)
    assert callable(load_app_configuration_environment)
    assert callable(load_app_configuration_settings)


def test_load_environment_variables_loads_dotenv_only(
    tmp_path, monkeypatch: pytest.MonkeyPatch
) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            [
                "DOTENV_ONLY=from-dotenv",
                "DOTENV_SHARED=from-dotenv",
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.delenv("DOTENV_ONLY", raising=False)
    monkeypatch.setenv("DOTENV_SHARED", "from-environment")

    settings = load_environment_variables(env_file)

    assert settings == {
        "DOTENV_ONLY": "from-dotenv",
        "DOTENV_SHARED": "from-environment",
    }
    assert os.environ["DOTENV_ONLY"] == "from-dotenv"
    assert os.environ["DOTENV_SHARED"] == "from-environment"


def test_load_app_configuration_settings_requires_endpoint(
    tmp_path, monkeypatch: pytest.MonkeyPatch
) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("", encoding="utf-8")
    monkeypatch.delenv(AZURE_APPCONFIG_ENDPOINT_ENV_VAR, raising=False)

    with pytest.raises(AzureAppConfigurationEndpointError) as exc_info:
        load_app_configuration_settings(env_file=env_file, credential=object())

    message = str(exc_info.value)
    assert "Azure App Configuration endpoint URL is required" in message
    assert "AZURE_APPCONFIG_ENDPOINT" in message


def test_load_app_configuration_settings_merges_local_overrides(
    tmp_path, monkeypatch: pytest.MonkeyPatch
) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            [
                "AZURE_APPCONFIG_ENDPOINT=https://example.azconfig.io",
                "LOCAL_ONLY=from-dotenv",
                "SHARED=from-dotenv",
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.delenv(AZURE_APPCONFIG_ENDPOINT_ENV_VAR, raising=False)
    monkeypatch.delenv("AZURE_ONLY", raising=False)
    monkeypatch.delenv("LOCAL_ONLY", raising=False)
    monkeypatch.setenv("SHARED", "from-environment")

    class FakeAzureAppConfigurationClient:
        def __init__(self, base_url: str, credential: object) -> None:
            self.base_url = base_url
            self.credential = credential

        def list_configuration_settings(self) -> list[SimpleNamespace]:
            return [
                SimpleNamespace(key="AZURE_ONLY", value="from-azure"),
                SimpleNamespace(key="SHARED", value="from-azure"),
                SimpleNamespace(key="EMPTY_VALUE", value=None),
            ]

    monkeypatch.setattr(
        helper, "AzureAppConfigurationClient", FakeAzureAppConfigurationClient
    )

    settings = load_app_configuration_settings(env_file=env_file, credential=object())

    assert settings["AZURE_ONLY"] == "from-azure"
    assert settings["LOCAL_ONLY"] == "from-dotenv"
    assert settings["SHARED"] == "from-environment"
    assert settings[AZURE_APPCONFIG_ENDPOINT_ENV_VAR] == "https://example.azconfig.io"
    assert "EMPTY_VALUE" not in settings
    assert "AZURE_ONLY" not in os.environ


def test_load_app_configuration_settings_excludes_unrelated_environment(
    tmp_path, monkeypatch: pytest.MonkeyPatch
) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            [
                "AZURE_APPCONFIG_ENDPOINT=https://example.azconfig.io",
                "DOTENV_KEY=from-dotenv",
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.delenv(AZURE_APPCONFIG_ENDPOINT_ENV_VAR, raising=False)
    monkeypatch.delenv("DOTENV_KEY", raising=False)
    monkeypatch.setenv("UNRELATED_ENV_VAR", "must-not-leak")

    class FakeAzureAppConfigurationClient:
        def __init__(self, base_url: str, credential: object) -> None:
            self.base_url = base_url
            self.credential = credential

        def list_configuration_settings(self) -> list[SimpleNamespace]:
            return [SimpleNamespace(key="AZURE_ONLY", value="from-azure")]

    monkeypatch.setattr(
        helper, "AzureAppConfigurationClient", FakeAzureAppConfigurationClient
    )

    settings = load_app_configuration_settings(env_file=env_file, credential=object())

    assert settings["AZURE_ONLY"] == "from-azure"
    assert settings["DOTENV_KEY"] == "from-dotenv"
    assert "UNRELATED_ENV_VAR" not in settings


def test_load_app_configuration_settings_keeps_process_env_over_azure(
    tmp_path, monkeypatch: pytest.MonkeyPatch
) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text(
        "AZURE_APPCONFIG_ENDPOINT=https://example.azconfig.io",
        encoding="utf-8",
    )
    monkeypatch.delenv(AZURE_APPCONFIG_ENDPOINT_ENV_VAR, raising=False)
    monkeypatch.setenv("SHARED", "from-environment")

    class FakeAzureAppConfigurationClient:
        def __init__(self, base_url: str, credential: object) -> None:
            self.base_url = base_url
            self.credential = credential

        def list_configuration_settings(self) -> list[SimpleNamespace]:
            return [SimpleNamespace(key="SHARED", value="from-azure")]

    monkeypatch.setattr(
        helper, "AzureAppConfigurationClient", FakeAzureAppConfigurationClient
    )

    settings = load_app_configuration_settings(env_file=env_file, credential=object())

    assert settings["SHARED"] == "from-environment"
    assert os.environ["SHARED"] == "from-environment"


def test_load_app_configuration_environment_can_override_process_env(
    tmp_path, monkeypatch: pytest.MonkeyPatch
) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text(
        "AZURE_APPCONFIG_ENDPOINT=https://example.azconfig.io",
        encoding="utf-8",
    )
    monkeypatch.delenv(AZURE_APPCONFIG_ENDPOINT_ENV_VAR, raising=False)
    monkeypatch.setenv("SHARED", "from-environment")

    class FakeAzureAppConfigurationClient:
        def __init__(self, base_url: str, credential: object) -> None:
            self.base_url = base_url
            self.credential = credential

        def list_configuration_settings(self) -> list[SimpleNamespace]:
            return [SimpleNamespace(key="SHARED", value="from-azure")]

    monkeypatch.setattr(
        helper, "AzureAppConfigurationClient", FakeAzureAppConfigurationClient
    )

    settings = load_app_configuration_environment(
        env_file=env_file,
        credential=object(),
        override=True,
    )

    assert settings["SHARED"] == "from-azure"
    assert os.environ["SHARED"] == "from-azure"


def test_load_app_configuration_settings_allows_endpoint_from_environment(
    tmp_path, monkeypatch: pytest.MonkeyPatch
) -> None:
    env_file = tmp_path / ".env"
    monkeypatch.setenv(
        AZURE_APPCONFIG_ENDPOINT_ENV_VAR, "https://environment.azconfig.io"
    )

    class FakeAzureAppConfigurationClient:
        def __init__(self, base_url: str, credential: object) -> None:
            self.base_url = base_url
            self.credential = credential

        def list_configuration_settings(self) -> list[SimpleNamespace]:
            assert self.base_url == "https://environment.azconfig.io"
            return [SimpleNamespace(key="AZURE_ONLY", value="from-azure")]

    monkeypatch.setattr(
        helper, "AzureAppConfigurationClient", FakeAzureAppConfigurationClient
    )

    settings = load_app_configuration_settings(env_file=env_file, credential=object())

    assert settings == {"AZURE_ONLY": "from-azure"}


def test_load_app_configuration_environment_sets_azure_environment_values(
    tmp_path, monkeypatch: pytest.MonkeyPatch
) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            [
                "AZURE_APPCONFIG_ENDPOINT=https://example.azconfig.io",
                "LOCAL_ONLY=from-dotenv",
                "SHARED=from-dotenv",
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.delenv(AZURE_APPCONFIG_ENDPOINT_ENV_VAR, raising=False)
    monkeypatch.delenv("AZURE_ONLY", raising=False)
    monkeypatch.delenv("LOCAL_ONLY", raising=False)
    monkeypatch.setenv("SHARED", "from-environment")

    class FakeAzureAppConfigurationClient:
        def __init__(self, base_url: str, credential: object) -> None:
            self.base_url = base_url
            self.credential = credential

        def list_configuration_settings(self) -> list[SimpleNamespace]:
            return [
                SimpleNamespace(key="AZURE_ONLY", value="from-azure"),
                SimpleNamespace(key="SHARED", value="from-azure"),
            ]

    monkeypatch.setattr(
        helper, "AzureAppConfigurationClient", FakeAzureAppConfigurationClient
    )

    settings = load_app_configuration_environment(
        env_file=env_file,
        credential=object(),
    )

    assert settings["AZURE_ONLY"] == "from-azure"
    assert settings["LOCAL_ONLY"] == "from-dotenv"
    assert settings["SHARED"] == "from-environment"
    assert os.environ["AZURE_ONLY"] == "from-azure"
    assert os.environ["LOCAL_ONLY"] == "from-dotenv"
    assert os.environ["SHARED"] == "from-environment"
