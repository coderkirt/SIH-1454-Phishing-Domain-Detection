"""Comprehensive tests and CI gating suite for Brand Guidance.

Validates:
1. CI Gate: 100% coverage of KNOWN_BRANDS (no new brand can merge without a guide)
2. Metadata Compliance: official domains, subdomain rules, logo pHash, never-does rules, and regulatory notes
3. Domain Classification Benchmark: 5 legit URLs and 5 phishing URLs per brand (all 25 brands = 250 test URLs)
4. Perceptual logo hashing (Hamming distance and matching thresholds)
"""

import pytest
from app.brand_verifier import (
    classify_brand_url,
    get_brand_registry,
    hamming_distance,
    is_logo_match,
    is_official_domain,
)
from app.corpus import KNOWN_BRANDS, load_corpus


@pytest.fixture(scope="module")
def registry():
    return get_brand_registry()


def test_ci_gating_known_brands_coverage(registry):
    """CI Gating Test: Every declared brand in KNOWN_BRANDS must have a dedicated guidance profile."""
    registered = set(registry.registered_brands)
    missing = KNOWN_BRANDS - registered
    assert not missing, f"CI Gate Failed: The following brands in KNOWN_BRANDS lack guidance guides: {sorted(missing)}"
    assert len(registered) >= len(KNOWN_BRANDS)


def test_brand_metadata_strict_compliance(registry):
    """Ensure every brand profile has complete structured fields."""
    for brand in KNOWN_BRANDS:
        profile = registry.get_profile(brand)
        assert profile is not None, f"Missing profile for brand: {brand}"
        assert len(profile.official_domains) >= 1, f"{brand}: official_domains cannot be empty"
        assert len(profile.logo_phash) == 16, f"{brand}: logo_phash must be a 16-hex character (64-bit) string"
        assert len(profile.never_does) >= 1, f"{brand}: must define at least one 'never_does' security invariant"
        assert len(profile.contact_channels) >= 1, f"{brand}: must define official reporting/contact channels"
        assert len(profile.regulatory_notes) >= 5, f"{brand}: must specify regulatory/compliance references"


