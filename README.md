# **The Invariant Meander: Dam Regulation Suppresses Migration Rates but Conserves the Geometric Template of Erosion**

**Authors:** [Your Names]  
**Correspondence:** [Your Email]  
**DOI:** [Link to paper once published]  
**License:** [e.g., MIT License]

---

## **Overview**

This repository contains the complete data and code to reproduce the analysis and figures for the manuscript **"The Invariant Meander: Dam Regulation Suppresses Migration Rates but Conserves the Geometric Template of Erosion"**.

This study demonstrates a fundamental decoupling in meander migration: the **spatial pattern of erosion (phase lag)** is an intrinsic geometric property invariant to dam regulation, while the **rate of migration (erodibility coefficient)** is extrinsically suppressed. We combine multi-sensor remote sensing, hydrologic analysis, and statistical modeling to show that dam regulation induces a state of **geomorphic dormancy**, where the river's meandering blueprint remains intact but its execution is halted by dampened hydraulics and enhanced biotic stabilization.

![Abstract Graphic](figures/abstract_graphic.png) *[Optional: Include a key figure from the paper]*

## **Key Findings**

1.  **Geometric Invariance:** The dimensionless curvature-migration phase lag (Δs/~W~) is statistically indistinguishable between regulated and unregulated rivers (~2.0 channel widths), confirming it as an intrinsic property.
2.  **Process Suppression:** Median migration rates and the erodibility coefficient (E) are suppressed by more than 50% in the regulated river.
3.  **Shift in Process Dominance:** Linear Mixed-Effects modeling reveals that riparian vegetation becomes the key constraint on channel migration under regulation, a signature of a dam-induced biogeomorphic feedback loop.

## **Repository Structure**

```
Riverine-Geomorphology-Metrics-GEE/
│
├── data/
│   ├── processed/           # Analysis-ready data (centerlines, metrics, model inputs)
│   ├── raw/                # Raw data (water masks, hydrologic records)
│   └── spatial/            # Watershed boundaries, study reach shapefiles
│
├── scripts/
│   ├── 01_data_acquisition.R      # GEE API calls for imagery & water mask generation
│   ├── 02_planform_metrics.py     # Centerline extraction, migration & curvature calculation
│   ├── 03_covariate_processing.R  # Processing ΔEVI, flow CV, clay content
│   ├── 04_phase_lag_analysis.R    # Cross-correlation to find optimal Δs/W
│   ├── 05_statistical_models.R    # LME model fitting & hypothesis testing
│   └── 06_figure_generation.R     # Code to regenerate all manuscript figures
│
├── figures/                # All generated figures (Fig1.tif, Fig2.pdf, etc.)
├── output/                 # Model results, statistical summaries
│
├── docs/
│   └── methodology_tutorial.ipynb  # Step-by-step Jupyter notebook tutorial
│
├── environment.yml         # Conda environment for Python dependencies
├── requirements.txt        # Pip requirements for Python dependencies
├── README.md               # This file
└── LICENSE
```

## **Quick Start**

### **1. Environment Setup**

To replicate the analysis environment:

**Using Conda (Recommended):**
```bash
conda env create -f environment.yml
conda activate invariant_meander
```

**Using Pip:**
```bash
pip install -r requirements.txt
```

### **2. Data Processing Pipeline**

Execute the scripts in order to reproduce the entire analysis:

```bash
# 1. Acquire satellite imagery and generate water masks (requires GEE authentication)
Rscript scripts/01_data_acquisition.R

# 2. Extract centerlines and calculate planform metrics
python scripts/02_planform_metrics.py

# 3. Process covariates (ΔEVI, hydrology, soils)
Rscript scripts/03_covariate_processing.R

# 4. Determine the optimal phase lag (Δs/W) for each river
Rscript scripts/04_phase_lag_analysis.R

# 5. Run the Linear Mixed-Effects models and statistical tests
Rscript scripts/05_statistical_models.R

# 6. Generate all manuscript figures
Rscript scripts/06_figure_generation.R
```

## **Data Sources**

| Dataset | Source | Purpose |
| :--- | :--- | :--- |
| **Optical Imagery** | USGS Landsat 5/7/8/9, ESA Sentinel-2 | Water masking, centerline delineation, ΔEVI |
| **Water Masks** | DeepLabV3 model (this study) | Primary input for channel planform |
| **Discharge Data** | USGS NWIS (Gauge 02425000, 02466030, etc.) | Calculation of flow regime (CV) |
| **Runoff Data** | ECMWF ERA5-Land | Basin-wide hydrologic variability |
| **Soil Data** | USDA NRCS SSURGO | Bank clay content as a geologic control |

## **Key Methodological Notes**

*   **Water Mask Model:** The fine-tuned DeepLabV3 model used for water classification is available in the `scripts/` directory. Pre-trained weights are hosted on [Zenodo/Mendeley Data - *link to be added upon publication*].
*   **Phase Lag Calculation:** The optimal dimensionless phase lag (Δs/~W~) was determined by maximizing the Spearman's ρ correlation between curvature and lagged migration rate across four candidate lags (1.5W, 2.0W, 2.5W, 3.0W), as implemented in `scripts/04_phase_lag_analysis.R`.
*   **Statistical Models:** All analyses account for spatial and temporal non-independence using Linear Mixed-Effects models with random intercepts for `Bend ID` and `Temporal Epoch`.

## **Citing This Work**

If you use this code or data in your research, please cite our publication:

> [Author(s)]. (2024). The Invariant Meander: Dam Regulation Suppresses Migration Rates but Conserves the Geometric Template of Erosion. *[Journal Name]*, [Volume], [Pages]. DOI: [To be added]

## **License**

This project is licensed under the [MIT License](LICENSE) - see the LICENSE file for details.

## **Acknowledgements**

We express our gratitude to the developers and contributors of the `Medial Axis Transform` and `curvaturepy` libraries. This material is based upon work supported by [Your Funding Agencies].

---








