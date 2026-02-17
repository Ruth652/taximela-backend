@echo off
echo ========================================
echo Building OTP 2.3.0 Graph
echo ========================================
echo.

cd otp

if not exist "otp-2.3.0-shaded.jar" (
    echo ERROR: OTP JAR not found!
    echo Please run: .\download-otp-2.3.bat first
    pause
    exit /b 1
)

echo Building graph... (This takes 2-5 minutes)
echo.

java -Xmx2G -jar otp-2.3.0-shaded.jar --build --save graphs/default

if exist "graphs\default\graph.obj" (
    echo.
    echo ========================================
    echo Graph build SUCCESS!
    echo ========================================
    echo.
    echo Next step: .\start-otp-2.3.bat
) else (
    echo.
    echo ERROR: Graph build failed!
)

echo.
pause
