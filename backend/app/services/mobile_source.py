"""Mobile SMS / WhatsApp native sources.

Chrome cannot read phone SMS or native WhatsApp chats.
This module is the future Android companion contract.
"""

PLANNED = True
STATUS = "PLANNED"
REASON = (
    "Native SMS requires an Android companion app with SMS permission. "
    "Native WhatsApp is not available through a Chrome extension. "
    "Desktop users can paste SMS text or upload a screenshot."
)


class MobileMessageSource:
    """Placeholder for an Android companion posting to POST /api/v1/analyze/content."""

    platform = "android"
    permission = "READ_SMS"
    implemented = False

    def collect(self):
        return {
            "implemented": False,
            "status": STATUS,
            "reason": REASON,
            "accepted_desktop_sources": ["paste_sms", "screenshot", "qr"],
        }
