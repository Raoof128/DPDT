"""
PDF Export Utility.

Generate PDF reports for poisoning analysis.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


class PDFReportGenerator:
    """Generate PDF reports (simplified HTML-based for portability)."""

    def __init__(self, output_dir: Path = Path("reports")):
        """Initialize report generator."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_report(
        self, analysis_results: Dict[str, Any], dataset_name: str = "unknown"
    ) -> Path:
        """Generate HTML report (PDF-compatible when printed)."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"poisoning_report_{dataset_name}_{timestamp}.html"
        filepath = self.output_dir / filename

        html = self._build_html(analysis_results, dataset_name)

        with open(filepath, "w") as f:
            f.write(html)

        return filepath

    def _build_html(self, results: Dict[str, Any], name: str) -> str:
        """Build HTML report content."""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Data Poisoning Analysis Report - {name}</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
        .container {{ max-width: 900px; margin: 0 auto; background: white; padding: 40px;
                      box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #34495e; margin-top: 30px; }}
        .score-box {{ display: inline-block; padding: 20px 40px; border-radius: 10px;
                      font-size: 24px; font-weight: bold; margin: 10px 0; }}
        .low {{ background: #27ae60; color: white; }}
        .medium {{ background: #f39c12; color: white; }}
        .high {{ background: #e74c3c; color: white; }}
        .critical {{ background: #8e44ad; color: white; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #3498db; color: white; }}
        .warning {{ background: #fff3cd; padding: 15px; border-left: 4px solid #f39c12;
                    margin: 15px 0; }}
        .info {{ background: #d1ecf1; padding: 15px; border-left: 4px solid #17a2b8;
                 margin: 15px 0; }}
        ul {{ padding-left: 20px; }}
        li {{ margin: 8px 0; }}
        .timestamp {{ color: #7f8c8d; font-size: 12px; }}
        .compliance {{ background: #e8f4fd; padding: 20px; border-radius: 8px; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🛡️ Data Poisoning Detection Report</h1>
        <p class="timestamp">Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        <p><strong>Dataset:</strong> {name}</p>

        <h2>Executive Summary</h2>
        {self._build_summary_section(results)}

        <h2>Detection Results</h2>
        {self._build_detection_section(results)}

        <h2>Risk Assessment</h2>
        {self._build_risk_section(results)}

        <h2>Recommendations</h2>
        {self._build_recommendations_section(results)}

        <h2>Compliance Mapping</h2>
        {self._build_compliance_section()}

        <h2>Appendix: Technical Details</h2>
        <pre style="background: #f8f9fa; padding: 15px; overflow-x: auto; font-size: 12px;">
{json.dumps(results, indent=2, default=str)[:3000]}...
        </pre>
    </div>
</body>
</html>
"""
        return html

    def _build_summary_section(self, results: Dict) -> str:
        score = results.get("poisoning_score", 0)
        if score < 25:
            level = "low"
        elif score < 50:
            level = "medium"
        elif score < 75:
            level = "high"
        else:
            level = "critical"

        return f"""
        <div class="score-box {level}">
            Overall Poisoning Score: {score:.1f}/100
        </div>
        <p>Suspected poisoned samples: <strong>{len(results.get('suspected_indices', []))}</strong></p>
        """

    def _build_detection_section(self, results: Dict) -> str:
        html = (
            "<table><tr><th>Detection Method</th><th>Score</th><th>Findings</th></tr>"
        )

        methods = [
            ("Spectral Signatures", results.get("spectral_score", 0)),
            ("Activation Clustering", results.get("clustering_score", 0)),
            ("Trigger Detection", results.get("trigger_score", 0)),
            ("Influence Analysis", results.get("influence_score", 0)),
        ]

        for name, score in methods:
            findings = "Anomalies detected" if score > 20 else "Clean"
            html += f"<tr><td>{name}</td><td>{score:.1f}</td><td>{findings}</td></tr>"

        html += "</table>"
        return html

    def _build_risk_section(self, results: Dict) -> str:
        risk = results.get("risk_result", {})
        score = risk.get("collapse_risk_score", 0)
        level = risk.get("risk_level", "UNKNOWN")

        return f"""
        <div class="{'warning' if score > 50 else 'info'}">
            <strong>Collapse Risk Score:</strong> {score:.1f}/100 ({level})
        </div>
        """

    def _build_recommendations_section(self, results: Dict) -> str:
        recs = results.get("recommendations", ["No specific recommendations"])
        items = "".join(f"<li>{r}</li>" for r in recs)
        return f"<ul>{items}</ul>"

    def _build_compliance_section(self) -> str:
        return """
        <div class="compliance">
            <h3>Regulatory Framework Mapping</h3>
            <ul>
                <li><strong>NIST AI RMF:</strong> Supports Govern, Map, Measure, Manage functions</li>
                <li><strong>ISO/IEC 42001:</strong> Aligns with AI management system requirements</li>
                <li><strong>OAIC ADM:</strong> Supports automated decision-making transparency</li>
            </ul>
        </div>
        """
