# 2a: Unlagged curvature vs migration correlation
from scipy.stats import spearmanr, pearsonr

# For all bends combined
all_curvature = df_valid['mean_curvature'].values
all_migration = df_valid['median_migration_rate'].values

pearson_r, pearson_p = pearsonr(all_curvature, all_migration)
spearman_rho, spearman_p = spearmanr(all_curvature, all_migration)

print("=== Figure 2a ===")
print(f"OLS R² = {pearson_r**2:.3f}")
print(f"Spearman's ρ = {spearman_rho:.3f}, p = {spearman_p:.4f}")

# 2c: Mann-Whitney U test for Δs/W between rivers
regulated_phase = df_valid[df_valid['river'] == 'Blackwarrior']['best_lag_abs_corr'].dropna()
unregulated_phase = df_valid[df_valid['river'] == 'Cahaba']['best_lag_abs_corr'].dropna()

u_stat, p_value = stats.mannwhitneyu(regulated_phase, unregulated_phase, alternative='two-sided')

print("\n=== Figure 2c ===")
print(f"Mann-Whitney U = {u_stat:.0f}, p = {p_value:.3f}")
print(f"Median Δs/W (regulated): {regulated_phase.median():.1f}")
print(f"Median Δs/W (unregulated): {unregulated_phase.median():.1f}")
print(f"Combined median: {pd.concat([regulated_phase, unregulated_phase]).median():.1f}")

# 2d: Distance from dam vs phase lag (regulated river only)
regulated_df = df_valid[df_valid['river'] == 'Blackwarrior'].dropna(subset=['DamDistance_km_mean', 'best_lag_abs_corr'])
spearman_rho_dist, spearman_p_dist = spearmanr(regulated_df['DamDistance_km_mean'], regulated_df['best_lag_abs_corr'])

print("\n=== Figure 2d ===")
print(f"Spearman's ρ (distance vs phase lag) = {spearman_rho_dist:.3f}, p = {spearman_p_dist:.3f}")
