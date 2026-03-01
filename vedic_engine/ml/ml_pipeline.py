"""
Machine Learning Pipeline — Learning Bayesian Weights from Labeled Chart Data.

═══════════════════════════════════════════════════════════════════════
ARCHITECTURE
═══════════════════════════════════════════════════════════════════════

The Problem with Hand-Tuned Weights
-------------------------------------
confidence.py currently uses:
  W_DASHA=0.25, W_TRANSIT=0.20, W_AV=0.15, W_YOGA=0.13,
  W_KP=0.12, W_FUNCTIONAL=0.08, W_HOUSE_LORD=0.07

These are EXPERT GUESSES. They represent an educated prior, not empirical truth.
They cannot distinguish which factors actually mattered for 10,000 real charts.

The ML Solution
---------------
1. CORPUS: 10,000+ charts from Astro-Databank (AA-rated birth times) with
   documented life events (marriage dates, career milestones, health crises).

2. FEATURE EXTRACTION: For each chart × event combination, run our prediction
   engine and extract the 7 raw component scores (before weighting).

3. TRAINING: Use XGBoost or sklearn LogisticRegression to learn the weights
   that maximally predict whether the event occurred during the indicated timing.

4. OUTPUT: A trained model file (.pkl or .json) that replaces the hard-coded weights.

Feature Vector (per chart × domain × date_window)
--------------------------------------------------
  [dasha_alignment, transit_score, av_score, yoga_activation,
   kp_score, functional_score, house_lord_score,
   promise_pct, tithi_quality, vara_quality, nakshatra_quality,
   yoga_quality, karana_quality, moon_phase_shukla,
   shadbala_ratio_dasha_lord, vimshopak_dasha_lord,
   is_vargottama_dasha_lord, is_retrograde_dasha_lord,
   argala_score, arudha_score]

Target
------
  Binary: 1 = event occurred within prediction window, 0 = did not occur.

Models
------
  PRIMARY:    XGBClassifier (handles non-linearity, missing values natively)
  SECONDARY:  LogisticRegression (interpretable weight extraction)
  VALIDATION: RandomForestClassifier (feature importance cross-check)
  CALIBRATION: CalibratedClassifierCV (convert scores to calibrated probabilities)

Status: SCAFFOLD — corpus pipeline and training loop defined.
        Feature extraction wired stub (connect to PredictionEngine output).
        Model training requires labeled data (not yet collected).

Dependencies (installed)
------------------------
  scikit-learn 1.8.0  ✅
  xgboost             ✅
  numpy               ✅
  pandas              ✅
  scipy               ✅
"""

from __future__ import annotations

import json
import logging
import os
import pickle
from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)

# ─── Storage paths ────────────────────────────────────────────────────────────

_HERE = Path(__file__).parent.parent  # vedic_engine/
_ML_DIR = _HERE / "ml"
_ML_DIR.mkdir(exist_ok=True)
_MODEL_PATH    = _ML_DIR / "trained_model.pkl"
_CORPUS_PATH   = _ML_DIR / "labeled_corpus.jsonl"
_FEATURES_PATH = _ML_DIR / "feature_matrix.npz"

# ─── Feature schema ───────────────────────────────────────────────────────────

