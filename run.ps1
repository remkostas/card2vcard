# Card2vCard - launch the app (Windows / PowerShell)
# Uses real GPT-4o extraction if OPENAI_API_KEY is set in THIS terminal session,
# otherwise falls back to keyless mock mode (fixed sample contact, no API call).
#
# For real extraction, set the key in your own session first (it is never written to disk):
#   $env:OPENAI_API_KEY = "sk-...your key..."
#   .\run.ps1
#
# Then open  http://127.0.0.1:7860  (use 127.0.0.1, not localhost - Gradio binds IPv4).

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if ($env:OPENAI_API_KEY) {
    $env:OCR_BACKEND = "openai"
    Write-Host "OPENAI mode - key detected in this session." -ForegroundColor Green
} else {
    $env:OCR_BACKEND = "mock"
    Write-Host "MOCK mode - no OPENAI_API_KEY in this session (no API calls, fixed sample)." -ForegroundColor Yellow
    Write-Host 'For real extraction:  $env:OPENAI_API_KEY = "sk-..."  then re-run .\run.ps1'
}

Write-Host "Open http://127.0.0.1:7860 once it starts (Ctrl+C to stop)." -ForegroundColor Cyan
Set-Location "$PSScriptRoot\app"
& "..\.venv\Scripts\python.exe" app.py
