# VIKTOR CLI Config Reference

Official sources:

- <https://docs.viktor.ai/docs/getting-started/fundamentals/app-types/>
- <https://docs.viktor.ai/docs/create-apps/references/viktor-config-toml/>
- <https://docs.viktor.ai/docs/create-apps/references/cli/>
- <https://docs.viktor.ai/docs/create-apps/development-tools-and-tips/use-python-packages/>
- <https://docs.viktor.ai/docs/create-apps/development-tools-and-tips/system-dependencies/>

## App Files

A local VIKTOR app normally has:

```text
my-app
├── app.py
├── requirements.txt
└── viktor.config.toml
```

For larger tree apps, the entry point can be `app/__init__.py` instead of `app.py`, with separate folders per entity type.

## `viktor.config.toml`

The config file is placed at the top level of the application folder and is written in TOML.

### `app_type`

`app_type` is required.

```toml
app_type = "simple"  # "editor" | "simple" | "tree"
```

- `editor`: one editor, one entity type, one unique unsaved user session. The user enters the editor directly. `InitialEntity`, `ParamsFromFile`, and `Summary` are not available.
- `simple`: one entity type, but users can create, save, edit, and restore multiple shared entities.
- `tree`: multiple entity types in a developer-defined hierarchy. Parent controllers define `children`. Top-level entities require `initial_entities` because that layer is not editable by the user.

### Other Config Keys

```toml
assets_path = "assets"
enable_privileged_api = false
packages = ["libgl1"]
python_version = "3.11"
registered_name = "my-app"
```

- `assets_path`: directory for app assets such as images, relative to the app folder.
- `enable_privileged_api`: lets app code bypass user access restrictions. Treat as sensitive.
- `packages`: Linux `apt-get` compatible system packages installed when the app is built.
- `python_version`: Python version used when publishing the application. This does not control the Python version used by local `venv` development; the CLI `configure` command controls that.
- `registered_name`: default production app name for publish commands. A CLI `--registered-name` flag overrides this value.

Tree apps can define:

```toml
welcome_text = "welcome.md"
```

Non-public apps can define:

```toml
worker_integrations = ["revit", "scia"]
oauth2_integrations = ["microsoft-entra"]
```

## Tree App Structure

Use a package-style app folder for multi-entity apps:

```text
my-folder
├── app
│   ├── blue_type
│   │   ├── __init__.py
│   │   ├── controller.py
│   │   └── parametrization.py
│   ├── green_type
│   │   ├── __init__.py
│   │   ├── controller.py
│   │   └── parametrization.py
│   └── __init__.py
├── requirements.txt
└── viktor.config.toml
```

Import controllers in `app/__init__.py`:

```python
from .blue_type.controller import BlueType
from .green_type.controller import Controller as GreenType
```

Define initial entities for tree apps:

```python
import viktor as vkt

initial_entities = [
    vkt.InitialEntity("Project", name="Example project", params={"width": 300}),
]
```

## Python Dependencies

App dependencies go in `requirements.txt`.

```text
viktor==X.X.X
drawSVG==1.3.1
```

Guidelines:

- Pin the VIKTOR SDK and app packages when reproducibility matters.
- Pinning avoids surprise breakage when package maintainers release new versions.
- Watch for version clashes with packages also used by the VIKTOR SDK.
- Explicitly list any package your app imports, even if it is currently present through the SDK.
- Check package licenses before using packages in commercial apps.

## System Dependencies

Use `packages` in `viktor.config.toml` when a Python package needs operating system packages that `pip` cannot install.

```toml
packages = ["libgl1"]
```

Published VIKTOR apps run on Linux, so package names must be `apt-get` compatible.

Common examples from the VIKTOR docs:

- `ffmpeg-python`: `ffmpeg`
- `kaleido`: `chromium`
- `opencv-python`: `python3-opencv`
- `pdf2docx`: `libgl1`
- `pyomo` with GLPK: `libglpk-dev`, `glpk-utils`
- `pytesseract`: `tesseract-ocr`
- `python-poppler`: `poppler-utils`, `libpoppler-cpp-dev`
- `pyvista` or `vtk`: `libgl1`

## CLI Setup

The VIKTOR CLI is used to install dependencies, start apps, run commands, run tests, and publish.

Initial setup:

```bash
viktor-cli configure
```

The CLI configuration asks for the environment, email address, token, isolation mode, and Python path. Isolation mode can be:

- `venv`: Python virtual environment for dependencies.
- `docker`: code and dependency management through Docker containers.

The CLI writes its account configuration to a `.viktor` folder in the user's home directory, not inside the app repository.

For WSL2 on Windows, use the Linux version of the CLI.

## Health Checks

Use:

```bash
viktor-cli check-system
viktor-cli check-system --docker
```

Default checks cover PyPI access, VIKTOR domain access, 64-bit Python configuration, and VIKTOR credentials. Docker checks also verify Docker, container access, user directory access, PyPI, VIKTOR domains, and credentials.

## Common Commands

```bash
viktor-cli apps
viktor-cli install
viktor-cli clean-start
viktor-cli start
viktor-cli run -- python -m unittest discover -s tests
viktor-cli test
viktor-cli clear
viktor-cli publish --registered-name my-app
```

Command notes:

- `install`: installs VIKTOR platform dependencies and app dependencies. Run it after changing `requirements.txt`.
- `clean-start`: installs and starts the app in a clean development workspace.
- `start`: connects local code to the platform for browser-based development. Stop it with `CTRL+C`.
- `run`: runs a command in the app container. Use `--` before the command when the command has flags.
- `test`: runs unit tests with `python -m unittest discover -s tests`, or a dotted path passed with `--path`.
- `clear`: clears entities and entity types from the development workspace database.
- `publish`: publishes code to a production app. Use only after preparing and checking the code.

Useful flags:

```bash
viktor-cli start --registered-name my-app --region us1
viktor-cli start -e FOO=foo
viktor-cli start --no-autoreload
viktor-cli run -- python --version
viktor-cli install --use-pip
```

Docker-only flags include `--max-memory`, `--dns`, `--python`, and `--volume`.

## Publishing Notes

The publish command performs checks and continues in the background once the spinner appears. After a successful CLI message, the browser may need a refresh before the latest app version appears.

Use `.viktorignore` in the app root to exclude development-only files from publication.

```text
tests/
test_*.py
*_test.py
docs/
*.md
```

Patterns follow `.gitignore` style. The `.viktorignore` file itself is excluded. Built-in exclusions already include `.git/`, `venv*/`, and Python cache directories.

Use `--use-filesystem` when the published contents should come from the current folder instead of committed git files.

## CI Commands

The CLI includes CI commands for Azure DevOps, GitHub Actions, and GitLab CI/CD:

```bash
viktor-cli ci-install
viktor-cli ci-test
viktor-cli ci-publish my-app --tag v1.2.3
```

`ci-test` runs `python -m unittest discover -s tests`.
