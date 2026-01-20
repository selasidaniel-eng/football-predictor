# ML Models Module - Phase 6

## Overview

The ML Models module implements machine learning-powered match prediction for the Football Predictor system. It includes feature engineering, model training, prediction generation, and performance evaluation.

## Architecture

### Components

1. **Feature Engineering** (`ml/features.py`)
   - Extracts features from database
   - Computes team statistics
   - Calculates form metrics
   - Head-to-head analysis
   - Injury impact analysis

2. **Model Training** (`ml/training.py`)
   - Multiple model types (Logistic Regression, Random Forest, Gradient Boosting, Ensemble)
   - Hyperparameter tuning
   - Cross-validation
   - Performance metrics calculation

3. **Prediction Generation** (`ml/training.py`)
   - Single match predictions
   - Batch predictions
   - Confidence scoring
   - Evaluation against actual results

4. **Configuration** (`ml/config.py`)
   - Model parameters
   - Feature engineering settings
   - Training hyperparameters

5. **API Endpoints** (`routes/ml.py`)
   - Model training
   - Feature importance analysis
   - Match predictions
   - Performance evaluation

## Feature Engineering

### Extracted Features

#### Team-Based Features
- Win rate (last N matches)
- Draw rate
- Goals scored average
- Goals conceded average
- Possession percentage (estimated)
- Passing accuracy (estimated)

#### Form Metrics
- Recent form points (win=3, draw=1, loss=0)
- Home form
- Away form
- Form differential

#### Head-to-Head Features
- Home team win rate vs opponent
- Away team win rate vs opponent
- Average total goals in H2H matchups

#### Contextual Features
- Injury count (team key players out)
- Rest days since last match
- Odds (home/draw/away probabilities)

### Configuration

```python
FeatureConfig(
    form_window=5,              # Last N matches for form
    injury_window=14,           # Days to consider for injuries
    head_to_head_window=20,     # H2H matches to consider
    normalize=True,             # Normalize features
    standardize=True            # Standardize features
)
```

## Model Types

### 1. Logistic Regression
- **Use Case**: Baseline model, interpretability
- **Parameters**:
  - C: Regularization (default: 1.0)
  - max_iter: 1000
- **Pros**: Fast, interpretable, good baseline
- **Cons**: Limited non-linearity capture

### 2. Random Forest
- **Use Case**: Balanced accuracy and speed
- **Parameters**:
  - n_estimators: 100
  - max_depth: 15
  - min_samples_split: 10
- **Pros**: Handles feature interactions, feature importance
- **Cons**: Less interpretable

### 3. Gradient Boosting
- **Use Case**: Maximum accuracy
- **Parameters**:
  - n_estimators: 100
  - learning_rate: 0.1
  - max_depth: 5
- **Pros**: Highest accuracy potential
- **Cons**: Slower, prone to overfitting

### 4. Ensemble
- **Use Case**: Production predictions
- **Approach**: Vote-based combination of multiple models
- **Weights**: Accuracy-based weighting of component models

## API Endpoints

### Training

**POST** `/api/v1/ml/train`

Train a new model on historical data.

**Query Parameters**:
- `league_id` (optional): Filter training data by league
- `model_type`: Model type (`ensemble`, `logistic`, `forest`, `boosting`)

