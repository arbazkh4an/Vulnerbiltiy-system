"""
SentinelAI — Report Service
PDF report generation using reportlab.
Adapts the existing VulnerabilityReportGenerator for the new AIReport format.
"""

import io
from datetime import datetime
from typing import Any

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.logging import get_logger

logger = get_logger(__name__)


class ReportGenerator:
    """Generate professional PDF vulnerability reports."""

    def __init__(self) -> None:
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()

    def _create_custom_styles(self) -> None:
        self.styles.add(
            ParagraphStyle(
                name="CustomTitle",
                parent=self.styles["Heading1"],
                fontSize=24,
                textColor=colors.HexColor("#10B981"),
                spaceAfter=30,
                alignment=TA_CENTER,
            )
        )
        self.styles.add(
            ParagraphStyle(
                name="SectionHeading",
                parent=self.styles["Heading2"],
                fontSize=16,
                textColor=colors.HexColor("#0F172A"),
                spaceAfter=12,
                spaceBefore=12,
            )
        )
        self.styles.add(
            ParagraphStyle(
                name="CustomBody",
                parent=self.styles["Normal"],
                fontSize=10,
                alignment=TA_JUSTIFY,
            )
        )

    def generate(
        self,
        url: str,
        ai_report: dict[str, Any],
        scan_id: str = "",
    ) -> bytes:
        """
        Generate a PDF report from the AI report data.

        Returns the PDF content as bytes.
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18,
        )

        story: list[Any] = []

        # Title page
        story.extend(self._title_page(url, scan_id))
        story.append(PageBreak())

        # Executive Summary
        story.extend(self._executive_summary(ai_report, url))
        story.append(Spacer(1, 0.2 * inch))

        # Findings
        story.extend(self._findings_section(ai_report.get("findings", [])))

        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()

        logger.info("pdf_report_generated", scan_id=scan_id, size_bytes=len(pdf_bytes))
        return pdf_bytes

    def _title_page(self, url: str, scan_id: str) -> list[Any]:
        story: list[Any] = []
        story.append(Paragraph("SentinelAI", self.styles["CustomTitle"]))
        story.append(Spacer(1, 0.3 * inch))
        story.append(
            Paragraph("Automated Vulnerability Scan Report", self.styles["Heading2"])
        )
        story.append(Spacer(1, 0.5 * inch))

        info = [
            ["Target URL:", url],
            ["Scan ID:", scan_id or "N/A"],
            ["Generated:", datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
        ]
        table = Table(info, colWidths=[2 * inch, 4 * inch])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F1F5F9")),
                    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
                    ("GRID", (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
                ]
            )
        )
        story.append(table)
        return story

    def _executive_summary(self, report: dict[str, Any], url: str) -> list[Any]:
        story: list[Any] = []
        story.append(Paragraph("Executive Summary", self.styles["SectionHeading"]))

        risk_score = report.get("risk_score", 0)
        summary = report.get("summary", "No summary available.")
        findings = report.get("findings", [])

        counts = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
        for f in findings:
            sev = f.get("severity", "info")
            counts[sev] = counts.get(sev, 0) + 1

        text = (
            f"<b>Risk Score: {risk_score}/100</b><br/><br/>"
            f"{summary}<br/><br/>"
            f"<b>Total Findings: {len(findings)}</b>"
        )
        story.append(Paragraph(text, self.styles["CustomBody"]))
        story.append(Spacer(1, 0.2 * inch))

        severity_data = [
            ["Severity", "Count", "Risk Level"],
            ["CRITICAL", str(counts["critical"]), "Immediate Action"],
            ["HIGH", str(counts["high"]), "Address Soon"],
            ["MEDIUM", str(counts["medium"]), "Moderate Risk"],
            ["LOW", str(counts["low"]), "Low Priority"],
        ]
        table = Table(severity_data, colWidths=[2 * inch, 1.5 * inch, 2.5 * inch])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F172A")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#FEE2E2")),
                    ("BACKGROUND", (0, 2), (-1, 2), colors.HexColor("#FFEDD5")),
                    ("BACKGROUND", (0, 3), (-1, 3), colors.HexColor("#FEF3C7")),
                    ("BACKGROUND", (0, 4), (-1, 4), colors.HexColor("#DBEAFE")),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
                    ("GRID", (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
                ]
            )
        )
        story.append(table)
        return story

    def _findings_section(self, findings: list[dict[str, Any]]) -> list[Any]:
        story: list[Any] = []
        story.append(Paragraph("Detailed Findings", self.styles["SectionHeading"]))
        story.append(Spacer(1, 0.1 * inch))

        if not findings:
            story.append(
                Paragraph(
                    "No vulnerabilities were detected. The target appears secure.",
                    self.styles["CustomBody"],
                )
            )
            return story

        for i, finding in enumerate(findings, 1):
            title = f"{i}. {finding.get('title', 'Unknown')}"
            story.append(Paragraph(title, self.styles["Heading3"]))
            story.append(Spacer(1, 0.1 * inch))

            info_rows = [
                ["Severity:", finding.get("severity", "N/A").upper()],
                ["OWASP:", finding.get("owasp_category", "N/A")],
                ["CVSS:", str(finding.get("cvss_score", "N/A"))],
                ["CWE:", finding.get("cwe_id", "N/A") or "N/A"],
            ]
            table = Table(info_rows, colWidths=[1.5 * inch, 4.5 * inch])
            table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F1F5F9")),
                        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, -1), 9),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                        ("GRID", (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
                    ]
                )
            )
            story.append(table)
            story.append(Spacer(1, 0.1 * inch))

            story.append(Paragraph("<b>Description:</b>", self.styles["CustomBody"]))
            story.append(
                Paragraph(
                    finding.get("description", "N/A"), self.styles["CustomBody"]
                )
            )
            story.append(Spacer(1, 0.1 * inch))

            story.append(Paragraph("<b>Evidence:</b>", self.styles["CustomBody"]))
            story.append(
                Paragraph(finding.get("evidence", "N/A"), self.styles["CustomBody"])
            )
            story.append(Spacer(1, 0.1 * inch))

            story.append(Paragraph("<b>Remediation:</b>", self.styles["CustomBody"]))
            rem_style = ParagraphStyle(
                "Remediation",
                parent=self.styles["CustomBody"],
                backColor=colors.HexColor("#D1FAE5"),
                borderColor=colors.HexColor("#10B981"),
                borderWidth=1,
                borderPadding=8,
            )
            story.append(
                Paragraph(finding.get("remediation", "N/A"), rem_style)
            )
            story.append(Spacer(1, 0.3 * inch))

        return story
