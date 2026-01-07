"""
PDF Report Generator
Creates professional vulnerability scan reports
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from datetime import datetime
import io
import logging

logger = logging.getLogger(__name__)

class VulnerabilityReportGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()
    
    def _create_custom_styles(self):
        """Create custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#10B981'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        # Section heading
        self.styles.add(ParagraphStyle(
            name='SectionHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#0F172A'),
            spaceAfter=12,
            spaceBefore=12
        ))
        
        # Normal text
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=TA_JUSTIFY
        ))
    
    def generate_report(self, scan_data, vulnerabilities):
        """
        Generate a PDF report for the vulnerability scan
        Args:
            scan_data: dict with scan information
            vulnerabilities: list of vulnerability dicts
        Returns:
            bytes: PDF file content
        """
        buffer = io.BytesIO()
        
        # Create PDF document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Build the document content
        story = []
        
        # Title page
        story.extend(self._create_title_page(scan_data))
        story.append(PageBreak())
        
        # Executive summary
        story.extend(self._create_executive_summary(scan_data))
        story.append(Spacer(1, 0.2*inch))
        
        # Vulnerability details
        story.extend(self._create_vulnerability_details(vulnerabilities))
        
        # Build PDF
        doc.build(story)
        
        # Get PDF content
        pdf_content = buffer.getvalue()
        buffer.close()
        
        return pdf_content
    
    def _create_title_page(self, scan_data):
        """Create the title page"""
        story = []
        
        # Title
        title = Paragraph("VulnScan AI", self.styles['CustomTitle'])
        story.append(title)
        story.append(Spacer(1, 0.3*inch))
        
        # Subtitle
        subtitle = Paragraph(
            "Automated Vulnerability Scan Report",
            self.styles['Heading2']
        )
        story.append(subtitle)
        story.append(Spacer(1, 0.5*inch))
        
        # Scan information table
        scan_info = [
            ['Target URL:', scan_data.get('target_url', 'N/A')],
            ['Scan ID:', str(scan_data.get('id', 'N/A'))],
            ['Scan Date:', self._format_date(scan_data.get('started_at', ''))],
            ['Status:', scan_data.get('scan_status', 'Unknown').upper()],
            ['Generated:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
        ]
        
        table = Table(scan_info, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F1F5F9')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#0F172A')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#CBD5E1'))
        ]))
        
        story.append(table)
        
        return story
    
    def _create_executive_summary(self, scan_data):
        """Create executive summary section"""
        story = []
        
        story.append(Paragraph("Executive Summary", self.styles['SectionHeading']))
        
        # Summary text
        total_vulns = scan_data.get('total_vulnerabilities', 0)
        critical = scan_data.get('critical_count', 0)
        high = scan_data.get('high_count', 0)
        medium = scan_data.get('medium_count', 0)
        low = scan_data.get('low_count', 0)
        
        summary_text = f"""
        This report presents the findings from an automated vulnerability scan of 
        <b>{scan_data.get('target_url', 'the target system')}</b>. The scan was conducted using 
        VulnScan AI, targeting OWASP Top 10:2025 vulnerabilities including Broken Access Control, 
        Injection, Security Misconfiguration, Cryptographic Failures, Insecure Design, and 
        Authentication Failures.
        <br/><br/>
        <b>Total Vulnerabilities Found: {total_vulns}</b>
        """
        
        story.append(Paragraph(summary_text, self.styles['CustomBody']))
        story.append(Spacer(1, 0.2*inch))
        
        # Severity breakdown table
        severity_data = [
            ['Severity Level', 'Count', 'Risk Level'],
            ['CRITICAL', str(critical), 'Immediate Action Required'],
            ['HIGH', str(high), 'Address Soon'],
            ['MEDIUM', str(medium), 'Moderate Risk'],
            ['LOW', str(low), 'Low Priority']
        ]
        
        severity_table = Table(severity_data, colWidths=[2*inch, 1.5*inch, 2.5*inch])
        severity_table.setStyle(TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F172A')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            # Critical row
            ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#FEE2E2')),
            ('TEXTCOLOR', (0, 1), (-1, 1), colors.HexColor('#991B1B')),
            # High row
            ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor('#FFEDD5')),
            ('TEXTCOLOR', (0, 2), (-1, 2), colors.HexColor('#9A3412')),
            # Medium row
            ('BACKGROUND', (0, 3), (-1, 3), colors.HexColor('#FEF3C7')),
            ('TEXTCOLOR', (0, 3), (-1, 3), colors.HexColor('#92400E')),
            # Low row
            ('BACKGROUND', (0, 4), (-1, 4), colors.HexColor('#DBEAFE')),
            ('TEXTCOLOR', (0, 4), (-1, 4), colors.HexColor('#1E3A8A')),
            # General styling
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#CBD5E1'))
        ]))
        
        story.append(severity_table)
        
        return story
    
    def _create_vulnerability_details(self, vulnerabilities):
        """Create detailed vulnerability listings"""
        story = []
        
        story.append(Paragraph("Detailed Findings", self.styles['SectionHeading']))
        story.append(Spacer(1, 0.1*inch))
        
        if not vulnerabilities:
            story.append(Paragraph(
                "No vulnerabilities were detected during this scan. The target appears to be secure.",
                self.styles['CustomBody']
            ))
            return story
        
        for i, vuln in enumerate(vulnerabilities, 1):
            # Vulnerability header
            vuln_title = f"{i}. {vuln.get('vulnerability_name', 'Unknown Vulnerability')}"
            story.append(Paragraph(vuln_title, self.styles['Heading3']))
            story.append(Spacer(1, 0.1*inch))
            
            # Vulnerability info table
            vuln_info = [
                ['Type:', vuln.get('vulnerability_type', 'N/A')],
                ['Severity:', vuln.get('severity', 'N/A').upper()],
                ['AI Prediction:', f"{vuln.get('ai_predicted_severity', 'N/A').upper()} ({vuln.get('ai_confidence', 0):.1f}% confidence)"],
                ['CWE:', f"{vuln.get('cwe_id', 'N/A')} - {vuln.get('cwe_name', 'N/A')}"],
                ['CVSS Score:', str(vuln.get('cvss_score', 'N/A'))],
                ['Affected URL:', vuln.get('affected_url', 'N/A')]
            ]
            
            # Add CVEs if available
            cves = vuln.get('cves', [])
            if cves:
                cve_list = ', '.join([cve.get('cve_id', '') for cve in cves])
                vuln_info.append(['CVEs:', cve_list])
            
            info_table = Table(vuln_info, colWidths=[1.5*inch, 4.5*inch])
            info_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F1F5F9')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#0F172A')),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#CBD5E1')),
                ('VALIGN', (0, 0), (-1, -1), 'TOP')
            ]))
            
            story.append(info_table)
            story.append(Spacer(1, 0.1*inch))
            
            # Description
            story.append(Paragraph("<b>Description:</b>", self.styles['CustomBody']))
            story.append(Paragraph(vuln.get('description', 'No description available'), self.styles['CustomBody']))
            story.append(Spacer(1, 0.1*inch))
            
            # Evidence
            story.append(Paragraph("<b>Evidence:</b>", self.styles['CustomBody']))
            story.append(Paragraph(vuln.get('evidence', 'No evidence available'), self.styles['CustomBody']))
            story.append(Spacer(1, 0.1*inch))
            
            # Remediation
            story.append(Paragraph("<b>Remediation:</b>", self.styles['CustomBody']))
            remediation_style = ParagraphStyle(
                'Remediation',
                parent=self.styles['CustomBody'],
                backColor=colors.HexColor('#D1FAE5'),
                borderColor=colors.HexColor('#10B981'),
                borderWidth=1,
                borderPadding=8
            )
            story.append(Paragraph(vuln.get('remediation', 'No remediation available'), remediation_style))
            story.append(Spacer(1, 0.3*inch))
        
        return story
    
    def _format_date(self, date_string):
        """Format date string for display"""
        try:
            if isinstance(date_string, str):
                dt = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
            else:
                dt = date_string
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            return 'N/A'
