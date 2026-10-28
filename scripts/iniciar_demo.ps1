[CmdletBinding()]
param(
    [string]$PythonPath
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
if (-not $PythonPath) {
    $PythonPath = Join-Path $repoRoot ".venv\Scripts\python.exe"
}

if (-not (Test-Path -LiteralPath $PythonPath -PathType Leaf)) {
    Write-Error (
        "No se encontró el intérprete del entorno virtual en '$PythonPath'. " +
        "Crea .venv e instala el proyecto antes de iniciar la demo."
    )
    exit 1
}

Push-Location $repoRoot
try {
    Write-Host "DataTrust API: http://127.0.0.1:8000"
    Write-Host "Para detener el servidor, presiona Ctrl+C."
    & $PythonPath -m uvicorn datatrust_api.main:app `
        --host 127.0.0.1 `
        --port 8000 `
        --workers 1
    exit $LASTEXITCODE
}
finally {
    Pop-Location
}
