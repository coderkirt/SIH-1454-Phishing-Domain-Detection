from app.services.psychology import analyze_message, analyze_text


def test_urgency_and_fear_hinglish():
    result = analyze_message("Aapka account block ho jayega. Abhi click karo.")
    assert "urgency_detected" in result["tags"]
    assert "fear_tactics" in result["tags"]
    assert result["score"] >= 24


def test_greed_bait():
    result = analyze_text("Congratulations you won a lottery. Claim now!")
    assert "greed_bait" in result["tags"]
    assert result["score"] > 0


def test_clean_message():
    result = analyze_text("Your monthly statement is ready to view in the app.")
    assert result["tags"] == []
    assert result["score"] == 0


def test_credential_pressure():
    result = analyze_message("Enter OTP to complete KYC immediately.")
    assert "credential_pressure" in result["tags"]
    assert "urgency_detected" in result["tags"]


def test_legitimate_countdown_is_not_enough():
    result = analyze_message("Offer expires in 00:32. Shop the Amazon sale.")
    assert "countdown" in result["tags"]
    # Psychological score exists, but the URL checker / risk engine must not
    # treat this as phishing by itself.
    assert result["score"] < 100
