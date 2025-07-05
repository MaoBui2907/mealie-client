# PowerShell script to upload package to TestPyPI
# Run this script after setting up your API token

Write-Host "🚀 Uploading mealie-client to TestPyPI..." -ForegroundColor Green

# Check if dist directory exists
if (-not (Test-Path "dist")) {
    Write-Host "❌ No dist directory found. Run 'pdm build' first." -ForegroundColor Red
    exit 1
}

# Check if API token is set
if (-not $env:TWINE_PASSWORD -and -not (Test-Path "~/.pypirc")) {
    Write-Host "❌ No API token found. Please set TWINE_PASSWORD or create ~/.pypirc" -ForegroundColor Red
    Write-Host "Example:" -ForegroundColor Yellow
    Write-Host '$env:TWINE_USERNAME = "__token__"' -ForegroundColor Yellow
    Write-Host '$env:TWINE_PASSWORD = "pypi-your-token-here"' -ForegroundColor Yellow
    exit 1
}

# Upload to TestPyPI
Write-Host "📦 Uploading to TestPyPI..." -ForegroundColor Blue
pdm run twine upload --repository testpypi dist/*

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Upload successful!" -ForegroundColor Green
    Write-Host "🔗 View your package at: https://test.pypi.org/project/mealie-client/" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "📥 To test installation:" -ForegroundColor Yellow
    Write-Host "pip install -i https://test.pypi.org/simple/ mealie-client" -ForegroundColor Yellow
} else {
    Write-Host "❌ Upload failed!" -ForegroundColor Red
    Write-Host "💡 Possible issues:" -ForegroundColor Yellow
    Write-Host "   - Package name already exists (try bumping version)" -ForegroundColor Yellow
    Write-Host "   - Invalid API token" -ForegroundColor Yellow
    Write-Host "   - Network issues" -ForegroundColor Yellow
} 