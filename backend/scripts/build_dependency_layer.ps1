param(
  [string]$Python = "python",
  [string]$OutputDir = "layer-build"
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$layerRoot = Join-Path $root $OutputDir
$pythonDir = Join-Path $layerRoot "python"
$zipPath = Join-Path $layerRoot "raycare-deps-layer.zip"

if (Test-Path $layerRoot) {
  Remove-Item -Recurse -Force $layerRoot
}

New-Item -ItemType Directory -Path $pythonDir | Out-Null

& $Python -m pip install -r (Join-Path $root "requirements.txt") -t $pythonDir

Compress-Archive -Path (Join-Path $pythonDir "*") -DestinationPath $zipPath -Force

Write-Output "Layer archive created at: $zipPath"
