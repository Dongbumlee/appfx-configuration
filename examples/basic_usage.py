"""Basic usage example for the appfx.configuration package."""

from appfx.configuration.env import load_environment_variables

if __name__ == "__main__":
    settings = load_environment_variables()
    print(settings)
