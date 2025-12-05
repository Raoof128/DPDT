"""
Collapse Risk API Endpoints.

POST /collapse_risk - Compute model collapse risk.
"""

from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.engines import (
    CollapseRiskEngine,
    DatasetGenerator,
    SpectralSignaturesDetector,
)
from backend.utils import get_logger

logger = get_logger("api.collapse")
router = APIRouter(prefix="/collapse_risk", tags=["collapse"])


class CollapseRequest(BaseModel):
    """Request for collapse risk assessment."""

    dataset_type: str = Field("image")
    n_samples: int = Field(1000, ge=10, le=50000)
    n_classes: int = Field(10, ge=2, le=100)
    poison_ratio: float = Field(0.1, ge=0.0, le=0.5)
    seed: int = Field(42)


class CollapseResponse(BaseModel):
    """Response with collapse risk results."""

    collapse_risk_score: float
    risk_level: str
    risk_factors: Dict[str, float]
    recommendations: List[str]
    details: Dict[str, Any]


@router.post("", response_model=CollapseResponse)
async def assess_collapse_risk(request: CollapseRequest) -> CollapseResponse:
    """
    Assess model collapse risk for a dataset.

    Analyzes:
    - Overfit potential
    - Representation collapse
    - Class boundary distortion
    - Poisoning density
    - Trigger confidence
    """
    logger.info(f"Assessing collapse risk for {request.dataset_type} dataset")

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

        # Get poisoning info
        spectral = SpectralSignaturesDetector()
        spectral_result = spectral.analyze(dataset.data, dataset.labels)

        poisoning_info = {
            "suspected_indices": spectral_result.suspected_indices,
            "trigger_score": spectral_result.poisoning_score,
        }

        # Assess risk
        risk_engine = CollapseRiskEngine()
        result = risk_engine.assess(dataset.data, dataset.labels, poisoning_info)

        return CollapseResponse(
            collapse_risk_score=result.collapse_risk_score,
            risk_level=result.risk_level.value,
            risk_factors=result.risk_factors,
            recommendations=result.recommendations,
            details=result.details,
        )

    except Exception as e:
        logger.error(f"Risk assessment failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
