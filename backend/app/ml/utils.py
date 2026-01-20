"""ML utilities and helper functions."""

import numpy as np
import pandas as pd
from typing import Tuple, List, Dict, Any
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import train_test_split
import logging

logger = logging.getLogger(__name__)


class DataProcessor:
    """Process and prepare data for ML models."""
    
    @staticmethod
    def handle_missing_values(
        X: np.ndarray,
        strategy: str = "mean"
    ) -> np.ndarray:
        """
        Handle missing values in features.
        
        Args:
            X: Feature matrix
            strategy: Strategy to use ('mean', 'median', 'drop')
            
        Returns:
            Processed feature matrix
        """
        X = np.array(X, dtype=float)
        
        if strategy == "mean":
            col_means = np.nanmean(X, axis=0)
            for i in range(X.shape[1]):
                X[np.isnan(X[:, i]), i] = col_means[i]
        
        elif strategy == "median":
            col_medians = np.nanmedian(X, axis=0)
            for i in range(X.shape[1]):
                X[np.isnan(X[:, i]), i] = col_medians[i]
        
        elif strategy == "drop":
            X = X[~np.isnan(X).any(axis=1)]
        
        return X
    
    @staticmethod
    def remove_outliers(
        X: np.ndarray,
        percentile: float = 0.95
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Remove outliers using percentile method.
        
        Args:
            X: Feature matrix
            percentile: Percentile threshold (0-1)
            
        Returns:
            Clean data and indices of removed rows
        """
        if len(X) == 0:
            return X, np.array([])
        
        X = np.array(X, dtype=float)
        lower = np.nanpercentile(X, (1 - percentile) * 100, axis=0)
        upper = np.nanpercentile(X, percentile * 100, axis=0)
        
        mask = np.all((X >= lower) & (X <= upper), axis=1)
        removed_indices = np.where(~mask)[0]
        
        return X[mask], removed_indices
    
    @staticmethod
    def normalize_features(
        X_train: np.ndarray,
        X_test: Optional[np.ndarray] = None,
        method: str = "standard"
    ) -> Tuple[np.ndarray, Optional[np.ndarray], Any]:
        """
        Normalize features.
        
        Args:
            X_train: Training features
            X_test: Test features (optional)
            method: 'standard' or 'minmax'
            
        Returns:
            Normalized train/test data and scaler
        """
        if method == "standard":
            scaler = StandardScaler()
        else:
            scaler = MinMaxScaler()
        
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test) if X_test is not None else None
        
        return X_train_scaled, X_test_scaled, scaler
    
    @staticmethod
    def split_data(
        X: np.ndarray,
        y: np.ndarray,
        test_size: float = 0.2,
        random_state: int = 42,
        stratify: bool = True
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Split data into train/test sets.
        
        Args:
            X: Features
            y: Labels
            test_size: Test set ratio
            random_state: Random seed
            stratify: Stratify by class
            
        Returns:
            X_train, X_test, y_train, y_test
        """
        stratify_arg = y if stratify else None
        return train_test_split(
            X, y,
            test_size=test_size,
            random_state=random_state,
            stratify=stratify_arg
        )


class FeatureScaler:
    """Scale features for different models."""
    
    def __init__(self):
        self.scaler = None
        self.feature_names = []
        self.feature_stats = {}
    
    def fit(self, X: pd.DataFrame, features: List[str]) -> None:
        """
        Fit scaler on data.
        
        Args:
            X: Feature data
            features: Feature names
        """
        self.feature_names = features
        self.scaler = StandardScaler()
        self.scaler.fit(X[features])
        
        # Store statistics
        for i, name in enumerate(features):
            self.feature_stats[name] = {
                "mean": self.scaler.mean_[i],
                "std": self.scaler.scale_[i]
            }
    
    def transform(self, X: pd.DataFrame) -> np.ndarray:
        """Transform features."""
        return self.scaler.transform(X[self.feature_names])
    
    def inverse_transform(self, X_scaled: np.ndarray) -> np.ndarray:
        """Inverse transform scaled features."""
        return self.scaler.inverse_transform(X_scaled)


class ModelMetrics:
    """Calculate model evaluation metrics."""
    
    @staticmethod
    def calculate_metrics(y_true: np.ndarray, y_pred: np.ndarray, y_proba: Optional[np.ndarray] = None) -> Dict[str, float]:
        """
        Calculate comprehensive metrics.
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            y_proba: Prediction probabilities (optional)
            
        Returns:
            Dictionary of metrics
        """
        from sklearn.metrics import (
            accuracy_score, precision_score, recall_score, f1_score,
            roc_auc_score, confusion_matrix, classification_report
        )
        
        metrics = {
            "accuracy": float(accuracy_score(y_true, y_pred)),
            "precision": float(precision_score(y_true, y_pred, average="weighted", zero_division=0)),
            "recall": float(recall_score(y_true, y_pred, average="weighted", zero_division=0)),
            "f1_score": float(f1_score(y_true, y_pred, average="weighted", zero_division=0)),
        }
        
        # ROC AUC for binary/multiclass
        if len(np.unique(y_true)) > 1:
            try:
                if len(np.unique(y_true)) == 2:
                    metrics["roc_auc"] = float(roc_auc_score(y_true, y_proba[:, 1] if y_proba is not None else y_pred))
                else:
                    metrics["roc_auc"] = float(roc_auc_score(y_true, y_proba, multi_class="ovr") if y_proba is not None else np.nan)
            except:
                metrics["roc_auc"] = np.nan
        
        # Confusion matrix
        cm = confusion_matrix(y_true, y_pred)
        metrics["confusion_matrix"] = cm.tolist()
        
        return metrics
    
    @staticmethod
    def get_feature_importance(model: Any) -> Dict[str, float]:
        """
        Extract feature importance from model.
        
        Args:
            model: Trained model
            
        Returns:
            Feature importance dictionary
        """
        importance = {}
        
        if hasattr(model, "feature_importances_"):
            importance_values = model.feature_importances_
        elif hasattr(model, "coef_"):
            importance_values = np.abs(model.coef_[0]) if len(model.coef_.shape) > 1 else np.abs(model.coef_)
        else:
            return importance
        
        # Normalize to sum to 1
        if np.sum(importance_values) > 0:
            importance_values = importance_values / np.sum(importance_values)
        
        return importance_values.tolist()


from typing import Optional
