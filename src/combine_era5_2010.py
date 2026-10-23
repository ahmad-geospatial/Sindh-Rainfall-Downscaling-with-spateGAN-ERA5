from pathlib import Path

import xarray as xr


project_root = Path(__file__).resolve().parents[1]
data_dir = project_root / "data" / "raw" / "era5"

files = sorted(data_dir.glob("era5_sindh_2010_*.nc"))

if len(files) != 12:
    raise SystemExit(f"Expected 12 monthly files, found {len(files)}.")

datasets = []

try:
    for file_path in files:
        dataset = xr.open_dataset(file_path)
        datasets.append(dataset)

        if "valid_time" not in dataset.sizes:
            raise SystemExit(f"Missing valid_time dimension in {file_path.name}.")

        if not {"cp", "lsp"}.issubset(dataset.data_vars):
            raise SystemExit(f"Expected cp and lsp variables in {file_path.name}.")

    combined = xr.concat(
        datasets,
        dim="valid_time",
        data_vars="minimal",
        coords="minimal",
        compat="override",
    ).sortby("valid_time")

    times = combined["valid_time"].values
    start_time = str(times[0])[:16]
    end_time = str(times[-1])[:16]

    if combined.sizes["valid_time"] != 8760:
        raise SystemExit(
            f"Expected 8760 hourly records, found {combined.sizes['valid_time']}."
        )

    if start_time != "2010-01-01T00:00" or end_time != "2010-12-31T23:00":
        raise SystemExit(f"Unexpected date range: {start_time} through {end_time}.")

    if not combined.indexes["valid_time"].is_unique:
        raise SystemExit("Duplicate timestamps found.")

    output_file = data_dir / "era5_sindh_2010_full.nc"
    temporary_file = data_dir / "era5_sindh_2010_full.partial.nc"

    combined.to_netcdf(
        temporary_file,
        engine="netcdf4",
        encoding={
            "cp": {"zlib": True, "complevel": 4},
            "lsp": {"zlib": True, "complevel": 4},
        },
    )

    temporary_file.replace(output_file)

    print(f"Saved verified annual file: {output_file}")
    print(f"Hourly records: {combined.sizes['valid_time']}")
    print(f"Date range: {start_time} through {end_time}")

finally:
    for dataset in datasets:
        dataset.close()