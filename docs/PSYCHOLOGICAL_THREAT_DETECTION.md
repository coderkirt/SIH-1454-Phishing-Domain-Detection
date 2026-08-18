# Psychological Threat Detection 2.0

`app/services/psychology.py` tags message language:

Urgency, Fear, Authority impersonation, Coercion, Financial pressure, Credential request, Countdown, Reward bait, Secrecy, Emotional manipulation.

Hinglish phrases such as `abhi click` and `block ho jayega` are included.

## False-positive rule

Psychological signals **alone cannot** produce HIGH or CRITICAL.

A shopping countdown or a real OTP reminder is not phishing by itself.

HIGH/CRITICAL requires a strong URL, domain, brand, intel, or community signal as well.

`RiskEngine` caps psych-only fusion at 35 (LOW/MEDIUM).
