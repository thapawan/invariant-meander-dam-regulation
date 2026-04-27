# Create Table 2 equivalent from LME results
print("\n=== Table 2: Fixed Effects Coefficients ===")
print(f"{'Predictor':<25} {'Coefficient':>12} {'Std. Error':>12} {'z':>10} {'p-value':>10} {'95% CI':>20}")
print("-" * 90)

# Extract from result object
for name, coef, se, pval in zip(result.params.index, result.params.values, result.bse.values, result.pvalues.values):
    ci_low = coef - 1.96 * se
    ci_high = coef + 1.96 * se
    print(f"{name:<25} {coef:>12.4f} {se:>12.4f} {coef/se:>10.2f} {pval:>10.4f} [{ci_low:>6.2f}, {ci_high:>6.2f}]")
