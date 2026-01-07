# Contributing to VulnScan AI Backend

Thank you for your interest in contributing to VulnScan AI!

## Development Setup

1. **Fork and Clone**
   \`\`\`bash
   git clone https://github.com/yourusername/vulnscan-ai.git
   cd vulnscan-ai/backend
   \`\`\`

2. **Create Virtual Environment**
   \`\`\`bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   \`\`\`

3. **Install Dependencies**
   \`\`\`bash
   pip install -r requirements.txt
   \`\`\`

4. **Setup Environment Variables**
   \`\`\`bash
   cp .env.example .env
   # Edit .env with your database credentials
   \`\`\`

## Code Style

### Python Style Guide
- Follow PEP 8 style guidelines
- Use type hints where possible
- Maximum line length: 100 characters
- Use docstrings for all functions and classes

### Example
\`\`\`python
def scan_vulnerability(url: str, vuln_type: str) -> dict:
    """
    Scan a URL for specific vulnerability type.
    
    Args:
        url: Target URL to scan
        vuln_type: Type of vulnerability to check
        
    Returns:
        dict: Vulnerability details if found
    """
    # Implementation
    pass
\`\`\`

## Adding New Vulnerability Scanners

1. Create new file in \`scanners/\` directory
2. Implement scanner class with \`scan()\` method
3. Return list of vulnerability dicts with required fields
4. Add scanner to \`owasp_scanner.py\`

### Required Vulnerability Fields
\`\`\`python
{
    'name': 'Vulnerability Name',
    'type': 'OWASP Category',
    'description': 'Detailed description',
    'cwe_id': 'CWE-XXX',
    'cwe_name': 'CWE Name',
    'cvss_score': 7.5,
    'severity': 'high',
    'remediation': 'How to fix',
    'affected_url': 'URL',
    'evidence': 'Technical evidence'
}
\`\`\`

## Adding New AI Models

1. Implement model in \`ai_model/\` directory
2. Inherit from base predictor or create new class
3. Update \`train_models.py\` to include new model
4. Document model parameters and performance

## Testing

### Manual Testing
\`\`\`bash
python app.py
# Test endpoints with curl or Postman
\`\`\`

### Future: Unit Tests
\`\`\`bash
pytest tests/
\`\`\`

## Commit Message Format

Use clear, descriptive commit messages:

\`\`\`
feat: Add XSS detection to scanner
fix: Correct CVSS score calculation
docs: Update API documentation
refactor: Optimize database queries
test: Add tests for severity predictor
\`\`\`

## Pull Request Process

1. Create feature branch from \`main\`
2. Make your changes
3. Test thoroughly
4. Update documentation
5. Submit PR with description of changes
6. Wait for review

## Areas for Contribution

- [ ] Additional vulnerability scanners
- [ ] Improved ML models
- [ ] Better error handling
- [ ] API rate limiting
- [ ] Authentication scanning
- [ ] WebSocket support for real-time updates
- [ ] Docker optimization
- [ ] Unit and integration tests
- [ ] Documentation improvements

## Questions?

Open an issue or contact the maintainers.
