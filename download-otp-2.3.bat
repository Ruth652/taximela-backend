@echo off
echo ========================================
echo Downloading OTP 2.3.0 (Stable Version)
echo ========================================
echo.

cd otp

if exist "otp-2.3.0-shaded.jar" (
    echo OTP 2.3.0 already exists.
    goto :end
)

echo Downloading OTP 2.3.0... (~100MB)
echo This may take a few minutes...
echo.

powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; $ProgressPreference = 'SilentlyContinue'; Invoke-WebRequest -Uri 'https://repo1.maven.org/maven2/org/opentripplanner/otp/2.3.0/otp-2.3.0-shaded.jar' -OutFile 'otp-2.3.0-shaded.jar'}"

if exist "otp-2.3.0-shaded.jar" (
    echo.
    echo Download complete!
    for %%A in (otp-2.3.0-shaded.jar) do echo File size: %%~zA bytes
) else (
    echo.
    echo ERROR: Download failed!
    pause
    exit /b 1
)

:end
echo.
echo ========================================
echo Ready to build graph!
echo ========================================
echo.
echo Next step: .\build-graph-2.3.bat
echo.
pause
