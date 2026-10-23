from math import asin, cos, radians, sin, sqrt
from pathlib import Path

import pandas as pd
import xarray as xr


project_root = Path(__file__).resolve().parents[1]
model_file = (
    project_root
    / "data/processed/spategan_sample/latlon/"
    / "spateGAN_ERA5_latlon_26.62N_68.38E_20100801_20100801_e10.nc"
)
station_file = project_root / "data/processed/sindh_daily_prcp.csv"
output_file = (
    project_root
    / "data/processed/spategan_sample/"
    / "station_comparison_2010-08-01.csv"
)
target_date = "2010-08-01"


def distance_km(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    value = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    return 2 * 6371 * asin(sqrt(value))


stations = pd.read_csv(station_file)
stations = stations.loc[stations["date"].astype(str) == target_date]

results = []

with xr.open_dataset(model_file, engine="h5netcdf") as ds:
    if ds["precipitation"].attrs.get("units") != "mm/h":
        raise ValueError("Expected model precipitation units to be mm/h.")

    # Each output step is 10 minutes: convert its rate to depth, then sum.
    daily_model_mm = ds["precipitation"].sum(dim="time") * (10 / 60)

    lat_min = float(ds["lat"].min())
    lat_max = float(ds["lat"].max())
    lon_min = float(ds["lon"].min())
    lon_max = float(ds["lon"].max())

    for _, station in stations.iterrows():
        lat = float(station["latitude"])
        lon = float(station["longitude"])
        observed = float(station["prcp_mm"])

        result = {
            "station_id": station["station_id"],
            "station_name": station["station_name"],
            "date": target_date,
            "observed_mm": observed,
            "model_nearest_cell_mm": None,
            "difference_mm": None,
            "nearest_cell_distance_km": None,
            "status": "inside patch",
        }

        if not (lat_min <= lat <= lat_max and lon_min <= lon <= lon_max):
            result["status"] = "outside model patch"
        else:
            cell = daily_model_mm.sel(lat=lat, lon=lon, method="nearest")
            grid_lat = float(cell["lat"])
            grid_lon = float(cell["lon"])
            modeled = float(cell)

            result["model_nearest_cell_mm"] = modeled
            result["difference_mm"] = modeled - observed
            result["nearest_cell_distance_km"] = distance_km(
                lat, lon, grid_lat, grid_lon
            )

        results.append(result)

output_file.parent.mkdir(parents=True, exist_ok=True)
comparison = pd.DataFrame(results)
comparison.to_csv(output_file, index=False)

print(comparison.to_string(index=False))
print(f"\nSaved comparison to: {output_file}")