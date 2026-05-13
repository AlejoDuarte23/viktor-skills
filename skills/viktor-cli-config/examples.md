# VIKTOR CLI Config Examples

## Minimal `viktor.config.toml`

```toml
app_type = "simple"
python_version = "3.11"
```

## Editor App Config

Use `editor` when each user should get one fresh session and saved shared entities are not needed.

```toml
app_type = "editor"
python_version = "3.11"
```

## Simple App Config

Use `simple` when the app has one entity type and users need to create, save, edit, and share multiple entities.

```toml
app_type = "simple"
registered_name = "bearing-pressure-check"
python_version = "3.11"
```

## Tree App Config

Use `tree` when the app needs multiple entity types in a hierarchy.

```toml
app_type = "tree"
welcome_text = "welcome.md"
python_version = "3.11"
```

## Config With Assets and System Packages

```toml
app_type = "simple"
assets_path = "assets"
packages = [
  "libgl1",
  "tesseract-ocr",
]
python_version = "3.11"
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

## First Local Setup

```bash
viktor-cli configure
viktor-cli check-system
viktor-cli install
viktor-cli start
```

Use the Linux CLI inside WSL2.

## Docker Local Setup Check

```bash
viktor-cli configure
viktor-cli check-system --docker
viktor-cli install
viktor-cli start
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

```bash
viktor-cli start --registered-name my-production-app
```

For a multi-region organization:

```bash
viktor-cli start --registered-name my-production-app --region us1
```

## Run With Environment Variables

```bash
viktor-cli start -e MODE=development
viktor-cli run -e MODE=development -- python -m unittest discover -s tests
```

## Publish Checklist

1. Check `app_type`, `python_version`, `packages`, and `registered_name` in `viktor.config.toml`.
2. Check `requirements.txt` pins.
3. Run tests.
4. Exclude development-only files with `.viktorignore`.
5. Publish.

```bash
viktor-cli test
viktor-cli publish --registered-name my-production-app
```

Use this only when the current filesystem should be published instead of committed git contents:

```bash
viktor-cli publish --registered-name my-production-app --use-filesystem
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