**Response**:
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
      "recall": 0.68,
      "f1_score": 0.69,
      "roc_auc": 0.75
    },
    "timestamp": "2024-01-15T10:30:00"
  }
}
```

### Status

**GET** `/api/v1/ml/status`

Get current model training status.

**Response**:
```json
{
  "status": "success",
  "data": {
    "model_trained": true,
    "model_name": "ensemble",
    "timestamp": "2024-01-15T10:30:00"
  }
}
```

### Feature Importance

**GET** `/api/v1/ml/features/top`

Get top important features.

**Query Parameters**:
- `top_n`: Number of features (default: 10, max: 30)

**Response**:
```json
{
  "status": "success",
  "data": {
    "top_features": [
      {"name": "home_form", "importance": 0.15},
      {"name": "away_form", "importance": 0.12},
      {"name": "form_diff", "importance": 0.10}
    ],
    "model_name": "ensemble",
    "timestamp": "2024-01-15T10:30:00"
  }
}
```

### Single Match Prediction

**POST** `/api/v1/ml/predict/{match_id}`

Generate prediction for specific match.

**Path Parameters**:
- `match_id`: Match identifier

**Response**:
```json
{
  "status": "success",
  "data": {
    "match_id": 123,
    "prediction": "home_win",
    "confidence": 0.72,
    "probabilities": {
      "home_win": 0.48,
      "draw": 0.25,
      "away_win": 0.27
    },
    "timestamp": "2024-01-15T10:30:00"
  }
}
```

### Upcoming Matches Prediction

**POST** `/api/v1/ml/predict-upcoming`

Generate predictions for upcoming matches.

**Query Parameters**:
- `limit`: Number of matches (default: 10, max: 50)
- `league_id` (optional): Filter by league

**Response**:
```json
{
  "status": "success",
  "data": {
    "predictions_count": 10,
    "predictions": [
      {
        "match_id": 124,
        "home_team": "Manchester United",
        "away_team": "Liverpool",
        "prediction": "draw",
        "confidence": 0.65,
        "probabilities": {
          "home_win": 0.35,
          "draw": 0.40,
          "away_win": 0.25
        }
      }
    ],
    "timestamp": "2024-01-15T10:30:00"
  }
}
```

### Evaluation

**POST** `/api/v1/ml/evaluate`

Evaluate prediction accuracy against historical results.

**Query Parameters**:
- `days_back`: Look back period (default: 7, max: 30)

**Response**:
```json
{
  "status": "success",
  "data": {
    "matches_evaluated": 45,
    "metrics": {
      "accuracy": 0.64,
      "precision": 0.66,
      "recall": 0.64,
      "f1_score": 0.65
    },
    "by_outcome": {
      "home_win": {"accuracy": 0.70, "count": 15},
      "draw": {"accuracy": 0.45, "count": 10},
      "away_win": {"accuracy": 0.65, "count": 20}
    },
    "timestamp": "2024-01-15T10:30:00"
  }
}
```

### Training History

**GET** `/api/v1/ml/training-history`

Get historical training sessions.

**Query Parameters**:
- `limit`: Maximum records (default: 10, max: 50)

**Response**:
```json
{
  "status": "success",
  "data": {
    "history_count": 5,
    "history": [
      {
        "timestamp": "2024-01-15T10:30:00",
        "model_type": "ensemble",
        "samples_used": 500,
        "accuracy": 0.68
      }
    ]
  }
}
```

### Health Check

**GET** `/api/v1/ml/health`

Check ML services health.

**Response**:
```json
{
  "status": "success",
  "data": {
    "feature_engineer": "ready",
    "training_engine": "ready",
    "prediction_generator": "ready",
    "model_trained": true,
    "timestamp": "2024-01-15T10:30:00"
  }
}
```

## Usage Examples

### Train Model

```bash
curl -X POST "http://localhost:8000/api/v1/ml/train" \
  -H "Content-Type: application/json" \
  -d '{"model_type": "ensemble"}'
```

### Get Predictions for Upcoming Matches

```bash
curl -X POST "http://localhost:8000/api/v1/ml/predict-upcoming?limit=10" \
  -H "Content-Type: application/json"
```

### Evaluate Model Accuracy

```bash
curl -X POST "http://localhost:8000/api/v1/ml/evaluate?days_back=7" \
  -H "Content-Type: application/json"
```

## Data Requirements

- **Minimum training samples**: 10 matches
- **Recommended training samples**: 500+ matches
- **Feature completeness**: 80%+ non-null values

## Performance Metrics

### Accuracy Benchmarks
- **Baseline (random)**: 33.3% (3-class problem)
- **Expected Range**: 55-70%
- **Target Accuracy**: 65%+

### Model Latency
- **Feature extraction**: <500ms per match
- **Single prediction**: <100ms
- **Batch predictions (10)**: <1s
- **Full retraining**: 1-5 minutes

## Limitations & Improvements

### Current Limitations
1. Limited historical data for new teams
2. No consideration of player transfers
3. Injuries approximated by count
4. No tactical/formation analysis

### Future Improvements
1. Player-level statistics
2. Manager influence analysis
3. Weather impact modeling
4. Advanced ensemble methods (stacking, blending)
5. Deep learning models (LSTM, transformers)
6. Real-time feature updates

## Configuration Reference

### Model Configuration

```python
ModelConfig(
    # Logistic Regression
    logistic_regression_C=1.0,
    logistic_regression_max_iter=1000,
    
    # Random Forest
    random_forest_n_estimators=100,
    random_forest_max_depth=15,
    random_forest_min_samples_split=10,
    
    # Gradient Boosting
    gradient_boosting_n_estimators=100,
    gradient_boosting_learning_rate=0.1,
    gradient_boosting_max_depth=5,
    
    # Training
    test_split_ratio=0.2,
    random_state=42
)
```

## Troubleshooting

### Model Not Training
- Check: Minimum training data available (10+ matches)
- Check: Database connectivity
- Check: Feature extraction errors in logs

### Low Accuracy
- Increase training data (aim for 500+ matches)
- Check feature engineering logic
- Verify data quality
- Try different model types

### High Latency
- Cache predictions for upcoming matches
- Use simpler model (logistic regression)
- Optimize feature extraction queries
- Add database indexes on frequently queried fields

## Integration Points

1. **Database**: Pulls match, team, injury data
2. **Predictions Module**: Stores AI predictions
3. **User Predictions**: Compares user picks vs AI
4. **Admin Panel**: Model monitoring and retraining

## Security Considerations

1. All endpoints require authentication (future implementation)
2. Rate limiting on prediction endpoints
3. Model versioning for reproducibility
4. Prediction audit trail for accountability
