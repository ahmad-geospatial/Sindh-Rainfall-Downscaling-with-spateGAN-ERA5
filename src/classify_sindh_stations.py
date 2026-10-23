import csv
import json
from pathlib import Path
from urllib.request import Request, urlopen

from shapely.geometry import Point, shape

project_root = Path(__file__).resolve().parents[1]
stations_file = project_root / "data" / "processed" / "pakistan_prcp_stations.csv"
output_file = project_root / "data" / "processed" / "sindh_prcp_stations.csv"

# Get the current Pakistan province boundary download link.
api_url = "https://www.geoboundaries.org/api/current/gbOpen/PAK/ADM1/"
request = Request(api_url, headers={"User-Agent": "SindhRainfallProject/1.0"})

with urlopen(request, timeout=60) as response:
    boundary_info = json.load(response)

boundary_url = boundary_info["gjDownloadURL"]
request = Request(boundary_url, headers={"User-Agent": "SindhRainfallProject/1.0"})

with urlopen(request, timeout=120) as response:
    boundary_data = json.load(response)

# Find the Sindh province polygon.
sindh_feature = next(
    feature
    for feature in boundary_data["features"]
    if feature.get("properties", {}).get("shapeName", "").strip().casefold() == "sindh"
)
sindh_boundary = shape(sindh_feature["geometry"])
jacobabad_point = Point(68.45, 28.284)
print("Boundary check for Jacobabad:", sindh_boundary.covers(jacobabad_point))

# Keep stations whose longitude/latitude points fall inside Sindh.
sindh_stations = []

with stations_file.open("r", encoding="utf-8-sig", newline="") as file:
    for station in csv.DictReader(file):
        point = Point(float(station["longitude"]), float(station["latitude"]))
        station_id = station["station_id"].strip()

        is_in_sindh_boundary = sindh_boundary.covers(point)

        # PMD lists station 41715 (Jacobabad) in its Sindh network.
        # Include it because the boundary file did not cover its station coordinates.
        is_pmd_sindh_station = station_id == "PKM00041715"

        if is_in_sindh_boundary or is_pmd_sindh_station:
            sindh_stations.append(station)

# Save the filtered station list.
with output_file.open("w", encoding="utf-8", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=sindh_stations[0].keys())
    writer.writeheader()
    writer.writerows(sindh_stations)

print(f"Sindh stations found: {len(sindh_stations)}")
print(f"Saved to: {output_file}")

for station in sindh_stations:
    print(
        station["station_id"],
        station["name"],
        station["latitude"],
        station["longitude"],
    )