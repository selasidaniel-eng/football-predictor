"""ML module initialization and utilities."""

from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class MLConfig:
    """Configuration for ML models."""
    
    # Model hyperparameters
    LOGISTIC_REGRESSION = {
        "max_iter": 1000,
        "random_state": 42,
        "C": 1.0,
    }
    
    RANDOM_FOREST = {
        "n_estimators": 100,
        "max_depth": 15,
        "min_samples_split": 10,
        "min_samples_leaf": 5,
        "random_state": 42,
    }
    
    GRADIENT_BOOSTING = {
        "n_estimators": 100,
        "learning_rate": 0.1,
        "max_depth": 5,
        "random_state": 42,
    }
    
    # Training configuration
    TEST_SIZE = 0.2
    VALIDATION_SIZE = 0.1
    RANDOM_STATE = 42
    
    # Feature engineering
    LOOKBACK_MATCHES = 10  # Use last N matches for form
    MIN_MATCHES_FOR_PREDICTION = 3  # Minimum matches to make prediction
    
    # Model evaluation
    THRESHOLD_HOME = 0.55  # Decision threshold for home win prediction
    THRESHOLD_DRAW = 0.35  # Decision threshold for draw prediction


class ModelMetrics:
    """Container for model performance metrics."""
    
    def __init__(self):
        """Initialize metrics."""
        self.accuracy: float = 0.0
        self.precision: float = 0.0
        self.recall: float = 0.0
        self.f1_score: float = 0.0
        self.auc_score: float = 0.0
        self.log_loss: float = 0.0
        self.confusion_matrix: List[List[int]] = []
        self.classification_report: Dict[str, Any] = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            "accuracy": round(self.accuracy, 4),
            "precision": round(self.precision, 4),
            "recall": round(self.recall, 4),
            "f1_score": round(self.f1_score, 4),
            "auc_score": round(self.auc_score, 4),
            "log_loss": round(self.log_loss, 4),
            "confusion_matrix": self.confusion_matrix,
            "classification_report": self.classification_report
        }


class FeatureSet:
    """Container for feature data."""
    
    def __init__(self, name: str):
        """Initialize feature set."""
        self.name = name
        self.features: List[str] = []
        self.data: Dict[str, Any] = {}
        self.scaler_params: Dict[str, Any] = {}
    
    def add_feature(self, feature_name: str, values: List[float]) -> None:
        """Add a feature to the set."""
        self.features.append(feature_name)
        self.data[feature_name] = values
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "features": self.features,
            "feature_count": len(self.features),
            "sample_count": len(next(iter(self.data.values()))) if self.data else 0
        }
