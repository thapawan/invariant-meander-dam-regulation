# 3a: Median migration rates
regulated_migration = df_valid[df_valid['river'] == 'Blackwarrior']['median_migration_rate'].dropna()
unregulated_migration = df_valid[df_valid['river'] == 'Cahaba']['median_migration_rate'].dropna()

print("=== Figure 3a ===")
print(f"Regulated (Black Warrior): median = {regulated_migration.median():.2f} m/yr, n = {len(regulated_migration)}")
print(f"Unregulated (Cahaba): median = {unregulated_migration.median():.2f} m/yr, n = {len(unregulated_migration)}")
print(f"Reduction: {(1 - regulated_migration.median()/unregulated_migration.median())*100:.1f}%")

# Mann-Whitney U test for migration rates
u_mig, p_mig = stats.mannwhitneyu(regulated_migration, unregulated_migration, alternative='two-sided')
print(f"Mann-Whitney U = {u_mig:.0f}, p = {p_mig:.4f}")

# 3c/3d: Median Absolute Deviation (MAD) for each epoch
print("\n=== MAD (Median Absolute Deviation) ===")
for epoch in [2000, 2018]:
    for river in ['Blackwarrior', 'Cahaba']:
        subset = df_valid[(df_valid['year'] == epoch) & (df_valid['river'] == river)]['median_migration_rate'].dropna()
        mad = np.median(np.abs(subset - subset.median()))
        print(f"{river} {epoch}: MAD = {mad:.2f}, n = {len(subset)}")

# MAD comparison (pooled by regulation status, not by epoch)
# Get MAD per bend (using absolute deviation from bend median)
# For simplicity, use the MAD of all migration rates per river
regulated_mad = np.median(np.abs(regulated_migration - regulated_migration.median()))
unregulated_mad = np.median(np.abs(unregulated_migration - unregulated_migration.median()))
print(f"\nPooled MAD: Regulated = {regulated_mad:.2f}, Unregulated = {unregulated_mad:.2f}")

u_mad, p_mad = stats.mannwhitneyu(
    np.abs(regulated_migration - regulated_migration.median()),
    np.abs(unregulated_migration - unregulated_migration.median()),
    alternative='two-sided'
)
print(f"Mann-Whitney U for MAD = {u_mad:.0f}, p = {p_mad:.4f}")
