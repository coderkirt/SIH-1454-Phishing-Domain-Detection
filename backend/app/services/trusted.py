"""Well-known official sites.

A hostname on this list is treated as the real company website: noisy
PhishTank/OpenPhish path matches (for example any YouTube /watch URL)
must not burn the whole domain. This is not a proof of safety for
user-content hosts such as sites.google.com or github.io.
"""

from typing import Optional

from app.services.url_normalize import get_registrable_domain

TRUSTED_DOMAINS = {
    # Google / YouTube
    "google.com", "google.co.in", "google.co.uk", "google.de", "google.fr",
    "google.co.jp", "google.ca", "google.com.au", "google.com.br",
    "google.es", "google.it", "google.co.kr", "google.ru", "google.com.mx",
    "google.com.tr", "google.com.sg", "google.com.hk", "google.co.id",
    "google.com.ar", "google.com.ua", "google.com.eg", "google.co.th",
    "google.com.pk", "google.com.sa", "google.com.vn", "google.com.ph",
    "google.com.my", "google.com.ng", "google.co.za", "google.ae",
    "gmail.com", "googlemail.com", "googleusercontent.com", "googleapis.com",
    "gstatic.com", "ggpht.com", "googlevideo.com", "googleadservices.com",
    "googlesyndication.com", "doubleclick.net", "withgoogle.com", "googleblog.com",
    "blogger.com", "android.com", "chrome.com", "chromium.org",
    "youtube.com", "youtu.be", "ytimg.com", "youtube-nocookie.com",
    "youtubekids.com", "youtubeeducation.com",
    # Microsoft
    "microsoft.com", "microsoftonline.com", "live.com", "outlook.com",
    "office.com", "office365.com", "sharepoint.com", "azure.com",
    "windows.com", "xbox.com", "bing.com", "msn.com", "skype.com",
    "github.com", "githubusercontent.com", "githubassets.com", "githubapp.com",
    "visualstudio.com", "vscode.dev", "npmjs.com", "nuget.org",
    # Apple
    "apple.com", "icloud.com", "me.com", "mzstatic.com", "aaplimg.com",
    # Meta
    "facebook.com", "fb.com", "fbcdn.net", "instagram.com", "cdninstagram.com",
    "whatsapp.com", "whatsapp.net", "messenger.com", "oculus.com", "meta.com",
    # Amazon
    "amazon.com", "amazon.in", "amazon.co.uk", "amazon.de", "amazon.co.jp",
    "amazon.ca", "amazon.fr", "amazon.es", "amazon.it", "amazon.com.au",
    "amazon.com.br", "amazonaws.com", "aws.amazon.com", "a2z.com",
    # Payments / Indian banks
    "paypal.com", "stripe.com", "visa.com", "mastercard.com",
    "paytm.com", "phonepe.com", "razorpay.com", "bhimupi.org.in",
    "npci.org.in", "sbi.co.in", "onlinesbi.sbi", "bank.sbi",
    "hdfcbank.com", "icicibank.com", "axisbank.com", "kotak.com",
    "yesbank.in", "pnbindia.in", "unionbankofindia.co.in", "canarabank.com",
    "irctc.co.in", "uidai.gov.in", "incometax.gov.in", "rbi.org.in",
    "india.gov.in", "mygov.in", "digilocker.gov.in",
    # Commerce / media / India
    "flipkart.com", "myntra.com", "ajio.com", "nykaa.com",
    "zomato.com", "swiggy.com", "bookmyshow.com", "makemytrip.com",
    "goibibo.com", "ola.com", "uber.com", "hotstar.com", "jiocinema.com",
    "jio.com", "airtel.in", "reliancedigital.in",
    # Global consumer
    "wikipedia.org", "wikimedia.org", "linkedin.com", "twitter.com", "x.com",
    "reddit.com", "netflix.com", "spotify.com", "twitch.tv", "discord.com",
    "discordapp.com", "telegram.org", "t.me", "zoom.us", "slack.com",
    "dropbox.com", "box.com", "adobe.com", "canva.com", "figma.com",
    "notion.so", "atlassian.com", "bitbucket.org", "trello.com", "asana.com",
    "salesforce.com", "oracle.com", "ibm.com", "intel.com", "nvidia.com",
    "cloudflare.com", "cloudflare.net", "mozilla.org", "firefox.com",
    "phishtank.com", "phishtank.net",
    "stackoverflow.com", "stackexchange.com", "quora.com",
    "bbc.com", "bbc.co.uk", "cnn.com", "nytimes.com", "reuters.com",
    "yahoo.com", "duckduckgo.com", "pinterest.com", "tumblr.com",
    "tiktok.com", "snapchat.com", "vimeo.com", "imdb.com",
    "booking.com", "airbnb.com", "expedia.com",
    "openai.com", "chatgpt.com", "anthropic.com", "claude.ai",
    "huggingface.co", "python.org", "pypi.org", "nodejs.org",
    "docker.com", "kubernetes.io", "ubuntu.com", "debian.org",
    "psitkanpur.com",
}

