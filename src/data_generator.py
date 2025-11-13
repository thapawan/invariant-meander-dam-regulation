"""
Synthetic Data Generator

Generates synthetic meander migration data for demonstration purposes.
This simulates the key finding: dam regulation suppresses migration rates
while preserving the geometric template of erosion.
"""

import numpy as np
from typing import Tuple, Dict, Optional


def generate_synthetic_channel(
    n_points: int = 100,
    sinuosity: float = 1.5,
    amplitude: float = 50.0,
    wavelength: float = 200.0
) -> np.ndarray:
    """
    Generate synthetic meandering channel centerline.
    
    Parameters
    ----------
    n_points : int
        Number of points along centerline
    sinuosity : float
        Channel sinuosity (ratio of channel length to valley length)
    amplitude : float
        Meander amplitude in meters
    wavelength : float
        Meander wavelength in meters
    
    Returns
    -------
    np.ndarray
        Channel positions (N x 2 array)
    """
    # Generate downstream coordinate
    s = np.linspace(0, wavelength * 5, n_points)
    
    # Generate meandering pattern
    k = 2 * np.pi / wavelength  # wave number
    
    # X coordinate: downstream
    x = s
    
    # Y coordinate: lateral position (sine wave)
    y = amplitude * np.sin(k * s)
    
    # Add some random perturbations for realism
    noise_x = np.random.normal(0, wavelength * 0.01, n_points)
    noise_y = np.random.normal(0, amplitude * 0.05, n_points)
    
    positions = np.column_stack([x + noise_x, y + noise_y])
    
    return positions


def generate_migration_data(
    n_reaches: int = 5,
    points_per_reach: int = 50,
    regulated_fraction: float = 0.5,
    time_delta: float = 10.0,
    suppression_factor: float = 0.3,
    curvature_migration_slope: float = 5.0,
    noise_level: float = 0.2,
    random_seed: Optional[int] = 42
) -> Dict[str, np.ndarray]:
    """
    Generate synthetic meander migration data.
    
    This generates data that demonstrates the key finding:
    - Dam regulation suppresses migration rates (by suppression_factor)
    - The migration template (curvature-migration relationship) is invariant
    
    Parameters
    ----------
    n_reaches : int
        Number of river reaches
    points_per_reach : int
        Number of measurement points per reach
    regulated_fraction : float
        Fraction of reaches that are regulated
    time_delta : float
        Time period in years
    suppression_factor : float
        How much regulation suppresses rates (0.3 = 70% reduction)
    curvature_migration_slope : float
        Slope of curvature-migration relationship
    noise_level : float
        Amount of random noise to add
    random_seed : int, optional
        Random seed for reproducibility
    
    Returns
    -------
    dict
        Dictionary containing all generated data
    """
    if random_seed is not None:
        np.random.seed(random_seed)
    
    n_total = n_reaches * points_per_reach
    
    # Generate curvatures (log-normal distribution)
    curvatures = np.random.lognormal(mean=-3, sigma=0.8, size=n_total)
    curvatures = np.clip(curvatures, 0.001, 0.5)
    
    # Assign regulation status to reaches
    n_regulated = int(n_reaches * regulated_fraction)
    reach_regulation = np.array([1] * n_regulated + [0] * (n_reaches - n_regulated))
    np.random.shuffle(reach_regulation)
    
    # Create arrays
    regulation_status = np.repeat(reach_regulation, points_per_reach)
    reach_ids = np.repeat(np.arange(n_reaches), points_per_reach)
    
    # Generate migration rates based on curvature
    # Key: The RELATIONSHIP (template) is the same, only the magnitude differs
    base_rates = curvature_migration_slope * curvatures
    
    # Apply suppression to regulated reaches
    migration_rates = np.where(
        regulation_status == 1,
        base_rates * suppression_factor,  # Suppressed rates
        base_rates  # Natural rates
    )
    
    # Add noise
    migration_rates += np.random.normal(0, noise_level, n_total)
    migration_rates = np.maximum(migration_rates, 0)  # Ensure non-negative
    
    # Generate channel positions for two time periods
    positions_t1 = []
    positions_t2 = []
    
    for i in range(n_reaches):
        # Generate base channel
        pos_t1 = generate_synthetic_channel(
            n_points=points_per_reach,
            amplitude=np.random.uniform(30, 70),
            wavelength=np.random.uniform(150, 250)
        )
        
        # Generate migrated positions
        idx_start = i * points_per_reach
        idx_end = (i + 1) * points_per_reach
        
        local_rates = migration_rates[idx_start:idx_end]
        
        # Add migration perpendicular to channel direction
        angles = np.random.uniform(0, 2 * np.pi, points_per_reach)
        dx = local_rates * time_delta * np.cos(angles)
        dy = local_rates * time_delta * np.sin(angles)
        
        pos_t2 = pos_t1 + np.column_stack([dx, dy])
        
        positions_t1.append(pos_t1)
        positions_t2.append(pos_t2)
    
    positions_t1 = np.vstack(positions_t1)
    positions_t2 = np.vstack(positions_t2)
    
    # Create time period identifiers (could have multiple time periods)
    time_periods = np.zeros(n_total)
    
    return {
        'curvatures': curvatures,
        'migration_rates': migration_rates,
        'regulation_status': regulation_status,
        'reach_ids': reach_ids,
        'time_periods': time_periods,
        'positions_t1': positions_t1,
        'positions_t2': positions_t2,
        'time_delta': time_delta,
        'n_reaches': n_reaches,
        'points_per_reach': points_per_reach
    }


def save_synthetic_data(data: Dict[str, np.ndarray], filepath: str) -> None:
    """
    Save synthetic data to CSV file.
    
    Parameters
    ----------
    data : dict
        Data dictionary from generate_migration_data
    filepath : str
        Path to save CSV file
    """
    import pandas as pd
    
    df = pd.DataFrame({
        'curvature': data['curvatures'],
        'migration_rate': data['migration_rates'],
        'regulated': data['regulation_status'],
        'reach_id': data['reach_ids'],
        'time_period': data['time_periods'],
        'x_t1': data['positions_t1'][:, 0],
        'y_t1': data['positions_t1'][:, 1],
        'x_t2': data['positions_t2'][:, 0],
        'y_t2': data['positions_t2'][:, 1]
    })
    
    df.to_csv(filepath, index=False)
    print(f"Synthetic data saved to {filepath}")


def load_synthetic_data(filepath: str) -> Dict[str, np.ndarray]:
    """
    Load synthetic data from CSV file.
    
    Parameters
    ----------
    filepath : str
        Path to CSV file
    
    Returns
    -------
    dict
        Data dictionary
    """
    import pandas as pd
    
    df = pd.read_csv(filepath)
    
    data = {
        'curvatures': df['curvature'].values,
        'migration_rates': df['migration_rate'].values,
        'regulation_status': df['regulated'].values,
        'reach_ids': df['reach_id'].values,
        'time_periods': df['time_period'].values,
        'positions_t1': df[['x_t1', 'y_t1']].values,
        'positions_t2': df[['x_t2', 'y_t2']].values,
    }
    
    return data
