"""Configuration for ML models."""

from dataclasses import dataclass
from enum import Enum


class ModelType(str, Enum):
    """Available model types."""
    LOGISTIC_REGRESSION = "logistic_regression"
    RANDOM_FOREST = "random_forest"
    GRADIENT_BOOSTING = "gradient_boosting"
    ENSEMBLE = "ensemble"


class PredictionType(str, Enum):
    """Types of predictions."""
    MATCH_WINNER = "match_winner"  # 0: Home Win, 1: Draw, 2: Away Win
    OVER_UNDER = "over_under"  # 0: Under, 1: Over
    BOTH_SCORE = "both_score"  # 0: No, 1: Yes


@dataclass
class ModelConfig:
    """Configuration for ML models."""
    
    # Model parameters
    logistic_regression_C: float = 1.0
    logistic_regression_max_iter: int = 1000
    
    random_forest_n_estimators: int = 100
    random_forest_max_depth: int = 15
    random_forest_min_samples_split: int = 10
    random_forest_min_samples_leaf: int = 4
    random_forest_random_state: int = 42
    
    gradient_boosting_n_estimators: int = 100
    gradient_boosting_learning_rate: float = 0.1
    gradient_boosting_max_depth: int = 5
    gradient_boosting_random_state: int = 42
    
    # Training parameters
    test_split_ratio: float = 0.2
    random_state: int = 42
    
    # Feature parameters
    missing_value_strategy: str = "mean"  # mean, median, drop
    outlier_percentile: float = 0.95
    
    # Prediction parameters
    min_confidence: float = 0.55
    confidence_calibration: bool = True
    
    @classmethod
    def default(cls):
        """Get default configuration."""
        return cls()


@dataclass
class FeatureConfig:
    """Configuration for feature engineering."""
    
    # Window sizes for rolling statistics
    form_window: int = 5  # Last N matches
    injury_window: int = 14  # Days
    head_to_head_window: int = 20  # Matches
    
    # Feature selection
    min_feature_importance: float = 0.001
    max_features: int = 50
    
    # Normalization
    normalize: bool = True
    standardize: bool = True
    
    @classmethod
    def default(cls):
        """Get default configuration."""
        return cls()
