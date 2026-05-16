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

## SCIA Worker App

Request: "Create a SCIA Engineer model from a VIKTOR app and show reactions."

Load:

- `viktor-core`
- `viktor-parametrization`
- `viktor-styling`
- `viktor-scia-worker`
- `viktor-table-data-view`
- `viktor-geometry-view` if model preview is required

## ETABS Worker App

Request: "Run ETABS from a VIKTOR app and show base reactions."

Load:

- `viktor-core`
- `viktor-parametrization`
- `viktor-styling`
- `viktor-etabs-worker`
- `viktor-table-data-view`
- `viktor-geometry-view` if model preview is required

## SAP2000 Worker App

Request: "Run SAP2000 from a VIKTOR app and extract support reactions."

Load:

- `viktor-core`
- `viktor-parametrization`
- `viktor-styling`
- `viktor-sap2000-worker`
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

## Automated Tests And Mocks

Request: "Add tests for the VIKTOR views and mock the external worker calls."

Load:

- `viktor-core`
- `viktor-cli-config`
- `viktor-testing`

## Word Report Download

Request: "Add a button that generates a Word report from Markdown."

Load:

- `viktor-core`
- `viktor-parametrization`
- `viktor-styling`
- `viktor-file-management`
- `viktor-cli-config`
- `viktor-reporting-pandoc`

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

## WebView Equation Report

Request: "Render a calculation report with MathJax equations in a VIKTOR WebView."

Load:

- `viktor-core`
- `viktor-parametrization`
- `viktor-styling`
- `viktor-webview`
- `viktor-webview-mathjax`
