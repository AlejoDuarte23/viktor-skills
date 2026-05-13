# VIKTOR CLI Config Examples

## Create A New App With The CLI

Use `create-app` when the platform app and local starter files do not exist yet. Keep the CLI registered name and `viktor.config.toml` registered name the same.

```bash
viktor-cli create-app "Bearing Pressure Check" --init --registered-name bearing-pressure-check --app-type simple
```

Expected config:

```toml
app_type = "simple"
registered_name = "bearing-pressure-check"
python_version = "3.12"
```

## Manual App From Scratch

Use this when you are creating the application files yourself instead of using `--init`.

Create these local files first:

```text
my-app
├── app.py
├── requirements.txt
└── viktor.config.toml
```

`viktor.config.toml`:

```toml
app_type = "simple"
registered_name = "bearing-pressure-check"
python_version = "3.12"
```

`requirements.txt`:

```text
viktor==X.X.X
```

Then create the platform app with the same registered name and install it locally:

```bash
viktor-cli create-app "Bearing Pressure Check" --registered-name bearing-pressure-check
viktor-cli install
viktor-cli start
```

For the first launch, `clean-start` can replace `install` plus `start`:

```bash
viktor-cli create-app "Bearing Pressure Check" --registered-name bearing-pressure-check
viktor-cli clean-start
```

## Minimal `viktor.config.toml`

```toml
app_type = "simple"
python_version = "3.12"
```

## Editor App Config

Use `editor` when each user should get one fresh session and saved shared entities are not needed.

```toml
app_type = "editor"
python_version = "3.12"
```

## Simple App Config

Use `simple` when the app has one entity type and users need to create, save, edit, and share multiple entities.

```toml
app_type = "simple"
registered_name = "bearing-pressure-check"
python_version = "3.12"
```

## Tree App Config

Use `tree` when the app needs multiple entity types in a hierarchy.

```toml
app_type = "tree"
welcome_text = "welcome.md"
python_version = "3.12"
```

## Config With Assets and System Packages

```toml
app_type = "simple"
assets_path = "assets"
packages = [
  "libgl1",
  "tesseract-ocr",
]
python_version = "3.12"
```

## Requirements With Pinned Packages

```text
viktor==X.X.X
drawSVG==1.3.1
```

Run this after changing `requirements.txt`:

```bash
viktor-cli install
```

Run the same command after adding any new Python dependency.

## First Local Setup

```bash
viktor-cli configure
viktor-cli check-system
viktor-cli clean-start
```

Use the Linux CLI inside WSL2.

## Docker Local Setup Check

```bash
viktor-cli configure
viktor-cli check-system --docker
viktor-cli clean-start
```

## Daily Development Loop

```bash
viktor-cli start
```

In a second terminal:

```bash
viktor-cli test
viktor-cli run -- python -m unittest discover -s tests
viktor-cli run -- python --version
```

## Start Against a Specific Registered App

Prefer matching `registered_name` in `viktor.config.toml`, then this is enough:

```bash
viktor-cli start
```

Use the explicit flag only when you intentionally need it, and keep it equal to the config value:

```bash
viktor-cli start --registered-name bearing-pressure-check
```

For a multi-region organization:

```bash
viktor-cli start --registered-name bearing-pressure-check --region us1
```

## Run With Environment Variables

```bash
viktor-cli start -e MODE=development
viktor-cli run -e MODE=development -- python -m unittest discover -s tests
```

## Publish Checklist

1. Check `app_type`, `python_version`, `packages`, and `registered_name` in `viktor.config.toml`.
2. Confirm `registered_name` matches the VIKTOR platform app you created or intend to publish to.
3. Check `requirements.txt` pins.
4. Run `viktor-cli install` if `requirements.txt` changed.
5. Run tests.
6. Exclude development-only files with `.viktorignore`.
7. Publish.

When the config has the right `registered_name`:

```bash
viktor-cli test
viktor-cli publish
```

When being explicit, use the same name as the config:

```bash
viktor-cli test
viktor-cli publish --registered-name bearing-pressure-check
```

Use this only when the current filesystem should be published instead of committed git contents:

```bash
viktor-cli publish --registered-name bearing-pressure-check --use-filesystem
```

## `.viktorignore`

```text
tests/
test_*.py
*_test.py
docs/
*.md
data/*.tmp
```
