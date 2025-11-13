"""
Unit tests for meander_analysis module
"""

import numpy as np
import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.meander_analysis import (
    calculate_migration_rate,
    calculate_curvature,
    analyze_migration_template,
    compare_regulated_unregulated
)


class TestMigrationRate:
    """Tests for calculate_migration_rate function"""
    
    def test_basic_migration_rate(self):
        """Test basic migration rate calculation"""
        # Create two position arrays
        positions_t1 = np.array([[0, 0], [1, 0], [2, 0]])
        positions_t2 = np.array([[0, 1], [1, 1], [2, 1]])
        time_delta = 10.0
        
        rates = calculate_migration_rate(positions_t1, positions_t2, time_delta)
        
        # All points moved 1 unit in 10 years = 0.1 m/yr
        expected = np.array([0.1, 0.1, 0.1])
        np.testing.assert_array_almost_equal(rates, expected)
    
    def test_zero_migration(self):
        """Test with no migration"""
        positions = np.array([[0, 0], [1, 0], [2, 0]])
        rates = calculate_migration_rate(positions, positions, 1.0)
        
        expected = np.zeros(3)
        np.testing.assert_array_almost_equal(rates, expected)
    
    def test_shape_mismatch_raises_error(self):
        """Test that mismatched shapes raise ValueError"""
        pos1 = np.array([[0, 0], [1, 0]])
        pos2 = np.array([[0, 0]])
        
        with pytest.raises(ValueError, match="same shape"):
            calculate_migration_rate(pos1, pos2, 1.0)
    
    def test_negative_time_raises_error(self):
        """Test that negative time delta raises ValueError"""
        positions = np.array([[0, 0], [1, 0]])
        
        with pytest.raises(ValueError, match="positive"):
            calculate_migration_rate(positions, positions, -1.0)


class TestCurvature:
    """Tests for calculate_curvature function"""
    
    def test_straight_line_curvature(self):
        """Test that straight line has zero curvature"""
        # Perfectly straight line
        positions = np.array([[i, 0] for i in range(20)])
        curvatures = calculate_curvature(positions, window_size=5)
        
        # Should be close to zero
        assert np.max(np.abs(curvatures)) < 0.01
    
    def test_circle_curvature(self):
        """Test curvature of circular arc"""
        # Create points on a circle of radius R
        R = 10.0
        theta = np.linspace(0, np.pi/2, 20)
        positions = np.column_stack([R * np.cos(theta), R * np.sin(theta)])
        
        curvatures = calculate_curvature(positions, window_size=5)
        
        # Curvature of circle = 1/R
        expected_curvature = 1.0 / R
        
        # Check middle values (edges may be less accurate)
        middle_curvatures = curvatures[5:15]
        assert np.abs(np.mean(middle_curvatures) - expected_curvature) < 0.05
    
    def test_small_array_raises_error(self):
        """Test that array smaller than window size raises error"""
        positions = np.array([[0, 0], [1, 1]])
        
        with pytest.raises(ValueError, match="too small"):
            calculate_curvature(positions, window_size=5)


class TestMigrationTemplate:
    """Tests for analyze_migration_template function"""
    
    def test_basic_template_analysis(self):
        """Test basic template analysis"""
        # Create synthetic data with linear relationship
        curvatures = np.linspace(0, 1, 100)
        migration_rates = 2.0 * curvatures + np.random.normal(0, 0.1, 100)
        
        bins, means, stds = analyze_migration_template(
            curvatures, migration_rates, bin_count=10
        )
        
        assert len(bins) == 10
        assert len(means) == 10
        assert len(stds) == 10
        
        # Check that means increase with curvature
        assert means[-1] > means[0]
    
    def test_mismatched_lengths_raises_error(self):
        """Test that mismatched array lengths raise error"""
        curvatures = np.array([1, 2, 3])
        rates = np.array([1, 2])
        
        with pytest.raises(ValueError, match="same length"):
            analyze_migration_template(curvatures, rates)


class TestCompareRegulatedUnregulated:
    """Tests for compare_regulated_unregulated function"""
    
    def test_comparison_with_invariant_template(self):
        """Test comparison when templates are invariant"""
        # Create data with same template but different magnitudes
        # Use same curvature range for both groups
        curvatures_unreg = np.linspace(0, 1, 100)
        curvatures_reg = np.linspace(0, 1, 100)
        
        # Unregulated: rates = 5 * curvature
        unreg_rates = 5.0 * curvatures_unreg + np.random.normal(0, 0.1, 100)
        
        # Regulated: rates = 2 * curvature (suppressed but same template)
        reg_rates = 2.0 * curvatures_reg + np.random.normal(0, 0.1, 100)
        
        comparison = compare_regulated_unregulated(
            curvatures_reg, reg_rates,
            curvatures_unreg, unreg_rates,
            bin_count=10
        )
        
        # Template correlation should be high
        assert comparison['template_correlation'] > 0.8
        
        # Suppression factor should be around 2/5 = 0.4
        assert 0.3 < comparison['rate_suppression_factor'] < 0.5
    
    def test_comparison_structure(self):
        """Test that comparison returns correct structure"""
        curvatures = np.random.rand(100)
        rates1 = np.random.rand(100)
        rates2 = np.random.rand(100)
        
        comparison = compare_regulated_unregulated(
            curvatures, rates1,
            curvatures, rates2,
            bin_count=5
        )
        
        # Check all expected keys are present
        expected_keys = [
            'regulated_bins', 'regulated_mean_rates', 'regulated_std_rates',
            'unregulated_bins', 'unregulated_mean_rates', 'unregulated_std_rates',
            'template_correlation', 'rate_suppression_factor',
            'regulated_template_normalized', 'unregulated_template_normalized'
        ]
        
        for key in expected_keys:
            assert key in comparison


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