# Hosts that sit on a trusted registrable domain but serve arbitrary user pages.
USER_CONTENT_HOSTS = {
    "sites.google.com",
    "docs.google.com",
    "forms.google.com",
    "script.google.com",
    "sheets.google.com",
    "slides.google.com",
    "drive.google.com",
    "storage.googleapis.com",
    "firebasestorage.googleapis.com",
    "blogspot.com",
    "blogger.com",
    "github.io",
    "gist.github.com",
    "raw.githubusercontent.com",
    "camo.githubusercontent.com",
    "objects.githubusercontent.com",
}

# High-traffic official paths. A dump row for one /watch or /search URL
# must not flag every other video or search on that site.
GENERIC_TRUSTED_PATHS = {
    "/", "/search", "/watch", "/results", "/feed", "/explore", "/trending",
    "/login", "/signin", "/signup", "/register", "/account", "/settings",
    "/url", "/imgres", "/maps", "/mail", "/webhp", "/imghp", "/pref",
    "/home", "/about", "/help", "/support", "/privacy", "/terms",
    "/new", "/notifications", "/messages", "/inbox", "/compose",
    "/c", "/channel", "/playlist", "/embed", "/shorts", "/live",
    "/features", "/pricing", "/blog", "/docs", "/download",
}

_GENERIC_FIRST_SEGMENTS = {
    "search", "watch", "results", "feed", "explore", "login", "signin",
    "signup", "account", "settings", "url", "maps", "mail", "home",
    "about", "help", "privacy", "terms", "notifications", "messages",
    "channel", "playlist", "embed", "shorts", "live", "c", "user",
    "hashtag", "tag", "category", "topics",
}


def _bare_host(hostname: str) -> str:
    host = (hostname or "").split(":")[0].lower().strip(".")
    if host.startswith("www."):
        host = host[4:]
    return host


def is_user_content_host(hostname: str) -> bool:
    host = _bare_host(hostname)
    if not host:
        return False
    for listed in USER_CONTENT_HOSTS:
        if host == listed or host.endswith("." + listed):
            return True
    return False


def is_trusted_destination(
    hostname: Optional[str] = None,
    registered_domain: Optional[str] = None,
) -> bool:
    """True for official Google / GitHub / YouTube style sites, not Sites/gists."""
    host = _bare_host(hostname or "")
    if is_user_content_host(host):
        return False
    domain = (registered_domain or "").lower() or get_registrable_domain(host)
    return bool(domain) and domain in TRUSTED_DOMAINS


def is_generic_trusted_path(path: str) -> bool:
    normalized = (path or "/").rstrip("/") or "/"
    if normalized in GENERIC_TRUSTED_PATHS:
        return True
    parts = [part for part in normalized.split("/") if part]
    if len(parts) == 1 and parts[0].lower() in _GENERIC_FIRST_SEGMENTS:
        return True
    return False
