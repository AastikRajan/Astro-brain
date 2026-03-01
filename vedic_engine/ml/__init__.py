# vedic_engine/ml/__init__.py
"""
Machine Learning Pipeline for Vedic Prediction Engine.

Provides:
  - CorpusBuilder      : Build labeled training corpus
  - extract_features() : Feature extraction from engine output
  - train_model()      : XGBoost/sklearn model training
  - predict_with_ml()  : Calibrated ML inference
  - save_model()       : Persist trained model
  - load_model()       : Load persisted model

Status: SCAFFOLD — training requires labeled corpus (yet to be collected).
"""

from vedic_engine.ml.ml_pipeline import (
    CorpusBuilder,
    LabeledExample,
    extract_features,
    train_model,
    predict_with_ml,
    save_model,
    load_model,
    FEATURE_NAMES,
    N_FEATURES,
)

__all__ = [
    "CorpusBuilder", "LabeledExample", "extract_features", "train_model",
    "predict_with_ml", "save_model", "load_model", "FEATURE_NAMES", "N_FEATURES",
]
