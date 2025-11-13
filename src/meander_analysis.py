"""
Meander Migration Analysis Module

This module provides functions to analyze meander migration patterns
in regulated and unregulated rivers, demonstrating that dam regulation
suppresses migration rates while conserving the geometric template of erosion.
"""

import numpy as np
import pandas as pd
from typing import Tuple, Dict, Optional


def calculate_migration_rate(
    positions_t1: np.ndarray,
    positions_t2: np.ndarray,
    time_delta: float
) -> np.ndarray:
    """
    Calculate migration rates between two time periods.
    
    Parameters
    ----------
    positions_t1 : np.ndarray
        Channel centerline positions at time 1 (N x 2 array)
    positions_t2 : np.ndarray
        Channel centerline positions at time 2 (N x 2 array)
    time_delta : float
        Time difference in years
    
    Returns
    -------
    np.ndarray
        Migration rates in meters per year
    """
    if positions_t1.shape != positions_t2.shape:
        raise ValueError("Position arrays must have the same shape")
    
    if time_delta <= 0:
        raise ValueError("Time delta must be positive")
    
    # Calculate Euclidean distance between corresponding points
    distances = np.sqrt(np.sum((positions_t2 - positions_t1) ** 2, axis=1))
    
    # Calculate migration rate
    migration_rates = distances / time_delta
    
    return migration_rates


def calculate_curvature(positions: np.ndarray, window_size: int = 5) -> np.ndarray:
    """
    Calculate local curvature along a channel centerline.
    
    Parameters
    ----------
    positions : np.ndarray
        Channel centerline positions (N x 2 array)
    window_size : int
        Window size for curvature calculation
    
    Returns
    -------
    np.ndarray
        Local curvature values
    """
    if len(positions) < window_size:
        raise ValueError("Position array too small for given window size")
    
    curvatures = np.zeros(len(positions))
    
    for i in range(window_size // 2, len(positions) - window_size // 2):
        # Get local window
        local_positions = positions[i - window_size // 2:i + window_size // 2 + 1]
        
        # Fit circle to points and calculate curvature
        # Simple approximation using three points
        if window_size >= 3:
            p1, p2, p3 = local_positions[0], local_positions[window_size // 2], local_positions[-1]
            
            # Calculate curvature from three points
            # Using Menger curvature formula
            denom = np.linalg.norm(p1 - p2) * np.linalg.norm(p2 - p3) * np.linalg.norm(p3 - p1)
            
            if denom > 1e-10:
                area = 0.5 * abs(
                    (p2[0] - p1[0]) * (p3[1] - p1[1]) - 
                    (p3[0] - p1[0]) * (p2[1] - p1[1])
                )
                curvatures[i] = 4 * area / denom
            else:
                curvatures[i] = 0
    
    # Fill edges with nearest values
    curvatures[:window_size // 2] = curvatures[window_size // 2]
    curvatures[-window_size // 2:] = curvatures[-window_size // 2 - 1]
    
    return curvatures


def analyze_migration_template(
    curvatures: np.ndarray,
    migration_rates: np.ndarray,
    bin_count: int = 10
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Analyze the relationship between curvature and migration rate
    to identify the migration template.
    
    Parameters
    ----------
    curvatures : np.ndarray
        Local curvature values
    migration_rates : np.ndarray
        Migration rates
    bin_count : int
        Number of bins for analysis
    
    Returns
    -------
    tuple
        (bin_centers, mean_rates, std_rates)
    """
    if len(curvatures) != len(migration_rates):
        raise ValueError("Curvature and migration rate arrays must have same length")
    
    # Remove invalid values
    valid_mask = ~(np.isnan(curvatures) | np.isnan(migration_rates))
    curvatures = curvatures[valid_mask]
    migration_rates = migration_rates[valid_mask]
    
    # Create bins
    curvature_bins = np.linspace(
        np.percentile(curvatures, 5),
        np.percentile(curvatures, 95),
        bin_count + 1
    )
    
    bin_centers = (curvature_bins[:-1] + curvature_bins[1:]) / 2
    mean_rates = np.zeros(bin_count)
    std_rates = np.zeros(bin_count)
    
    for i in range(bin_count):
        mask = (curvatures >= curvature_bins[i]) & (curvatures < curvature_bins[i + 1])
        if np.sum(mask) > 0:
            mean_rates[i] = np.mean(migration_rates[mask])
            std_rates[i] = np.std(migration_rates[mask])
    
    return bin_centers, mean_rates, std_rates


def compare_regulated_unregulated(
    regulated_curvatures: np.ndarray,
    regulated_rates: np.ndarray,
    unregulated_curvatures: np.ndarray,
    unregulated_rates: np.ndarray,
    bin_count: int = 10
) -> Dict[str, np.ndarray]:
    """
    Compare migration templates between regulated and unregulated rivers.
    
    This function demonstrates the key finding: dam regulation suppresses
    migration rates while preserving the geometric template.
    
    Parameters
    ----------
    regulated_curvatures : np.ndarray
        Curvatures for regulated river
    regulated_rates : np.ndarray
        Migration rates for regulated river
    unregulated_curvatures : np.ndarray
        Curvatures for unregulated river
    unregulated_rates : np.ndarray
        Migration rates for unregulated river
    bin_count : int
        Number of bins for analysis
    
    Returns
    -------
    dict
        Dictionary containing comparison results
    """
    # Analyze both datasets
    reg_bins, reg_mean, reg_std = analyze_migration_template(
        regulated_curvatures, regulated_rates, bin_count
    )
    unreg_bins, unreg_mean, unreg_std = analyze_migration_template(
        unregulated_curvatures, unregulated_rates, bin_count
    )
    
    # Calculate normalized templates (shape of relationship)
    reg_template_norm = reg_mean / (np.max(reg_mean) + 1e-10)
    unreg_template_norm = unreg_mean / (np.max(unreg_mean) + 1e-10)
    
    # Calculate correlation between normalized templates
    template_correlation = np.corrcoef(reg_template_norm, unreg_template_norm)[0, 1]
    
    # Calculate rate suppression factor
    rate_suppression = np.mean(reg_mean) / (np.mean(unreg_mean) + 1e-10)
    
    return {
        'regulated_bins': reg_bins,
        'regulated_mean_rates': reg_mean,
        'regulated_std_rates': reg_std,
        'unregulated_bins': unreg_bins,
        'unregulated_mean_rates': unreg_mean,
        'unregulated_std_rates': unreg_std,
        'template_correlation': template_correlation,
        'rate_suppression_factor': rate_suppression,
        'regulated_template_normalized': reg_template_norm,
        'unregulated_template_normalized': unreg_template_norm
    }
