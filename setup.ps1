# Card2vCard - one-time local setup (Windows / PowerShell)
# Creates an isolated Python 3.11 virtual environment and installs the pinned deps.
# Run this once after cloning. Then use .\run.ps1 to start the app.

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "Creating Python 3.11 virtual environment (.venv)..." -ForegroundColor Cyan
py -3.11 -m venv .venv

Write-Host "Upgrading pip..." -ForegroundColor Cyan
.\.venv\Scripts\python.exe -m pip install --upgrade pip --quiet

Write-Host "Installing pinned dependencies from requirements.txt..." -ForegroundColor Cyan
.\.venv\Scripts\python.exe -m pip install -r requirements.txt --quiet

Write-Host ""
Write-Host "Setup complete." -ForegroundColor Green
Write-Host "Start the app with:  .\run.ps1"
