"""
SentinelAI — URL Validator Tests
Tests for SSRF protection and URL validation.
"""

import pytest

from app.core.exceptions import InvalidURLException, PrivateIPBlocked
from app.core.validators import validate_scan_url


class TestValidURLs:
    """Valid URLs should pass validation."""

    def test_https_url(self):
        result = validate_scan_url("https://example.com")
        assert result == "https://example.com"

    def test_http_url(self):
        result = validate_scan_url("http://example.com")
        assert result == "http://example.com"

    def test_url_with_path(self):
        result = validate_scan_url("https://example.com/path/to/page")
        assert result == "https://example.com/path/to/page"

    def test_url_with_port(self):
        result = validate_scan_url("https://example.com:8080")
        assert result == "https://example.com:8080"

    def test_url_with_whitespace(self):
        result = validate_scan_url("  https://example.com  ")
        assert result == "https://example.com"


class TestInvalidURLs:
    """Malformed or disallowed URLs should raise InvalidURLException."""

    def test_empty_url(self):
        with pytest.raises(InvalidURLException):
            validate_scan_url("")

    def test_whitespace_only(self):
        with pytest.raises(InvalidURLException):
            validate_scan_url("   ")

    def test_no_protocol(self):
        with pytest.raises(InvalidURLException):
            validate_scan_url("example.com")

    def test_ftp_protocol(self):
        with pytest.raises(InvalidURLException):
            validate_scan_url("ftp://example.com")

    def test_file_protocol(self):
        with pytest.raises(InvalidURLException):
            validate_scan_url("file:///etc/passwd")

    def test_javascript_protocol(self):
        with pytest.raises(InvalidURLException):
            validate_scan_url("javascript:alert(1)")

    def test_data_protocol(self):
        with pytest.raises(InvalidURLException):
            validate_scan_url("data:text/html,<h1>hi</h1>")


class TestSSRFBlocking:
    """Private and internal IPs should raise PrivateIPBlocked."""

    def test_localhost(self):
        with pytest.raises(PrivateIPBlocked):
            validate_scan_url("http://localhost")

    def test_127_0_0_1(self):
        with pytest.raises(PrivateIPBlocked):
            validate_scan_url("http://127.0.0.1")

    def test_ipv6_loopback(self):
        with pytest.raises(PrivateIPBlocked):
            validate_scan_url("http://[::1]")

    def test_private_10_range(self):
        with pytest.raises(PrivateIPBlocked):
            validate_scan_url("http://10.0.0.1")

    def test_private_172_range(self):
        with pytest.raises(PrivateIPBlocked):
            validate_scan_url("http://172.16.0.1")

    def test_private_192_range(self):
        with pytest.raises(PrivateIPBlocked):
            validate_scan_url("http://192.168.1.1")

    def test_metadata_aws(self):
        with pytest.raises(PrivateIPBlocked):
            validate_scan_url("http://169.254.169.254")

    def test_metadata_google(self):
        with pytest.raises(PrivateIPBlocked):
            validate_scan_url("http://metadata.google.internal")

    def test_dot_local(self):
        with pytest.raises(PrivateIPBlocked):
            validate_scan_url("http://myserver.local")

    def test_dot_localhost(self):
        with pytest.raises(PrivateIPBlocked):
            validate_scan_url("http://app.localhost")

    def test_blocked_port_ssh(self):
        with pytest.raises(PrivateIPBlocked):
            validate_scan_url("http://example.com:22")

    def test_blocked_port_rdp(self):
        with pytest.raises(PrivateIPBlocked):
            validate_scan_url("http://example.com:3389")

    def test_zero_ip(self):
        with pytest.raises(PrivateIPBlocked):
            validate_scan_url("http://0.0.0.0")
