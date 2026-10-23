"""List Pakistan GHCN-Daily stations with precipitation records."""

import csv
from pathlib import Path
from shutil import copyfileobj
from urllib.request import Request, urlopen

BASE_URL = "https://www.ncei.noaa.gov/pub/data/ghcn/daily/"
PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
OUTPUT_FILE = PROJECT_ROOT / "data" / "processed" / "pakistan_prcp_stations.csv"


def download_if_missing(filename):
    """Download a NOAA metadata file once and reuse the local copy."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    destination = RAW_DIR / filename

    if destination.exists():
        print(f"Using existing file: {destination.name}")
        return destination

    url = BASE_URL + filename
    temporary_file = destination.with_suffix(destination.suffix + ".part")
    request = Request(url, headers={"User-Agent": "Sindh rainfall learning project"})

    print(f"Downloading {filename}...")
    with urlopen(request, timeout=120) as response:
        with temporary_file.open("wb") as output:
            copyfileobj(response, output)

    temporary_file.replace(destination)
    return destination


def read_pakistan_stations(stations_file):
    """Read Pakistan station IDs, coordinates, elevations, and names."""
    stations = {}

    with stations_file.open(encoding="ascii", errors="replace") as file:
        for line in file:
            station_id = line[0:11].strip()

            # NOAA's first two station-ID characters identify the country.
            if not station_id.startswith("PK"):
                continue

            latitude = line[12:20].strip()
            longitude = line[21:30].strip()
            elevation = line[31:37].strip()
            name = line[41:71].strip()

            if not latitude or not longitude:
                continue

            elevation_m = float(elevation) if elevation else None
            if elevation_m is not None and elevation_m <= -999:
                elevation_m = None  # NOAA's missing-elevation code

            stations[station_id] = {
                "station_id": station_id,
                "name": name,
                "latitude": float(latitude),
                "longitude": float(longitude),
                "elevation_m": elevation_m,
            }

    return stations


def read_pakistan_precipitation_inventory(inventory_file, stations):
    """Keep Pakistan inventory rows for daily precipitation (PRCP)."""
    rows = []

    with inventory_file.open(encoding="ascii", errors="replace") as file:
        for line in file:
            station_id = line[0:11].strip()
            element = line[31:35].strip()

            if not station_id.startswith("PK") or element != "PRCP":
                continue

            station = stations.get(station_id)
            if station is None:
                continue

            rows.append(
                {
                    **station,
                    "first_prcp_year": int(line[36:40]),
                    "last_prcp_year": int(line[41:45]),
                }
            )

    return sorted(rows, key=lambda row: row["station_id"])


def main():
    stations_file = download_if_missing("ghcnd-stations.txt")
    inventory_file = download_if_missing("ghcnd-inventory.txt")

    stations = read_pakistan_stations(stations_file)
    precipitation_rows = read_pakistan_precipitation_inventory(
        inventory_file, stations
    )

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "station_id",
        "name",
        "latitude",
        "longitude",
        "elevation_m",
        "first_prcp_year",
        "last_prcp_year",
    ]

    with OUTPUT_FILE.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(precipitation_rows)

    print(f"Pakistan stations in station metadata: {len(stations)}")
    print(f"Pakistan stations with PRCP inventory: {len(precipitation_rows)}")
    print(f"Saved results to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()