# IBSU მიღების ჩატბოტი — ვებ-ინტერფეისის გამშვები (ბრაუზერში გაიხსნება).
# გამოყენება:  მარჯვენა წკაპი → "Run with PowerShell", ან:  .\run_web.ps1
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

# ვექტორული ბაზა თუ არ არსებობს — ჯერ ავაშენოთ
if (-not (Test-Path ".\chroma_store")) {
    Write-Host "ვაშენებ ვექტორულ ბაზას (ერთჯერადი ნაბიჯი)..." -ForegroundColor Yellow
    & .\venv\Scripts\python.exe -m src.ingest
}

& .\venv\Scripts\streamlit.exe run app_streamlit.py
