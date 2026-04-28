# The Invariant Meander: Dam Regulation Suppresses Migration Rates but Conserves the Geometric Template of Erosion
---

## 📌 Overview

This repository contains the complete, reproducible data and code for the manuscript:

> **"Decoupled Adjustment of Meander Planform Geometry and Migration Rate Under Dam Regulation"**

The study demonstrates a fundamental decoupling in meander response to anthropogenic flow regulation: the **spatial template of erosion (curvature–migration phase lag)** remains invariant under dam regulation, while the **process rate (migration and erodibility)** is substantially suppressed. Using a paired‑watershed design, multi‑temporal satellite imagery (2000–2024), and a Linear Mixed‑Effects framework, we show that regulation shifts process dominance from hydraulic to biotic control—a state we term *geomorphic dormancy*.

---

## 🔑 Key Findings

| Finding | Result |
|:--------|:-------|
| **Phase lag invariance** | Δs/W ≈ 2.0 channel widths in both rivers; statistically indistinguishable (Mann–Whitney U = 1,842, p = 0.41) |
| **Migration suppression** | Regulated river median = 0.67 m/yr (n=56); unregulated = 1.45 m/yr (n=73); 54% reduction (p < 0.001) |
| **Erodibility suppression** | E reduced by >50% under regulation |
| **Vegetation × regulation interaction** | ΔEVI effect: β = –0.08 (p = 0.15) unregulated; β = –0.41 (p < 0.001) regulated |
| **Geomorphic dormancy** | Bend‑scale heterogeneity explains 38% of variance in log(E) (ICC = 0.38) |

---

## 📂 Repository Structure

```
invariant-meander-dam-regulation/
│
├── Data/                              # All input data
│   ├── raw/                           # Original satellite & hydrologic data
│   │   ├── centerlines/
│   │   ├── meander_cutoff/
│   │   ├── usgs_discharge/
│   │   └── ssurgo_clay/
│   │   └── water_masks/
│   ├── processed/                     # Analysis‑ready datasets
│   │   ├── ikeda_ready_points_fixed.csv
│   │   ├── ikeda_ready_bends_enhanced.csv
│   │   ├── ikeda_ready_fields_dictionary.csv
│   │   ├── comprehensive_migration_phase_lag_analysis.xlsx
│   │   └── figure3_clay_vs_evi.csv
├── Examples/                          # Tutorials & reproducible examples
│   ├── Readme
│   ├── plot_usgs_discharge.ipynb
│   ├── tutorial_notebook.ipynb
├── Results/                           # All generated outputs
│   ├── figures/                       # Manuscript figures (PNG, PDF, SVG)
│   │   ├── Figure_1_map.png
│   │   ├── Figure_2_phase_lag.png
│   │   ├── Figure_3_migration_suppression.png
│   │   ├── Figure_4_erodibility.png
│   │   ├── Figure_5_sensitivity.png
│   │   └── supplementary_figures/
│       ├── centerline_with_EVI_CV_DamDistance_with_CVdiff.csv
│       ├── validation_dambin_stats.csv
├── Scripts/
│   ├── Python/                              # All analysis code
│   ├── 01_load_data.py               
│   ├── 02_Phase Lag Invariance.py    
│   ├── 03_Migration Rate Suppression.py      
│   ├── 04_Erodibility Coefficient and LME Model.py       
│   ├── 05_Flood-Migration Coupling.py             
│   ├── 06_Sensitivity Analysis.py        
│   ├── 07_Summary Statistics.py     
│   ├── 08_Qcv.py                  
│   ├── 09_verification.py
│   ├── 10_Epoch Stability Test.py    
│
├── environment.yml                    # Conda environment (Python 3.9+)
├── requirements.txt                   # Pip dependencies
├── LICENSE                            # MIT License
└── README.md                          # This file
```

---

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/thapawan/invariant-meander-dam-regulation.git
cd invariant-meander-dam-regulation
```


### 2. Explore Step‑by‑Step (Jupyter Notebooks)

```bash
jupyter notebook Examples/
```

---

## 📊 Data Sources

| Dataset | Source | Purpose |
|:--------|:-------|:--------|
| **Optical Satellite Imagery** | USGS Landsat 5/7/8/9, ESA Sentinel‑2 | Water masking, centerline extraction, ΔEVI |
| **Water Masks** | DeepLabV3 model (this study) | Primary input for channel planform |
| **Discharge Data** | USGS NWIS (#02425000, #02466030, #02466031) | Flow variability (Qcv) |
| **Runoff Data** | ECMWF ERA5‑Land | Basin‑wide hydrologic variability |
| **Soil Data** | USDA NRCS SSURGO | Bank clay content (geologic control) |

---

## 🔬 Methodological Highlights

### Phase Lag Determination (Δs/W)

- **Range tested:** 1.5–3.0 channel widths at **0.1W increments** (finer than typical 0.5W)
- **Optimization:** Maximized median Spearman correlation across bends
- **Uncertainty:** Bootstrap resampling (n = 1,000) for 95% confidence intervals
- **Width multiplier sensitivity:** Tested 1.0, 1.3, and 1.6 – conclusion unchanged

### Linear Mixed‑Effects Model

**Equation:**

```
log(E) = β₀ + β₁(CV_Q) + β₂(ΔEVI) + β₃(Regulated) + β₄(Clay Content) + β₅(ΔEVI × Regulated) + u_Bend + ε
```

- **Estimation:** Restricted Maximum Likelihood (REML)
- **Random effects:** Random intercept for each bend (n = 124)
- **ICC:** σ²_Bend / (σ²_Bend + σ²_ε) = 0.38

### Statistical Tests

| Test | Variables | Result |
|:-----|:----------|:-------|
| Mann‑Whitney U | Phase lag distributions | U = 1,842, p = 0.41 |
| Mann‑Whitney U | Migration rates | U = 285, p < 0.001 |
| Mann‑Whitney U | MAD | U = 312, p = 0.002 |
| Kolmogorov‑Smirnov | Δs/W (strict criteria) | p = 0.97 |
| Kolmogorov‑Smirnov | Δs/W (lenient criteria) | p = 0.04 (median diff = 0.007W) |

---

## 📈 Reproducing Figures

Each manuscript figure can be regenerated independently:

```bash
# Generate all figures
python Scripts/R Scripts

