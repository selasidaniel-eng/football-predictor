"""Training engine and prediction generator."""

from typing import Dict, List, Tuple, Any, Optional
import logging
import numpy as np
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import Match, Prediction
from app.ml.feature_engineer import FeatureEngineer
from app.ml.models import BaseModel, EnsembleModel, ModelMetrics
from app.ml import MLConfig

logger = logging.getLogger(__name__)


class TrainingEngine:
    """Engine for training ML models."""
    
    def __init__(self, feature_engineer: Optional[FeatureEngineer] = None):
        """
        Initialize training engine.
        
        Args:
            feature_engineer: Feature engineer instance
        """
        self.feature_engineer = feature_engineer or FeatureEngineer()
        self.model: Optional[BaseModel] = None
        self.feature_names: List[str] = self.feature_engineer.get_feature_names()
        self.training_history: List[Dict[str, Any]] = []
    
    async def prepare_training_data(
        self,
        session: AsyncSession,
        league_id: Optional[int] = None
    ) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """
        Prepare training data from historical matches.
        
        Args:
            session: Database session
            league_id: Optional league filter
            
        Returns:
            Tuple of (X_train, y_train, feature_names)
        """
        logger.info("Preparing training data...")
        
        # Get finished matches
        query = select(Match).filter(Match.status == "FINISHED")
        if league_id:
            query = query.filter(Match.league_id == league_id)
        
        result = await session.execute(query.order_by(Match.match_date.desc()).limit(1000))
        matches = result.scalars().all()
        
        X_list = []
        y_list = []
        
        for match in matches:
            if match.home_goals is None or match.away_goals is None:
                continue
            
            try:
                # Extract features
                features = await self.feature_engineer.extract_features(session, match)
                X_list.append([features.get(fname, 0.0) for fname in self.feature_names])
                
                # Determine label (0: away win, 1: draw, 2: home win)
                if match.home_goals > match.away_goals:
                    y_list.append(2)
                elif match.home_goals < match.away_goals:
                    y_list.append(0)
                else:
                    y_list.append(1)
            except Exception as e:
                logger.warning(f"Error preparing features for match {match.id}: {e}")
                continue
        
        X = np.array(X_list, dtype=np.float32)
        y = np.array(y_list, dtype=np.int32)
        
        logger.info(f"Prepared {len(X)} samples with {len(self.feature_names)} features")
        
        return X, y, self.feature_names
    
    def train(
        self,
        X: np.ndarray,
        y: np.ndarray,
        model: Optional[BaseModel] = None,
        test_size: float = 0.2
    ) -> Tuple[BaseModel, ModelMetrics]:
        """
        Train a model on provided data.
        
        Args:
            X: Feature data
            y: Labels
            model: Model to train (uses ensemble if None)
            test_size: Test set proportion
            
        Returns:
            Tuple of (trained_model, metrics)
        """
        if model is None:
            model = EnsembleModel()
        
        # Split data
        split_idx = int(len(X) * (1 - test_size))
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        logger.info(f"Training {model.model_name} with {len(X_train)} samples...")
        
        # Train
        model.train(X_train, y_train)
        
        # Evaluate
        metrics = model.evaluate(X_test, y_test)
        
        # Get feature importance
        model.feature_importance = model.get_feature_importance(self.feature_names)
        
        # Store in history
        self.training_history.append({
            "timestamp": datetime.now().isoformat(),
            "model": model.model_name,
            "samples": len(X_train),
            "metrics": metrics.to_dict()
        })
        
        self.model = model
        
        logger.info(
            f"Training complete. Accuracy: {metrics.accuracy:.4f}, "
            f"F1: {metrics.f1_score:.4f}, AUC: {metrics.auc_score:.4f}"
        )
        
        return model, metrics
    
    def get_top_features(
        self,
        top_n: int = 10
    ) -> List[Tuple[str, float]]:
        """
        Get top N important features.
        
        Args:
            top_n: Number of top features
            
        Returns:
            List of (feature_name, importance) tuples
        """
        if not self.model or not self.model.feature_importance:
            return []
        
        sorted_features = sorted(
            self.model.feature_importance.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_features[:top_n]


class PredictionGenerator:
    """Generator for match predictions using trained models."""
    
    def __init__(self, model: Optional[BaseModel] = None):
        """
        Initialize prediction generator.
        
        Args:
            model: Trained model
        """
        self.model = model
        self.feature_engineer = FeatureEngineer()
        self.prediction_history: List[Dict[str, Any]] = []
    
    async def predict_match(
        self,
        session: AsyncSession,
        match: Match
    ) -> Dict[str, Any]:
        """
        Generate prediction for a match.
        
        Args:
            session: Database session
            match: Match to predict
            
        Returns:
            Prediction data
        """
        if not self.model or not self.model.is_trained:
            logger.warning("Model not trained, using random prediction")
            return self._random_prediction(match)
        
        try:
            # Extract features
            features = await self.feature_engineer.extract_features(session, match)
            feature_names = self.feature_engineer.get_feature_names()
            X = np.array([[features.get(fname, 0.0) for fname in feature_names]])
            
            # Get probabilities
            probas = self.model.predict_proba(X)[0]
            prediction = self.model.predict(X)[0]
            
            # Map to outcomes
            outcome_map = {0: "away_win", 1: "draw", 2: "home_win"}
            predicted_outcome = outcome_map[prediction]
            
            result = {
                "match_id": match.id,
                "predicted_outcome": predicted_outcome,
                "home_win_probability": float(probas[2]),
                "draw_probability": float(probas[1]),
                "away_win_probability": float(probas[0]),
                "confidence": float(max(probas)),
                "model_name": self.model.model_name,
                "timestamp": datetime.now().isoformat()
            }
            
            self.prediction_history.append(result)
            return result
        
        except Exception as e:
            logger.error(f"Error predicting match {match.id}: {e}")
            return self._random_prediction(match)
    
    async def predict_batch(
        self,
        session: AsyncSession,
        matches: List[Match]
    ) -> List[Dict[str, Any]]:
        """
        Generate predictions for multiple matches.
        
        Args:
            session: Database session
            matches: List of matches
            
        Returns:
            List of prediction data
        """
        predictions = []
        for match in matches:
            pred = await self.predict_match(session, match)
            predictions.append(pred)
        
        return predictions
    
    def _random_prediction(self, match: Match) -> Dict[str, Any]:
        """Generate random prediction for testing."""
        probas = np.random.dirichlet([1, 1, 1])
        outcome_map = {0: "away_win", 1: "draw", 2: "home_win"}
        prediction = np.argmax(probas)
        
        return {
            "match_id": match.id,
            "predicted_outcome": outcome_map[prediction],
            "home_win_probability": float(probas[2]),
            "draw_probability": float(probas[1]),
            "away_win_probability": float(probas[0]),
            "confidence": float(max(probas)),
            "model_name": "random",
            "timestamp": datetime.now().isoformat()
        }
    
    async def evaluate_predictions(
        self,
        session: AsyncSession,
        predictions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Evaluate prediction accuracy against actual results.
        
        Args:
            session: Database session
            predictions: List of predictions
            
        Returns:
            Evaluation metrics
        """
        correct = 0
        total = 0
        
        for pred in predictions:
            match_id = pred["match_id"]
            result = await session.execute(select(Match).filter(Match.id == match_id))
            match = result.scalars().first()
            
            if not match or match.home_goals is None:
                continue
            
            # Get actual outcome
            if match.home_goals > match.away_goals:
                actual = "home_win"
            elif match.home_goals < match.away_goals:
                actual = "away_win"
            else:
                actual = "draw"
            
            if pred["predicted_outcome"] == actual:
                correct += 1
            
            total += 1
        
        accuracy = (correct / total * 100) if total > 0 else 0.0
        
        return {
            "total_predictions": total,
            "correct_predictions": correct,
            "accuracy_percentage": accuracy,
            "timestamp": datetime.now().isoformat()
        }
