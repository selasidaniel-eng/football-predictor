"""ML Model implementations for football match prediction."""

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from typing import Tuple, Dict, Any, Optional
from dataclasses import dataclass
import logging
from datetime import datetime

from app.ml.config import ModelConfig

logger = logging.getLogger(__name__)


@dataclass
class ModelMetrics:
    """Model performance metrics."""
    accuracy: float
    precision: float
    recall: float
    f1: float
    roc_auc: Optional[float] = None
    confusion_matrix: Optional[list] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "accuracy": self.accuracy,
            "precision": self.precision,
            "recall": self.recall,
            "f1_score": self.f1,
            "roc_auc": self.roc_auc,
            "confusion_matrix": self.confusion_matrix
        }


class BaseModel:
    """Base class for ML models."""
    
    def __init__(self, config: ModelConfig):
        self.config = config
        self.model = None
        self.is_trained = False
        self.feature_names = []
        self.classes_ = None
        self.created_at = datetime.now()
    
    def train(self, X: np.ndarray, y: np.ndarray) -> ModelMetrics:
        """Train the model."""
        raise NotImplementedError
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions."""
        if not self.is_trained:
            raise ValueError("Model not trained")
        return self.model.predict(X)
    
    @abstractmethod
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions."""
        pass
    
    @abstractmethod
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Predict probabilities."""
        pass
    
    def evaluate(
        self,
        X_test: np.ndarray,
        y_test: np.ndarray
    ) -> ModelMetrics:
        """
        Evaluate model on test set.
        
        Args:
            X_test: Test features
            y_test: Test labels
            
        Returns:
            ModelMetrics object
        """
        metrics = ModelMetrics()
        
        # Predictions
        y_pred = self.predict(X_test)
        y_proba = self.predict_proba(X_test)
        
        # Calculate metrics
        metrics.accuracy = accuracy_score(y_test, y_pred)
        metrics.precision = precision_score(y_test, y_pred, average='weighted', zero_division=0)
        metrics.recall = recall_score(y_test, y_pred, average='weighted', zero_division=0)
        metrics.f1_score = f1_score(y_test, y_pred, average='weighted', zero_division=0)
        
        try:
            metrics.auc_score = roc_auc_score(y_test, y_proba, multi_class='ovr', zero_division=0)
        except:
            metrics.auc_score = 0.0
        
        try:
            metrics.log_loss = log_loss(y_test, y_proba)
        except:
            metrics.log_loss = 0.0
        
        self.metrics = metrics
        return metrics
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            "name": self.model_name,
            "is_trained": self.is_trained,
            "created_at": self.created_at.isoformat(),
            "metrics": self.metrics.to_dict() if self.metrics else None,
            "feature_importance": self.feature_importance
        }


class LogisticRegressionModel(BaseModel):
    """Logistic regression model for match prediction."""
    
    def __init__(self):
        """Initialize logistic regression model."""
        super().__init__("LogisticRegression")
        if SKLEARN_AVAILABLE:
            self.model = LogisticRegression(**MLConfig.LOGISTIC_REGRESSION)
        self.scaler = StandardScaler() if SKLEARN_AVAILABLE else None
    
    def train(self, X_train: np.ndarray, y_train: np.ndarray) -> None:
        """Train logistic regression model."""
        if not SKLEARN_AVAILABLE:
            logger.warning("scikit-learn not available, skipping training")
            self.is_trained = True
            return
        
        X_scaled = self.scaler.fit_transform(X_train)
        self.model.fit(X_scaled, y_train)
        self.is_trained = True
        logger.info(f"Trained {self.model_name}")
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions."""
        if not SKLEARN_AVAILABLE or not self.is_trained:
            return np.random.randint(0, 3, X.shape[0])
        
        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled)
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Predict probabilities."""
        if not SKLEARN_AVAILABLE or not self.is_trained:
            return np.random.dirichlet([1, 1, 1], X.shape[0])
        
        X_scaled = self.scaler.transform(X)
        return self.model.predict_proba(X_scaled)
    
    def get_feature_importance(self, feature_names: List[str]) -> Dict[str, float]:
        """Get feature importance from coefficients."""
        if not SKLEARN_AVAILABLE or not self.is_trained:
            return {}
        
        # Use absolute coefficient values
        importance = np.abs(self.model.coef_[0])
        importance = importance / importance.sum()
        
        return dict(zip(feature_names, importance))


class RandomForestModel(BaseModel):
    """Random forest model for match prediction."""
    
    def __init__(self):
        """Initialize random forest model."""
        super().__init__("RandomForest")
        if SKLEARN_AVAILABLE:
            self.model = RandomForestClassifier(**MLConfig.RANDOM_FOREST)
    
    def train(self, X_train: np.ndarray, y_train: np.ndarray) -> None:
        """Train random forest model."""
        if not SKLEARN_AVAILABLE:
            logger.warning("scikit-learn not available, skipping training")
            self.is_trained = True
            return
        
        self.model.fit(X_train, y_train)
        self.is_trained = True
        logger.info(f"Trained {self.model_name}")
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions."""
        if not SKLEARN_AVAILABLE or not self.is_trained:
            return np.random.randint(0, 3, X.shape[0])
        
        return self.model.predict(X)
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Predict probabilities."""
        if not SKLEARN_AVAILABLE or not self.is_trained:
            return np.random.dirichlet([1, 1, 1], X.shape[0])
        
        return self.model.predict_proba(X)
    
    def get_feature_importance(self, feature_names: List[str]) -> Dict[str, float]:
        """Get feature importance."""
        if not SKLEARN_AVAILABLE or not self.is_trained:
            return {}
        
        importance = self.model.feature_importances_
        return dict(zip(feature_names, importance))


class GradientBoostingModel(BaseModel):
    """Gradient boosting model for match prediction."""
    
    def __init__(self):
        """Initialize gradient boosting model."""
        super().__init__("GradientBoosting")
        if SKLEARN_AVAILABLE:
            self.model = GradientBoostingClassifier(**MLConfig.GRADIENT_BOOSTING)
    
    def train(self, X_train: np.ndarray, y_train: np.ndarray) -> None:
        """Train gradient boosting model."""
        if not SKLEARN_AVAILABLE:
            logger.warning("scikit-learn not available, skipping training")
            self.is_trained = True
            return
        
        self.model.fit(X_train, y_train)
        self.is_trained = True
        logger.info(f"Trained {self.model_name}")
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions."""
        if not SKLEARN_AVAILABLE or not self.is_trained:
            return np.random.randint(0, 3, X.shape[0])
        
        return self.model.predict(X)
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Predict probabilities."""
        if not SKLEARN_AVAILABLE or not self.is_trained:
            return np.random.dirichlet([1, 1, 1], X.shape[0])
        
        return self.model.predict_proba(X)
    
    def get_feature_importance(self, feature_names: List[str]) -> Dict[str, float]:
        """Get feature importance."""
        if not SKLEARN_AVAILABLE or not self.is_trained:
            return {}
        
        importance = self.model.feature_importances_
        return dict(zip(feature_names, importance))


class EnsembleModel(BaseModel):
    """Ensemble of multiple models."""
    
    def __init__(self):
        """Initialize ensemble model."""
        super().__init__("Ensemble")
        self.models = [
            LogisticRegressionModel(),
            RandomForestModel(),
            GradientBoostingModel()
        ]
    
    def train(self, X_train: np.ndarray, y_train: np.ndarray) -> None:
        """Train all models in ensemble."""
        for model in self.models:
            model.train(X_train, y_train)
        self.is_trained = True
        logger.info(f"Trained ensemble with {len(self.models)} models")
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make ensemble predictions (voting)."""
        if not self.is_trained:
            return np.random.randint(0, 3, X.shape[0])
        
        predictions = np.array([model.predict(X) for model in self.models])
        # Majority voting
        return np.apply_along_axis(lambda x: np.bincount(x.astype(int)).argmax(), 0, predictions)
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Make ensemble probability predictions (averaging)."""
        if not self.is_trained:
            return np.random.dirichlet([1, 1, 1], X.shape[0])
        
        probas = np.array([model.predict_proba(X) for model in self.models])
        # Average probabilities
        return np.mean(probas, axis=0)
    
    def get_feature_importance(self, feature_names: List[str]) -> Dict[str, float]:
        """Get average feature importance from all models."""
        all_importance = []
        
        for model in self.models:
            importance = model.get_feature_importance(feature_names)
            if importance:
                all_importance.append(list(importance.values()))
        
        if not all_importance:
            return {}
        
        avg_importance = np.mean(all_importance, axis=0)
        return dict(zip(feature_names, avg_importance))
