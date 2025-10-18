<#
PowerShell helper script to create a virtual environment, install packages from requirements.txt,
and run project scripts.

Usage: run this in PowerShell (as regular user). This script will:
 - Create .venv in the repo root if missing
 - Install packages from requirements.txt into that venv
 - Offer to run `python ingest.py` or `python retriever_test.py`

Adapt as needed.
#>

param(
    [switch]$Recreate,
    [switch]$InstallOnly,
    [string]$Run = "",
)

$ErrorActionPreference = 'Stop'

$RepoRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $RepoRoot

$VenvDir = Join-Path $RepoRoot '.venv'
$Python = Join-Path $VenvDir 'Scripts\python.exe'

if ($Recreate -and (Test-Path $VenvDir)) {
    Write-Host "Removing existing venv..."
    Remove-Item -Recurse -Force $VenvDir
}

if (-not (Test-Path $Python)) {
    Write-Host "Creating virtual environment at $VenvDir"
    python -m venv $VenvDir
} else {
    Write-Host "Virtual environment exists at $VenvDir"
}

Write-Host "Upgrading pip and installing requirements..."
& $Python -m pip install --upgrade pip setuptools wheel
& $Python -m pip install -r requirements.txt

if ($InstallOnly) {
    Write-Host "Installation complete. Exiting because -InstallOnly was passed."
    exit 0
}

if ($Run -ne "") {
    Write-Host "Running: python $Run"
    & $Python $Run
    exit $LASTEXITCODE
}

Write-Host "You can now run the project using the venv at $VenvDir"
Write-Host "Examples:"
Write-Host "  .\\.venv\\Scripts\\Activate.ps1 ; python ingest.py"
Write-Host "  .\\.venv\\Scripts\\Activate.ps1 ; python retriever_test.py"
Write-Host "Or run this script with -Run ingest.py"

Exit 0
