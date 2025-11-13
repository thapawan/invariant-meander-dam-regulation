#!/usr/bin/env python3
"""
Extract centerlines and calculate planform metrics from water masks
Requires: geopandas, rasterio, scikit-image, numpy
"""

import geopandas as gpd
import rasterio
from rasterio import features
import numpy as np
from skimage.morphology import medial_axis, skeletonize
from skimage import measure
import pandas as pd
from scipy.interpolate import CubicSpline
import curvaturepy as curv  # Assuming this is available

def extract_centerline(water_mask_path):
    """Extract centerline from water mask using medial axis transform"""
    with rasterio.open(water_mask_path) as src:
        water_mask = src.read(1)
        transform = src.transform
        
    # Clean mask and skeletonize
    cleaned_mask = clean_water_mask(water_mask)
    skeleton, distance = medial_axis(cleaned_mask, return_distance=True)
    
    # Convert skeleton to vector
    centerline = skeleton_to_centerline(skeleton, transform)
    
    return centerline

def calculate_curvature(centerline_gdf, smoothing_factor=0.1):
    """Calculate signed curvature along centerline"""
    # Extract coordinates
    coords = np.array([(pt.x, pt.y) for pt in centerline_gdf.geometry])
    
    # Smooth centerline with cubic spline
    t = np.arange(len(coords))
    cs_x = CubicSpline(t, coords[:, 0])
    cs_y = CubicSpline(t, coords[:, 1])
    
    # Calculate derivatives for curvature
    t_smooth = np.linspace(0, len(coords)-1, len(coords)*10)
    dx = cs_x.derivative()(t_smooth)
    ddx = cs_x.derivative(2)(t_smooth)
    dy = cs_y.derivative()(t_smooth) 
    ddy = cs_y.derivative(2)(t_smooth)
    
    # Curvature formula: κ = (dx*ddy - dy*ddx) / (dx^2 + dy^2)^(3/2)
    curvature = (dx * ddy - dy * ddx) / (dx**2 + dy**2)**(1.5)
    
    return curvature

def calculate_migration_rate(centerline_2000, centerline_2018, centerline_2024):
    """Calculate migration rates between epochs"""
    # Create migration dataframe
    migration_data = []
    
    # Calculate migration 2000-2018
    mig_2000_2018 = orthogonal_migration(centerline_2000, centerline_2018, years=18)
    # Calculate migration 2018-2024  
    mig_2018_2024 = orthogonal_migration(centerline_2018, centerline_2024, years=6)
    
    return pd.DataFrame({
        'median_migration_rate': [np.median(mig_2000_2018), np.median(mig_2018_2024)],
        'max_migration_rate': [np.percentile(mig_2000_2018, 95), np.percentile(mig_2018_2024, 95)],
        'epoch': ['2000-2018', '2018-2024']
    })

def main():
    """Main processing workflow"""
    rivers = ['black_warrior', 'cahaba']
    epochs = [2000, 2018, 2024]
    
    all_metrics = []
    
    for river in rivers:
        river_metrics = []
        
        # Load centerlines for all epochs
        centerlines = {}
        for epoch in epochs:
            mask_path = f"data/raw/{river}_water_mask_{epoch}.tif"
            centerlines[epoch] = extract_centerline(mask_path)
        
        # Calculate curvature for each epoch
        curvature_data = {}
        for epoch, centerline in centerlines.items():
            curvature_data[epoch] = calculate_curvature(centerline)
        
        # Calculate migration rates
        migration_rates = calculate_migration_rate(
            centerlines[2000], centerlines[2018], centerlines[2024]
        )
        
        # Compile results
        river_result = {
            'river': river,
            'curvature': curvature_data,
            'migration_rates': migration_rates,
            'centerlines': centerlines
        }
        
        all_metrics.append(river_result)
    
    # Save results
    import pickle
    with open('data/processed/planform_metrics.pkl', 'wb') as f:
        pickle.dump(all_metrics, f)

if __name__ == "__main__":
    main()
