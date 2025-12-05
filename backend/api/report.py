"""
Report API Endpoints.

GET /report - Generate analysis report.
"""

from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from backend.engines import (
    ActivationClusteringDetector,
    CollapseRiskEngine,
    DatasetGenerator,
    SpectralSignaturesDetector,
)
from backend.utils import get_logger
from backend.utils.pdf_export import PDFReportGenerator

logger = get_logger("api.report")
router = APIRouter(prefix="/report", tags=["report"])


class ReportRequest(BaseModel):
    """Request for report generation."""

    dataset_type: str = Field("image")
    n_samples: int = Field(500, ge=10, le=10000)
    n_classes: int = Field(5, ge=2, le=50)
    poison_ratio: float = Field(0.1, ge=0.0, le=0.5)
    seed: int = Field(42)
    dataset_name: str = Field("synthetic_dataset")


@router.post("", response_class=HTMLResponse)
async def generate_report(request: ReportRequest):
    """
    Generate comprehensive HTML report for dataset analysis.

    Includes executive summary, detection results, risk assessment,
    recommendations, and compliance mapping.
    """
    logger.info(f"Generating report for {request.dataset_name}")

    try:
        # Generate dataset
        generator = DatasetGenerator()
        if request.dataset_type == "image":
            dataset = generator.generate_image_dataset(
                n_samples=request.n_samples,
                n_classes=request.n_classes,
                poison_ratio=request.poison_ratio,
                seed=request.seed,
            )
        else:
            dataset = generator.generate_tabular_dataset(
                n_samples=request.n_samples,
                n_classes=request.n_classes,
                poison_ratio=request.poison_ratio,
                seed=request.seed,
            )

        # Run analyses
        spectral = SpectralSignaturesDetector()
        spectral_result = spectral.analyze(dataset.data, dataset.labels)

        clustering = ActivationClusteringDetector()
        clustering_result = clustering.analyze(dataset.data, dataset.labels)

        risk_engine = CollapseRiskEngine()
        risk_result = risk_engine.assess(
            dataset.data,
            dataset.labels,
            {
                "suspected_indices": spectral_result.suspected_indices,
                "trigger_score": spectral_result.poisoning_score,
            },
        )

        # Compile results
        results = {
            "poisoning_score": (
                spectral_result.poisoning_score + clustering_result.poisoning_score
            )
            / 2,
            "suspected_indices": spectral_result.suspected_indices,
            "spectral_score": spectral_result.poisoning_score,
            "clustering_score": clustering_result.poisoning_score,
            "trigger_score": 0,
            "influence_score": 0,
            "risk_result": {
                "collapse_risk_score": risk_result.collapse_risk_score,
                "risk_level": risk_result.risk_level.value,
            },
            "recommendations": risk_result.recommendations,
        }

        # Generate report
        report_gen = PDFReportGenerator(output_dir=Path("logs/reports"))
        report_path = report_gen.generate_report(results, request.dataset_name)

        with open(report_path, "r") as f:
            html_content = f.read()

        return HTMLResponse(content=html_content)

    except Exception as e:
        logger.error(f"Report generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
