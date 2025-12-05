"""
Clean API Endpoints.

POST /clean - Clean poisoned dataset.
"""

from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.engines import (
    CleansingMode,
    DatasetCleanser,
    DatasetGenerator,
    SpectralSignaturesDetector,
)
from backend.utils import get_logger

logger = get_logger("api.clean")
router = APIRouter(prefix="/clean", tags=["clean"])


class CleanRequest(BaseModel):
    """Request for dataset cleaning."""

    dataset_type: str = Field("image")
    n_samples: int = Field(1000, ge=10, le=50000)
    n_classes: int = Field(10, ge=2, le=100)
    poison_ratio: float = Field(0.1, ge=0.0, le=0.5)
    seed: int = Field(42)
    mode: str = Field("safe", description="Cleaning mode: strict, safe, review")
    confidence_threshold: float = Field(0.7, ge=0.0, le=1.0)


class CleanResponse(BaseModel):
    """Response with cleaning results."""

    original_samples: int
    removed_samples: int
    remaining_samples: int
    removal_ratio: float
    removed_indices: List[int]
    relabel_suggestions: List[Dict[str, Any]]
    mode: str


@router.post("", response_model=CleanResponse)
async def clean_dataset(request: CleanRequest) -> CleanResponse:
    """
    Clean a poisoned dataset by removing suspected samples.

    Supports three modes:
    - STRICT: Remove all flagged samples
    - SAFE: Remove only high-confidence detections
    - REVIEW: Generate suggestions without removing
    """
    logger.info(f"Cleaning dataset with mode={request.mode}")

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

        # Detect poisoning first
        spectral = SpectralSignaturesDetector()
        result = spectral.analyze(dataset.data, dataset.labels)

        # Clean dataset
        mode_map = {
            "strict": CleansingMode.STRICT,
            "safe": CleansingMode.SAFE,
            "review": CleansingMode.REVIEW,
        }
        cleanser = DatasetCleanser(
            mode=mode_map.get(request.mode, CleansingMode.SAFE),
            confidence_threshold=request.confidence_threshold,
        )

        clean_result = cleanser.clean(
            dataset.data,
            dataset.labels,
            result.suspected_indices,
            result.outlier_scores,
        )

        return CleanResponse(
            original_samples=clean_result.summary["original_samples"],
            removed_samples=clean_result.summary["removed_samples"],
            remaining_samples=clean_result.summary["remaining_samples"],
            removal_ratio=clean_result.summary["removal_ratio"],
            removed_indices=clean_result.removed_indices,
            relabel_suggestions=clean_result.relabel_suggestions[:20],
            mode=request.mode,
        )

    except Exception as e:
        logger.error(f"Cleaning failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
