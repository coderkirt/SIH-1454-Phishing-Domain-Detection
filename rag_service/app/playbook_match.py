"""Keyword playbook matcher.

Retrieval can attach the wrong scam note when a URL only says "verify".
This scorer reads the address, the message, and the threat tags, and picks
a playbook only when the words actually belong to that scam.
"""

from __future__ import annotations

import re
from typing import List, Optional, Sequence, Tuple

from app.corpus import CorpusDocument, load_corpus

# (playbook id, list of (points, pattern)). Patterns are applied to a
# lowercased blob of the URL, message, and tags.
_RULES: List[Tuple[str, List[Tuple[int, str]]]] = [
    (
        "playbook-prize-lottery-bait",
        [
            (6, r"\b(lottery|lucky draw|jackpot|prize money|you have won|you won|kbc|cashback|winnings)\b"),
            (4, r"\b(congratulations|congratulation|winner|won)\b"),
            (3, r"\b(prize|reward points)\b"),
        ],
    ),
    (
        "playbook-account-suspension-lure",
        [
            (6, r"\b(suspended|suspension|account locked|unusual activity|unauthorized login|reactivate|deactivat\w*)\b"),
            (4, r"\b(verify|verification|login|log-in|signin|sign-in|secure-login|netbanking)\b"),
            (2, r"\b(password|account)\b"),
        ],
    ),
    (
        "playbook-otp-kyc-theft",
        [
            (6, r"\b(kyc update|update your kyc|enter otp|aadhaar|aadhar|pan card)\b"),
            (3, r"\b(kyc|otp)\b"),
        ],
    ),
    (
        "playbook-upi-collect-request",
        [
            (6, r"\b(upi collect|upi pin|collect request)\b"),
            (3, r"\bupi\b"),
        ],
    ),
    (
        "playbook-tax-refund-impersonation",
        [
            (6, r"\b(income tax|tax refund|itr refund)\b"),
        ],
    ),
    (
        "playbook-delivery-parcel-scam",
        [
            (6, r"\b(parcel|fedex|dhl|customs fee|could not be delivered)\b"),
        ],
    ),
    (
        "playbook-electricity-utility-disconnection",
        [
            (6, r"\b(electricity|power will be disconnected|unpaid bill)\b"),
        ],
    ),
    (
        "playbook-job-task-investment-scam",
        [
            (6, r"\b(work from home|part-time job|like youtube|task scam)\b"),
        ],
    ),
    (
        "playbook-crypto-investment-pig-butchering",
        [
            (6, r"\b(crypto|usdt|bitcoin|telegram pool)\b"),
        ],
    ),
    (
        "playbook-ceo-fraud-bec",
        [
            (6, r"\b(wire transfer|ceo|confidential)\b"),
        ],
    ),
    (
        "playbook-tech-support-remote-access",
        [
            (6, r"\b(tech support|anydesk|teamviewer|trojan|do not shut down)\b"),
        ],
    ),
    (
        "playbook-sextortion-blackmail-threat",
        [
            (6, r"\b(webcam|sextortion|adult websites|leak video)\b"),
        ],
    ),
    (
        "playbook-romance-catfishing-bait",
        [
            (5, r"\b(my love|gold jewelry|customs demands)\b"),
        ],
    ),
    (
        "playbook-sim-swap-telecom-verification",
        [
            (6, r"\b(sim card|esim|deactivate in)\b"),
        ],
    ),
    (
        "playbook-quishing-qr",
        [
            (6, r"\b(qr code|scan this qr)\b"),
        ],
    ),
    (
        "playbook-fake-invoice-billing-dispute",
        [
            (5, r"\b(auto-renewed|invoice|billing support)\b"),
        ],
    ),
]

_MIN_SCORE = 4


def _blob(scan_url: str, content_text: str, threat_tags: Sequence[str]) -> str:
    parts = [scan_url or "", content_text or "", " ".join(threat_tags or [])]
    text = " ".join(parts).lower().replace("-", " ").replace("_", " ").replace("/", " ")
    return re.sub(r"\s+", " ", text)


def score_playbooks(scan_url: str = "", content_text: str = "", threat_tags: Optional[Sequence[str]] = None) -> List[Tuple[str, int]]:
    """Return (playbook id, score) pairs, highest first. Zero scores are omitted."""
    text = _blob(scan_url, content_text, threat_tags or [])
    scored: List[Tuple[str, int]] = []
    for playbook_id, patterns in _RULES:
        total = 0
        for points, pattern in patterns:
            hits = {hit for hit in re.findall(pattern, text) if hit}
            total += points * len(hits)
        if total:
            scored.append((playbook_id, total))
    # "kyc" inside a verify/login address is still an account lure, not a prize
    # and not a separate OTP scam, unless the message actually asks for an OTP.
    by_id = dict(scored)
    account = by_id.get("playbook-account-suspension-lure", 0)
    if account >= 4 and not re.search(r"\b(enter otp|kyc update|update your kyc|aadhaar|aadhar|pan card)\b", text):
        by_id["playbook-otp-kyc-theft"] = 0
    if account >= 4 and not re.search(r"\b(lottery|jackpot|prize|won|winner|cashback|congratulations)\b", text):
        by_id["playbook-prize-lottery-bait"] = 0
    scored = [(playbook_id, points) for playbook_id, points in by_id.items() if points]
    scored.sort(key=lambda item: item[1], reverse=True)
    return scored


def match_playbook(
    scan_url: str = "",
    content_text: str = "",
    threat_tags: Optional[Sequence[str]] = None,
) -> Optional[CorpusDocument]:
    """Return the playbook document when one scam is clearly ahead of the others."""
    scored = score_playbooks(scan_url, content_text, threat_tags)
    if not scored or scored[0][1] < _MIN_SCORE:
        return None
    if len(scored) > 1 and scored[0][1] < scored[1][1] + 2:
        return None
    winner = scored[0][0]
    for doc in load_corpus():
        if doc.id == winner and doc.category == "playbook":
            return doc
    return None
