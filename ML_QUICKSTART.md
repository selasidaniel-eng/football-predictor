# ML Module Quick Start Guide

## Installation

### Prerequisites
```bash
pip install scikit-learn numpy pandas
pip install sqlalchemy
```

### Project Structure
```
backend/
├── app/
│   ├── ml/
│   │   ├── __init__.py
│   │   ├── config.py          # Configuration classes
│   │   ├── features.py        # Feature engineering
│   │   ├── utils.py           # Utility functions
│   │   └── models.py          # (To be implemented)
│   └── routes/
│       └── ml.py              # API endpoints
└── docs/
    └── ML_MODELS.md           # Full documentation
```

## Quick Start

### 1. Check ML Service Health
```bash
curl -X GET "http://localhost:8000/api/v1/ml/health"
```

Expected Response:
```json
{
  "status": "success",
  "data": {
    "feature_engineer": "ready",
    "training_engine": "ready",
    "prediction_generator": "ready",
    "model_trained": false
  }
}
```

### 2. Train a Model
```bash
curl -X POST "http://localhost:8000/api/v1/ml/train?model_type=ensemble"
```

Expected Response:
```json
{
  "status": "success",
  "data": {
    "message": "Trained ensemble with 500 samples",
    "samples_used": 500,
    "features": 18,
    "metrics": {
      "accuracy": 0.68,
      "precision": 0.70,
      "recall": 0.68
    }
  }
}
```

### 3. Make Predictions
```bash
# Single match
curl -X POST "http://localhost:8000/api/v1/ml/predict/1"

# Upcoming matches
curl -X POST "http://localhost:8000/api/v1/ml/predict-upcoming?limit=10"
```

### 4. Evaluate Model
```bash
curl -X POST "http://localhost:8000/api/v1/ml/evaluate?days_back=7"
```

## Common Tasks

### Training a New Model
```python
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.ml.features import FeatureEngineer
from app.ml.config import FeatureConfig

async def train():
    # Create feature engineer
    config = FeatureConfig()
    engineer = FeatureEngineer(config)
    
    # Extract features from database
    # (Implementation depends on your database session)
    X, feature_names = await engineer.extract_features(db, matches)
    
    # Train model
    # (Model training to be implemented)
```

### Making Predictions
```bash
# For a specific match
curl -X POST "http://localhost:8000/api/v1/ml/predict/1"

# For upcoming matches (next 10)
curl -X POST "http://localhost:8000/api/v1/ml/predict-upcoming?limit=10"

# For upcoming matches in a league
curl -X POST "http://localhost:8000/api/v1/ml/predict-upcoming?limit=10&league_id=1"
```

### Analyzing Feature Importance
```bash
# Top 10 features
curl -X GET "http://localhost:8000/api/v1/ml/features/top?top_n=10"

# Top 20 features
curl -X GET "http://localhost:8000/api/v1/ml/features/top?top_n=20"
```

### Checking Model Status
```bash
curl -X GET "http://localhost:8000/api/v1/ml/status"
```

## Configuration

### Default Feature Config
```python
FeatureConfig(
    form_window=5,              # Last 5 matches for form
    injury_window=14,           # 14 days for injuries
    head_to_head_window=20,     # Last 20 H2H matches
    normalize=True,
    standardize=True
)
```

### Custom Feature Config
```python
from app.ml.config import FeatureConfig

config = FeatureConfig(
    form_window=10,             # Change to 10 matches
    injury_window=7,            # Change to 7 days
    head_to_head_window=10,     # Change to 10 matches
    normalize=True,
    standardize=True
)
```

## Features Extracted

The system extracts these features from match data:

### Team Performance (12 features)
- Home: win rate, draw rate, goals for/against, possession, passing acc
- Away: win rate, draw rate, goals for/against, possession, passing acc

### Form Metrics (3 features)
- Home form, away form, form differential

### Head-to-Head (3 features)
- Home win rate vs opponent, away win rate, average total goals

### Context (3 features)
- Home injuries, away injuries, Rest days (combined)

### Odds (3 features)
- Home odds, draw odds, away odds

**Total: 18+ features**

## Model Types

### Logistic Regression
- Fast, interpretable, good baseline
- Use for quick predictions or baseline comparison

### Random Forest
- Balanced accuracy and speed
- Good feature importance analysis
- Recommended for most use cases

### Gradient Boosting
- Highest accuracy potential
- Slower training and prediction
- Use when maximum accuracy needed

### Ensemble
- Combines multiple models
- Vote-based predictions
- Most robust approach (recommended)

## Evaluation Metrics

After training, you can evaluate model performance:

```bash
# Evaluate on last 7 days of matches
curl -X POST "http://localhost:8000/api/v1/ml/evaluate?days_back=7"
```

Metrics provided:
- **Accuracy**: Percentage of correct predictions
- **Precision**: Of predicted positives, how many were correct
- **Recall**: Of actual positives, how many were found
- **F1 Score**: Harmonic mean of precision and recall
- **Confusion Matrix**: Detailed breakdown by outcome

## Performance Tips

1. **Faster Predictions**: Use logistic regression for low-latency requirements
2. **Better Accuracy**: Use ensemble or gradient boosting
3. **Feature Analysis**: Use random forest for feature importance
4. **Caching**: Cache predictions for upcoming matches (implement in Phase 7)
5. **Database**: Add indexes on frequently queried fields

## Troubleshooting

### "Insufficient training data"
- Need at least 10 matches to train
- Recommended: 500+ matches for good model

### "Model not trained yet"
- Train a model first: `POST /api/v1/ml/train`

### "Match not found"
- Verify match ID exists in database
- Check match hasn't been deleted

### Slow Predictions
- Feature extraction may be slow if database is unoptimized
- Add indexes to match, team, injury tables
- Consider caching features

## Integration Checklist

- [x] Feature engineering module
- [x] Configuration system
- [x] Utility functions
- [x] API endpoints
- [x] Documentation
- [ ] Implement actual model training (in progress)
- [ ] Add prediction caching
- [ ] Add performance monitoring
- [ ] Add user-facing UI

## Next Steps

1. **Implement Model Training** (`ml/models.py`)
   - Create EnsembleModel class
   - Implement training logic
   - Add hyperparameter tuning

2. **Implement Predictions** (`ml/training.py`)
   - PredictionGenerator class
   - Single/batch predictions
   - Confidence scoring

3. **Add Frontend** (Phase 7)
   - Display predictions
   - Show feature importance
   - Model performance dashboard

## Support

For issues or questions:
1. Check `docs/ML_MODELS.md` for detailed API documentation
2. Review `examples/ml_usage.py` for code examples
3. Check `tests/test_ml.py` for usage patterns
4. Review logs for error details

## Additional Resources

- **Full Documentation**: [ML_MODELS.md](./docs/ML_MODELS.md)
- **Code Examples**: [ml_usage.py](./examples/ml_usage.py)
- **Unit Tests**: [test_ml.py](./tests/test_ml.py)
- **Configuration**: [config.py](./app/ml/config.py)
