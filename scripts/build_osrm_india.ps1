# Stop any running OSRM containers
Write-Host "Stopping existing OSRM containers..."
$existing = docker ps -q --filter "ancestor=osrm/osrm-backend"
if ($existing) { docker stop $existing; docker rm $existing }

$dataPath = "D:\Projects & Internships\resq-mar\data\osrm"

Write-Host "1/4: Extracting India map (This may take 30-60+ minutes depending on your CPU/RAM)..."
docker run --rm -v "${dataPath}:/data" osrm/osrm-backend osrm-extract -p /opt/car.lua /data/india-latest.osm.pbf

Write-Host "2/4: Partitioning India map..."
docker run --rm -v "${dataPath}:/data" osrm/osrm-backend osrm-partition /data/india-latest.osrm

Write-Host "3/4: Customizing India map..."
docker run --rm -v "${dataPath}:/data" osrm/osrm-backend osrm-customize /data/india-latest.osrm

Write-Host "4/4: Starting full India routing server on port 5000..."
docker run -d --name osrm-india-server -p 5000:5000 -v "${dataPath}:/data" osrm/osrm-backend osrm-routed --algorithm mld /data/india-latest.osrm

Write-Host "Done! Pan-India routing is now live."
