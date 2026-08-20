# DevTrend Intelligence Platform - Windows Setup Script
Write-Host "Setting up DevTrend Intelligence Platform..." -ForegroundColor Green

# Copy env file
if (-not (Test-Path .env)) {
    Copy-Item .env.example .env
    Write-Host ".env file created. Please fill in your credentials." -ForegroundColor Yellow
}

# Start PostgreSQL
docker-compose up -d postgres
Start-Sleep -Seconds 10

Write-Host "Setup complete. Run .\scripts\init_project.ps1 to start." -ForegroundColor Green