| Figure | Description | Script Reference |
|:-------|:------------|:-----------------|
| Figure 1 | Study area map | Generated in 08_figures.py |
| Figure 2 | Phase lag analysis | 08_figures.py --figure 2 |
| Figure 3 | Migration suppression | 08_figures.py --figure 3 |
| Figure 4 | Erodibility & mechanisms | 08_figures.py --figure 4 |
| Figure 5 | Sensitivity analysis | 08_figures.py --figure 5 |

---

## 📋 Dependencies

### Python (>=3.9)

| Package | Version | Purpose |
|:--------|:--------|:--------|
| pandas | ≥1.5.0 | Data manipulation |
| numpy | ≥1.23.0 | Numerical operations |
| scipy | ≥1.9.0 | Statistical tests |
| statsmodels | ≥0.13.0 | LME models, REML |
| matplotlib | ≥3.6.0 | Figure generation |
| seaborn | ≥0.12.0 | Statistical visualizations |
| openpyxl | ≥3.0.0 | Excel file I/O |

### R (for optional spatial processing)

| Package | Purpose |
|:--------|:--------|
| sf | Vector data handling |
| raster / terra | Raster operations |
| lme4 | Alternative LME implementation |
| ggplot2 | Alternative figure generation |

---

## 📝 Verification of Reproducibility

Run the following to verify your environment and data:

python Scripts/R Scripts
```

Expected output:

```
✓ Python 3.9+
✓ All required packages installed
✓ Data files found (n = 7)
✓ Directory structure correct
✓ Ready to run analysis
```

---

## 🧪 Example: Run LME Model on Your Own Data

```python
import pandas as pd
import statsmodels.api as sm
from statsmodels.formula.api import mixedlm

# Load your bend‑epoch data
df = pd.read_csv('Data/processed/ikeda_ready_bends_enhanced.csv')

# Create log(E)
df['E'] = df['median_migration_rate'] / (abs(df['mean_curvature']) + 1e-10)
df['log_E'] = np.log(df['E'] + 1e-10)

# Prepare variables
df['Regulated'] = (df['river'] == 'Blackwarrior').astype(int)
df['DeltaEVI_x_Regulated'] = df['Delta_EVI_change_unitless_mean'] * df['Regulated']

# Fit model
model = mixedlm(
    "log_E ~ CV_runoff_selected_mean + Delta_EVI_change_unitless_mean + Regulated + Clay_Content + DeltaEVI_x_Regulated",
    df, groups=df["bend_id"], re_formula="~1"
)
result = model.fit()
print(result.summary())
```

---

## 📄 Citation

If you use this code or data in your research, please cite:

```bibtex
@article{Thapa2024_InvariantMeander,
  title = {Decoupled Adjustment of Meander Planform Geometry and Migration Rate Under Dam Regulation},
  author = {},
  journal = {[Journal Name]},
  volume = {[Volume]},
  pages = {[Pages]},
  year = {2024},
  doi = {[DOI to be added]}
}
```

---

## 🤝 Contributing

Issues and pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

---

## 📧 Contact

**Corresponding Author:** 
**Email:** 
**Institution:**

---

## 📜 License

This project is licensed under the **MIT License** – see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgements

- Developers and contributors of `Medial Axis Transform` and `curvaturepy`
- USGS for discharge data and Landsat/Sentinel imagery
- ECMWF for ERA5‑Land reanalysis
- USDA NRCS for SSURGO soil data

---

## ✅ Final Checklist for Reproducibility

| Requirement | Status |
|:------------|:-------|
| Raw data included or referenced | ✅ (USGS, ECMWF, USGS – public) |
| Processed data provided | ✅ (CSV, Excel in Data/processed) |
| All scripts numbered and ordered | ✅ (01–10y) |
| README with instructions | ✅ |
| License included | ✅ (MIT) |
| Tutorial notebooks | ✅ (Examples/) |
| Figure generation code | ✅ (Scripts) |

---

**Last Updated:** April 2026 
**Repository DOI:** [To be added upon publication]
