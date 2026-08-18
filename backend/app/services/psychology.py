"""Psychological Threat Detection 2.0 — message-level social engineering."""

from typing import Dict

CATEGORIES = {
    "urgency_detected": {
        "label": "Urgency",
        "points": 12,
        "patterns": [
            "urgent", "act now", "act-now", "immediately", "immediate action",
            "action required", "last chance", "final warning", "limited time",
            "right now", "don't wait", "dont wait", "abhi click", "abhi karo",
            "jaldi karo", "turant",
        ],
    },
    "fear_tactics": {
        "label": "Fear",
        "points": 12,
        "patterns": [
            "account blocked", "will be blocked", "account suspended", "suspended",
            "security breach", "unauthorized access", "legal action",
            "police complaint", "band ho jayega", "block ho jayega",
            "will be deleted", "will be closed",
        ],
    },
    "authority_impersonation": {
        "label": "Impersonation",
        "points": 12,
        "patterns": [
            "bank security", "security department", "government notice",
            "police notice", "income tax department", "rbi", "cyber cell",
            "kyc department",
        ],
    },
    "coercion": {
        "label": "Coercion",
        "points": 10,
        "patterns": [
            "failure to verify", "will result in suspension", "must verify",
            "mandatory kyc", "or your account",
        ],
    },
    "financial_pressure": {
        "label": "Financial Pressure",
        "points": 10,
        "patterns": [
            "payment required", "refund pending", "pay immediately",
            "outstanding amount", "fine imposed", "transfer now",
        ],
    },
    "credential_pressure": {
        "label": "Credential Request",
        "points": 14,
        "patterns": [
            "enter otp", "share otp", "confirm password", "verify otp",
            "enter password", "cvv", "pin number", "aadhaar otp",
            "update kyc", "complete kyc",
        ],
    },
    "countdown": {
        "label": "Countdown",
        "points": 8,
        "patterns": [
            "expires in", "00:", "offer expires", "within 10 minutes",
            "within 5 minutes",
        ],
    },
    "greed_bait": {
        "label": "Reward Bait",
        "points": 10,
        "patterns": [
            "you won", "you have won", "lottery", "prize", "free gift",
            "claim now", "claim your", "jackpot", "congratulations",
            "lucky draw", "inaam",
        ],
    },
    "secrecy": {
        "label": "Secrecy",
        "points": 8,
        "patterns": [
            "do not tell", "don't tell anyone", "keep this confidential",
            "secret code", "do not share this message",
        ],
    },
    "emotional_manipulation": {
        "label": "Emotional Manipulation",
        "points": 10,
        "patterns": [
            "help me urgently", "emergency payment", "i am in trouble",
            "accident", "hospital bill", "please beta",
        ],
    },
}


def analyze_text(text: str) -> Dict:
    """Backward-compatible wrapper used by the existing URL checker."""
    result = analyze_message(text)
    return {
        "score": min(int(result["score"] * 0.4), 40),
        "tags": result["tags"],
        "findings": result["findings"],
    }


def analyze_message(text: str) -> Dict:
    """
    Full message psychological analysis.
    score is 0-100. Psychological signals alone are not a phishing verdict.
    """
    text_lower = (text or "").lower()
    score = 0
    tags = []
    findings = []
    labels = []

    for tag, spec in CATEGORIES.items():
        matched = [p for p in spec["patterns"] if p in text_lower]
        if matched:
            score += spec["points"]
            tags.append(tag)
            labels.append(spec["label"])
            findings.append(f"{spec['label']}: '{matched[0]}'")

    return {
        "score": min(score, 100),
        "tags": tags,
        "labels": labels,
        "findings": findings,
        "signal_count": len(tags),
    }
