# The Invariant Meander: Dam Regulation and Geomorphic Dormancy

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Do dams change where rivers erode or just how fast?**

This repository provides data and code to demonstrate that **dam regulation suppresses meander migration rates while preserving the geometric template of erosion**, inducing a state of **geomorphic dormancy**.

## Overview

Rivers naturally migrate through lateral erosion and deposition, creating meandering patterns. This study shows that while dam regulation dramatically slows down these processes, it does not fundamentally alter *where* erosion occurs. The relationship between channel curvature and migration rate (the "migration template") remains invariant, but the overall process rates are suppressed.

### Key Findings

1. **Rate Suppression**: Dam regulation reduces migration rates by ~70-80% compared to unregulated conditions
2. **Invariant Template**: The geometric relationship between curvature and migration remains unchanged (high correlation r > 0.9)
3. **Geomorphic Dormancy**: Rivers enter a dormant state where the erosion blueprint is preserved but process rates are suppressed

## Repository Structure

```
invariant-meander-dam-regulation/
├── data/                          # Data directory (generated)
│   └── synthetic_migration_data.csv
├── src/                           # Source code modules
│   ├── __init__.py
│   ├── meander_analysis.py       # Core migration analysis functions
│   ├── lme_model.py               # Linear Mixed Effects modeling
│   ├── visualization.py           # Plotting functions
│   └── data_generator.py          # Synthetic data generation
├── notebooks/                     # Analysis scripts
│   └── main_analysis.py           # Main analysis demonstration
├── tests/                         # Unit tests
├── figures/                       # Generated figures (output)
├── requirements.txt               # Python dependencies
├── .gitignore
└── README.md
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. Clone the repository:
```bash
git clone https://github.com/thapawan/invariant-meander-dam-regulation.git
cd invariant-meander-dam-regulation
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Quick Start

Run the main analysis script to generate synthetic data and produce all figures:

```bash
python notebooks/main_analysis.py
```

This will:
- Generate synthetic meander migration data
- Perform comparative analysis between regulated and unregulated reaches
- Fit Linear Mixed Effects models
- Create publication-quality figures
- Output summary statistics

### Using the Modules

#### 1. Meander Migration Analysis

```python
from src.meander_analysis import (
    calculate_migration_rate,
    calculate_curvature,
    compare_regulated_unregulated
)

# Calculate migration rates
rates = calculate_migration_rate(positions_t1, positions_t2, time_delta=10.0)

# Calculate curvature
curvatures = calculate_curvature(positions, window_size=5)

# Compare regulated vs unregulated
comparison = compare_regulated_unregulated(
    regulated_curvatures, regulated_rates,
    unregulated_curvatures, unregulated_rates
)
```

#### 2. Linear Mixed Effects Modeling

```python
from src.lme_model import prepare_lme_data, fit_lme_model, interpret_results

# Prepare data
lme_data = prepare_lme_data(
    curvatures, migration_rates, 
    regulation_status, reach_ids
)

# Fit model
model_result, summary_df = fit_lme_model(lme_data)

# Interpret results
interpretation = interpret_results(summary_df)
```

#### 3. Visualization

```python
from src.visualization import (
    plot_migration_template_comparison,
    plot_lme_results,
    plot_geomorphic_dormancy
)

# Create comparison plot
fig = plot_migration_template_comparison(
    comparison,
    save_path='figures/template_comparison.png'
)
```

#### 4. Data Generation

```python
from src.data_generator import generate_migration_data

# Generate synthetic data
data = generate_migration_data(
    n_reaches=10,
    points_per_reach=100,
    regulated_fraction=0.5,
    suppression_factor=0.25
)
```

## Methodology

### Linear Mixed Effects Model

The analysis uses Linear Mixed Effects (LME) models to test the hypotheses:

```
migration_rate ~ curvature + regulated + curvature × regulated + (1|reach_id)
```

Where:
- `curvature`: Local channel curvature
- `regulated`: Binary indicator (1 = regulated, 0 = unregulated)
- `curvature × regulated`: Interaction term
- `(1|reach_id)`: Random intercept for each river reach

**Key predictions:**
- **Significant negative `regulated` coefficient** → rates are suppressed
- **Non-significant interaction term** → template is invariant

### Geomorphic Dormancy Index

The dormancy index quantifies the suppression:

```
Dormancy Index = median(regulated_rates) / median(unregulated_rates)
```

Values close to 0 indicate strong dormancy; values close to 1 indicate no effect.

## Output

The analysis generates three main figures:

1. **Migration Template Comparison**
   - Panel A: Absolute migration rates vs. curvature
   - Panel B: Normalized templates showing invariance

2. **LME Model Results**
   - Coefficient plot with significance testing
   - Key findings summary

3. **Geomorphic Dormancy**
   - Violin plots comparing rate distributions
   - Dormancy index visualization

## Testing

Run unit tests:

```bash
python -m pytest tests/
```

## Data

This repository uses synthetic data that simulates realistic meander migration patterns. The data generation follows established principles:

- Curvature follows log-normal distribution (consistent with natural rivers)
- Migration rates scale linearly with curvature (Howard & Knutson, 1984)
- Dam regulation applies a uniform suppression factor
- Spatial autocorrelation via reach-level random effects

For analysis with real remote sensing data, users should replace the synthetic data with:
- Channel centerline positions from aerial/satellite imagery
- Time-series measurements (minimum 2 time periods)
- Classification of regulated vs. unregulated reaches

## Scientific Background

This work builds on several key concepts in fluvial geomorphology:

- **Meander migration theory** (Howard & Knutson, 1984; Ikeda et al., 1981)
- **Dam effects on river morphology** (Williams & Wolman, 1984; Grant, 2012)
- **Geomorphic dormancy** (Thomas, 2001) - landforms persist in inactive states

### References

- Howard, A.D., & Knutson, T.R. (1984). Sufficient conditions for river meandering. *Water Resources Research*.
- Williams, G.P., & Wolman, M.G. (1984). Downstream effects of dams. *USGS Professional Paper*.
- Grant, G.E. (2012). The geomorphic response of gravel-bed rivers to dams. *Gravel-Bed Rivers*.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Citation

If you use this code or methodology in your research, please cite:

```
@software{invariant_meander_2024,
  title={The Invariant Meander: Dam Regulation Suppresses Migration Rates but Conserves the Geometric Template of Erosion},
  author={Your Name},
  year={2024},
  url={https://github.com/thapawan/invariant-meander-dam-regulation}
}
```

## Contact

For questions or collaborations, please open an issue on GitHub.

---

**Keywords**: meander migration, dam regulation, geomorphic dormancy, river morphology, Linear Mixed Effects models, remote sensing