# 25 Brands x (5 Legit + 5 Phishing) = 250 Ground-Truth Benchmark Cases
BRAND_TEST_CASES = {
    "sbi": {
        "legit": [
            "https://onlinesbi.sbi/retail/login.htm",
            "https://retail.onlinesbi.sbi/portal",
            "https://sbi.co.in/web/personal-banking",
            "https://bank.sbi/home",
            "https://onlinesbi.sbi",
        ],
        "phishing": [
            "https://onlinesbi-kyc-update.top/login",
            "https://secure-login.onlinesbi.sbi.evilphish.com",
            "https://sbi-rewards-point.xyz/claim",
            "https://onlinesbi-pan-verification.top",
            "https://sbi-netbanking-blocked.online/update",
        ],
    },
    "hdfc": {
        "legit": [
            "https://netbanking.hdfcbank.com/netbanking",
            "https://www.hdfcbank.com/personal",
            "https://hdfcbank.com/login",
            "https://leads.hdfcbank.com/cards",
            "https://hdfcbank.com",
        ],
        "phishing": [
            "https://hdfc-netbanking-verify.xyz",
            "https://hdfc-rewards-points.top/claim",
            "https://secure-hdfcbank.com.phishportal.net",
            "https://hdfc-pan-kyc-alert.online",
            "https://netbanking-hdfc-portal.top",
        ],
    },
    "icici": {
        "legit": [
            "https://infinity.icicibank.com/corp/AuthenticationController",
            "https://www.icicibank.com/personal-banking",
            "https://icicibank.com/login",
            "https://loan.icicibank.com/apply",
            "https://icicibank.com",
        ],
        "phishing": [
            "https://icicibank-login-verify.top",
            "https://icici-rewards-redeem.xyz",
            "https://secure-login.icici-card-protect.online",
            "https://icicibank.com.attackerdomain.in",
            "https://icici-pan-update.site",
        ],
    },
    "axis": {
        "legit": [
            "https://retail.axisbank.co.in/wps/portal/rBanking/axisebanking",
            "https://www.axisbank.com/retail",
            "https://axisbank.com/login",
            "https://cards.axisbank.com",
            "https://axisbank.com",
        ],
        "phishing": [
            "https://axis-kyc-update.xyz",
            "https://axis-netbanking-portal.top",
            "https://axis-card-protect.site",
            "https://retail-axisbank.co.in.fakehost.com",
            "https://axis-pan-unblock.online",
        ],
    },
    "paypal": {
        "legit": [
            "https://www.paypal.com/signin",
            "https://paypal.com/in/webapps/mpp/home",
            "https://paypal.me/businessuser",
            "https://identity.paypal.com/login",
            "https://paypal.com",
        ],
        "phishing": [
            "https://paypal-account-verify.xyz/login",
            "https://paypa1-security-check.com",
            "https://paypal.com.account-notice.top",
            "https://update-paypal-dispute.online",
            "https://paypal-invoice-cancellation.site",
        ],
    },
    "amazon": {
        "legit": [
            "https://www.amazon.com/gp/css/order-history",
            "https://amazon.in/your-orders",
            "https://sellercentral.amazon.com",
            "https://amazon.co.uk",
            "https://amazon.com",
        ],
        "phishing": [
            "https://amazon-order-cancelled.top/support",
            "https://amzn-security.xyz/login",
            "https://amazon.com.order-alert-verify.info",
            "https://amazon-refund-department.online",
            "https://amazon-security-alert.top",
        ],
    },
    "google": {
        "legit": [
            "https://accounts.google.com/signin/v2/identifier",
            "https://myaccount.google.com/security",
            "https://mail.google.com/mail/u/0",
            "https://drive.google.com/drive/my-drive",
            "https://google.com",
        ],
        "phishing": [
            "https://accounts-google-verify.top/login",
            "https://google-storage-full.xyz/upgrade",
            "https://g00gle-login.com/auth",
            "https://google.com.account-suspension.info",
            "https://accounts-google-signin.online",
        ],
    },
    "youtube": {
        "legit": [
            "https://studio.youtube.com/channel",
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtu.be/testvideo",
            "https://tv.youtube.com",
            "https://youtube.com",
        ],
        "phishing": [
            "https://youtube-copyright-strike.top/dispute",
            "https://creator-monetization-review.xyz",
            "https://yt-partner-verify.online",
            "https://youtube.com.claim-reward.top",
            "https://youtube-sponsorship-review.site",
        ],
    },
    "github": {
        "legit": [
            "https://github.com/login",
            "https://api.github.com/user",
            "https://github.blog/news",
            "https://docs.github.com/en",
            "https://github.com",
        ],
        "phishing": [
            "https://github-security-audit.top/auth",
            "https://git-token-expired.xyz",
            "https://github-repo-verify.online",
            "https://github.com.token-recovery.site",
            "https://g1thub-auth.com",
        ],
    },
    "microsoft": {
        "legit": [
            "https://login.microsoftonline.com/common/oauth2/authorize",
            "https://office.com/launch/word",
            "https://account.microsoft.com/security",
            "https://outlook.live.com/owa",
            "https://microsoft.com",
        ],
        "phishing": [
            "https://microsoft-onedrive-document.top/login",
            "https://office365-password-expiry.xyz",
            "https://micros0ft-auth.online",
            "https://login.microsoftonline.com.fakeportal.info",
            "https://microsoft-security-admin.site",
        ],
    },
    "apple": {
        "legit": [
            "https://appleid.apple.com/sign-in",
            "https://www.icloud.com/find",
            "https://support.apple.com",
            "https://developer.apple.com/account",
            "https://apple.com",
        ],
        "phishing": [
            "https://findmy-iphone-alert.top/track",
            "https://icloud-storage-locked.xyz/verify",
            "https://appleid-verification.online",
            "https://apple.com.device-locate.site",
            "https://app1e-security-id.com",
        ],
    },
    "paytm": {
        "legit": [
            "https://paytm.com/recharge",
            "https://business.paytm.com",
            "https://paytmbank.com",
            "https://developer.paytm.com",
            "https://paytm.com",
        ],
        "phishing": [
            "https://paytm-kyc-unblock.top/update",
            "https://paytm-wallet-cashback.xyz",
            "https://paytm-fastag-recharge.online",
            "https://paytm.com.wallet-verify.site",
            "https://paytm-kyc-officer.info",
        ],
    },
    "phonepe": {
        "legit": [
            "https://www.phonepe.com/business-solutions",
            "https://phonepe.com/en",
            "https://phonepe.com/merchant",
            "https://blog.phonepe.com",
            "https://phonepe.com",
        ],
        "phishing": [
            "https://phonepe-reward-scratch.top/claim",
            "https://phonepe-collect-bonus.xyz",
            "https://phonepe-kyc-update.online",
            "https://phonepe.com.reward-spin.site",
            "https://phonepe-cashback-portal.top",
        ],
    },
    "irctc": {
        "legit": [
            "https://www.irctc.co.in/nget/train-search",
            "https://irctc.co.in",
            "https://irctctourism.com",
            "https://air.irctc.co.in",
            "https://catering.irctc.co.in",
        ],
        "phishing": [
            "https://irctc-tatkal-booking.top/download",
            "https://irctc-ticket-refund.xyz/claim",
            "https://irctc-agent-portal.online",
            "https://irctc.co.in.tatkal-agent.site",
            "https://irctc-train-booking-app.top",
        ],
    },
    "flipkart": {
        "legit": [
            "https://www.flipkart.com/account/orders",
            "https://flipkart.com",
            "https://seller.flipkart.com",
            "https://stories.flipkart.com",
            "https://flipkart.com/plus",
        ],
        "phishing": [
            "https://flipkart-bigbillion-sale.top/deals",
            "https://flipkart-lucky-draw.xyz/claim",
            "https://flipkart-spin-wheel.online",
            "https://flipkart.com.free-iphone.site",
            "https://flipkart-flash-deals.top",
        ],
    },
    "whatsapp": {
        "legit": [
            "https://web.whatsapp.com",
            "https://www.whatsapp.com/download",
            "https://api.whatsapp.com/send",
            "https://faq.whatsapp.com",
            "https://whatsapp.com",
        ],
        "phishing": [
            "https://web-whatsapp-sync.top/login",
            "https://wa-web-auth.xyz/qr",
            "https://whatsapp-gold-download.online",
            "https://web.whatsapp.com.attacker.site",
            "https://whatsapp-verification-code.info",
        ],
    },
    "instagram": {
        "legit": [
            "https://www.instagram.com/accounts/login",
            "https://instagram.com",
            "https://about.instagram.com",
            "https://help.instagram.com",
            "https://business.instagram.com",
        ],
        "phishing": [
            "https://instagram-copyright-infringement.top/appeal",
            "https://ig-blue-badge-verify.xyz",
            "https://instagram-appeal.online",
            "https://instagram.com.badge-claim.site",
            "https://1nstagram-verify.com",
        ],
    },
    "facebook": {
        "legit": [
            "https://www.facebook.com/login.php",
            "https://fb.com",
            "https://meta.com",
            "https://business.facebook.com",
            "https://facebook.com",
        ],
        "phishing": [
            "https://meta-business-suite-suspend.top/appeal",
            "https://facebook-page-violation.xyz",
            "https://fb-support-chat.online",
            "https://facebook.com.security-appeal.site",
            "https://faceb00k-login.com",
        ],
    },
    "netflix": {
        "legit": [
            "https://www.netflix.com/login",
            "https://netflix.com/browse",
            "https://help.netflix.com",
            "https://jobs.netflix.com",
            "https://netflix.com",
        ],
        "phishing": [
            "https://netflix-account-onhold.top/billing",
            "https://update-netflix-payment.xyz",
            "https://netflix-free-year.online",
            "https://netflix.com.update-card.site",
            "https://netfl1x-verify.com",
        ],
    },
    "uidai": {
        "legit": [
            "https://uidai.gov.in",
            "https://myaadhaar.uidai.gov.in",
            "https://resident.uidai.gov.in",
            "https://eaadhaar.uidai.gov.in",
            "https://appointments.uidai.gov.in",
        ],
        "phishing": [
            "https://aadhaar-biometric-unlock.top/verify",
            "https://uidai-pan-link.xyz",
            "https://download-eaadhaar-free.online",
            "https://uidai.gov.in.commercial-portal.com",
            "https://aadhaar-verification-portal.site",
        ],
    },
    "incometax": {
        "legit": [
            "https://incometax.gov.in/iec/foportal",
            "https://efiling.incometax.gov.in",
            "https://eportal.incometax.gov.in",
            "https://incometax.gov.in",
            "https://www.incometax.gov.in",
        ],
        "phishing": [
            "https://incometax-refund-approved.top/claim",
            "https://it-refund-portal.xyz/verify",
            "https://pan-card-tax-update.online",
            "https://incometax.gov.in.tax-refund.org",
            "https://efiling-incometax-portal.site",
        ],
    },
    "fedex": {
        "legit": [
            "https://www.fedex.com/en-us/tracking.html",
            "https://fedex.com",
            "https://crossborder.fedex.com",
            "https://developer.fedex.com",
            "https://fedex.com/in",
        ],
        "phishing": [
            "https://fedex-customs-fee.top/pay",
            "https://track-fedex-package.xyz/address",
            "https://fedex-delivery-hold.online",
            "https://fedex.com.parcel-notice.site",
            "https://fedx-courier-track.com",
        ],
    },
    "dhl": {
        "legit": [
            "https://www.dhl.com/en/express/tracking.html",
            "https://mydhl.express.dhl",
            "https://dhl.com",
            "https://express.dhl",
            "https://supplychain.dhl.com",
        ],
        "phishing": [
            "https://dhl-tracking-portal.top/login",
            "https://dhl-customs-clearance.xyz",
            "https://dhl-package-pending.online",
            "https://dhl.com.clearance-notice.site",
            "https://dh1-express-tracking.com",
        ],
    },
    "linkedin": {
        "legit": [
            "https://www.linkedin.com/login",
            "https://linkedin.com/feed",
            "https://learning.linkedin.com",
            "https://business.linkedin.com",
            "https://linkedin.com",
        ],
        "phishing": [
            "https://linkedin-message-alert.top/view",
            "https://linkedin-job-offer.xyz/apply",
            "https://lnkedin-verify.com",
            "https://linkedin.com.message-notification.site",
            "https://linkedin-account-security.online",
        ],
    },
    "naukri": {
        "legit": [
            "https://www.naukri.com/mnjuser/homepage",
            "https://naukri.com",
            "https://naukrigulf.com",
            "https://resdex.naukri.com",
            "https://naukri.com/jobs-in-india",
        ],
        "phishing": [
            "https://naukri-job-selection.top/offer",
            "https://naukri-interview-letter.xyz",
            "https://naukri-registration-fee.online",
            "https://naukri.com.gate-pass.site",
            "https://naukr1-career-portal.com",
        ],
    },
}


