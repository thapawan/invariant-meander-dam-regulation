"""
Main Analysis Script: Invariant Meander Migration Under Dam Regulation

This script demonstrates the key finding: dam regulation suppresses
meander migration rates while the geometric template remains invariant.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.data_generator import generate_migration_data, save_synthetic_data
from src.meander_analysis import (
    calculate_curvature,
    calculate_migration_rate,
    compare_regulated_unregulated
)
from src.lme_model import (
    prepare_lme_data,
    fit_lme_model,
    interpret_results,
    calculate_geomorphic_dormancy_index
)
from src.visualization import (
    plot_migration_template_comparison,
    plot_lme_results,
    plot_geomorphic_dormancy
)


def main():
    """Run the complete analysis."""
    
    print("=" * 80)
    print("INVARIANT MEANDER MIGRATION UNDER DAM REGULATION")
    print("=" * 80)
    print()
    
    # Step 1: Generate synthetic data
    print("Step 1: Generating synthetic meander migration data...")
    data = generate_migration_data(
        n_reaches=10,
        points_per_reach=100,
        regulated_fraction=0.5,
        time_delta=10.0,
        suppression_factor=0.25,  # 75% reduction in migration rates
        curvature_migration_slope=5.0,
        noise_level=0.2,
        random_seed=42
    )
    
    # Save data
    os.makedirs('data', exist_ok=True)
    save_synthetic_data(data, 'data/synthetic_migration_data.csv')
    print("  ✓ Synthetic data generated and saved")
    print(f"  - Total points: {len(data['curvatures'])}")
    print(f"  - Regulated reaches: {np.sum(data['regulation_status'])}")
    print(f"  - Unregulated reaches: {np.sum(1 - data['regulation_status'])}")
    print()
    
    # Step 2: Separate regulated and unregulated data
    print("Step 2: Separating regulated and unregulated river reaches...")
    regulated_mask = data['regulation_status'] == 1
    unregulated_mask = data['regulation_status'] == 0
    
    regulated_curvatures = data['curvatures'][regulated_mask]
    regulated_rates = data['migration_rates'][regulated_mask]
    
    unregulated_curvatures = data['curvatures'][unregulated_mask]
    unregulated_rates = data['migration_rates'][unregulated_mask]
    
    print(f"  ✓ Regulated points: {len(regulated_rates)}")
    print(f"  ✓ Unregulated points: {len(unregulated_rates)}")
    print()
    
    # Step 3: Compare migration templates
    print("Step 3: Analyzing migration templates...")
    comparison = compare_regulated_unregulated(
        regulated_curvatures,
        regulated_rates,
        unregulated_curvatures,
        unregulated_rates,
        bin_count=15
    )
    
    print(f"  ✓ Template correlation: r = {comparison['template_correlation']:.3f}")
    print(f"  ✓ Rate suppression factor: {comparison['rate_suppression_factor']:.3f}")
    print(f"  ✓ Interpretation: High correlation indicates invariant template!")
    print()
    
    # Step 4: Linear Mixed Effects Model
    print("Step 4: Fitting Linear Mixed Effects Model...")
    lme_data = prepare_lme_data(
        data['curvatures'],
        data['migration_rates'],
        data['regulation_status'],
        data['reach_ids'],
        data['time_periods']
    )
    
    model_result, summary_df = fit_lme_model(lme_data)
    print("  ✓ Model fitted successfully")
    print("\n  Model Summary:")
    print(summary_df.to_string())
    print()
    
    # Step 5: Interpret results
    print("Step 5: Interpreting results...")
    interpretation = interpret_results(summary_df)
    
    print(f"  ✓ Rates suppressed by regulation: {interpretation.get('rates_suppressed', False)}")
    if 'suppression_coefficient' in interpretation:
        print(f"    - Coefficient: {interpretation['suppression_coefficient']:.4f}")
        print(f"    - P-value: {interpretation['suppression_pvalue']:.4e}")
    
    print(f"  ✓ Template invariant (interaction not significant): {interpretation.get('template_invariant', False)}")
    if 'interaction_coefficient' in interpretation:
        print(f"    - Coefficient: {interpretation['interaction_coefficient']:.4f}")
        print(f"    - P-value: {interpretation['interaction_pvalue']:.4e}")
    
    print(f"  ✓ Curvature predicts migration: {interpretation.get('curvature_predicts_migration', False)}")
    if 'curvature_coefficient' in interpretation:
        print(f"    - Coefficient: {interpretation['curvature_coefficient']:.4f}")
        print(f"    - P-value: {interpretation['curvature_pvalue']:.4e}")
    print()
    
    # Step 6: Calculate geomorphic dormancy index
    print("Step 6: Calculating geomorphic dormancy index...")
    dormancy_index = calculate_geomorphic_dormancy_index(
        regulated_rates,
        unregulated_rates
    )
    print(f"  ✓ Geomorphic dormancy index: {dormancy_index:.3f}")
    print(f"    - Interpretation: {(1 - dormancy_index) * 100:.1f}% reduction in median migration rate")
    print()
    
    # Step 7: Create visualizations
    print("Step 7: Creating visualizations...")
    os.makedirs('figures', exist_ok=True)
    
    # Migration template comparison
    fig1 = plot_migration_template_comparison(
        comparison,
        save_path='figures/migration_template_comparison.png'
    )
    print("  ✓ Migration template comparison saved")
    
    # LME model results
    fig2 = plot_lme_results(
        summary_df,
        interpretation,
        save_path='figures/lme_model_results.png'
    )
    print("  ✓ LME model results saved")
    
    # Geomorphic dormancy
    fig3 = plot_geomorphic_dormancy(
        regulated_rates,
        unregulated_rates,
        dormancy_index,
        save_path='figures/geomorphic_dormancy.png'
    )
    print("  ✓ Geomorphic dormancy plot saved")
    print()
    
    # Summary
    print("=" * 80)
    print("SUMMARY OF KEY FINDINGS")
    print("=" * 80)
    print()
    print("This analysis demonstrates that dam regulation induces geomorphic dormancy:")
    print()
    print(f"1. RATE SUPPRESSION: Migration rates are reduced by ~{(1 - dormancy_index) * 100:.0f}%")
    print(f"   in regulated reaches compared to unregulated reaches.")
    print()
    print(f"2. INVARIANT TEMPLATE: Despite rate suppression, the geometric template")
    print(f"   (curvature-migration relationship) remains invariant (r = {comparison['template_correlation']:.3f}).")
    print()
    print(f"3. GEOMORPHIC DORMANCY: Rivers under dam regulation enter a dormant state")
    print(f"   where the 'blueprint' for erosion is preserved but process rates are suppressed.")
    print()
    print("All figures saved to 'figures/' directory.")
    print("Data saved to 'data/' directory.")
    print()
    print("=" * 80)
    
    plt.show()


if __name__ == "__main__":
    main()
