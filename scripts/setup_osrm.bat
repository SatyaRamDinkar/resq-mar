@echo off
echo =========================================
echo OSRM Setup for ResQ-MAR (Full India)
echo =========================================
echo This script downloads Full India OSM data and starts OSRM server.
echo Requires: Docker installed and running
echo Note: Full-India map processing requires ~16GB RAM and ~20GB of disk space.
echo.

:: Step 1: Create directory
if not exist "data\osrm" mkdir data\osrm
cd data\osrm

:: Step 2: Download India OSM extract (Geofabrik)
echo [INFO] Downloading Full India OSM extract...
curl -L -o india-latest.osm.pbf https://download.geofabrik.de/asia/india-latest.osm.pbf

:: Step 3: Run OSRM extraction (Docker)
echo [INFO] Running OSRM extraction (this may take a while)...
docker run -t -v "%cd%:/data" osrm/osrm-backend osrm-extract -p /opt/car.lua /data/india-latest.osm.pbf

:: Step 4: Run OSRM partition
echo [INFO] Partitioning...
docker run -t -v "%cd%:/data" osrm/osrm-backend osrm-partition /data/india-latest.osrm

:: Step 5: Run OSRM customize
echo [INFO] Customizing...
docker run -t -v "%cd%:/data" osrm/osrm-backend osrm-customize /data/india-latest.osrm

:: Step 6: Start OSRM server
echo [INFO] Starting OSRM server on port 5000...
echo [OK] OSRM will be available at http://localhost:5000
start docker run -t -i -p 5000:5000 -v "%cd%:/data" osrm/osrm-backend osrm-routed --algorithm mld /data/india-latest.osrm

echo =========================================
echo OSRM is running at http://localhost:5000
echo Test in browser: http://localhost:5000/route/v1/driving/83.2185,17.6868;83.2200,17.6900?overview=false
echo =========================================
pause
