# NVD API Integration

## Overview
Integration with NIST National Vulnerability Database (NVD) API for CVE/CWE/CVSS data.

## Features
- Fetch CVE information by CWE ID
- CVSS v3 score retrieval
- Published and modified dates
- Caching mechanism to reduce API calls

## NVD API Setup

### Get API Key (Recommended for Production)

1. Request an API key from: https://nvd.nist.gov/developers/request-an-api-key
2. Set environment variable:
\`\`\`bash
export NVD_API_KEY="your-api-key-here"
\`\`\`

### Rate Limits
- **Without API key**: 5 requests per 30 seconds
- **With API key**: 50 requests per 30 seconds

## Usage Example

\`\`\`python
from integrations.nvd_api import NVDIntegration

nvd = NVDIntegration()

# Fetch CVEs for a CWE
cve_data = nvd.get_cve_data('CWE-79')

for cve in cve_data['cves']:
    print(f"CVE: {cve['id']}")
    print(f"CVSS: {cve['cvss_score']}")
    print(f"Description: {cve['description']}")
\`\`\`

## Cache Behavior

The integration caches CVE data for 24 hours to minimize API calls and improve performance.

## Production Notes

1. Enable API key for higher rate limits
2. Implement retry logic with exponential backoff
3. Monitor API usage and quotas
4. Consider using a local NVD mirror for high-volume scanning
