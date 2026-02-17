@echo off
echo ========================================
echo Checking OTP Versions
echo ========================================
echo.

echo Trying OTP 2.6.0 (Latest Stable)...
cd otp
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; try { Invoke-WebRequest -Uri 'https://repo1.maven.org/maven2/org/opentripplanner/otp/2.6.0/otp-2.6.0-shaded.jar' -OutFile 'otp-2.6.0-shaded.jar' -ErrorAction Stop; Write-Host 'SUCCESS: OTP 2.6.0 downloaded!' -ForegroundColor Green; Get-Item 'otp-2.6.0-shaded.jar' | Select-Object Name, @{Name='Size(MB)';Expression={[math]::Round($_.Length/1MB,2)}} } catch { Write-Host 'FAILED: OTP 2.6.0 not available' -ForegroundColor Red }}"
cd ..

echo.
pause
