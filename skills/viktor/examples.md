# VIKTOR Router Examples

## Footing Design App

Request: "Build a VIKTOR app for isolated footing design."

Load:

- `viktor-core`
- `viktor-parametrization`
- `viktor-styling`
- `viktor-table-data-view` if the app returns tabular checks
- `viktor-geometry-view` if the app displays a 3D footing model

## Excel Upload App

Request: "Let the user upload an Excel file and preview the rows."

Load:

- `viktor-core`
- `viktor-parametrization`
- `viktor-styling`
- `viktor-upload-excel`
- `viktor-table-data-view`

## Autodesk Quantity App

Request: "Select a Revit model from ACC and calculate wall quantities."

Load:

- `viktor-core`
- `viktor-parametrization`
- `viktor-styling`
- `viktor-aec-data-model`
- `viktor-table-data-view`

## STAAD Worker App

Request: "Run STAAD.Pro from a VIKTOR app and show member forces."

Load:

- `viktor-core`
- `viktor-parametrization`
- `viktor-styling`
- `viktor-staad-pro-worker`
- `viktor-table-data-view`
- `viktor-geometry-view` if model visualization is required

## ETABS Worker App

Request: "Run ETABS from a VIKTOR app and show base reactions."

Load:

- `viktor-core`
- `viktor-parametrization`
- `viktor-styling`
- `viktor-etabs-worker`
- `viktor-table-data-view`
- `viktor-geometry-view` if model preview is required

## REST Or SDK Automation

Request: "Use VIKTOR APIs to list workspaces and trigger a computation."

Load:

- `viktor-rest-api` for platform REST endpoints
- `viktor-sdk-api` for Python SDK entity data and computations

## CLI And Dependency Setup

Request: "Configure the VIKTOR app and add a package or system dependency."

Load:

- `viktor-cli-config`
- `viktor-core` if the change affects app structure

## Built-In LLM App

Request: "Add VIKTOR's built-in LLM with tool use and image input."

Load:

- `viktor-core`
- `viktor-parametrization`
- `viktor-styling`
- `viktor-llm`

## Interactive WebView App

Request: "Create an interactive Plotly WebView where clicking a point updates VIKTOR inputs."

Load:

- `viktor-core`
- `viktor-parametrization`
- `viktor-styling`
- `viktor-webview`
