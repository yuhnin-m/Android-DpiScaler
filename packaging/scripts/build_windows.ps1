$ErrorActionPreference = "Stop"

$root = (Resolve-Path (Join-Path $PSScriptRoot "../..")).Path
$specPath = Join-Path $root "packaging/pyinstaller/android_dpiscaler.spec"
$artifactsDir = Join-Path $root "artifacts"

Set-Location $root

$appName = python -c "from core.app_metadata import APP_NAME; print(APP_NAME)"

if (Test-Path (Join-Path $root "build")) { Remove-Item (Join-Path $root "build") -Recurse -Force }
if (Test-Path (Join-Path $root "dist")) { Remove-Item (Join-Path $root "dist") -Recurse -Force }
if (Test-Path $artifactsDir) { Remove-Item $artifactsDir -Recurse -Force }
New-Item -ItemType Directory -Path $artifactsDir | Out-Null

python -m PyInstaller --noconfirm --clean $specPath

$distDir = Join-Path $root "dist/$appName"
if (-not (Test-Path $distDir)) {
  throw "Expected dist folder not found: $distDir"
}

$zipPath = Join-Path $artifactsDir "$appName-windows.zip"
Compress-Archive -Path (Join-Path $distDir "*") -DestinationPath $zipPath -Force

Write-Host "Windows artifact created: $zipPath"
