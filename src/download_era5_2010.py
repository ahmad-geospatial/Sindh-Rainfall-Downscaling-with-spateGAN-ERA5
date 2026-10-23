from calendar import monthrange
from pathlib import Path

import cdsapi

YEAR = 2010
DATASET = "reanalysis-era5-single-levels"

project_root = Path(__file__).resolve().parents[1]
output_dir = project_root / "data" / "raw" / "era5"
output_dir.mkdir(parents=True, exist_ok=True)

client = cdsapi.Client()
times = [f"{hour:02d}:00" for hour in range(24)]

for month_number in range(1, 13):
    month = f"{month_number:02d}"
    days = [
        f"{day:02d}"
        for day in range(1, monthrange(YEAR, month_number)[1] + 1)
    ]

    output_file = output_dir / f"era5_sindh_{YEAR}_{month}.nc"

    # Keep a completed monthly file if the script is run again.
    if output_file.exists() and output_file.stat().st_size > 0:
        print(f"Already exists; skipping: {output_file.name}")
        continue

    partial_file = output_dir / f"era5_sindh_{YEAR}_{month}.partial.nc"

    request = {
        "product_type": ["reanalysis"],
        "variable": [
            "convective_precipitation",
            "large_scale_precipitation",
        ],
        "year": [str(YEAR)],
        "month": [month],
        "day": days,
        "time": times,
        # North, west, south, east
        "area": [33, 61, 20, 76],
        "data_format": "netcdf",
        "download_format": "unarchived",
    }

    print(f"Requesting {YEAR}-{month}...")
    client.retrieve(DATASET, request, str(partial_file))
    partial_file.replace(output_file)
    print(f"Saved: {output_file.name}")

print("All monthly ERA5 requests are complete.")