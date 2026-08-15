from app.services.psychology import analyze_text


def test_urgency_and_fear_hinglish():
    result = analyze_text("Aapka account block ho jayega. Abhi click karo.")
    assert "urgency_detected" in result["tags"]
    assert "fear_tactics" in result["tags"]
    assert result["score"] >= 30


def test_greed_bait():
    result = analyze_text("Congratulations you won a lottery. Claim now!")
    assert "greed_bait" in result["tags"]
    assert result["score"] > 0


def test_clean_message():
    result = analyze_text("Your monthly statement is ready to view in the app.")
    assert result["tags"] == []
    assert result["score"] == 0
