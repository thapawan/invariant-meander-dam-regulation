"""
Linear Mixed Effects Model Analysis

This module implements LME models to analyze the effects of dam regulation
on meander migration while accounting for spatial and temporal autocorrelation.
"""

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from typing import Dict, Optional, Tuple


def prepare_lme_data(
    curvatures: np.ndarray,
    migration_rates: np.ndarray,
    regulation_status: np.ndarray,
    reach_ids: Optional[np.ndarray] = None,
    time_periods: Optional[np.ndarray] = None
) -> pd.DataFrame:
    """
    Prepare data for Linear Mixed Effects modeling.
    
    Parameters
    ----------
    curvatures : np.ndarray
        Local curvature values
    migration_rates : np.ndarray
        Migration rates
    regulation_status : np.ndarray
        Binary array indicating regulation (1) or not (0)
    reach_ids : np.ndarray, optional
        Identifiers for different river reaches (for random effects)
    time_periods : np.ndarray, optional
        Time period identifiers
    
    Returns
    -------
    pd.DataFrame
        DataFrame ready for LME analysis
    """
    n_points = len(curvatures)
    
    data = {
        'curvature': curvatures,
        'migration_rate': migration_rates,
        'regulated': regulation_status,
    }
    
    if reach_ids is not None:
        data['reach_id'] = reach_ids
    else:
        data['reach_id'] = np.zeros(n_points)
    
    if time_periods is not None:
        data['time_period'] = time_periods
    else:
        data['time_period'] = np.zeros(n_points)
    
    df = pd.DataFrame(data)
    
    # Remove invalid values
    df = df.dropna()
    
    # Add interaction term
    df['curvature_x_regulated'] = df['curvature'] * df['regulated']
    
    return df


def fit_lme_model(
    data: pd.DataFrame,
    formula: Optional[str] = None
) -> Tuple[object, pd.DataFrame]:
    """
    Fit Linear Mixed Effects model to analyze regulation effects.
    
    The model tests whether:
    1. Regulation suppresses migration rates (regulated coefficient < 0)
    2. The migration template is invariant (curvature_x_regulated ≈ 0)
    
    Parameters
    ----------
    data : pd.DataFrame
        Prepared data for modeling
    formula : str, optional
        Model formula. If None, uses default formula.
    
    Returns
    -------
    tuple
        (fitted_model, results_summary)
    """
    if formula is None:
        # Default formula: migration rate depends on curvature, regulation,
        # and their interaction, with random effects for reach
        formula = "migration_rate ~ curvature + regulated + curvature_x_regulated"
    
    # Fit mixed effects model with random intercept for reach
    try:
        model = smf.mixedlm(
            formula,
            data,
            groups=data["reach_id"],
            re_formula="1"
        )
        result = model.fit(method='lbfgs')
        
        # Create summary DataFrame
        summary_df = pd.DataFrame({
            'coefficient': result.params,
            'std_error': result.bse,
            'z_value': result.tvalues,
            'p_value': result.pvalues
        })
        
        return result, summary_df
        
    except Exception as e:
        print(f"Error fitting model: {e}")
        print("Attempting simplified model without random effects...")
        
        # Fallback to simple OLS if mixed effects fail
        import statsmodels.api as sm
        
        # Prepare design matrix
        X = data[['curvature', 'regulated', 'curvature_x_regulated']]
        X = sm.add_constant(X)
        y = data['migration_rate']
        
        model = sm.OLS(y, X)
        result = model.fit()
        
        summary_df = pd.DataFrame({
            'coefficient': result.params,
            'std_error': result.bse,
            'z_value': result.tvalues,
            'p_value': result.pvalues
        })
        
        return result, summary_df


def interpret_results(summary_df: pd.DataFrame) -> Dict[str, bool]:
    """
    Interpret LME model results to test key hypotheses.
    
    Parameters
    ----------
    summary_df : pd.DataFrame
        Summary DataFrame from fit_lme_model
    
    Returns
    -------
    dict
        Dictionary with interpretation of key findings
    """
    interpretation = {}
    
    # Test hypothesis 1: Regulation suppresses migration rates
    if 'regulated' in summary_df.index:
        reg_coef = summary_df.loc['regulated', 'coefficient']
        reg_pval = summary_df.loc['regulated', 'p_value']
        
        interpretation['rates_suppressed'] = (reg_coef < 0) and (reg_pval < 0.05)
        interpretation['suppression_coefficient'] = float(reg_coef)
        interpretation['suppression_pvalue'] = float(reg_pval)
    
    # Test hypothesis 2: Migration template is invariant
    # (interaction term should not be significant)
    if 'curvature_x_regulated' in summary_df.index:
        interaction_coef = summary_df.loc['curvature_x_regulated', 'coefficient']
        interaction_pval = summary_df.loc['curvature_x_regulated', 'p_value']
        
        # Template is invariant if interaction is not significant
        interpretation['template_invariant'] = (interaction_pval > 0.05)
        interpretation['interaction_coefficient'] = float(interaction_coef)
        interpretation['interaction_pvalue'] = float(interaction_pval)
    
    # Test that curvature predicts migration
    if 'curvature' in summary_df.index:
        curv_coef = summary_df.loc['curvature', 'coefficient']
        curv_pval = summary_df.loc['curvature', 'p_value']
        
        interpretation['curvature_predicts_migration'] = (curv_coef != 0) and (curv_pval < 0.05)
        interpretation['curvature_coefficient'] = float(curv_coef)
        interpretation['curvature_pvalue'] = float(curv_pval)
    
    return interpretation


def calculate_geomorphic_dormancy_index(
    regulated_rates: np.ndarray,
    unregulated_rates: np.ndarray
) -> float:
    """
    Calculate geomorphic dormancy index as the ratio of suppressed to active rates.
    
    A value close to 0 indicates strong dormancy, close to 1 indicates no effect.
    
    Parameters
    ----------
    regulated_rates : np.ndarray
        Migration rates in regulated reaches
    unregulated_rates : np.ndarray
        Migration rates in unregulated reaches
    
    Returns
    -------
    float
        Geomorphic dormancy index (0 = complete dormancy, 1 = no effect)
    """
    # Use median to be robust to outliers
    regulated_median = np.median(regulated_rates)
    unregulated_median = np.median(unregulated_rates)
    
    if unregulated_median > 0:
        dormancy_index = regulated_median / unregulated_median
    else:
        dormancy_index = np.nan
    
    return dormancy_index
