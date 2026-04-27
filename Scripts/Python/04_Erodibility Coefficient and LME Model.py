# 4a: Erodibility coefficient E
regulated_E = df_valid[df_valid['river'] == 'Blackwarrior']['E'].dropna()
unregulated_E = df_valid[df_valid['river'] == 'Cahaba']['E'].dropna()

print("=== Figure 4a ===")
print(f"Regulated E: median = {regulated_E.median():.2f}, n = {len(regulated_E)}")
print(f"Unregulated E: median = {unregulated_E.median():.2f}, n = {len(unregulated_E)}")
print(f"Reduction: {(1 - regulated_E.median()/unregulated_E.median())*100:.1f}%")

# 4c: Clay content vs ΔEVI correlation
# Load clay data
clay_df = pd.read_csv('figure3_clay_vs_evi.csv')
clay_corr, clay_p = spearmanr(clay_df['Clay_Content'], clay_df['Delta_EVI'])
print(f"\n=== Figure 4c ===")
print(f"Spearman's ρ (Clay vs ΔEVI) = {clay_corr:.3f}, p = {clay_p:.3f}")

# 4d: Qcv comparison
print(f"\n=== Figure 4d ===")
print("Qcv values from Table 3:")
print("Black Warrior (Regulated) 2000-2018: 1.26")
print("Black Warrior (Regulated) 2018-2024: 1.15")
print("Cahaba (Unregulated) 2000-2018: 1.40")
print("Cahaba (Unregulated) 2018-2024: 1.30")

# ============================================================
# LME MODEL (Table 2)
# ============================================================

# Prepare data for LME
# Need: log_E, CV_Q, ΔEVI, Regulated (binary), Clay Content, interaction

# Create binary regulation variable
df_valid['Regulated'] = (df_valid['river'] == 'Blackwarrior').astype(int)

# Create interaction term
df_valid['DeltaEVI_x_Regulated'] = df_valid['Delta_EVI_change_unitless_mean'] * df_valid['Regulated']

# For clay content, we need to merge from the clay file
# If clay data is at bend level, merge on bend_id
# If not available, run LME without clay (for demonstration)
# Here we assume clay data is available; if not, remove β₄

# Run LME model
model = mixedlm(
    "log_E ~ CV_runoff_selected_mean + Delta_EVI_change_unitless_mean + Regulated + Clay_Content + DeltaEVI_x_Regulated",
    df_valid,
    groups=df_valid["bend_id"],
    re_formula="~1"
)

# If Clay_Content column doesn't exist, use this instead:
# model = mixedlm(
#     "log_E ~ CV_runoff_selected_mean + Delta_EVI_change_unitless_mean + Regulated + DeltaEVI_x_Regulated",
#     df_valid,
#     groups=df_valid["bend_id"],
#     re_formula="~1"
# )

result = model.fit()

print("\n=== Table 2: LME Model Results ===")
print(result.summary())

# Extract variance components
var_bend = result.cov_re.iloc[0, 0] if result.cov_re.size > 0 else 0
var_resid = result.scale
icc = var_bend / (var_bend + var_resid) if (var_bend + var_resid) > 0 else 0

print(f"\nRandom effects:")
print(f"σ²_Bend = {var_bend:.4f}")
print(f"σ²_ε = {var_resid:.4f}")
print(f"ICC = {icc:.3f} ({icc*100:.1f}% of variance explained by bends)")
