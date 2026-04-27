print("\n=== Sample Size Verification ===")
for river in ['Blackwarrior', 'Cahaba']:
    for epoch in [2000, 2018]:
        subset = df[(df['river'] == river) & (df['year'] == epoch)]
        print(f"{river} {epoch}: {len(subset)} bends")

print(f"\nTotal observations (N): {len(df_valid)}")
print(f"Total bends: {df_valid['bend_id'].nunique()}")
print(f"Expected N (124 bends × 2 epochs) = 248")
