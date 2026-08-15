"""Psychological Threat Detection.

Phishing is not just a URL problem - attackers use urgency, fear and greed
to make victims act without thinking. This module scans text (URLs, SMS,
WhatsApp messages, emails) for those manipulation patterns.
"""

from typing import Dict

URGENCY_PATTERNS = [
    "urgent", "act now", "act-now", "actnow", "hurry", "immediately",
    "immediate action", "action required", "expires today", "expiry",
    "expires", "24 hours", "24hrs", "48 hours", "last chance",
    "final warning", "final notice", "limited time", "limited-time",
    "right now", "dont wait", "don't wait",
    # Hinglish urgency
    "abhi click", "abhi karo", "jaldi karo", "jaldi se", "turant",
]

FEAR_PATTERNS = [
    "account blocked", "account-blocked", "account will be blocked",
    "will be blocked", "account suspended", "suspended", "deactivated",
    "unauthorized access", "unusual activity", "security alert",
    "legal action", "police complaint", "penalty", "your account is at risk",
    "verify or lose", "will be deleted", "will be closed",
    # Hinglish fear
    "band ho jayega", "block ho jayega", "bandh ho jayega",
]

GREED_PATTERNS = [
    "winner", "you won", "you-won", "you have won", "lottery", "prize",
    "free gift", "free-gift", "cashback", "claim now", "claim-now",
    "claim your", "reward", "jackpot", "congratulations", "lucky draw",
    "scratch card", "free recharge",
    # Hinglish greed
    "inaam", "muft",
]


def analyze_text(text: str) -> Dict:
    """
    Scan text for psychological manipulation patterns.
    Returns: {"score": 0-40, "tags": [...], "findings": [...]}
    """
    text_lower = (text or "").lower()
    score = 0
    tags = []
    findings = []

    def scan(patterns, points, tag, label):
        nonlocal score
        matched = [p for p in patterns if p in text_lower]
        if matched:
            score += points
            tags.append(tag)
            findings.append(f"{label}: '{matched[0]}'")

    scan(URGENCY_PATTERNS, 15, "urgency_detected", "Urgency pressure language found")
    scan(FEAR_PATTERNS, 15, "fear_tactics", "Fear/threat language found")
    scan(GREED_PATTERNS, 12, "greed_bait", "Too-good-to-be-true bait found")

    return {"score": min(score, 40), "tags": tags, "findings": findings}
