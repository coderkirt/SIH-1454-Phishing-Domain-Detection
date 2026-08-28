"""TLS / SSL certificate inspection for scanned HTTPS hosts.

A padlock is not proof of safety — many phishing sites have valid certificates.
This module still records issuer, expiry, hostname match and chain trust so the
Technical View can show them. Connections are blocked by the SSRF guard first.
"""

from __future__ import annotations

import os
import ssl
import socket
import tempfile
from datetime import datetime, timezone
from typing import Dict, Optional
from urllib.parse import urlparse

from app.services.ssrf import UnsafeURLError, assert_public_http_url

ENABLE_ONLINE_CHECKS = os.getenv("ENABLE_ONLINE_CHECKS", "true").strip().lower() != "false"
TIMEOUT_SECONDS = 5.0


def _empty(**overrides) -> Dict:
    data = {
        "checked": False,
        "status": "not_checked",
        "label": "Not checked",
        "issuer": None,
        "subject": None,
        "valid_from": None,
        "valid_to": None,
        "days_remaining": None,
        "hostname_ok": None,
        "chain_ok": None,
        "self_signed": None,
        "error": None,
        "risk_points": 0,
        "findings": [],
        "tags": [],
    }
    data.update(overrides)
    return data


def _name_value(entries, key: str) -> Optional[str]:
    for rdn in entries or ():
        for field, value in rdn:
            if field == key:
                return value
    return None


