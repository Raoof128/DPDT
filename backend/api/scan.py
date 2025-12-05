"""
Scan API Endpoints.

POST /scan - Scan dataset for poisoning indicators.
"""

from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.engines import DatasetGenerator, DatasetValidator
from backend.utils import get_logger

logger = get_logger("api.scan")
router = APIRouter(prefix="/scan", tags=["scan"])


class ScanRequest(BaseModel):
    """Request model for dataset scan."""

    dataset_type: str = Field(..., description="Type: image, text, tabular")
    n_samples: int = Field(1000, ge=10, le=100000)
    n_classes: int = Field(10, ge=2, le=1000)
    poison_ratio: float = Field(0.0, ge=0.0, le=0.5)
    seed: int = Field(42)


class ScanResponse(BaseModel):
    """Response model for dataset scan."""

    is_valid: bool
    quality_score: float
    n_samples: int
    n_classes: int
    anomalies: List[Dict[str, Any]]
    warnings: List[str]
    fingerprint: Dict[str, Any]  # Contains strings and ints
    stats: Dict[str, Any]


@router.post("", response_model=ScanResponse)
async def scan_dataset(request: ScanRequest) -> ScanResponse:
    """
    Scan a synthetic dataset for quality issues and anomalies.

    This endpoint generates a synthetic dataset and validates it,
    returning quality scores, anomalies, and fingerprint.
    """
    logger.info(
        f"Scanning {request.dataset_type} dataset with {request.n_samples} samples"
    )

    try:
        # Generate synthetic dataset
        generator = DatasetGenerator()

        if request.dataset_type == "image":
            dataset = generator.generate_image_dataset(
                n_samples=request.n_samples,
                n_classes=request.n_classes,
                poison_ratio=request.poison_ratio,
                seed=request.seed,
            )
        elif request.dataset_type == "text":
            dataset = generator.generate_text_dataset(
                n_samples=request.n_samples,
                n_classes=request.n_classes,
                poison_ratio=request.poison_ratio,
                seed=request.seed,
            )
        elif request.dataset_type == "tabular":
            dataset = generator.generate_tabular_dataset(
                n_samples=request.n_samples,
                n_classes=request.n_classes,
                poison_ratio=request.poison_ratio,
                seed=request.seed,
            )
        else:
            raise HTTPException(
                status_code=400, detail=f"Unknown dataset type: {request.dataset_type}"
            )

        # Validate dataset
        validator = DatasetValidator()
        result = validator.validate(dataset)

        return ScanResponse(
            is_valid=result.is_valid,
            quality_score=result.quality_score,
            n_samples=request.n_samples,
            n_classes=request.n_classes,
            anomalies=result.anomalies,
            warnings=result.warnings,
            fingerprint=result.fingerprint or {},
            stats=result.stats,
        )

    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    except Exception as e:
        logger.error(f"Scan failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
