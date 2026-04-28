import pandas as pd

df = pd.read_csv('features_model_ready_cleaned.csv')

# Count unique bend_ids (ignore year suffix by extracting the numeric part)
df['bend_base'] = df.apply(lambda x: x['bend_id'].split('_')[-1], axis=1)

regulated = df[df['river'] == 'Blackwarrior']['bend_base'].unique()
unregulated = df[df['river'] == 'Cahaba']['bend_base'].unique()

print(f"Regulated unique bends: {len(regulated)}")
print(f"Unregulated unique bends: {len(unregulated)}")
print(f"Total: {len(regulated) + len(unregulated)}")

# Output should be:
# Regulated unique bends: 50
# Unregulated unique bends: 74
# Total: 124
