"""
Multi-signal risk fusion.

Weights are starting defaults, not proven-optimal. They can be changed in
DEFAULT_WEIGHTS. Psychological signals cannot produce HIGH/CRITICAL alone.
"""

from typing import Dict

# Documented starting weights. Sum = 1.0
DEFAULT_WEIGHTS = {
    "url": 0.22,
    "domain": 0.16,
    "ml": 0.10,
    "nlp": 0.10,
    "psychological": 0.10,
    "threat_intel": 0.10,
    "brand": 0.08,
    "redirect": 0.04,
    "sender": 0.05,
    "community": 0.05,
}


def _level(score: int) -> str:
    if score >= 70:
        return "CRITICAL"
    if score >= 50:
        return "HIGH"
    if score >= 30:
        return "MEDIUM"
    return "LOW"


def fuse(signals: Dict[str, float], weights: Dict[str, float] = None) -> Dict:
    weights = dict(weights or DEFAULT_WEIGHTS)
    cleaned = {key: max(0.0, min(100.0, float(signals.get(key, 0) or 0))) for key in weights}

    raw = sum(cleaned[key] * weights[key] for key in weights)
    score = int(round(min(raw, 100)))

    # False-positive guard: psychology / marketing language alone stays LOW/MEDIUM
    strong = any(cleaned[key] >= 40 for key in ("url", "domain", "threat_intel", "brand", "community"))
    psych_only = cleaned["psychological"] >= 20 and not strong
    if psych_only:
        score = min(score, 35)

    fired = sum(1 for value in cleaned.values() if value >= 20)
    # Confidence = how many independent signals agree. Not model accuracy.
    confidence = min(95, 35 + fired * 10)

    return {
        "risk_score": score,
        "risk_level": _level(score),
        "scam_risk": score,
        "model_probability": score,
        "model_confidence": confidence,
        "signals": {key: int(round(cleaned[key])) for key in weights},
        "weights": weights,
        "methodology": (
            "Weighted fusion of independent signals. "
            "Model confidence is agreement between signals, not detection accuracy. "
            "Scam risk is an estimated score from available evidence, not a calibrated probability of fraud."
        ),
    }
