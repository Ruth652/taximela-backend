# TaxiMela OTP Setup Script (PowerShell)
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "TaxiMela OTP Setup Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Create otp directory if it doesn't exist
if (-not (Test-Path "otp")) {
    New-Item -ItemType Directory -Path "otp" | Out-Null
}

Set-Location otp

# Remove corrupted file if exists
if (Test-Path "otp-2.8.1-shaded.jar") {
    Write-Host "Removing existing file..." -ForegroundColor Yellow
    Remove-Item "otp-2.8.1-shaded.jar" -Force
}

Write-Host "Downloading OTP 2.8.1... (This may take a few minutes, ~100MB)" -ForegroundColor Green
Write-Host ""

$url = "https://repo1.maven.org/maven2/org/opentripplanner/otp/2.8.1/otp-2.8.1-shaded.jar"
$output = "otp-2.8.1-shaded.jar"

try {
    # Use WebClient for better download with progress
    $webClient = New-Object System.Net.WebClient
    $webClient.DownloadFile($url, $output)
    
    Write-Host ""
    Write-Host "Download complete!" -ForegroundColor Green
    
    # Check file size
    $fileSize = (Get-Item $output).Length / 1MB
    Write-Host "File size: $([math]::Round($fileSize, 2)) MB" -ForegroundColor Cyan
    
    if ($fileSize -lt 50) {
        Write-Host ""
        Write-Host "ERROR: Downloaded file is too small. Download may have failed." -ForegroundColor Red
        Write-Host "Expected size: ~100MB, Got: $([math]::Round($fileSize, 2)) MB" -ForegroundColor Red
        exit 1
    }
    
} catch {
    Write-Host ""
    Write-Host "ERROR: Download failed!" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setup complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "To build the graph, run: .\build-graph.bat" -ForegroundColor Yellow
Write-Host "To start OTP server, run: .\start-otp.bat" -ForegroundColor Yellow
Write-Host ""
