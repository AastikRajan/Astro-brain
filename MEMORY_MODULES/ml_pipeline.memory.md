# Module: ml_pipeline.py
## Last Updated: 2026-03-02

## PURPOSE
Machine learning pipeline scaffold for training prediction calibration models from historical chart data. Supports feature extraction from astrological features, training scikit-learn classifiers, and using trained models to calibrate or replace the rule-based confidence scores. Currently in scaffold stage — not wired into main prediction pipeline.

## KEY FUNCTIONS

### train_model(training_data, target, model_type) → dict
- **Purpose:** Train an ML model on historical chart + outcome data
- **Inputs:** feature matrix, outcome labels, model type ("rf"/"lgbm"/"logistic")
- **Returns:** `{model, metrics, feature_importance}`

### predict_ml(model, chart_features) → float
- **Purpose:** Get ML prediction for a chart's domain outcome probability
- **Inputs:** trained model object, feature vector
- **Returns:** probability float 0–1

## DEPENDENCIES
scikit-learn (optional), numpy, pandas

## RECENT CHANGES
- 2026-03-02: Created as scaffold (not yet wired into prediction pipeline)
