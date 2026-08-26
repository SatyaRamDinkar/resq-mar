# OSRM Integration Guide

## 1. What is OSRM?
**Open Source Routing Machine (OSRM)** is a C++ routing engine designed for use with OpenStreetMap data. It provides highly efficient routing queries including shortest paths, distance matrices, and turn-by-turn navigation data.

## 2. Why OSRM Matters for ResQ-MAR
Prior to Phase 4 Step 6, ResQ-MAR relied on the Haversine formula (straight-line/great-circle distance) for ETA estimations and VRP matrix building. 
- **The Problem:** Haversine assumes emergency vehicles can drive through buildings, cross rivers without bridges, and ignore one-way streets.
- **The Solution:** OSRM provides real road distances. This improves ETA accuracy by 20-40% and is critical for disaster scenarios like floods where roads may be submerged or impassable.

## 3. Installation
1. Ensure **Docker Desktop** is installed and running.
2. Run the automated setup script:
   - Windows: `scripts\setup_osrm.bat`
   - Linux/Mac: `scripts/setup_osrm.sh`
3. Wait approximately 5-10 minutes for the Sri Lanka extract to download and compile.
4. Verify the server is running by hitting:
   `curl http://localhost:5000/route/v1/driving/79.8612,6.9271;79.8650,6.9300?overview=false`

## 4. Architecture Update
- **Before:** `vrp_solver.py` -> `calculate_haversine()`
- **After:** `Routing Module` -> `OSRMClient` -> `[OSRM Server on :5000]`
- **Fallback:** If OSRM is unavailable, `OSRMClient` automatically wraps coordinates back through the internal Haversine function to guarantee 100% uptime.

## 5. API Endpoints Used
The internal client utilizes three primary OSRM endpoints:
- `/route/v1/driving/{coords}`: Point-to-point distance and ETA.
- `/table/v1/driving/{coords}`: Generates the full NxN matrix for OR-Tools.
- `/nearest/v1/driving/{coord}`: Road snapping for accurate geo-visualization.

## 6. Fallback Behavior
If OSRM is taken down, ResQ-MAR automatically reverts to Haversine mode.
- Speed is estimated at an average of **40 km/h** for duration matrices.
- The VRP solver logs `[WARN] OSRM unavailable, using haversine fallback`.
- No solver code crashes; backward compatibility is strictly maintained.

## 7. Performance
- **OSRM Local Server:** ~10-50ms per query. Matrix build (~20x20) takes ~1s.
- **Haversine:** ~0.1ms per query. Matrix build takes ~0.01s.
- **Trade-off:** VRP solving takes marginally longer, but dispatch is rooted in physical reality.

## 8. Troubleshooting
- **Docker not running:** Start Docker Desktop.
- **Port 5000 in use:** Edit the setup scripts and `OSRMClient` init to use a different port (e.g., 5001).
- **Out of memory:** OSRM MLD algorithm requires roughly 2GB of RAM for the Sri Lanka extract.
