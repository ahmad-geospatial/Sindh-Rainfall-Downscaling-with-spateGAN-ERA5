import calendar
import csv
from datetime import date
from pathlib import Path
from urllib.request import Request, urlopen

project_root = Path(__file__).resolve().parents[1]
stations_file = project_root / "data" / "processed" / "sindh_prcp_stations.csv"
raw_folder = project_root / "data" / "raw" / "ghcn_daily"
processed_folder = project_root / "data" / "processed"

raw_folder.mkdir(parents=True, exist_ok=True)
processed_folder.mkdir(parents=True, exist_ok=True)

daily_rows = []
audit_rows = []

with stations_file.open("r", encoding="utf-8-sig", newline="") as file:
    stations = list(csv.DictReader(file))

for station in stations:
    station_id = station["station_id"].strip()
    station_name = station["name"].strip()

    url = (
        "https://www.ncei.noaa.gov/pub/data/ghcn/daily/all/"
        f"{station_id}.dly"
    )
    request = Request(url, headers={"User-Agent": "SindhRainfallProject/1.0"})

    print(f"Downloading {station_id} ({station_name})...")

    with urlopen(request, timeout=60) as response:
        file_contents = response.read()

    raw_file = raw_folder / f"{station_id}.dly"
    raw_file.write_bytes(file_contents)

    observations = []
    missing_values = 0
    quality_flagged_values = 0
    trace_values = 0

    for line in file_contents.decode("ascii").splitlines():
        if len(line) < 269 or line[17:21] != "PRCP":
            continue

        year = int(line[11:15])
        month = int(line[15:17])
        days_in_month = calendar.monthrange(year, month)[1]

        for day in range(1, days_in_month + 1):
            start = 21 + (day - 1) * 8
            value_text = line[start : start + 5]
            measurement_flag = line[start + 5 : start + 6].strip()
            quality_flag = line[start + 6 : start + 7].strip()
            source_flag = line[start + 7 : start + 8].strip()

            value_tenths_mm = int(value_text)

            if value_tenths_mm == -9999:
                missing_values += 1
                continue

            observation_date = date(year, month, day)
            precipitation_mm = value_tenths_mm / 10

            if quality_flag:
                quality_flagged_values += 1

            if measurement_flag == "T":
                trace_values += 1

            observations.append(observation_date)

            daily_rows.append(
                {
                    "station_id": station_id,
                    "station_name": station_name,
                    "latitude": station["latitude"],
                    "longitude": station["longitude"],
                    "date": observation_date.isoformat(),
                    "prcp_mm": precipitation_mm,
                    "measurement_flag": measurement_flag,
                    "quality_flag": quality_flag,
                    "source_flag": source_flag,
                }
            )

    if observations:
        first_date = min(observations).isoformat()
        last_date = max(observations).isoformat()
    else:
        first_date = ""
        last_date = ""

    audit_rows.append(
        {
            "station_id": station_id,
            "station_name": station_name,
            "first_observation": first_date,
            "last_observation": last_date,
            "nonmissing_observations": len(observations),
            "missing_value_markers": missing_values,
            "quality_flagged_observations": quality_flagged_values,
            "trace_observations": trace_values,
        }
    )

daily_output = processed_folder / "sindh_daily_prcp.csv"
with daily_output.open("w", encoding="utf-8", newline="") as file:
    fieldnames = [
        "station_id",
        "station_name",
        "latitude",
        "longitude",
        "date",
        "prcp_mm",
        "measurement_flag",
        "quality_flag",
        "source_flag",
    ]
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(daily_rows)

audit_output = processed_folder / "sindh_station_coverage.csv"
with audit_output.open("w", encoding="utf-8", newline="") as file:
    fieldnames = [
        "station_id",
        "station_name",
        "first_observation",
        "last_observation",
        "nonmissing_observations",
        "missing_value_markers",
        "quality_flagged_observations",
        "trace_observations",
    ]
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(audit_rows)

print(f"\nDaily observations saved to: {daily_output}")
print(f"Coverage summary saved to: {audit_output}")
print("\nStation coverage:")
for row in audit_rows:
    print(
        row["station_id"],
        row["station_name"],
        row["first_observation"],
        "to",
        row["last_observation"],
        "| observations:",
        row["nonmissing_observations"],
        "| quality flagged:",
        row["quality_flagged_observations"],
    )