FEATURE_NAMES = [
    # Core prediction engine outputs (7 weighted components)
    "dasha_alignment",
    "transit_score",
    "av_score",
    "yoga_activation",
    "kp_score",
    "functional_score",
    "house_lord_score",

    # Promise gate
    "promise_pct",
    "promise_pillars",              # 0/1/2/3 pillars active

    # Panchanga quality
    "tithi_quality_score",          # -1/0/1
    "vara_quality_score",
    "nakshatra_quality_score",
    "yoga_quality_score",
    "karana_quality_score",
    "moon_is_waxing",               # 0/1

    # Dasha lord qualities
    "shadbala_ratio_mahadasha",     # 0.0–2.0 (actual/minimum)
    "shadbala_ratio_antardasha",
    "vimshopak_mahadasha",          # 0–20
    "is_vargottama_mahadasha",      # 0/1
    "is_retrograde_mahadasha",      # 0/1
    "mahadasha_house",              # 1–12

    # Jaimini enrichment
    "chara_dasha_alignment",        # 0.0–1.0
    "argala_strength",              # net Argala score for domain house
    "arudha_quality",               # 0.0–1.0

    # Transit enrichment
    "saturn_transit_favorable",     # 0/1
    "jupiter_transit_favorable",    # 0/1
    "n_planet_transits_active",     # count of active transits

    # Ashtakvarga
    "av_score_house2",              # 0–56 (2nd house total)
    "av_score_house11",             # 11th house total
]

N_FEATURES = len(FEATURE_NAMES)


# ─── Labeled example ──────────────────────────────────────────────────────────

@dataclass
class LabeledExample:
    """One training example: chart × domain × prediction_window → event_occurred."""
    chart_id:         str          # unique chart identifier (e.g. "astro_123")
    domain:           str          # "career", "marriage", etc.
    prediction_date:  str          # ISO date: start of prediction window
    event_occurred:   int          # 1 = event happened in window, 0 = did not
    event_date:       Optional[str] = None  # actual event date (if known)
    source:           str = "astrodatabank"
    birth_rating:     str = "AA"   # Rodden Rating

    # Raw feature vector (populated by extract_features())
    features: List[float] = field(default_factory=lambda: [0.0] * N_FEATURES)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ─── Feature extraction ───────────────────────────────────────────────────────

def extract_features(
    engine_output: Dict[str, Any],
    domain: str,
) -> np.ndarray:
    """
    Extract the flat feature vector from PredictionEngine output.

    Parameters
    ----------
    engine_output : dict returned by PredictionEngine.generate_domain_report()
    domain        : e.g. "career"

    Returns
    -------
    np.ndarray of shape (N_FEATURES,), dtype float32.

    NOTE: Keys below match the output structure of the current engine.
    Adjust if engine output dict schema changes.
    """
    assert len(FEATURE_NAMES) == N_FEATURES

    def _get(path: str, default: float = 0.0) -> float:
        """Navigate nested dicts with dot-notation path."""
        parts = path.split(".")
        obj = engine_output
        for p in parts:
            if isinstance(obj, dict):
                obj = obj.get(p, None)
            else:
                return default
            if obj is None:
                return default
        try:
            return float(obj)
        except (TypeError, ValueError):
            return default

    vec = np.zeros(N_FEATURES, dtype=np.float32)

    # ── 7 core score components ───────────────────────────────────────────
    timing = engine_output.get("timing_analysis", {})
    vec[0] = _get("timing_analysis.dasha_alignment")
    vec[1] = _get("timing_analysis.transit_score")
    vec[2] = _get("timing_analysis.av_score")
    vec[3] = _get("timing_analysis.yoga_activation")
    vec[4] = _get("timing_analysis.kp_score")
    vec[5] = _get("timing_analysis.functional_score")
    vec[6] = _get("timing_analysis.house_lord_score")

    # ── Promise ───────────────────────────────────────────────────────────
    promise = engine_output.get("promise", {})
    vec[7] = float(promise.get("promise_pct", 0.5))
    vec[8] = float(len(promise.get("pillars", {}) or {}))

    # ── Panchanga ──────────────────────────────────────────────────────────
    panch = engine_output.get("panchanga", {})
    vec[9]  = float((panch.get("tithi", {}) or {}).get("quality_score", 0))
    vec[10] = float((panch.get("vara",  {}) or {}).get("quality_score", 0))
    vec[11] = float((panch.get("nakshatra", {}) or {}).get("quality_score", 0))
    vec[12] = float((panch.get("yoga",  {}) or {}).get("quality_score", 0))
    vec[13] = float((panch.get("karana",{}) or {}).get("quality_score", 0))
    vec[14] = 1.0 if panch.get("moon_waxing") else 0.0

    # ── Dasha lord strengths ───────────────────────────────────────────────
    shadbala = engine_output.get("shadbala", {})
    vimshopak = engine_output.get("vimshopak", {})
    dasha_info = engine_output.get("dashas", {}).get("vimshottari", {})
    maha_lord  = (dasha_info.get("mahadasha", {}) or {}).get("planet", "")
    antar_lord = (dasha_info.get("antardasha", {}) or {}).get("planet", "")

    vec[15] = float((shadbala.get(maha_lord, {}) or {}).get("ratio", 1.0))
    vec[16] = float((shadbala.get(antar_lord, {}) or {}).get("ratio", 1.0))
    vec[17] = float((vimshopak.get(maha_lord, {}) or {}).get("score", 10.0))
    vec[18] = 1.0 if maha_lord in engine_output.get("vargottama_planets", []) else 0.0
    vec[19] = 1.0 if engine_output.get("retrogrades", {}).get(maha_lord) else 0.0
    planets_h= engine_output.get("planet_houses", {})
    vec[20] = float(planets_h.get(maha_lord, 0))

    # ── Jaimini ───────────────────────────────────────────────────────────
    jaimini = engine_output.get("jaimini", {})
    vec[21] = float(jaimini.get("chara_dasha_alignment", 0.5))
    vec[22] = float(jaimini.get("argala_score", 0.0))
    vec[23] = float(jaimini.get("arudha_quality", 0.5))

    # ── Transits ──────────────────────────────────────────────────────────
    transits = engine_output.get("transits", {})
    vec[24] = 1.0 if transits.get("saturn_favorable") else 0.0
    vec[25] = 1.0 if transits.get("jupiter_favorable") else 0.0
    vec[26] = float(transits.get("n_active_transits", 0))

    # ── Ashtakvarga ───────────────────────────────────────────────────────
    av = engine_output.get("ashtakvarga", {})
    house_av = (av.get("bhava_pinda", {}) or {})
    vec[27] = float(house_av.get(2, 28.0))   # house 2 AV
    vec[28] = float(house_av.get(11, 28.0))  # house 11 AV

    return vec


