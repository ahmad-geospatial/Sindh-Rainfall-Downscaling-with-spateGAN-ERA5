from pathlib import Path

import cdsapi


project_root = Path(__file__).resolve().parents[1]
output_file = (
    project_root
    / "data"
    / "raw"
    / "era5"
    / "era5_sindh_sample_2010-08-01.nc"
)
output_file.parent.mkdir(parents=True, exist_ok=True)

request = {
    "product_type": ["reanalysis"],
    "variable": [
        "convective_precipitation",
        "large_scale_precipitation",
    ],
    "year": ["2010"],
    "month": ["06"],
    "day": ["06","07"],
    "time": [f"{hour:02d}:00" for hour in range(24)],
    # North, west, south, east
    "area": [33, 61, 20, 76],
    "data_format": "netcdf",
    "download_format": "unarchived",
}

client = cdsapi.Client()
client.retrieve(
    "reanalysis-era5-single-levels",
    request,
    str(output_file),
)

print(f"Saved ERA5 sample to: {output_file}")