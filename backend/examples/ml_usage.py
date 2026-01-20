"""Example usage guide for ML module."""

import asyncio
import httpx
from datetime import datetime

BASE_URL = "http://localhost:8000"


async def train_model_example():
    """Example: Train a new ML model."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/v1/ml/train",
            params={
                "model_type": "ensemble",
                "league_id": None
            }
        )
        
        result = response.json()
        print("Training Result:")
        print(f"  Status: {result['status']}")
        print(f"  Samples Used: {result['data']['samples_used']}")
        print(f"  Accuracy: {result['data']['metrics']['accuracy']:.4f}")
        print(f"  F1 Score: {result['data']['metrics']['f1_score']:.4f}")
        
        return result


async def check_model_status_example():
    """Example: Check if model is trained."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/api/v1/ml/status")
        
        result = response.json()
        print("Model Status:")
        print(f"  Trained: {result['data']['model_trained']}")
        print(f"  Model: {result['data']['model_name']}")
        
        return result


async def get_top_features_example():
    """Example: Get top important features."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/api/v1/ml/features/top",
            params={"top_n": 15}
        )
        
        result = response.json()
        print("Top Features:")
        for i, feature in enumerate(result['data']['top_features'], 1):
            print(f"  {i}. {feature['name']}: {feature['importance']:.4f}")
        
        return result


async def predict_specific_match_example(match_id: int):
    """Example: Predict outcome for a specific match."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/v1/ml/predict/{match_id}"
        )
        
        result = response.json()
        data = result['data']
        print(f"Prediction for Match {match_id}:")
        print(f"  Prediction: {data['prediction']}")
        print(f"  Confidence: {data['confidence']:.2%}")
        print(f"  Probabilities:")
        print(f"    Home Win: {data['probabilities']['home_win']:.2%}")
        print(f"    Draw: {data['probabilities']['draw']:.2%}")
        print(f"    Away Win: {data['probabilities']['away_win']:.2%}")
        
        return result


async def predict_upcoming_matches_example():
    """Example: Get predictions for upcoming matches."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/v1/ml/predict-upcoming",
            params={
                "limit": 10,
                "league_id": None
            }
        )
        
        result = response.json()
        data = result['data']
        
        print(f"Upcoming Match Predictions ({data['predictions_count']} matches):")
        for i, pred in enumerate(data['predictions'][:5], 1):
            print(f"\n  {i}. {pred['home_team']} vs {pred['away_team']}")
            print(f"     Prediction: {pred['prediction']}")
            print(f"     Confidence: {pred['confidence']:.2%}")
        
        return result


async def evaluate_model_example():
    """Example: Evaluate model accuracy on recent matches."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/v1/ml/evaluate",
            params={"days_back": 7}
        )
        
        result = response.json()
        data = result['data']
        
        print(f"Model Evaluation (Last {data['matches_evaluated']} matches):")
        print(f"  Accuracy: {data['metrics']['accuracy']:.2%}")
        print(f"  Precision: {data['metrics']['precision']:.2%}")
        print(f"  Recall: {data['metrics']['recall']:.2%}")
        print(f"  F1 Score: {data['metrics']['f1_score']:.2%}")
        
        print("\n  By Outcome:")
        for outcome, metrics in data['by_outcome'].items():
            print(f"    {outcome}: {metrics['accuracy']:.2%} ({metrics['count']} matches)")
        
        return result


async def get_training_history_example():
    """Example: Get training history."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/api/v1/ml/training-history",
            params={"limit": 5}
        )
        
        result = response.json()
        data = result['data']
        
        print(f"Training History ({data['history_count']} records):")
        for i, record in enumerate(data['history'], 1):
            dt = datetime.fromisoformat(record['timestamp'])
            print(f"  {i}. {dt.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"     Model: {record['model_type']}")
            print(f"     Samples: {record['samples_used']}")
            print(f"     Accuracy: {record['accuracy']:.2%}")
        
        return result


async def check_ml_health_example():
    """Example: Check ML services health."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/api/v1/ml/health")
        
        result = response.json()
        data = result['data']
        
        print("ML Services Health:")
        print(f"  Feature Engineer: {data['feature_engineer']}")
        print(f"  Training Engine: {data['training_engine']}")
        print(f"  Prediction Generator: {data['prediction_generator']}")
        print(f"  Model Trained: {'Yes' if data['model_trained'] else 'No'}")
        
        return result


# Complete workflow example
async def complete_workflow_example():
    """Example: Complete workflow from training to evaluation."""
    print("=" * 60)
    print("ML Module Complete Workflow Example")
    print("=" * 60)
    
    # 1. Check health
    print("\n[1] Checking ML services health...")
    await check_ml_health_example()
    
    # 2. Check model status
    print("\n[2] Checking current model status...")
    status = await check_model_status_example()
    
    # 3. If no model trained, train one
    if not status['data']['model_trained']:
        print("\n[3] Training new model...")
        await train_model_example()
    
    # 4. Get top features
    print("\n[4] Getting top important features...")
    await get_top_features_example()
    
    # 5. Get predictions for upcoming matches
    print("\n[5] Getting predictions for upcoming matches...")
    await predict_upcoming_matches_example()
    
    # 6. Predict specific match (assuming match_id=1)
    print("\n[6] Predicting specific match (ID=1)...")
    await predict_specific_match_example(match_id=1)
    
    # 7. Evaluate model
    print("\n[7] Evaluating model accuracy...")
    await evaluate_model_example()
    
    # 8. Get training history
    print("\n[8] Getting training history...")
    await get_training_history_example()
    
    print("\n" + "=" * 60)
    print("Workflow Complete!")
    print("=" * 60)


# Direct usage example for development
def example_feature_engineering():
    """Example: Direct usage of feature engineering."""
    from app.ml.features import FeatureEngineer
    from app.ml.config import FeatureConfig
    
    # Create engineer
    config = FeatureConfig(
        form_window=5,
        injury_window=14,
        head_to_head_window=20
    )
    engineer = FeatureEngineer(config)
    
    print("Feature Engineer configured:")
    print(f"  Form window: {config.form_window}")
    print(f"  Injury window: {config.injury_window} days")
    print(f"  H2H window: {config.head_to_head_window}")


def example_data_processing():
    """Example: Direct usage of data processing."""
    import numpy as np
    from app.ml.utils import DataProcessor
    
    # Sample data with missing values
    X = np.array([
        [1.0, 2.0, 3.0],
        [4.0, np.nan, 6.0],
        [7.0, 8.0, np.nan]
    ])
    
    print("Original data shape:", X.shape)
    print("Missing values:", np.isnan(X).sum())
    
    # Handle missing values
    X_clean = DataProcessor.handle_missing_values(X, strategy="mean")
    print("\nAfter handling missing values:")
    print("Missing values:", np.isnan(X_clean).sum())
    
    # Normalize
    X_normalized, _, scaler = DataProcessor.normalize_features(X_clean)
    print("\nAfter normalization:")
    print("Mean:", np.mean(X_normalized, axis=0))
    print("Std:", np.std(X_normalized, axis=0))


if __name__ == "__main__":
    # Run async examples
    print("Running async examples...")
    asyncio.run(complete_workflow_example())
    
    # Run direct examples
    print("\n\nRunning direct usage examples...")
    print("\n--- Feature Engineering ---")
    example_feature_engineering()
    
    print("\n--- Data Processing ---")
    example_data_processing()
