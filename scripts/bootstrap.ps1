param(
    [switch]$SkipBuild = $false,
    [switch]$SkipStart = $false
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$EnvFile = Join-Path $ProjectRoot ".env"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "CloudSentinel Bootstrap Script (PowerShell)" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

function Test-Command($cmd) {
    return Get-Command $cmd -ErrorAction SilentlyContinue
}

Write-Host "`nChecking dependencies..." -ForegroundColor Yellow
$deps = @("docker", "docker", "python", "pip")
foreach ($dep in $deps) {
    if (-not (Test-Command $dep)) {
        Write-Host "ERROR: $dep is not installed. Please install it first." -ForegroundColor Red
        exit 1
    }
}
Write-Host "Dependencies OK" -ForegroundColor Green

if (-not (Test-Path $EnvFile)) {
    Write-Host "`nCreating .env from .env.example..." -ForegroundColor Yellow
    Copy-Item (Join-Path $ProjectRoot ".env.example") $EnvFile
    Write-Host "Created .env file. Please review and update it with your settings." -ForegroundColor Green
} else {
    Write-Host "`.env file already exists." -ForegroundColor Gray
}

$dirs = @("backend\plugins", "logs", "data")
foreach ($dir in $dirs) {
    $path = Join-Path $ProjectRoot $dir
    if (-not (Test-Path $path)) {
        Write-Host "Creating $dir directory..." -ForegroundColor Yellow
        New-Item -ItemType Directory -Path $path -Force | Out-Null
    }
}

if (-not $SkipBuild) {
    Write-Host "`nBuilding Docker images..." -ForegroundColor Yellow
    Set-Location $ProjectRoot
    docker compose build
}

if (-not $SkipStart) {
    Write-Host "`nStarting services..." -ForegroundColor Yellow
    docker compose up -d postgres redis

    Write-Host "`nWaiting for PostgreSQL..." -ForegroundColor Yellow
    $maxAttempts = 30
    for ($i = 1; $i -le $maxAttempts; $i++) {
        try {
            $result = docker compose exec -T postgres pg_isready -U cloudsentinel 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Host "PostgreSQL is ready" -ForegroundColor Green
                break
            }
        } catch {}
        if ($i -eq $maxAttempts) {
            Write-Host "ERROR: PostgreSQL did not become ready in time" -ForegroundColor Red
            exit 1
        }
        Start-Sleep -Seconds 2
    }

    Write-Host "`nWaiting for Redis..." -ForegroundColor Yellow
    for ($i = 1; $i -le $maxAttempts; $i++) {
        try {
            $result = docker compose exec -T redis redis-cli ping 2>&1
            if ($result -match "PONG") {
                Write-Host "Redis is ready" -ForegroundColor Green
                break
            }
        } catch {}
        if ($i -eq $maxAttempts) {
            Write-Host "ERROR: Redis did not become ready in time" -ForegroundColor Red
            exit 1
        }
        Start-Sleep -Seconds 2
    }

    Write-Host "`nStarting all services..." -ForegroundColor Yellow
    docker compose up -d

    Write-Host "`nWaiting for backend health check..." -ForegroundColor Yellow
    for ($i = 1; $i -le $maxAttempts; $i++) {
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 5
            if ($response.StatusCode -eq 200) {
                Write-Host "Backend is healthy" -ForegroundColor Green
                break
            }
        } catch {}
        if ($i -eq $maxAttempts) {
            Write-Host "WARNING: Backend health check did not pass in time. Check logs with: docker compose logs backend" -ForegroundColor Yellow
            exit 1
        }
        Start-Sleep -Seconds 2
    }
}

Write-Host "`n==========================================" -ForegroundColor Cyan
Write-Host "CloudSentinel is running!" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host "Health:   http://localhost:8000/health" -ForegroundColor White
Write-Host "Metrics:  http://localhost:8000/metrics" -ForegroundColor White
Write-Host "`nTo view logs: docker compose logs -f" -ForegroundColor Gray
Write-Host "To stop:     docker compose down" -ForegroundColor Gray
Write-Host "==========================================" -ForegroundColor Cyan
