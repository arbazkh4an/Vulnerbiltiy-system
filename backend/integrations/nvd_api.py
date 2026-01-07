"""
NVD API Integration
Fetches CVE, CWE, and CVSS data from the National Vulnerability Database
"""

import requests
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class NVDIntegration:
    def __init__(self):
        self.base_url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
        self.cache = {}
        self.cache_duration = timedelta(hours=24)
    
    def get_cve_data(self, cwe_id):
        """
        Fetch CVE data from NVD API based on CWE ID
        Args:
            cwe_id: CWE identifier (e.g., "CWE-79")
        Returns:
            dict with CVE information
        """
        # Check cache first
        if cwe_id in self.cache:
            cached_data, cached_time = self.cache[cwe_id]
            if datetime.now() - cached_time < self.cache_duration:
                return cached_data
        
        try:
            # Map common CWEs to example CVEs (in production, use actual API)
            # Note: NVD API has rate limits, this is a simplified implementation
            cve_mappings = self._get_cve_mapping(cwe_id)
            
            # Cache the result
            self.cache[cwe_id] = (cve_mappings, datetime.now())
            
            return cve_mappings
            
        except Exception as e:
            logger.error(f"Error fetching CVE data: {str(e)}")
            return {'cves': []}
    
    def _get_cve_mapping(self, cwe_id):
        """
        Get CVE mappings for common CWEs
        In production, this would query the actual NVD API
        """
        # Common CWE to CVE mappings for demonstration
        mappings = {
            'CWE-79': [  # XSS
                {
                    'id': 'CVE-2024-1234',
                    'description': 'Cross-site scripting vulnerability allows remote attackers to inject arbitrary web script',
                    'cvss_score': 7.5,
                    'published_date': '2024-01-15',
                    'last_modified': '2024-01-20'
                }
            ],
            'CWE-89': [  # SQL Injection
                {
                    'id': 'CVE-2024-5678',
                    'description': 'SQL injection vulnerability in authentication mechanism',
                    'cvss_score': 9.8,
                    'published_date': '2024-02-10',
                    'last_modified': '2024-02-15'
                }
            ],
            'CWE-284': [  # Improper Access Control
                {
                    'id': 'CVE-2024-9012',
                    'description': 'Broken access control allows unauthorized access to administrative functions',
                    'cvss_score': 8.8,
                    'published_date': '2024-03-05',
                    'last_modified': '2024-03-10'
                }
            ],
            'CWE-319': [  # Cleartext Transmission
                {
                    'id': 'CVE-2024-3456',
                    'description': 'Sensitive data transmitted without encryption',
                    'cvss_score': 7.5,
                    'published_date': '2024-04-01',
                    'last_modified': '2024-04-05'
                }
            ],
            'CWE-521': [  # Weak Password Requirements
                {
                    'id': 'CVE-2024-7890',
                    'description': 'Weak password policy allows easily guessable passwords',
                    'cvss_score': 5.3,
                    'published_date': '2024-05-12',
                    'last_modified': '2024-05-15'
                }
            ],
            'CWE-209': [  # Information Exposure
                {
                    'id': 'CVE-2024-2345',
                    'description': 'Debug information disclosure reveals sensitive system details',
                    'cvss_score': 5.3,
                    'published_date': '2024-06-20',
                    'last_modified': '2024-06-25'
                }
            ],
            'CWE-1021': [  # Clickjacking
                {
                    'id': 'CVE-2024-6789',
                    'description': 'Missing frame protection allows clickjacking attacks',
                    'cvss_score': 4.3,
                    'published_date': '2024-07-08',
                    'last_modified': '2024-07-12'
                }
            ]
        }
        
        cves = mappings.get(cwe_id, [])
        return {'cves': cves}
    
    def query_nvd_api(self, cwe_id):
        """
        Query the actual NVD API (use this in production with API key)
        """
        try:
            # Extract CWE number
            cwe_number = cwe_id.replace('CWE-', '')
            
            # NVD API endpoint with CWE filter
            params = {
                'cweId': f'CWE-{cwe_number}',
                'resultsPerPage': 5
            }
            
            # Note: Add API key header in production
            # headers = {'apiKey': 'your-nvd-api-key'}
            
            response = requests.get(
                self.base_url,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                vulnerabilities = data.get('vulnerabilities', [])
                
                cves = []
                for vuln in vulnerabilities[:5]:  # Limit to 5 CVEs
                    cve_data = vuln.get('cve', {})
                    cves.append({
                        'id': cve_data.get('id', ''),
                        'description': cve_data.get('descriptions', [{}])[0].get('value', ''),
                        'cvss_score': self._extract_cvss_score(cve_data),
                        'published_date': cve_data.get('published', '')[:10],
                        'last_modified': cve_data.get('lastModified', '')[:10]
                    })
                
                return {'cves': cves}
            
        except Exception as e:
            logger.error(f"Error querying NVD API: {str(e)}")
        
        return {'cves': []}
    
    def _extract_cvss_score(self, cve_data):
        """Extract CVSS v3 score from CVE data"""
        try:
            metrics = cve_data.get('metrics', {})
            cvss_v3 = metrics.get('cvssMetricV31', [{}])[0]
            return cvss_v3.get('cvssData', {}).get('baseScore', 0.0)
        except:
            return 0.0
