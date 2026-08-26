#!/bin/bash
echo "========================================="
echo "OSRM Setup for ResQ-MAR"
echo "========================================="
echo "This script downloads Sri Lanka OSM data and starts OSRM server."
echo "Requires: Docker installed and running"
echo ""

# Step 1: Create directory
mkdir -p data/osrm
cd data/osrm

# Step 2: Download Sri Lanka OSM extract (Geofabrik)
echo "[INFO] Downloading Sri Lanka OSM extract..."
wget -O sri-lanka-latest.osm.pbf https://download.geofabrik.de/asia/sri-lanka-latest.osm.pbf

# Step 3: Run OSRM extraction (Docker)
echo "[INFO] Running OSRM extraction (this may take 5-10 minutes)..."
docker run -t -v $(pwd):/data osrm/osrm-backend osrm-extract -p /opt/car.lua /data/sri-lanka-latest.osm.pbf

# Step 4: Run OSRM partition
echo "[INFO] Partitioning..."
docker run -t -v $(pwd):/data osrm/osrm-backend osrm-partition /data/sri-lanka-latest.osrm

# Step 5: Run OSRM customize
echo "[INFO] Customizing..."
docker run -t -v $(pwd):/data osrm/osrm-backend osrm-customize /data/sri-lanka-latest.osrm

# Step 6: Start OSRM server
echo "[INFO] Starting OSRM server on port 5000..."
echo "[OK] OSRM will be available at http://localhost:5000"
docker run -t -i -p 5000:5000 -v $(pwd):/data osrm/osrm-backend osrm-routed --algorithm mld /data/sri-lanka-latest.osrm

echo "========================================="
echo "OSRM is running at http://localhost:5000"
echo "Test: curl 'http://localhost:5000/route/v1/driving/79.8612,6.9271;79.8650,6.9300?overview=false'"
echo "========================================="
