@echo off
echo ========================================
echo Building OTP Graph
echo ========================================
echo.

cd otp

REM Copy GTFS data
echo Copying GTFS data...
if not exist "graphs\default\gtfs" mkdir graphs\default\gtfs
xcopy /Y /E ..\data\gtfs\* graphs\default\gtfs\

REM Copy router config
echo Copying router config...
copy /Y ..\data\router-config.json graphs\default\

REM Copy OSM data (if exists)
if exist "graphs\default\addis-ababa.osm.pbf" (
    echo OSM data already exists.
) else (
    echo OSM data not found. Graph will be built with GTFS only.
)

echo.
echo Building graph... (This may take a few minutes)
java -Xmx2G -jar otp-2.8.1-shaded.jar --build --save graphs/default

echo.
echo ========================================
echo Graph build complete!
echo ========================================
echo.
echo To start OTP server, run: start-otp.bat
echo.
pause
