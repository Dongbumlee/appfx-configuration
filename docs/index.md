# appfx.configuration Documentation

The PyPI/distribution name is `appfx-configuration`. The Python import namespace
remains `appfx.configuration`, including Azure helpers at
`appfx.configuration.azure`.

Use `appfx.configuration.env` to load `.env` values into environment variables.
Use `appfx.configuration.azure` to load `.env` plus Azure App Configuration
values either as a dictionary or into `os.environ`.

Azure helpers expect the Azure App Configuration endpoint URL in `.env` or
`os.environ` under the exact key `AZURE_APPCONFIG_ENDPOINT`.

Future documentation should include user guides, API reference, and design notes
for the package.
