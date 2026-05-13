$ErrorActionPreference = "Stop"

if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
    throw "winget was not found. Install App Installer from Microsoft Store, then rerun this script."
}

winget install `
    --source winget `
    --exact `
    --id JohnMacFarlane.Pandoc `
    --accept-source-agreements `
    --accept-package-agreements

$pandocCommand = Get-Command pandoc -ErrorAction SilentlyContinue
if ($pandocCommand) {
    & $pandocCommand.Source --version
    exit 0
}

$candidatePaths = @(
    Join-Path $env:LOCALAPPDATA "Pandoc\pandoc.exe",
    "C:\Program Files\Pandoc\pandoc.exe"
)

foreach ($candidatePath in $candidatePaths) {
    if (Test-Path $candidatePath) {
        & $candidatePath --version
        Write-Host "Pandoc is installed. Open a new terminal if 'pandoc' is not on PATH yet."
        exit 0
    }
}

Write-Warning "Pandoc may have installed, but pandoc.exe was not found on PATH. Open a new terminal and run: pandoc --version"
exit 1
