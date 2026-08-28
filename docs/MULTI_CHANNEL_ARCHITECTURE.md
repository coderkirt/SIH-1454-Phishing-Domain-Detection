# Multi-channel architecture

PhishShield / CyberGuard is a **modular monolith**. Every channel normalizes into one pipeline.

```
URL | pasted email | WhatsApp text | SMS paste | webpage | QR | screenshot
                              |
                      ContentNormalizer
                              |
                 urls[] + text + sender + language
                              |
        +----------+----------+-----------+
        |          |          |           |
   URLChecker  Psychology  Brand/Sender  Reputation
        |          |          |           |
        +----------+----------+-----------+
                              |
                         RiskEngine
                              |
                    Simple View / Technical View
```

## Honesty limits
- Chrome extension cannot read phone SMS.
- WhatsApp Web / Gmail only if the user pastes content or a future extension reads **visible** DOM with permission.
- Psychological language alone cannot mark CRITICAL (false-positive guard).
- Community reports are a signal, not proof.
- Model confidence ≠ accuracy.