def _parse_cert_dict(cert: dict, host: str) -> Dict:
    subject = _name_value(cert.get("subject"), "commonName") or host
    issuer = _name_value(cert.get("issuer"), "organizationName") or _name_value(
        cert.get("issuer"), "commonName"
    )
    subject_org = _name_value(cert.get("subject"), "organizationName")
    issuer_cn = _name_value(cert.get("issuer"), "commonName")
    not_before = cert.get("notBefore")
    not_after = cert.get("notAfter")
    days_remaining = None
    expired = False
    if not_after:
        try:
            expiry = datetime.fromtimestamp(ssl.cert_time_to_seconds(not_after), tz=timezone.utc)
            days_remaining = int((expiry - datetime.now(timezone.utc)).total_seconds() // 86400)
            expired = days_remaining < 0
            not_after = expiry.strftime("%Y-%m-%d")
        except (ValueError, OverflowError, OSError):
            pass
    if not_before:
        try:
            start = datetime.fromtimestamp(ssl.cert_time_to_seconds(not_before), tz=timezone.utc)
            not_before = start.strftime("%Y-%m-%d")
        except (ValueError, OverflowError, OSError):
            pass

    self_signed = bool(
        issuer_cn and subject and issuer_cn.lower() == subject.lower() and not issuer
    ) or bool(subject_org and issuer and subject_org.lower() == issuer.lower() and issuer_cn == subject)

    sans = [value for kind, value in cert.get("subjectAltName") or () if kind == "DNS"]
    return {
        "subject": subject,
        "issuer": issuer or issuer_cn,
        "valid_from": not_before,
        "valid_to": not_after,
        "days_remaining": days_remaining,
        "expired": expired,
        "self_signed": self_signed,
        "san": sans[:8],
    }


def _decode_pem(pem: str) -> dict:
    handle, path = tempfile.mkstemp(suffix=".pem")
    try:
        os.write(handle, pem.encode("ascii", errors="ignore"))
        os.close(handle)
        decode = getattr(ssl._ssl, "_test_decode_cert", None)
        if not decode:
            return {}
        return decode(path)
    except Exception:
        return {}
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass


def inspect_tls(url: str) -> Dict:
    """Return certificate facts and risk points. Fail-soft on timeout or SSRF."""
    if not ENABLE_ONLINE_CHECKS:
        return _empty(status="disabled", label="Online TLS checks are disabled")

    parsed = urlparse(url if "://" in url else f"https://{url}")
    if parsed.scheme == "http":
        return _empty(
            status="http",
            label="No TLS — site is HTTP, not HTTPS",
            findings=["Site uses HTTP instead of HTTPS"],
            tags=["no_https"],
            risk_points=0,
            checked=True,
        )
    if parsed.scheme != "https":
        return _empty(status="skipped", label="Not an HTTPS URL")

    host = (parsed.hostname or "").lower().rstrip(".")
    port = parsed.port or 443
    if not host:
        return _empty(status="skipped", label="Missing host")

    try:
        assert_public_http_url(f"https://{host}:{port}/")
    except UnsafeURLError as exc:
        return _empty(status="blocked", label="TLS check skipped (SSRF guard)", error=str(exc))

    verified = False
    hostname_ok = False
    chain_ok = False
    verify_error = None
    cert_dict = None

    try:
        context = ssl.create_default_context()
        with socket.create_connection((host, port), timeout=TIMEOUT_SECONDS) as sock:
            with context.wrap_socket(sock, server_hostname=host) as ssock:
                cert_dict = ssock.getpeercert()
                verified = True
                hostname_ok = True
                chain_ok = True
    except ssl.SSLCertVerificationError as exc:
        verify_error = exc.verify_message or str(exc)
        lowered = verify_error.lower()
        hostname_ok = "hostname" not in lowered
        chain_ok = "hostname" in lowered
    except (socket.timeout, TimeoutError):
        return _empty(status="timeout", label="TLS handshake timed out", error="timeout", checked=True)
    except OSError as exc:
        return _empty(status="unreachable", label="Could not open a TLS connection", error=str(exc)[:160], checked=True)

    if cert_dict is None:
        try:
            try:
                pem = ssl.get_server_certificate((host, port), timeout=TIMEOUT_SECONDS)
            except TypeError:
                pem = ssl.get_server_certificate((host, port))
            cert_dict = _decode_pem(pem)
        except Exception:
            cert_dict = {}

    parsed_cert = _parse_cert_dict(cert_dict, host) if cert_dict else {}
    findings = []
    tags = []
    points = 0

    if verified:
        status = "ok"
        label = f"Valid certificate from {parsed_cert.get('issuer') or 'a trusted CA'}"
    elif verify_error and "hostname" in verify_error.lower():
        status = "hostname_mismatch"
        label = "Certificate hostname does not match this site"
        findings.append("TLS hostname mismatch — the certificate is for a different name")
        tags.append("tls_hostname_mismatch")
        points += 30
        hostname_ok = False
        chain_ok = True
    elif parsed_cert.get("self_signed") or (verify_error and "self signed" in verify_error.lower()):
        status = "self_signed"
        label = "Self-signed or untrusted TLS certificate"
        findings.append("Self-signed or untrusted TLS certificate")
        tags.append("tls_untrusted")
        points += 20
        hostname_ok = hostname_ok if verify_error else None
        chain_ok = False
    elif verify_error:
        status = "untrusted"
        label = "TLS certificate could not be verified"
        findings.append(f"TLS verification failed: {verify_error[:120]}")
        tags.append("tls_untrusted")
        points += 18
        chain_ok = False
    else:
        status = "unknown"
        label = "TLS certificate could not be read"

    if parsed_cert.get("expired"):
        findings.append("TLS certificate has expired")
        tags.append("tls_expired")
        points += 25
        if status == "ok":
            status = "expired"
            label = "TLS certificate has expired"
            verified = False
    elif parsed_cert.get("days_remaining") is not None and parsed_cert["days_remaining"] <= 7:
        findings.append(f"TLS certificate expires in {parsed_cert['days_remaining']} day(s)")
        points += 8

    return {
        "checked": True,
        "status": status,
        "label": label,
        "issuer": parsed_cert.get("issuer"),
        "subject": parsed_cert.get("subject"),
        "valid_from": parsed_cert.get("valid_from"),
        "valid_to": parsed_cert.get("valid_to"),
        "days_remaining": parsed_cert.get("days_remaining"),
        "hostname_ok": hostname_ok if verified or verify_error else None,
        "chain_ok": chain_ok if verified or verify_error else None,
        "self_signed": parsed_cert.get("self_signed"),
        "error": verify_error,
        "risk_points": min(points, 40),
        "findings": findings,
        "tags": tags,
    }
