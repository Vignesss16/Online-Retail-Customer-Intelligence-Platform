# Windows PowerShell setup script for Intelligent Online Retail PySpark project
$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

Write-Host "=== Setting up PySpark Retail Intelligence on Windows ===" -ForegroundColor Cyan

# 1. Check/Set Java 21
$JavaCand = "C:\Program Files\Microsoft\jdk-21.0.12.101-hotspot"
if (Test-Path "$JavaCand\bin\java.exe") {
    $env:JAVA_HOME = $JavaCand
    Write-Host "[OK] JAVA_HOME set to: $JavaCand" -ForegroundColor Green
} else {
    Write-Host "[INFO] Installing OpenJDK 21 via winget..." -ForegroundColor Yellow
    winget install --id Microsoft.OpenJDK.21 --accept-source-agreements --accept-package-agreements --exact
}

# 2. Virtual environment with Python 3.12 (using uv)
$VenvPython = "D:\MajorPRoject\.venv\Scripts\python.exe"
if (-not (Test-Path $VenvPython)) {
    Write-Host "[INFO] Creating virtual environment at D:\MajorPRoject\.venv..." -ForegroundColor Yellow
    uv venv --python 3.12 D:\MajorPRoject\.venv
    uv pip install --python $VenvPython -r requirements.txt
}

# 3. Create .venv junction in project root if missing
if (-not (Test-Path "$ProjectRoot\.venv")) {
    cmd /c "mklink /J `"$ProjectRoot\.venv`" `"D:\MajorPRoject\.venv`""
}

# 4. Register Jupyter kernel
& $VenvPython -m ipykernel install --user --name bda-retail --display-name "Python (BDA Retail)"

Write-Host "`n=== Setup Completed Successfully! ===" -ForegroundColor Green
Write-Host "To run pipeline:   .venv\Scripts\python.exe -m src.pipeline" -ForegroundColor Cyan
Write-Host "To run dashboard:  .venv\Scripts\streamlit.exe run app/streamlit_app.py" -ForegroundColor Cyan
Write-Host "To run tests:      .venv\Scripts\pytest.exe -q" -ForegroundColor Cyan
