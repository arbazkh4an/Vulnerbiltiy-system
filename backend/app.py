"""
VulnScan AI - Python Backend API
Flask-based vulnerability scanning engine
Targets OWASP Top 10:2025 vulnerabilities
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import logging
import io

# Import scanner modules
from scanners.owasp_scanner import OWASPScanner
from ai_model.severity_predictor import SeverityPredictor
from integrations.nvd_api import NVDIntegration

# Initialize Flask app
app = Flask(__name__)
CORS(app, origins=["*"])  # Configure based on your frontend domain in production

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database connection
def get_db_connection():
    """Establish connection to PostgreSQL database"""
    conn = psycopg2.connect(
        os.environ.get('DATABASE_URL'),
        cursor_factory=RealDictCursor
    )
    return conn

# Initialize components
scanner = OWASPScanner()
ai_predictor = SeverityPredictor()
nvd_integration = NVDIntegration()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'VulnScan AI Backend',
        'version': '1.0.0'
    })

@app.route('/api/scan/start', methods=['POST'])
def start_scan():
    """
    Start a new vulnerability scan
    Expects: { "scanId": int, "url": str }
    """
    try:
        data = request.json
        scan_id = data.get('scanId')
        target_url = data.get('url')

        if not scan_id or not target_url:
            return jsonify({'error': 'scanId and url are required'}), 400

        logger.info(f"Starting scan {scan_id} for {target_url}")

        # Update scan status to running
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            UPDATE scans 
            SET scan_status = 'running', started_at = NOW()
            WHERE id = %s
        """, (scan_id,))
        conn.commit()

        # Perform vulnerability scan
        vulnerabilities = scanner.scan(target_url)
        
        # Process each vulnerability
        critical_count = 0
        high_count = 0
        medium_count = 0
        low_count = 0

        for vuln in vulnerabilities:
            # Get AI severity prediction
            ai_prediction = ai_predictor.predict_severity(vuln)
            
            # Fetch CVE/CWE data from NVD
            nvd_data = nvd_integration.get_cve_data(vuln.get('cwe_id'))
            
            # Insert vulnerability into database
            cur.execute("""
                INSERT INTO vulnerabilities (
                    scan_id, vulnerability_name, vulnerability_type,
                    description, cwe_id, cwe_name, cvss_score,
                    severity, ai_predicted_severity, ai_confidence,
                    remediation, affected_url, evidence
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                scan_id,
                vuln['name'],
                vuln['type'],
                vuln['description'],
                vuln['cwe_id'],
                vuln['cwe_name'],
                vuln['cvss_score'],
                vuln['severity'],
                ai_prediction['predicted_severity'],
                ai_prediction['confidence'],
                vuln['remediation'],
                vuln['affected_url'],
                vuln['evidence']
            ))
            
            vuln_id = cur.fetchone()['id']
            
            # Insert CVE mappings
            if nvd_data.get('cves'):
                for cve in nvd_data['cves']:
                    cur.execute("""
                        INSERT INTO cve_mappings (
                            vulnerability_id, cve_id, cve_description,
                            cvss_v3_score, published_date, last_modified
                        ) VALUES (%s, %s, %s, %s, %s, %s)
                    """, (
                        vuln_id,
                        cve['id'],
                        cve['description'],
                        cve['cvss_score'],
                        cve['published_date'],
                        cve['last_modified']
                    ))
            
            # Count by severity
            severity = vuln['severity'].lower()
            if severity == 'critical':
                critical_count += 1
            elif severity == 'high':
                high_count += 1
            elif severity == 'medium':
                medium_count += 1
            elif severity == 'low':
                low_count += 1

        # Update scan with final counts
        cur.execute("""
            UPDATE scans 
            SET 
                scan_status = 'completed',
                completed_at = NOW(),
                total_vulnerabilities = %s,
                critical_count = %s,
                high_count = %s,
                medium_count = %s,
                low_count = %s
            WHERE id = %s
        """, (
            len(vulnerabilities),
            critical_count,
            high_count,
            medium_count,
            low_count,
            scan_id
        ))
        
        conn.commit()
        cur.close()
        conn.close()

        logger.info(f"Scan {scan_id} completed. Found {len(vulnerabilities)} vulnerabilities.")

        return jsonify({
            'success': True,
            'scanId': scan_id,
            'vulnerabilities_found': len(vulnerabilities),
            'critical': critical_count,
            'high': high_count,
            'medium': medium_count,
            'low': low_count
        })

    except Exception as e:
        logger.error(f"Error during scan: {str(e)}")
        
        # Update scan status to failed
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("""
                UPDATE scans 
                SET scan_status = 'failed'
                WHERE id = %s
            """, (scan_id,))
            conn.commit()
            cur.close()
            conn.close()
        except:
            pass
        
        return jsonify({'error': str(e)}), 500

@app.route('/api/scan/status/<int:scan_id>', methods=['GET'])
def get_scan_status(scan_id):
    """Get the current status of a scan"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT scan_status, total_vulnerabilities,
                   critical_count, high_count, medium_count, low_count
            FROM scans
            WHERE id = %s
        """, (scan_id,))
        
        result = cur.fetchone()
        cur.close()
        conn.close()

        if not result:
            return jsonify({'error': 'Scan not found'}), 404

        return jsonify(dict(result))

    except Exception as e:
        logger.error(f"Error fetching scan status: {str(e)}")
        return jsonify({'error': str(e)}), 500

from pdf_generator.report_generator import VulnerabilityReportGenerator

@app.route('/api/generate-pdf', methods=['POST'])
def generate_pdf():
    """
    Generate PDF report for a vulnerability scan
    Expects: { "scan": {...}, "vulnerabilities": [...] }
    """
    try:
        data = request.json
        scan = data.get('scan')
        vulnerabilities = data.get('vulnerabilities', [])

        if not scan:
            return jsonify({'error': 'Scan data is required'}), 400

        logger.info(f"Generating PDF report for scan {scan.get('id')}")

        # Generate PDF
        generator = VulnerabilityReportGenerator()
        pdf_content = generator.generate_report(scan, vulnerabilities)

        # Return PDF as response
        return send_file(
            io.BytesIO(pdf_content),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"vulnerability-report-{scan.get('id')}.pdf"
        )

    except Exception as e:
        logger.error(f"Error generating PDF: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
