"""
Unit tests for LME model module
"""

import numpy as np
import pandas as pd
import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.lme_model import (
    prepare_lme_data,
    fit_lme_model,
    interpret_results,
    calculate_geomorphic_dormancy_index
)


class TestPrepareLMEData:
    """Tests for prepare_lme_data function"""
    
    def test_basic_data_preparation(self):
        """Test basic data preparation"""
        n = 100
        curvatures = np.random.rand(n)
        rates = np.random.rand(n)
        regulation = np.random.randint(0, 2, n)
        
        df = prepare_lme_data(curvatures, rates, regulation)
        
        assert len(df) <= n  # May be less if NaN values removed
        assert 'curvature' in df.columns
        assert 'migration_rate' in df.columns
        assert 'regulated' in df.columns
        assert 'reach_id' in df.columns
        assert 'curvature_x_regulated' in df.columns
    
    def test_interaction_term(self):
        """Test that interaction term is calculated correctly"""
        curvatures = np.array([1.0, 2.0, 3.0])
        rates = np.array([0.5, 1.0, 1.5])
        regulation = np.array([0, 1, 1])
        
        df = prepare_lme_data(curvatures, rates, regulation)
        
        expected_interaction = curvatures * regulation
        np.testing.assert_array_almost_equal(
            df['curvature_x_regulated'].values, 
            expected_interaction
        )
    
    def test_with_reach_ids(self):
        """Test with custom reach IDs"""
        n = 50
        curvatures = np.random.rand(n)
        rates = np.random.rand(n)
        regulation = np.random.randint(0, 2, n)
        reach_ids = np.repeat([1, 2, 3, 4, 5], 10)
        
        df = prepare_lme_data(curvatures, rates, regulation, reach_ids)
        
        assert 'reach_id' in df.columns
        assert set(df['reach_id'].unique()).issubset({1, 2, 3, 4, 5})


class TestFitLMEModel:
    """Tests for fit_lme_model function"""
    
    def test_model_fitting(self):
        """Test that model can be fitted"""
        # Create realistic data
        n = 200
        curvatures = np.random.lognormal(mean=-3, sigma=0.8, size=n)
        regulation = np.random.randint(0, 2, n)
        
        # Create migration rates with known relationships
        rates = 5.0 * curvatures * (1 - 0.7 * regulation) + np.random.normal(0, 0.5, n)
        rates = np.maximum(rates, 0)
        
        reach_ids = np.repeat(range(10), 20)
        
        df = prepare_lme_data(curvatures, rates, regulation, reach_ids)
        
        result, summary_df = fit_lme_model(df)
        
        assert result is not None
        assert isinstance(summary_df, pd.DataFrame)
        assert 'coefficient' in summary_df.columns
        assert 'p_value' in summary_df.columns
    
    def test_summary_structure(self):
        """Test that summary has correct structure"""
        n = 100
        df = prepare_lme_data(
            np.random.rand(n),
            np.random.rand(n),
            np.random.randint(0, 2, n)
        )
        
        result, summary_df = fit_lme_model(df)
        
        expected_columns = ['coefficient', 'std_error', 'z_value', 'p_value']
        for col in expected_columns:
            assert col in summary_df.columns


class TestInterpretResults:
    """Tests for interpret_results function"""
    
    def test_interpretation_structure(self):
        """Test that interpretation has correct structure"""
        # Create mock summary DataFrame
        summary_df = pd.DataFrame({
            'coefficient': [1.0, -0.5, 0.1],
            'std_error': [0.1, 0.1, 0.1],
            'z_value': [10.0, -5.0, 1.0],
            'p_value': [0.001, 0.001, 0.3]
        }, index=['curvature', 'regulated', 'curvature_x_regulated'])
        
        interpretation = interpret_results(summary_df)
        
        assert 'rates_suppressed' in interpretation
        assert 'template_invariant' in interpretation
        assert 'curvature_predicts_migration' in interpretation
    
    def test_suppression_detection(self):
        """Test detection of rate suppression"""
        summary_df = pd.DataFrame({
            'coefficient': [-0.8],
            'std_error': [0.1],
            'z_value': [-8.0],
            'p_value': [0.001]
        }, index=['regulated'])
        
        interpretation = interpret_results(summary_df)
        
        # Should detect suppression (negative coefficient, significant)
        assert interpretation['rates_suppressed'] == True
    
    def test_invariance_detection(self):
        """Test detection of template invariance"""
        summary_df = pd.DataFrame({
            'coefficient': [0.05],
            'std_error': [0.1],
            'z_value': [0.5],
            'p_value': [0.6]
        }, index=['curvature_x_regulated'])
        
        interpretation = interpret_results(summary_df)
        
        # Should detect invariance (non-significant interaction)
        assert interpretation['template_invariant'] == True


class TestGeomorphicDormancyIndex:
    """Tests for calculate_geomorphic_dormancy_index function"""
    
    def test_basic_calculation(self):
        """Test basic dormancy index calculation"""
        regulated = np.array([1.0, 1.5, 2.0])
        unregulated = np.array([4.0, 5.0, 6.0])
        
        index = calculate_geomorphic_dormancy_index(regulated, unregulated)
        
        # Median of regulated is 1.5, unregulated is 5.0
        expected = 1.5 / 5.0
        assert abs(index - expected) < 0.01
    
    def test_no_suppression(self):
        """Test when there is no suppression"""
        rates = np.array([1.0, 2.0, 3.0])
        
        index = calculate_geomorphic_dormancy_index(rates, rates)
        
        # Should be close to 1.0 (no effect)
        assert abs(index - 1.0) < 0.01
    
    def test_complete_dormancy(self):
        """Test when there is complete dormancy"""
        regulated = np.array([0.0, 0.0, 0.0])
        unregulated = np.array([1.0, 2.0, 3.0])
        
        index = calculate_geomorphic_dormancy_index(regulated, unregulated)
        
        # Should be close to 0 (complete dormancy)
        assert index == 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
