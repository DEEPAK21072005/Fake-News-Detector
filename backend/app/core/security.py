import re
import ipaddress
import urllib.parse
from typing import Tuple, Optional


DISALLOWED_SCHEMES = {"file", "gopher", "ftp", "ldap", "dict", "netdoc"}
PRIVATE_IP_RANGES = [
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),
    ipaddress.ip_network("fe80::/10"),
]


def is_safe_url(url: str) -> Tuple[bool, Optional[str]]:
    """
    Validate URLs against SSRF (Server-Side Request Forgery) attacks and malicious schemes.
    """
    if not url or not isinstance(url, str):
        return False, "URL cannot be empty."

    url = url.strip()
    parsed = urllib.parse.urlparse(url)

    if parsed.scheme.lower() not in ("http", "https"):
        return False, f"Unsupported scheme: {parsed.scheme}. Only HTTP and HTTPS are permitted."

    hostname = parsed.hostname
    if not hostname:
        return False, "Invalid URL hostname."

    # Check for localhost or local names
    if hostname.lower() in ("localhost", "127.0.0.1", "0.0.0.0", "::1"):
        return False, "Access to localhost/loopback addresses is prohibited."

    try:
        ip = ipaddress.ip_address(hostname)
        for net in PRIVATE_IP_RANGES:
            if ip in net:
                return False, "Access to private or local network IP addresses is restricted."
    except ValueError:
        # Hostname is a domain name, not a raw IP
        pass

    return True, None


def sanitize_text(text: str, max_chars: int = 100000) -> str:
    """Sanitize and truncate text input safely."""
    if not text:
        return ""
    # Strip null bytes and control chars (except newline and tab)
    sanitized = "".join(c for c in text if c in ("\n", "\r", "\t") or (ord(c) >= 32 and ord(c) != 127))
    return sanitized[:max_chars].strip()
