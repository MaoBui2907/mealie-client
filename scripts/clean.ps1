# PowerShell script to clean build artifacts

Write-Host "🧹 Cleaning build artifacts..." -ForegroundColor Green

# Remove dist directory
if (Test-Path "dist") {
    Remove-Item -Recurse -Force "dist"
    Write-Host "✅ Removed dist/" -ForegroundColor Yellow
}

# Remove build directory
if (Test-Path "build") {
    Remove-Item -Recurse -Force "build"
    Write-Host "✅ Removed build/" -ForegroundColor Yellow
}

# Remove egg-info directories
Get-ChildItem -Name "*.egg-info" -Directory | ForEach-Object {
    Remove-Item -Recurse -Force $_
    Write-Host "✅ Removed $_" -ForegroundColor Yellow
}

# Remove __pycache__ directories
Get-ChildItem -Recurse -Name "__pycache__" -Directory | ForEach-Object {
    Remove-Item -Recurse -Force $_.FullName
    Write-Host "✅ Removed $($_.FullName)" -ForegroundColor Yellow
}

# Remove .pyc files
Get-ChildItem -Recurse -Name "*.pyc" | ForEach-Object {
    Remove-Item -Force $_.FullName
    Write-Host "✅ Removed $($_.FullName)" -ForegroundColor Yellow
}

Write-Host "🎉 Clean complete!" -ForegroundColor Green 