def test_domain_classification_benchmark():
    """Evaluate domain classification benchmark: 100% precision on 125 legit and 125 phishing URLs."""
    for brand, cases in BRAND_TEST_CASES.items():
        # 1. Test Legit URLs
        for legit_url in cases["legit"]:
            is_valid = is_official_domain(brand, legit_url)
            assert is_valid is True, f"False Negative: Official URL '{legit_url}' rejected for brand '{brand}'"

            classification = classify_brand_url(brand, legit_url)
            assert classification["is_official"] is True
            assert classification["status"] == "OFFICIAL"

        # 2. Test Phishing URLs
        for phish_url in cases["phishing"]:
            is_valid = is_official_domain(brand, phish_url)
            assert is_valid is False, f"False Positive: Phishing URL '{phish_url}' accepted as official for '{brand}'"

            classification = classify_brand_url(brand, phish_url)
            assert classification["is_official"] is False
            assert classification["status"] in ("PHISHING_LOOKALIKE", "THIRD_PARTY")


def test_perceptual_hash_matching():
    """Verify perceptual hash (pHash) Hamming distance calculations."""
    phash_orig = "a3f0c1b4892c5d1e"
    # Identical hash: distance 0
    assert hamming_distance(phash_orig, phash_orig) == 0
    assert is_logo_match(phash_orig, phash_orig) is True

    # 1-bit difference: Hamming distance 1 (match)
    phash_close = "a3f0c1b4892c5d1f"
    assert hamming_distance(phash_orig, phash_close) == 1
    assert is_logo_match(phash_orig, phash_close, max_distance=10) is True

    # Completely different logo: distance > 20 (reject)
    phash_diff = "5c6d7e8f9a0b1e2f"
    assert hamming_distance(phash_orig, phash_diff) > 15
    assert is_logo_match(phash_orig, phash_diff, max_distance=10) is False
