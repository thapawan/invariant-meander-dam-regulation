"""
Unit tests for data_generator module
"""

import numpy as np
import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.data_generator import (
    generate_synthetic_channel,
    generate_migration_data
)


class TestGenerateSyntheticChannel:
    """Tests for generate_synthetic_channel function"""
    
    def test_basic_generation(self):
        """Test basic channel generation"""
        positions = generate_synthetic_channel(n_points=100)
        
        assert positions.shape == (100, 2)
        assert not np.any(np.isnan(positions))
    
    def test_custom_parameters(self):
        """Test with custom parameters"""
        positions = generate_synthetic_channel(
            n_points=50,
            amplitude=100.0,
            wavelength=300.0
        )
        
        assert positions.shape == (50, 2)


class TestGenerateMigrationData:
    """Tests for generate_migration_data function"""
    
    def test_basic_data_generation(self):
        """Test basic migration data generation"""
        data = generate_migration_data(
            n_reaches=5,
            points_per_reach=20,
            random_seed=42
        )
        
        # Check all expected keys are present
        expected_keys = [
            'curvatures', 'migration_rates', 'regulation_status',
            'reach_ids', 'time_periods', 'positions_t1', 'positions_t2',
            'time_delta', 'n_reaches', 'points_per_reach'
        ]
        
        for key in expected_keys:
            assert key in data
    
    def test_data_dimensions(self):
        """Test that data has correct dimensions"""
        n_reaches = 4
        points_per_reach = 25
        
        data = generate_migration_data(
            n_reaches=n_reaches,
            points_per_reach=points_per_reach,
            random_seed=42
        )
        
        n_total = n_reaches * points_per_reach
        
        assert len(data['curvatures']) == n_total
        assert len(data['migration_rates']) == n_total
        assert len(data['regulation_status']) == n_total
        assert data['positions_t1'].shape == (n_total, 2)
        assert data['positions_t2'].shape == (n_total, 2)
    
    def test_regulation_fraction(self):
        """Test that regulation fraction is approximately correct"""
        data = generate_migration_data(
            n_reaches=10,
            points_per_reach=50,
            regulated_fraction=0.5,
            random_seed=42
        )
        
        # Should be roughly 50% regulated
        regulated_fraction = np.mean(data['regulation_status'])
        assert 0.4 < regulated_fraction < 0.6
    
    def test_suppression_factor(self):
        """Test that suppression factor is applied correctly"""
        suppression = 0.3
        
        data = generate_migration_data(
            n_reaches=10,
            points_per_reach=100,
            regulated_fraction=0.5,
            suppression_factor=suppression,
            random_seed=42
        )
        
        regulated_mask = data['regulation_status'] == 1
        unregulated_mask = data['regulation_status'] == 0
        
        reg_median = np.median(data['migration_rates'][regulated_mask])
        unreg_median = np.median(data['migration_rates'][unregulated_mask])
        
        # Ratio should be close to suppression factor
        ratio = reg_median / unreg_median
        
        # Allow some tolerance due to noise
        assert 0.2 < ratio < 0.5
    
    def test_reproducibility(self):
        """Test that random seed makes results reproducible"""
        data1 = generate_migration_data(
            n_reaches=5,
            points_per_reach=20,
            random_seed=123
        )
        
        data2 = generate_migration_data(
            n_reaches=5,
            points_per_reach=20,
            random_seed=123
        )
        
        # Should be exactly the same
        np.testing.assert_array_equal(
            data1['curvatures'], 
            data2['curvatures']
        )
        np.testing.assert_array_equal(
            data1['migration_rates'], 
            data2['migration_rates']
        )
    
    def test_curvature_migration_relationship(self):
        """Test that curvature and migration have positive correlation"""
        data = generate_migration_data(
            n_reaches=10,
            points_per_reach=100,
            random_seed=42
        )
        
        # Within each regulation status, should have positive correlation
        for status in [0, 1]:
            mask = data['regulation_status'] == status
            corr = np.corrcoef(
                data['curvatures'][mask],
                data['migration_rates'][mask]
            )[0, 1]
            
            # Should be positive (relaxed threshold due to noise)
            assert corr > 0.3
    
    def test_non_negative_rates(self):
        """Test that migration rates are non-negative"""
        data = generate_migration_data(
            n_reaches=5,
            points_per_reach=20,
            random_seed=42
        )
        
        assert np.all(data['migration_rates'] >= 0)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
