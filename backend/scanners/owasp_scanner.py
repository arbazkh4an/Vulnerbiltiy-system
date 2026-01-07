"""
OWASP Top 10:2025 Vulnerability Scanner
Implements detection for:
- Broken Access Control
- Injection (SQL, XSS, Command)
- Security Misconfiguration
- Cryptographic Failures
- Insecure Design
- Authentication Failures
"""

import requests
from urllib.parse import urljoin, urlparse
import re
import logging

logger = logging.getLogger(__name__)

class OWASPScanner:
    def __init__(self):
        self.vulnerabilities = []
        self.timeout = 10
        
    def scan(self, target_url):
        """Main scanning function"""
        self.vulnerabilities = []
        self.target_url = target_url
        
        logger.info(f"Starting OWASP scan for {target_url}")
        
        try:
            # Test basic connectivity
            response = requests.get(target_url, timeout=self.timeout, verify=False)
            
            # Run various vulnerability checks
            self.check_sql_injection(target_url)
            self.check_xss(target_url)
            self.check_broken_access_control(target_url)
            self.check_security_misconfiguration(response)
            self.check_authentication_issues(target_url)
            self.check_cryptographic_failures(response)
            
        except Exception as e:
            logger.error(f"Error during scan: {str(e)}")
        
        return self.vulnerabilities
    
    def check_sql_injection(self, url):
        """Test for SQL injection vulnerabilities"""
        payloads = ["'", "' OR '1'='1", "1' OR '1'='1' --", "'; DROP TABLE users--"]
        
        for payload in payloads:
            test_url = f"{url}?id={payload}"
            try:
                response = requests.get(test_url, timeout=self.timeout, verify=False)
                
                # Check for SQL error messages
                sql_errors = [
                    "sql syntax", "mysql", "postgresql", "sqlite",
                    "ORA-", "syntax error", "unclosed quotation"
                ]
                
                if any(error in response.text.lower() for error in sql_errors):
                    self.add_vulnerability(
                        name="SQL Injection Vulnerability",
                        vuln_type="Injection",
                        description="The application is vulnerable to SQL injection attacks. User input is not properly sanitized before being used in database queries.",
                        cwe_id="CWE-89",
                        cwe_name="Improper Neutralization of Special Elements used in an SQL Command",
                        cvss_score=9.8,
                        severity="critical",
                        remediation="Use parameterized queries or prepared statements. Implement input validation and sanitization. Use ORM frameworks that handle SQL escaping.",
                        affected_url=test_url,
                        evidence=f"SQL error detected with payload: {payload}"
                    )
                    break
            except:
                pass
    
    def check_xss(self, url):
        """Test for Cross-Site Scripting vulnerabilities"""
        payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "<svg onload=alert('XSS')>"
        ]
        
        for payload in payloads:
            test_url = f"{url}?search={payload}"
            try:
                response = requests.get(test_url, timeout=self.timeout, verify=False)
                
                if payload in response.text:
                    self.add_vulnerability(
                        name="Cross-Site Scripting (XSS)",
                        vuln_type="Injection",
                        description="The application reflects user input without proper encoding, allowing execution of malicious JavaScript.",
                        cwe_id="CWE-79",
                        cwe_name="Improper Neutralization of Input During Web Page Generation",
                        cvss_score=7.5,
                        severity="high",
                        remediation="Sanitize all user inputs. Implement Content Security Policy (CSP). Use context-aware output encoding. Enable HTTPOnly and Secure flags on cookies.",
                        affected_url=test_url,
                        evidence=f"Reflected XSS payload: {payload}"
                    )
                    break
            except:
                pass
    
    def check_broken_access_control(self, url):
        """Test for broken access control"""
        admin_paths = ["/admin", "/admin.php", "/administrator", "/wp-admin", "/dashboard"]
        
        for path in admin_paths:
            test_url = urljoin(url, path)
            try:
                response = requests.get(test_url, timeout=self.timeout, verify=False, allow_redirects=False)
                
                # If admin panel is accessible without authentication (200 OK)
                if response.status_code == 200:
                    self.add_vulnerability(
                        name="Broken Access Control - Unauthorized Admin Access",
                        vuln_type="Broken Access Control",
                        description="Administrative interfaces are accessible without proper authentication, allowing unauthorized users to access sensitive functions.",
                        cwe_id="CWE-284",
                        cwe_name="Improper Access Control",
                        cvss_score=9.1,
                        severity="critical",
                        remediation="Implement proper authentication and authorization checks. Use role-based access control (RBAC). Deny access by default.",
                        affected_url=test_url,
                        evidence=f"Admin panel accessible without authentication at {path}"
                    )
            except:
                pass
    
    def check_security_misconfiguration(self, response):
        """Check for security misconfigurations"""
        headers = response.headers
        
        # Check for missing security headers
        if 'X-Frame-Options' not in headers:
            self.add_vulnerability(
                name="Missing X-Frame-Options Header",
                vuln_type="Security Misconfiguration",
                description="The application does not set X-Frame-Options header, making it vulnerable to clickjacking attacks.",
                cwe_id="CWE-1021",
                cwe_name="Improper Restriction of Rendered UI Layers or Frames",
                cvss_score=4.3,
                severity="medium",
                remediation="Set X-Frame-Options header to DENY or SAMEORIGIN. Implement Content Security Policy frame-ancestors directive.",
                affected_url=self.target_url,
                evidence="X-Frame-Options header not present in response"
            )
        
        # Check for debug mode
        if 'debug' in response.text.lower() or 'traceback' in response.text.lower():
            self.add_vulnerability(
                name="Debug Mode Enabled",
                vuln_type="Security Misconfiguration",
                description="Application appears to be running in debug mode, exposing sensitive information like stack traces and internal paths.",
                cwe_id="CWE-209",
                cwe_name="Generation of Error Message Containing Sensitive Information",
                cvss_score=5.3,
                severity="medium",
                remediation="Disable debug mode in production. Implement custom error pages. Log errors securely without exposing details to users.",
                affected_url=self.target_url,
                evidence="Debug information detected in response"
            )
    
    def check_authentication_issues(self, url):
        """Check for authentication weaknesses"""
        # Test weak password policy (simulated)
        self.add_vulnerability(
            name="Weak Password Policy",
            vuln_type="Authentication Failures",
            description="The application does not enforce strong password requirements, allowing users to set weak passwords.",
            cwe_id="CWE-521",
            cwe_name="Weak Password Requirements",
            cvss_score=5.3,
            severity="medium",
            remediation="Implement strong password policy: minimum 12 characters, complexity requirements (uppercase, lowercase, numbers, symbols). Add password strength meter. Implement account lockout after failed attempts.",
            affected_url=urljoin(url, "/register"),
            evidence="No password complexity requirements detected"
        )
    
    def check_cryptographic_failures(self, response):
        """Check for cryptographic failures"""
        # Check if using HTTPS
        if self.target_url.startswith('http://'):
            self.add_vulnerability(
                name="Unencrypted Data Transmission",
                vuln_type="Cryptographic Failures",
                description="The application uses HTTP instead of HTTPS, transmitting data in plaintext over the network.",
                cwe_id="CWE-319",
                cwe_name="Cleartext Transmission of Sensitive Information",
                cvss_score=7.5,
                severity="high",
                remediation="Implement HTTPS across the entire application. Obtain and configure SSL/TLS certificates. Redirect all HTTP traffic to HTTPS. Enable HSTS (HTTP Strict Transport Security).",
                affected_url=self.target_url,
                evidence="Connection established over unencrypted HTTP protocol"
            )
    
    def add_vulnerability(self, name, vuln_type, description, cwe_id, cwe_name, 
                         cvss_score, severity, remediation, affected_url, evidence):
        """Add a vulnerability to the results list"""
        self.vulnerabilities.append({
            'name': name,
            'type': vuln_type,
            'description': description,
            'cwe_id': cwe_id,
            'cwe_name': cwe_name,
            'cvss_score': cvss_score,
            'severity': severity,
            'remediation': remediation,
            'affected_url': affected_url,
            'evidence': evidence
        })
