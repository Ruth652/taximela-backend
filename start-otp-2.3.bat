@echo off
echo ========================================
echo Starting OTP 2.3.0 Server
echo ========================================
echo.

cd otp

if not exist "graphs\default\graph.obj" (
    echo ERROR: Graph not found!
    echo Please run: .\build-graph-2.3.bat first
    pause
    exit /b 1
)

echo Starting OTP server...
echo.
echo Server URL: http://localhost:8080
echo API Endpoint: http://localhost:8080/otp/routers/default
echo.
echo Press Ctrl+C to stop
echo.

java -Xmx2G -jar otp-2.3.0-shaded.jar --load --serve graphs/default
