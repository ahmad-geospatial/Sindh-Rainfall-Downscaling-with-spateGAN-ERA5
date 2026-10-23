import csv
from collections import Counter
from datetime import date
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
stations_file = project_root / "data" / "processed" / "sindh_prcp_stations.csv"
daily_file = project_root / "data" / "processed" / "sindh_daily_prcp.csv"
output_file = project_root / "data" / "processed" / "sindh_station_annual_coverage.csv"

with stations_file.open("r", encoding="utf-8-sig", newline="") as file:
    station_ids = [row["station_id"].strip() for row in csv.DictReader(file)]

dates_by_station = {station_id: set() for station_id in station_ids}

with daily_file.open("r", encoding="utf-8-sig", newline="") as file:
    for row in csv.DictReader(file):
        # Use observations with no NOAA quality flag.
        if row["quality_flag"].strip():
            continue

        station_id = row["station_id"].strip()
        observation_date = date.fromisoformat(row["date"])
        dates_by_station[station_id].add(observation_date)

date_counts = Counter(
    observation_date
    for station_dates in dates_by_station.values()
    for observation_date in station_dates
)

first_dates = [
    min(station_dates)
    for station_dates in dates_by_station.values()
    if station_dates
]
last_dates = [
    max(station_dates)
    for station_dates in dates_by_station.values()
    if station_dates
]

shared_start = max(first_dates)
shared_end = min(last_dates)

print(f"Shared date envelope: {shared_start} to {shared_end}")
print("This is the shared span, not a guarantee of complete daily data.")

# Use complete calendar years inside the shared date envelope.
first_full_year = shared_start.year + 1
last_full_year = shared_end.year - 1
annual_rows = []

for year in range(first_full_year, last_full_year + 1):
    days_in_year = (date(year + 1, 1, 1) - date(year, 1, 1)).days

    row = {
        "year": year,
        "calendar_days": days_in_year,
    }

    for station_id in station_ids:
        days = sum(
            observation_date.year == year
            for observation_date in dates_by_station[station_id]
        )
        row[f"{station_id}_days"] = days

    dates_with_all_stations = sum(
        observation_date.year == year and count == len(station_ids)
        for observation_date, count in date_counts.items()
    )
    dates_with_at_least_three = sum(
        observation_date.year == year and count >= 3
        for observation_date, count in date_counts.items()
    )

    row["days_all_stations_reported"] = dates_with_all_stations
    row["days_at_least_3_stations_reported"] = dates_with_at_least_three
    annual_rows.append(row)

if annual_rows:
    fieldnames = list(annual_rows[0].keys())

    with output_file.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(annual_rows)

    print(f"\nAnnual summary saved to: {output_file}")
    print("\nYear | all 5 stations reported | at least 3 reported")
    for row in annual_rows:
        print(
            row["year"],
            "|",
            row["days_all_stations_reported"],
            "|",
            row["days_at_least_3_stations_reported"],
        )
else:
    print("There are no complete calendar years inside the shared date envelope.")