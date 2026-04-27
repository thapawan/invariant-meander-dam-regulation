import pandas as pd
import numpy as np
import scipy.stats as stats
import statsmodels.api as sm
from statsmodels.formula.api import mixedlm
import matplotlib.pyplot as plt
import seaborn as sns

# Load your bends data (one row per bend per epoch)
df = pd.read_csv('ikeda_ready_bends_enhanced.csv')

# Display basic info
print(f"Total observations: {len(df)}")
print(f"Unique bends: {df['bend_id'].nunique()}")
print(f"Rivers: {df['river'].unique()}")
print(f"Epochs: {df['year'].unique()}")

# Create log(E) = log(migration_rate / curvature)
df['curvature_abs'] = df['mean_curvature_abs']
df['E'] = df['median_migration_rate'] / (df['curvature_abs'] + 1e-10)
df['log_E'] = np.log(df['E'] + 1e-10)

# Filter valid rows
df_valid = df[df['log_E'].notna() & np.isfinite(df['log_E'])].copy()
print(f"\nValid observations: {len(df_valid)}")
