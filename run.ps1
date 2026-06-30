# IBSU მიღების ჩატბოტი — ტერმინალის ჩატის გამშვები.
# გამოყენება:  მარჯვენა წკაპი → "Run with PowerShell", ან:  .\run.ps1
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

# ვექტორული ბაზა თუ არ არსებობს — ჯერ ავაშენოთ
if (-not (Test-Path ".\chroma_store")) {
    Write-Host "ვაშენებ ვექტორულ ბაზას (ერთჯერადი ნაბიჯი)..." -ForegroundColor Yellow
    & .\venv\Scripts\python.exe -m src.ingest
}

& .\venv\Scripts\python.exe app_cli.py