# ─── Corpus builder ───────────────────────────────────────────────────────────

class CorpusBuilder:
    """
    Incrementally builds the labeled training corpus.

    Usage
    -----
        builder = CorpusBuilder()
        builder.add_example(engine_output, domain="career",
                            prediction_date="2025-01-01",
                            event_occurred=1,
                            chart_id="astro_001")
        builder.save()

    The corpus is saved as JSONL (one JSON object per line) to
    vedic_engine/ml/labeled_corpus.jsonl.
    """

    def __init__(self, path: Path = _CORPUS_PATH):
        self.path = path
        self.examples: List[LabeledExample] = []
        if path.exists():
            self._load_existing()

    def _load_existing(self) -> None:
        with open(self.path, "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        d = json.loads(line)
                        ex = LabeledExample(**{k: v for k, v in d.items() if k != "features"})
                        ex.features = d.get("features", [0.0] * N_FEATURES)
                        self.examples.append(ex)
                    except Exception:
                        pass
        logger.info(f"[ml_pipeline] Loaded {len(self.examples)} existing examples.")

    def add_example(
        self,
        engine_output: Dict[str, Any],
        domain: str,
        prediction_date: str,
        event_occurred: int,
        chart_id: str,
        event_date: Optional[str] = None,
        source: str = "astrodatabank",
        birth_rating: str = "AA",
    ) -> None:
        """Extract features from engine output and add to corpus."""
        features = extract_features(engine_output, domain)
        ex = LabeledExample(
            chart_id=chart_id,
            domain=domain,
            prediction_date=prediction_date,
            event_occurred=event_occurred,
            event_date=event_date,
            source=source,
            birth_rating=birth_rating,
            features=features.tolist(),
        )
        self.examples.append(ex)

    def save(self) -> None:
        with open(self.path, "a") as f:
            for ex in self.examples:
                f.write(json.dumps(ex.to_dict()) + "\n")
        logger.info(f"[ml_pipeline] Saved {len(self.examples)} examples to {self.path}")

    def build_matrix(
        self,
        domain: Optional[str] = None,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Return (X, y) arrays for model training."""
        filtered = [ex for ex in self.examples
                    if (domain is None or ex.domain == domain)
                    and len(ex.features) == N_FEATURES]
        X = np.array([ex.features for ex in filtered], dtype=np.float32)
        y = np.array([ex.event_occurred for ex in filtered], dtype=np.int32)
        return X, y


# ─── Model training ───────────────────────────────────────────────────────────

def train_model(
    X: np.ndarray,
    y: np.ndarray,
    model_type: str = "xgboost",
    calibrate: bool = True,
    test_size: float = 0.20,
    random_state: int = 42,
) -> Dict[str, Any]:
    """
    Train prediction model on feature matrix X and labels y.

    Parameters
    ----------
    X          : (n_samples, N_FEATURES) float32 array
    y          : (n_samples,) int array — 0/1 labels
    model_type : "xgboost" | "logistic" | "random_forest"
    calibrate  : wrap with CalibratedClassifierCV (Platt scaling)
    test_size  : fraction held out for evaluation
    random_state : reproducibility seed

    Returns
    -------
    {
      "model": trained sklearn/xgboost model,
      "metrics": {"accuracy": float, "auc_roc": float, "brier_score": float},
      "feature_importances": {feature_name: importance_score},
      "model_type": str,
      "n_train": int,
      "n_test": int,
    }
    """
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, roc_auc_score, brier_score_loss
    from sklearn.calibration import CalibratedClassifierCV

    assert len(X) >= 20, "Need at least 20 labeled examples to train."
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )

    # ── Model selection ───────────────────────────────────────────────────
    if model_type == "xgboost":
        try:
            from xgboost import XGBClassifier
            base_model = XGBClassifier(
                n_estimators=300,
                max_depth=4,
                learning_rate=0.05,
                subsample=0.8,
                colsample_bytree=0.8,
                use_label_encoder=False,
                eval_metric="logloss",
                random_state=random_state,
                n_jobs=-1,
            )
        except ImportError:
            logger.warning("[ml_pipeline] xgboost not available; falling back to random_forest.")
            model_type = "random_forest"

    if model_type == "logistic":
        from sklearn.linear_model import LogisticRegression
        from sklearn.preprocessing import StandardScaler
        from sklearn.pipeline import Pipeline
        base_model = Pipeline([
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(max_iter=1000, C=1.0, random_state=random_state)),
        ])

    if model_type == "random_forest":
        from sklearn.ensemble import RandomForestClassifier
        base_model = RandomForestClassifier(
            n_estimators=200, max_depth=6, random_state=random_state, n_jobs=-1
        )

    # ── Calibration wrapper ────────────────────────────────────────────────
    if calibrate and model_type != "logistic":
        from sklearn.calibration import CalibratedClassifierCV
        model = CalibratedClassifierCV(base_model, cv=5, method="isotonic")
    else:
        model = base_model

    model.fit(X_train, y_train)

    # ── Metrics ───────────────────────────────────────────────────────────
    y_pred   = model.predict(X_test)
    y_proba  = model.predict_proba(X_test)[:, 1]
    acc      = accuracy_score(y_test, y_pred)
    auc      = roc_auc_score(y_test, y_proba) if len(set(y_test)) > 1 else 0.0
    brier    = brier_score_loss(y_test, y_proba)

    # ── Feature importances ────────────────────────────────────────────────
    importances: Dict[str, float] = {}
    try:
        if model_type == "xgboost":
            raw_imp = base_model.feature_importances_
        elif model_type == "random_forest":
            raw_imp = base_model.feature_importances_
        elif model_type == "logistic":
            raw_imp = abs(base_model.named_steps["clf"].coef_[0])
        else:
            raw_imp = np.ones(N_FEATURES)

        for fname, imp in zip(FEATURE_NAMES, raw_imp):
            importances[fname] = round(float(imp), 6)
    except Exception:
        pass

    logger.info(
        f"[ml_pipeline] Trained {model_type}: "
        f"acc={acc:.3f} AUC={auc:.3f} Brier={brier:.4f} "
        f"(n_train={len(X_train)}, n_test={len(X_test)})"
    )

    return {
        "model":               model,
        "metrics":             {"accuracy": round(acc,4), "auc_roc": round(auc,4), "brier_score": round(brier,4)},
        "feature_importances": importances,
        "model_type":          model_type,
        "n_train":             len(X_train),
        "n_test":              len(X_test),
    }


def save_model(model, path: Path = _MODEL_PATH) -> None:
    with open(path, "wb") as f:
        pickle.dump(model, f)
    logger.info(f"[ml_pipeline] Model saved to {path}")


def load_model(path: Path = _MODEL_PATH):
    if not path.exists():
        raise FileNotFoundError(f"No trained model at {path}. Run train_model() first.")
    with open(path, "rb") as f:
        return pickle.load(f)


# ─── Inference ───────────────────────────────────────────────────────────────

def predict_with_ml(
    engine_output: Dict[str, Any],
    domain: str,
    model=None,
) -> Dict[str, float]:
    """
    Use trained ML model to produce calibrated confidence for a domain.

    Falls back to raw engine confidence if model not available.

    Returns
    -------
    {
      "ml_confidence":     float,   # calibrated probability from ML model
      "feature_vector":    list,    # N_FEATURES values (for debugging)
      "model_available":   bool,
    }
    """
    if model is None:
        try:
            model = load_model()
        except FileNotFoundError:
            raw_conf = engine_output.get("confidence", 0.5)
            return {
                "ml_confidence":   raw_conf,
                "feature_vector":  [],
                "model_available": False,
            }

    vec = extract_features(engine_output, domain)
    try:
        proba = model.predict_proba(vec.reshape(1, -1))[0][1]
    except Exception as e:
        logger.warning(f"[ml_pipeline] predict_with_ml failed: {e}")
        proba = engine_output.get("confidence", 0.5)

    return {
        "ml_confidence":   round(float(proba), 4),
        "feature_vector":  vec.tolist(),
        "model_available": True,
    }


# ─── Astro-Databank scraper scaffold ─────────────────────────────────────────

def scrape_astrodatabank_stub(max_charts: int = 100) -> List[Dict[str, Any]]:
    """
    SCAFFOLD — Astro-Databank corpus collection.

    Astro-Databank (https://www.astro.com/astro-databank/) has 90,000+
    charts with documented life events. AA-rated charts have verified birth times.

    Implementation Plan (not yet coded):
    1. Use requests + BeautifulSoup to parse the ADB search API.
    2. Filter: Rodden Rating == "AA", life events with precise dates.
    3. Extract: birth date/time/place, event category (marriage, career, death),
       event date, event description.
    4. Store in labeled_corpus.jsonl via CorpusBuilder.add_example().

    Legal Note: Check ADB's Terms of Service before scraping.
    Ethically prefer their bulk data export if available.

    Parameters
    ----------
    max_charts : maximum number of charts to fetch

    Returns
    -------
    List of raw chart dicts (schema TBD from ADB structure).
    Raises NotImplementedError until implemented.
    """
    raise NotImplementedError(
        "Astro-Databank scraper not yet implemented. "
        "Provide labeled corpus in vedic_engine/ml/labeled_corpus.jsonl "
        "using the LabeledExample schema."
    )
