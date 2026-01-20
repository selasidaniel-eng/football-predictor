"""Tests for ML module."""

import pytest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

from app.ml.features import FeatureEngineer
from app.ml.config import FeatureConfig, ModelConfig
from app.ml.utils import DataProcessor, ModelMetrics


class TestFeatureEngineer:
    """Test feature engineering."""
    
    def test_init_with_default_config(self):
        """Test initialization with default config."""
        engineer = FeatureEngineer()
        assert engineer.config is not None
        assert engineer.feature_names == []
    
    def test_init_with_custom_config(self):
        """Test initialization with custom config."""
        config = FeatureConfig(form_window=10)
        engineer = FeatureEngineer(config)
        assert engineer.config.form_window == 10
    
    @pytest.mark.asyncio
    async def test_extract_features_empty_matches(self):
        """Test extraction with empty matches list."""
        engineer = FeatureEngineer()
        db = AsyncMock()
        
        X, names = await engineer.extract_features(db, [])
        
        assert len(X) == 0
        assert len(names) == 0


class TestDataProcessor:
    """Test data processing utilities."""
    
    def test_handle_missing_values_mean(self):
        """Test missing value handling with mean strategy."""
        X = np.array([
            [1.0, 2.0, 3.0],
            [4.0, np.nan, 6.0],
            [7.0, 8.0, np.nan]
        ])
        
        X_clean = DataProcessor.handle_missing_values(X, strategy="mean")
        
        assert not np.isnan(X_clean).any()
        assert X_clean.shape == X.shape
    
    def test_handle_missing_values_median(self):
        """Test missing value handling with median strategy."""
        X = np.array([
            [1.0, 2.0, 3.0],
            [4.0, np.nan, 6.0],
            [7.0, 8.0, np.nan]
        ])
        
        X_clean = DataProcessor.handle_missing_values(X, strategy="median")
        
        assert not np.isnan(X_clean).any()
        assert X_clean.shape == X.shape
    
    def test_remove_outliers(self):
        """Test outlier removal."""
        X = np.array([
            [1.0, 2.0],
            [2.0, 3.0],
            [3.0, 4.0],
            [100.0, 200.0],  # Outlier
            [4.0, 5.0]
        ])
        
        X_clean, removed = DataProcessor.remove_outliers(X, percentile=0.95)
        
        assert len(X_clean) < len(X)
        assert len(removed) > 0
    
    def test_normalize_features_standard(self):
        """Test feature normalization with standard scaling."""
        X_train = np.array([[1, 2], [3, 4], [5, 6]])
        X_test = np.array([[2, 3], [4, 5]])
        
        X_train_scaled, X_test_scaled, scaler = DataProcessor.normalize_features(
            X_train, X_test, method="standard"
        )
        
        # Check shapes
        assert X_train_scaled.shape == X_train.shape
        assert X_test_scaled.shape == X_test.shape
        
        # Check scaling
        assert np.mean(X_train_scaled) < 0.1  # Close to 0
        assert np.std(X_train_scaled) < 1.1   # Close to 1
    
    def test_split_data(self):
        """Test train/test split."""
        X = np.random.rand(100, 5)
        y = np.random.randint(0, 3, 100)
        
        X_train, X_test, y_train, y_test = DataProcessor.split_data(
            X, y, test_size=0.2
        )
        
        assert len(X_train) == 80
        assert len(X_test) == 20
        assert len(y_train) == 80
        assert len(y_test) == 20


class TestModelMetrics:
    """Test model metrics calculation."""
    
    def test_calculate_metrics_binary(self):
        """Test metrics for binary classification."""
        y_true = np.array([0, 0, 1, 1])
        y_pred = np.array([0, 1, 0, 1])
        y_proba = np.array([[1, 0], [0.6, 0.4], [0.3, 0.7], [0, 1]])
        
        metrics = ModelMetrics.calculate_metrics(y_true, y_pred, y_proba)
        
        assert "accuracy" in metrics
        assert "precision" in metrics
        assert "recall" in metrics
        assert "f1_score" in metrics
        assert "confusion_matrix" in metrics
        
        # Accuracy should be 0.5 (2 correct, 2 incorrect)
        assert metrics["accuracy"] == 0.5
    
    def test_calculate_metrics_multiclass(self):
        """Test metrics for multiclass classification."""
        y_true = np.array([0, 1, 2, 0, 1, 2])
        y_pred = np.array([0, 1, 2, 0, 1, 1])
        
        metrics = ModelMetrics.calculate_metrics(y_true, y_pred)
        
        assert metrics["accuracy"] == 5/6
        assert all(k in metrics for k in ["precision", "recall", "f1_score"])
    
    def test_get_feature_importance_tree(self):
        """Test feature importance extraction from tree models."""
        from sklearn.ensemble import RandomForestClassifier
        
        X = np.array([[1, 2], [3, 4], [5, 6], [7, 8]])
        y = np.array([0, 1, 0, 1])
        
        model = RandomForestClassifier(random_state=42)
        model.fit(X, y)
        
        importance = ModelMetrics.get_feature_importance(model)
        
        assert isinstance(importance, list)
        assert len(importance) == 2
        assert all(0 <= x <= 1 for x in importance)
        assert abs(sum(importance) - 1.0) < 0.01  # Sum should be ~1


class TestModelConfig:
    """Test model configuration."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = ModelConfig.default()
        
        assert config.logistic_regression_C == 1.0
        assert config.random_forest_n_estimators == 100
        assert config.test_split_ratio == 0.2
        assert config.min_confidence == 0.55
    
    def test_custom_config(self):
        """Test custom configuration."""
        config = ModelConfig(
            logistic_regression_C=0.5,
            random_forest_n_estimators=200
        )
        
        assert config.logistic_regression_C == 0.5
        assert config.random_forest_n_estimators == 200


class TestFeatureConfig:
    """Test feature configuration."""
    
    def test_default_feature_config(self):
        """Test default feature configuration."""
        config = FeatureConfig.default()
        
        assert config.form_window == 5
        assert config.injury_window == 14
        assert config.normalize is True
        assert config.standardize is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
