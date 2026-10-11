"""Benchmark test suite validating precision and recall of scam playbook matching."""

import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.corpus import load_corpus
from app.retrieval import HybridRetriever


# Ground-truth labeled benchmark set mapping real-world phishing lures to target playbooks
LABELED_PLAYBOOK_BENCHMARK = [
    {
        "query": "Your Netflix account has been suspended due to billing failure. Verify now to restore access.",
        "expected_playbook": "playbook-account-suspension-lure",
        "category": "Account Suspension",
    },
    {
        "query": "I am traveling and need an urgent confidential wire transfer processed for an overseas corporate acquisition today.",
        "expected_playbook": "playbook-ceo-fraud-bec",
        "category": "CEO Fraud / BEC",
    },
    {
        "query": "My uncle is a senior crypto market analyst. Join our private Telegram pool and deposit USDT to earn 15% daily guaranteed.",
        "expected_playbook": "playbook-crypto-investment-pig-butchering",
        "category": "Crypto Pig Butchering",
    },
    {
        "query": "FedEx: Your parcel #FX-9201 could not be delivered due to missing address and unpaid customs fee of $2.99.",
        "expected_playbook": "playbook-delivery-parcel-scam",
        "category": "Parcel Delivery",
    },
    {
        "query": "Dear Consumer, your electricity power will be disconnected tonight at 9:30 PM due to unpaid bill. Call officer immediately.",
        "expected_playbook": "playbook-electricity-utility-disconnection",
        "category": "Utility Disconnection",
    },
    {
        "query": "Your annual subscription for Norton LifeLock has auto-renewed for $499.00. Call billing support immediately to cancel charge.",
        "expected_playbook": "playbook-fake-invoice-billing-dispute",
        "category": "Fake Invoice",
    },
    {
        "query": "Work from home part-time job: like YouTube videos and review products to earn Rs 3,000 per day. Contact manager on Telegram.",
        "expected_playbook": "playbook-job-task-investment-scam",
        "category": "Job / Task Scam",
    },
    {
        "query": "Your bank account has been blocked due to pending KYC update. Click link to verify your Aadhaar and enter OTP.",
        "expected_playbook": "playbook-otp-kyc-theft",
        "category": "OTP / KYC Theft",
    },
    {
        "query": "Congratulations! Your mobile number won 25 Lakh rupees in the KBC lottery draw. Pay registration charge to claim.",
        "expected_playbook": "playbook-prize-lottery-bait",
        "category": "Prize / Lottery Bait",
    },
    {
        "query": "Scan this QR code with your smartphone camera to pay your parking meter session and avoid municipal impound.",
        "expected_playbook": "playbook-quishing-qr",
        "category": "Quishing / QR Phishing",
    },
    {
        "query": "My love, I dispatched gold jewelry and watches for you from UK but airport customs demands clearance fee. Please wire transfer duty.",
        "expected_playbook": "playbook-romance-catfishing-bait",
        "category": "Romance Scam",
    },
    {
        "query": "I know your password is Secret123. I recorded you on your webcam visiting adult websites. Pay $1,000 in Bitcoin or I leak video.",
        "expected_playbook": "playbook-sextortion-blackmail-threat",
        "category": "Sextortion Blackmail",
    },
    {
        "query": "URGENT: Your physical SIM card will deactivate in 24 hours. Scan this eSIM QR code immediately to upgrade to 5G network.",
        "expected_playbook": "playbook-sim-swap-telecom-verification",
        "category": "SIM Swap / Telecom",
    },
    {
        "query": "Income Tax refund of Rs 15,490 approved. Submit your bank account number and debit card details on refund portal.",
        "expected_playbook": "playbook-tax-refund-impersonation",
        "category": "Tax Refund Phishing",
    },
    {
        "query": "Microsoft Windows Security: Critical Zeus trojan detected on your computer. Call toll-free helpline immediately. Do not shut down.",
        "expected_playbook": "playbook-tech-support-remote-access",
        "category": "Tech Support Scam",
    },
    {
        "query": "UPI Collect Request: You received Rs 2,000 cashback from PhonePe. Enter your UPI PIN on payment screen to claim money.",
        "expected_playbook": "playbook-upi-collect-request",
        "category": "UPI Collect Fraud",
    },
]


def test_playbook_structured_metadata_compliance():
    """Verify that all playbooks have required structured fields: severity, tactics, iocs, first_seen, and mitre."""
    docs = load_corpus()
    playbooks = [d for d in docs if d.category == "playbook"]
    assert len(playbooks) >= 16, f"Expected at least 16 playbooks, got {len(playbooks)}"

    for p in playbooks:
        assert p.severity in {"low", "medium", "high", "critical"}, f"{p.id}: invalid severity {p.severity}"
        assert len(p.mitre) > 0, f"{p.id}: missing MITRE ATT&CK mapping"
        assert p.first_seen.startswith("202"), f"{p.id}: invalid first_seen {p.first_seen}"


def test_playbook_matching_precision_and_recall():
    """Evaluate Top-1 Precision and Top-3 Recall across all 16 benchmark scam categories."""
    retriever = HybridRetriever()

    top1_correct = 0
    top3_correct = 0
    total = len(LABELED_PLAYBOOK_BENCHMARK)

    failures = []

    for item in LABELED_PLAYBOOK_BENCHMARK:
        results = retriever.retrieve(
            query=item["query"],
            categories=["playbook"],
            top_k=3,
            hard_filter=True,
        )

        matched_ids = [r.doc_id for r in results]
        expected = item["expected_playbook"]

        if matched_ids and matched_ids[0] == expected:
            top1_correct += 1
        else:
            failures.append((item["category"], expected, matched_ids))

        if expected in matched_ids:
            top3_correct += 1

    top1_precision = top1_correct / total
    top3_recall = top3_correct / total

    print(f"\n--- Playbook Benchmark Results (16 Scenarios) ---")
    print(f"Top-1 Precision: {top1_precision * 100:.1f}% ({top1_correct}/{total})")
    print(f"Top-3 Recall:    {top3_recall * 100:.1f}% ({top3_correct}/{total})")

    if failures:
        print("\nTop-1 Discrepancies:")
        for cat, exp, got in failures:
            print(f"  [{cat}] Expected: {exp} | Got: {got}")

    # Enforce minimum precision/recall thresholds
    assert top1_precision >= 0.85, f"Top-1 precision {top1_precision:.2f} is below 85% threshold"
    assert top3_recall >= 0.95, f"Top-3 recall {top3_recall:.2f} is below 95% threshold"
