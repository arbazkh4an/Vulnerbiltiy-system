"""
SentinelAI — URL Validation & SSRF Protection
Validates scan target URLs and blocks private/internal network access.
"""

import ipaddress
import socket
from urllib.parse import urlparse

from app.core.exceptions import InvalidURLException, PrivateIPBlocked

# Protocols that can be scanned
_ALLOWED_PROTOCOLS = {"http", "https"}

# Hostnames that must be blocked
_BLOCKED_HOSTNAMES = frozenset(
    {
        "localhost",
        "127.0.0.1",
        "::1",
        "0.0.0.0",
        "metadata.google.internal",
        "metadata.google",
        "169.254.169.254",
        "metadata.aws.internal",
    }
)

# Blocked TLD suffixes
_BLOCKED_SUFFIXES = (".local", ".localhost", ".internal")

# Ports that should never be scanned
_BLOCKED_PORTS = frozenset({22, 23, 3389, 5900, 6379, 27017, 5432, 3306})


def _is_private_ip(hostname: str) -> bool:
    """Check if a hostname resolves to a private or reserved IP address."""
    try:
        addr = ipaddress.ip_address(hostname)
        return (
            addr.is_private
            or addr.is_loopback
            or addr.is_reserved
            or addr.is_link_local
            or addr.is_multicast
        )
    except ValueError:
        # Not a raw IP — try resolving the hostname
        pass

    try:
        resolved = socket.getaddrinfo(hostname, None, socket.AF_UNSPEC, socket.SOCK_STREAM)
        for family, _, _, _, sockaddr in resolved:
            ip_str = sockaddr[0]
            addr = ipaddress.ip_address(ip_str)
            if (
                addr.is_private
                or addr.is_loopback
                or addr.is_reserved
                or addr.is_link_local
            ):
                return True
    except (socket.gaierror, OSError):
        # DNS resolution failed — allow the scan attempt (it will fail naturally)
        pass

    return False


def validate_scan_url(url: str) -> str:
    """
    Validate and sanitize a URL for scanning.

    Returns the validated URL string.
    Raises InvalidURLException or PrivateIPBlocked on failure.
    """
    if not url or not url.strip():
        raise InvalidURLException("URL is required")

    url = url.strip()

    # Parse the URL
    try:
        parsed = urlparse(url)
    except Exception:
        raise InvalidURLException("Malformed URL")

    # Enforce protocol
    scheme = (parsed.scheme or "").lower()
    if scheme not in _ALLOWED_PROTOCOLS:
        raise InvalidURLException(
            f"Only HTTP and HTTPS protocols are allowed. Got: {scheme or 'none'}"
        )

    # Must have a hostname
    hostname = (parsed.hostname or "").lower()
    if not hostname:
        raise InvalidURLException("URL must include a hostname")

    # Block known dangerous hostnames
    if hostname in _BLOCKED_HOSTNAMES:
        raise PrivateIPBlocked(f"Hostname '{hostname}' is blocked")

    # Block dangerous suffixes
    for suffix in _BLOCKED_SUFFIXES:
        if hostname.endswith(suffix):
            raise PrivateIPBlocked(f"Hostname suffix '{suffix}' is not allowed")

    # Block dangerous ports
    port = parsed.port
    if port and port in _BLOCKED_PORTS:
        raise PrivateIPBlocked(f"Port {port} is not allowed for scanning")

    # Block private/internal IPs
    if _is_private_ip(hostname):
        raise PrivateIPBlocked("Scanning private or internal networks is not allowed")

    return url
