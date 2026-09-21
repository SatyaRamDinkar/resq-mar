@echo off
echo =========================================
echo OSRM Setup for ResQ-MAR (India Version)
echo =========================================
echo This script downloads India (Southern Zone (Andhra Pradesh)) OSM data and starts OSRM server.
echo Requires: Docker installed and running
echo.

:: Step 1: Create directory
if not exist "data\osrm" mkdir data\osrm
cd data\osrm

:: Step 2: Download India Southern Zone (Andhra Pradesh) OSM extract (Geofabrik)
echo [INFO] Downloading India (Southern Zone (Andhra Pradesh)) OSM extract...
curl -L -o india-southern-zone-latest.osm.pbf https://download.geofabrik.de/asia/india/southern-zone-latest.osm.pbf

:: Step 3: Run OSRM extraction (Docker)
echo [INFO] Running OSRM extraction (this may take 5-10 minutes)...
docker run -t -v "%cd%:/data" osrm/osrm-backend osrm-extract -p /opt/car.lua /data/india-southern-zone-latest.osm.pbf

:: Step 4: Run OSRM partition
echo [INFO] Partitioning...
docker run -t -v "%cd%:/data" osrm/osrm-backend osrm-partition /data/india-southern-zone-latest.osrm

:: Step 5: Run OSRM customize
echo [INFO] Customizing...
docker run -t -v "%cd%:/data" osrm/osrm-backend osrm-customize /data/india-southern-zone-latest.osrm

:: Step 6: Start OSRM server
echo [INFO] Starting OSRM server on port 5000...
echo [OK] OSRM will be available at http://localhost:5000
start docker run -t -i -p 5000:5000 -v "%cd%:/data" osrm/osrm-backend osrm-routed --algorithm mld /data/india-southern-zone-latest.osrm

echo =========================================
echo OSRM is running at http://localhost:5000
echo Test in browser: http://localhost:5000/route/v1/driving/83.2185,17.6868;83.2200,17.6900?overview=false
echo =========================================
pause
