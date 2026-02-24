@echo off
echo ========================================
echo Starting OTP Server 2.8.1
echo ========================================
echo.

cd otp

REM Check if graph exists
if not exist "graphs\default\graph.obj" (
    echo ERROR: Graph not found!
    echo Please run build-graph.bat first.
    echo.
    pause
    exit /b 1
)

echo Starting OTP server on http://localhost:8080
echo API Documentation: http://localhost:8080/otp/routers/default
echo.
echo Press Ctrl+C to stop the server
echo.

java -Xmx2G -jar otp-2.8.1-shaded.jar --load --serve graphs/default
