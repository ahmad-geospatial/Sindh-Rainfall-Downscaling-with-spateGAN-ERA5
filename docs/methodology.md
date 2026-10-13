# Method and evaluation

## Project objective

This project applies the released pretrained spateGAN-ERA5 model to hourly ERA5 precipitation over Sindh, Pakistan. We will first reproduce the authors' radar example, then assess what we can learn by applying the workflow in Sindh.

The paper describes downscaling hourly ERA5 precipitation, at roughly 24 km resolution, to probabilistic rainfall fields at 2 km and 10-minute intervals. These fine-scale fields are generated possibilities conditioned on the coarser input, not observed rainfall.

## Why begin with the published example?

Reproducing the authors' radar example gives us a known case for learning the data preparation, model inputs, output format, and evaluation steps. It checks whether we can follow the published workflow; it does not validate the model in Pakistan.

## Sindh workflow

1. Choose a study area and period, and record the boundary source.
2. Inspect station locations, rainfall records, dates, and completeness before choosing gauge comparisons.
3. Prepare ERA5 inputs using the variables, units, timestamps, and spatial context required by the model.
4. Run the released model and retain its multiple generated realizations.
5. Aggregate the output before comparing it with coarser products or daily gauge totals.
6. Report results alongside missing observations and regional transfer limits.

## Evaluation ladder

| Check | What it can tell us | What it cannot tell us |
|---|---|---|
| Reproduce the published German radar example | Whether our reproduction follows the published workflow | Whether the model is accurate in Sindh |
| Aggregate output to ERA5's hourly grid | Whether broad totals remain consistent with the input | Whether the generated fine-scale pattern is correct |
| Compare with IMERG at matched scales | How two precipitation estimates compare | Independent ground truth or 2 km accuracy |
| Compare daily totals with eligible NOAA GHCN-Daily stations | Agreement at available station locations and dates | Storm timing, 10-minute intensity, or 2 km rainfall structure |
| Compare with local gauges, if available | Point-observation agreement at the gauge's reporting interval | Full spatial rainfall truth without a sufficiently dense network |

IMERG is a satellite estimate, not independent ground truth. NOAA GHCN-Daily can support daily comparisons only. We will inspect the station inventory and records before deciding whether any Sindh stations are usable.

## Interpretation and limitations

The pretrained model was developed using gauge-adjusted radar observations in Germany. That does not establish its performance in Sindh. Without local high-resolution observations, the generated 2 km patterns and 10-minute storm structure cannot be directly verified. A visually detailed map is not evidence that the detail is correct.

We will distinguish benchmark reproduction and consistency checks from validation. We will also report the model's ensemble spread and note temporal and spatial mismatches.

## References

- Glawion et al. (2025), [Global spatio-temporal ERA5 precipitation downscaling to km and sub-hourly scale using generative AI](https://doi.org/10.1038/s41612-025-01103-y).
- [spateGAN-ERA5 implementation](https://github.com/LGlawion/spateGAN_ERA5).
- NOAA NCEI, [GHCN-Daily](https://www.ncei.noaa.gov/products/land-based-station/global-historical-climatology-network-daily).
- NASA GPM, [IMERG](https://gpm.nasa.gov/data/imerg).
