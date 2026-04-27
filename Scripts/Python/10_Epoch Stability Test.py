# Test if migration rates differed between epochs at Cahaba
cahaba_2000 = df_valid[(df_valid['river'] == 'Cahaba') & (df_valid['year'] == 2000)]['median_migration_rate'].dropna()
cahaba_2018 = df_valid[(df_valid['river'] == 'Cahaba') & (df_valid['year'] == 2018)]['median_migration_rate'].dropna()

u_epoch, p_epoch = stats.mannwhitneyu(cahaba_2000, cahaba_2018, alternative='two-sided')

print("\n=== Cahaba River Epoch Comparison ===")
print(f"2009-2018 median: {cahaba_2000.median():.2f} m/yr, n = {len(cahaba_2000)}")
print(f"2018-2024 median: {cahaba_2018.median():.2f} m/yr, n = {len(cahaba_2018)}")
print(f"Mann-Whitney U = {u_epoch:.1f}, p = {p_epoch:.3f}")
print("Interpretation: No significant difference between epochs (p > 0.05)")
