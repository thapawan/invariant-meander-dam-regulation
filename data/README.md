# Data Directory

This directory contains the meander migration data used in the analysis.

## Files

### synthetic_migration_data.csv

Synthetic meander migration data generated to demonstrate the key findings of this study.

**Columns:**
- `curvature`: Local channel curvature (1/m)
- `migration_rate`: Lateral migration rate (m/yr)
- `regulated`: Binary indicator (1 = regulated by dam, 0 = unregulated)
- `reach_id`: Identifier for river reach (used for spatial grouping)
- `time_period`: Time period identifier
- `x_t1`, `y_t1`: Channel centerline position at time 1 (m)
- `x_t2`, `y_t2`: Channel centerline position at time 2 (m)

**Generation Parameters:**
- Number of reaches: 10 (5 regulated, 5 unregulated)
- Points per reach: 100
- Time delta: 10 years
- Suppression factor: 0.25 (75% reduction in migration rates)

## Using Real Data

To use this analysis framework with real remote sensing data:

1. Prepare your data in a similar CSV format with at minimum:
   - Channel curvature values
   - Migration rates (or positions at two time periods)
   - Regulation status for each measurement point

2. Load your data using pandas:
   ```python
   import pandas as pd
   df = pd.read_csv('your_data.csv')
   ```

3. Run the analysis following the examples in `notebooks/main_analysis.py`

## Data Sources for Real Analysis

For conducting this analysis with real river data, potential sources include:

- **Landsat Archive**: Long-term satellite imagery (1970s-present)
- **National Agriculture Imagery Program (NAIP)**: High-resolution aerial imagery
- **Google Earth Engine**: Cloud-based platform for processing remote sensing data
- **RivaMAP**: Automated river morphology extraction from satellite imagery

## Citation

When using this synthetic data for demonstrations, please cite this repository.
