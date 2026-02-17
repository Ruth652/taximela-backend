# OTP 2.8.1 Setup Instructions

## Prerequisites
- Java 17 or higher installed
- Check with: `java -version`

## Setup Steps

### 1. Download OTP
```bash
setup-otp.bat
```
This downloads OTP 2.8.1 JAR file (~100MB) to the `otp/` directory.

### 2. Build Graph
```bash
build-graph.bat
```
This builds the routing graph from:
- GTFS transit data (`data/gtfs/`)
- OSM map data (`otp/graphs/default/addis-ababa.osm.pbf`)
- Router config (`data/router-config.json`)

**Note:** Graph building takes 2-5 minutes.

### 3. Start OTP Server
```bash
start-otp.bat
```
Server will start on: http://localhost:8080

## API Endpoints

- **Health Check:** http://localhost:8080/otp/routers/default
- **Plan Route:** http://localhost:8080/otp/routers/default/plan
- **API Docs:** http://localhost:8080/otp/routers/default/index

## Memory Settings

Default: 2GB RAM (`-Xmx2G`)

To change, edit the `.bat` files and modify `-Xmx2G` to:
- `-Xmx1G` for 1GB (minimum)
- `-Xmx4G` for 4GB (recommended for large cities)

## Troubleshooting

**"Java not found"**
- Install Java 17: https://adoptium.net/

**"Out of memory"**
- Increase `-Xmx` value in the batch files

**Graph build fails**
- Check GTFS data exists in `data/gtfs/`
- Check OSM data exists in `otp/graphs/default/`

## Version
OTP Version: 2.8.1 (Latest)
