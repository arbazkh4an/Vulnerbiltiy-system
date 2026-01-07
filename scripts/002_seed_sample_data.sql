-- Sample data for demonstration purposes
-- This helps showcase the system during FYP defense

-- Insert sample scan (using a placeholder user_id - will be replaced with actual user)
INSERT INTO scans (user_id, target_url, scan_status, total_vulnerabilities, critical_count, high_count, medium_count, low_count, started_at, completed_at)
VALUES 
    ('demo-user', 'https://example-vulnerable-site.com', 'completed', 8, 2, 3, 2, 1, NOW() - INTERVAL '2 hours', NOW() - INTERVAL '1 hour')
ON CONFLICT DO NOTHING;

-- Get the last inserted scan_id
DO $$
DECLARE
    demo_scan_id INTEGER;
BEGIN
    SELECT id INTO demo_scan_id FROM scans WHERE target_url = 'https://example-vulnerable-site.com' LIMIT 1;
    
    -- Insert sample vulnerabilities
    INSERT INTO vulnerabilities (scan_id, vulnerability_name, vulnerability_type, description, cwe_id, cwe_name, cvss_score, severity, ai_predicted_severity, ai_confidence, remediation, affected_url, evidence)
    VALUES 
        (demo_scan_id, 'SQL Injection in Login Form', 'Injection', 'The login form is vulnerable to SQL injection attacks, allowing attackers to bypass authentication.', 'CWE-89', 'Improper Neutralization of Special Elements used in an SQL Command', 9.8, 'critical', 'critical', 95.5, 'Use parameterized queries or prepared statements. Implement input validation and sanitization.', 'https://example-vulnerable-site.com/login', 'Parameter "username" accepts unsanitized SQL: '' OR ''1''=''1'),
        
        (demo_scan_id, 'Broken Access Control on Admin Panel', 'Broken Access Control', 'Admin panel accessible without proper authentication checks, allowing unauthorized users to access sensitive functions.', 'CWE-284', 'Improper Access Control', 9.1, 'critical', 'high', 88.3, 'Implement proper role-based access control (RBAC). Verify user permissions on server-side before granting access.', 'https://example-vulnerable-site.com/admin', 'Direct access to /admin endpoint bypasses authentication middleware'),
        
        (demo_scan_id, 'Cross-Site Scripting (XSS) in Search', 'Injection', 'Stored XSS vulnerability in search functionality allows execution of arbitrary JavaScript code.', 'CWE-79', 'Improper Neutralization of Input During Web Page Generation', 7.5, 'high', 'high', 92.1, 'Sanitize all user inputs. Implement Content Security Policy (CSP). Use context-aware output encoding.', 'https://example-vulnerable-site.com/search', 'Input <script>alert(1)</script> executed in browser'),
        
        (demo_scan_id, 'Insecure Direct Object Reference', 'Broken Access Control', 'User profile endpoints expose data through predictable IDs without authorization checks.', 'CWE-639', 'Authorization Bypass Through User-Controlled Key', 6.5, 'high', 'medium', 76.8, 'Implement indirect reference maps. Validate user authorization for every object access.', 'https://example-vulnerable-site.com/api/user/123', 'Incrementing user ID exposes other user profiles'),
        
        (demo_scan_id, 'Missing Authentication on API Endpoint', 'Authentication Failures', 'Critical API endpoints lack authentication, exposing sensitive operations.', 'CWE-306', 'Missing Authentication for Critical Function', 8.2, 'high', 'high', 90.2, 'Implement JWT or session-based authentication. Require authentication tokens for all sensitive endpoints.', 'https://example-vulnerable-site.com/api/delete-account', 'No authentication header required for deletion'),
        
        (demo_scan_id, 'Sensitive Data Exposure in Response', 'Cryptographic Failures', 'API responses contain sensitive data like passwords and tokens in plaintext.', 'CWE-312', 'Cleartext Storage of Sensitive Information', 5.3, 'medium', 'medium', 82.5, 'Remove sensitive fields from API responses. Use field-level encryption for sensitive data.', 'https://example-vulnerable-site.com/api/users', 'Response includes password_hash field'),
        
        (demo_scan_id, 'Security Misconfiguration - Debug Mode', 'Security Misconfiguration', 'Application running in debug mode exposes stack traces and internal paths.', 'CWE-209', 'Generation of Error Message Containing Sensitive Information', 4.3, 'medium', 'low', 71.2, 'Disable debug mode in production. Implement custom error pages. Log errors securely.', 'https://example-vulnerable-site.com/error', 'Stack trace reveals application structure'),
        
        (demo_scan_id, 'Weak Password Policy', 'Authentication Failures', 'Password requirements are insufficient, allowing weak passwords.', 'CWE-521', 'Weak Password Requirements', 3.7, 'low', 'low', 68.9, 'Implement strong password policies: minimum length, complexity requirements, password strength meter.', 'https://example-vulnerable-site.com/register', 'Accepts passwords like "123456"')
    ON CONFLICT DO NOTHING;
    
    -- Insert CVE mappings for some vulnerabilities
    INSERT INTO cve_mappings (vulnerability_id, cve_id, cve_description, cvss_v3_score, published_date, last_modified)
    SELECT v.id, 'CVE-2023-12345', 'SQL Injection vulnerability in authentication systems', 9.8, '2023-06-15', '2023-06-20'
    FROM vulnerabilities v WHERE v.scan_id = demo_scan_id AND v.vulnerability_name = 'SQL Injection in Login Form'
    ON CONFLICT DO NOTHING;
    
    INSERT INTO cve_mappings (vulnerability_id, cve_id, cve_description, cvss_v3_score, published_date, last_modified)
    SELECT v.id, 'CVE-2023-23456', 'Access control bypass in web applications', 8.8, '2023-05-10', '2023-05-15'
    FROM vulnerabilities v WHERE v.scan_id = demo_scan_id AND v.vulnerability_name = 'Broken Access Control on Admin Panel'
    ON CONFLICT DO NOTHING;
    
    INSERT INTO cve_mappings (vulnerability_id, cve_id, cve_description, cvss_v3_score, published_date, last_modified)
    SELECT v.id, 'CVE-2023-34567', 'Cross-site scripting in search functionality', 7.5, '2023-07-22', '2023-07-28'
    FROM vulnerabilities v WHERE v.scan_id = demo_scan_id AND v.vulnerability_name LIKE '%XSS%'
    ON CONFLICT DO NOTHING;
END $$;
