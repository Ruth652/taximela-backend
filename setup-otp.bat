@echo off
echo ========================================
echo TaxiMela OTP Setup Script
echo ========================================
echo.

REM Create otp directory if it doesn't exist
if not exist "otp" mkdir otp
cd otp

REM Download OTP 2.8.1 if not already downloaded
if exist "otp-2.8.1-shaded.jar" (
    echo Deleting corrupted JAR file...
    del otp-2.8.1-shaded.jar
)

echo Downloading OTP 2.8.1... (This may take a few minutes, ~100MB)
echo.
curl -L --progress-bar -o otp-2.8.1-shaded.jar https://repo1.maven.org/maven2/org/opentripplanner/otp/2.8.1/otp-2.8.1-shaded.jar

if exist "otp-2.8.1-shaded.jar" (
    echo.
    echo Download complete!
    echo Verifying file size...
    dir otp-2.8.1-shaded.jar | find "otp-2.8.1"
) else (
    echo.
    echo ERROR: Download failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo Setup complete!
echo ========================================
echo.
echo To build the graph, run: build-graph.bat
echo To start OTP server, run: start-otp.bat
echo.
pause
