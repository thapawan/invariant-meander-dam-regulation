"""
Visualization Module

Functions to create publication-quality figures demonstrating
the invariant meander migration template under dam regulation.
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, Optional, Tuple


def plot_migration_template_comparison(
    comparison_results: Dict[str, np.ndarray],
    save_path: Optional[str] = None,
    figsize: Tuple[int, int] = (12, 5)
) -> plt.Figure:
    """
    Create a figure comparing migration templates between regulated and unregulated rivers.
    
    Parameters
    ----------
    comparison_results : dict
        Results from compare_regulated_unregulated function
    save_path : str, optional
        Path to save figure
    figsize : tuple
        Figure size (width, height)
    
    Returns
    -------
    plt.Figure
        Matplotlib figure object
    """
    fig, axes = plt.subplots(1, 2, figsize=figsize)
    
    # Panel A: Absolute migration rates
    ax = axes[0]
    
    # Plot unregulated
    ax.errorbar(
        comparison_results['unregulated_bins'],
        comparison_results['unregulated_mean_rates'],
        yerr=comparison_results['unregulated_std_rates'],
        marker='o', label='Unregulated', capsize=5, linewidth=2,
        color='#2E86AB', alpha=0.8
    )
    
    # Plot regulated
    ax.errorbar(
        comparison_results['regulated_bins'],
        comparison_results['regulated_mean_rates'],
        yerr=comparison_results['regulated_std_rates'],
        marker='s', label='Regulated (Dam)', capsize=5, linewidth=2,
        color='#A23B72', alpha=0.8
    )
    
    ax.set_xlabel('Local Curvature', fontsize=12, fontweight='bold')
    ax.set_ylabel('Migration Rate (m/yr)', fontsize=12, fontweight='bold')
    ax.set_title('A) Absolute Migration Rates', fontsize=13, fontweight='bold')
    ax.legend(loc='best', frameon=True, shadow=True)
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # Panel B: Normalized templates
    ax = axes[1]
    
    ax.plot(
        comparison_results['unregulated_bins'],
        comparison_results['unregulated_template_normalized'],
        marker='o', label='Unregulated', linewidth=2.5,
        color='#2E86AB', alpha=0.8
    )
    
    ax.plot(
        comparison_results['regulated_bins'],
        comparison_results['regulated_template_normalized'],
        marker='s', label='Regulated (Dam)', linewidth=2.5,
        color='#A23B72', alpha=0.8
    )
    
    ax.set_xlabel('Local Curvature', fontsize=12, fontweight='bold')
    ax.set_ylabel('Normalized Migration Rate', fontsize=12, fontweight='bold')
    ax.set_title('B) Invariant Migration Template', fontsize=13, fontweight='bold')
    
    # Add correlation text
    corr = comparison_results['template_correlation']
    ax.text(
        0.05, 0.95, f'Template Correlation: r = {corr:.3f}',
        transform=ax.transAxes, fontsize=11,
        verticalalignment='top',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    )
    
    ax.legend(loc='best', frameon=True, shadow=True)
    ax.grid(True, alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    return fig


def plot_lme_results(
    summary_df,
    interpretation: Dict[str, bool],
    save_path: Optional[str] = None,
    figsize: Tuple[int, int] = (10, 6)
) -> plt.Figure:
    """
    Create a figure showing LME model results.
    
    Parameters
    ----------
    summary_df : pd.DataFrame
        Summary DataFrame from LME model
    interpretation : dict
        Interpretation results
    save_path : str, optional
        Path to save figure
    figsize : tuple
        Figure size
    
    Returns
    -------
    plt.Figure
        Matplotlib figure object
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    # Create coefficient plot
    variables = summary_df.index.tolist()
    coefficients = summary_df['coefficient'].values
    errors = summary_df['std_error'].values
    
    # Color code by significance
    colors = ['#2E86AB' if p < 0.05 else '#CCCCCC' 
              for p in summary_df['p_value'].values]
    
    y_pos = np.arange(len(variables))
    
    ax.barh(y_pos, coefficients, xerr=errors, color=colors, alpha=0.7, capsize=5)
    ax.axvline(x=0, color='black', linestyle='--', linewidth=1)
    
    ax.set_yticks(y_pos)
    ax.set_yticklabels(variables, fontsize=11)
    ax.set_xlabel('Coefficient Value', fontsize=12, fontweight='bold')
    ax.set_title('Linear Mixed Effects Model Results', fontsize=14, fontweight='bold')
    
    # Add legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#2E86AB', alpha=0.7, label='Significant (p < 0.05)'),
        Patch(facecolor='#CCCCCC', alpha=0.7, label='Not Significant')
    ]
    ax.legend(handles=legend_elements, loc='best')
    
    # Add interpretation text
    text_str = "Key Findings:\n"
    if interpretation.get('rates_suppressed', False):
        text_str += "✓ Dam regulation suppresses migration rates\n"
    if interpretation.get('template_invariant', False):
        text_str += "✓ Migration template is invariant\n"
    if interpretation.get('curvature_predicts_migration', False):
        text_str += "✓ Curvature predicts migration\n"
    
    ax.text(
        0.98, 0.98, text_str,
        transform=ax.transAxes,
        fontsize=10,
        verticalalignment='top',
        horizontalalignment='right',
        bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.3)
    )
    
    ax.grid(True, alpha=0.3, axis='x', linestyle='--')
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    return fig


def plot_geomorphic_dormancy(
    regulated_rates: np.ndarray,
    unregulated_rates: np.ndarray,
    dormancy_index: float,
    save_path: Optional[str] = None,
    figsize: Tuple[int, int] = (10, 6)
) -> plt.Figure:
    """
    Create violin plot showing geomorphic dormancy.
    
    Parameters
    ----------
    regulated_rates : np.ndarray
        Migration rates in regulated reaches
    unregulated_rates : np.ndarray
        Migration rates in unregulated reaches
    dormancy_index : float
        Geomorphic dormancy index
    save_path : str, optional
        Path to save figure
    figsize : tuple
        Figure size
    
    Returns
    -------
    plt.Figure
        Matplotlib figure object
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    # Prepare data for violin plot
    import pandas as pd
    
    data = pd.DataFrame({
        'Migration Rate (m/yr)': np.concatenate([unregulated_rates, regulated_rates]),
        'Condition': ['Unregulated'] * len(unregulated_rates) + 
                     ['Regulated\n(Geomorphic Dormancy)'] * len(regulated_rates)
    })
    
    # Create violin plot
    sns.violinplot(
        data=data,
        x='Condition',
        y='Migration Rate (m/yr)',
        palette=['#2E86AB', '#A23B72'],
        ax=ax,
        alpha=0.7
    )
    
    # Add box plot overlay
    sns.boxplot(
        data=data,
        x='Condition',
        y='Migration Rate (m/yr)',
        width=0.3,
        ax=ax,
        color='white',
        linewidth=2
    )
    
    ax.set_ylabel('Migration Rate (m/yr)', fontsize=12, fontweight='bold')
    ax.set_xlabel('River Condition', fontsize=12, fontweight='bold')
    ax.set_title('Dam-Induced Geomorphic Dormancy', fontsize=14, fontweight='bold')
    
    # Add dormancy index annotation
    ax.text(
        0.5, 0.98,
        f'Dormancy Index: {dormancy_index:.3f}\n(Regulated/Unregulated Median)',
        transform=ax.transAxes,
        fontsize=11,
        horizontalalignment='center',
        verticalalignment='top',
        bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.3)
    )
    
    ax.grid(True, alpha=0.3, axis='y', linestyle='--')
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    return fig
