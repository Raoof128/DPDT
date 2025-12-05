"""
Poison Detection API Endpoints.

POST /detect_poison - Full poisoning detection pipeline.
"""

from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.engines import (
    ActivationClusteringDetector,
    DatasetGenerator,
    SimplifiedInfluenceEstimator,
    SpectralSignaturesDetector,
    UniversalTriggerDetector,
)
from backend.utils import get_logger

logger = get_logger("api.poison")
router = APIRouter(prefix="/detect_poison", tags=["poison"])


class DetectRequest(BaseModel):
    """Request for poisoning detection."""

    dataset_type: str = Field(..., description="Type: image, text, tabular")
    n_samples: int = Field(1000, ge=10, le=50000)
    n_classes: int = Field(10, ge=2, le=100)
    poison_ratio: float = Field(0.1, ge=0.0, le=0.5)
    seed: int = Field(42)
    run_spectral: bool = Field(True)
    run_clustering: bool = Field(True)
    run_influence: bool = Field(True)
    run_trigger: bool = Field(True)


class DetectResponse(BaseModel):
    """Response with detection results."""

    poisoning_score: float
    suspected_indices: List[int]
    spectral_result: Dict[str, Any]
    clustering_result: Dict[str, Any]
    influence_result: Dict[str, Any]
    trigger_result: Dict[str, Any]
    ground_truth_poison_indices: List[int]
    detection_accuracy: Dict[str, float]


@router.post("", response_model=DetectResponse)
async def detect_poison(request: DetectRequest) -> DetectResponse:
    """
    Run full poisoning detection pipeline on synthetic dataset.

    Applies spectral signatures, activation clustering, influence
    estimation, and trigger detection to identify poisoned samples.
    """
    logger.info(f"Running poison detection on {request.dataset_type} dataset")

    try:
        # Generate synthetic dataset with known poisoning
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
        else:
            dataset = generator.generate_tabular_dataset(
                n_samples=request.n_samples,
                n_classes=request.n_classes,
                poison_ratio=request.poison_ratio,
                seed=request.seed,
            )

        ground_truth = dataset.metadata.get("poison_indices", [])
        all_suspected = set()
        results = {}

        # 1. Spectral Signatures
        if request.run_spectral:
            spectral = SpectralSignaturesDetector()
            spectral_result = spectral.analyze(dataset.data, dataset.labels)
            results["spectral"] = {
                "score": spectral_result.poisoning_score,
                "n_suspected": len(spectral_result.suspected_indices),
            }
            all_suspected.update(spectral_result.suspected_indices)
        else:
            results["spectral"] = {"score": 0, "n_suspected": 0}

        # 2. Activation Clustering
        if request.run_clustering:
            clustering = ActivationClusteringDetector()
            clustering_result = clustering.analyze(dataset.data, dataset.labels)
            results["clustering"] = {
                "score": clustering_result.poisoning_score,
                "n_suspected": len(clustering_result.suspected_indices),
                "n_misaligned": len(clustering_result.misaligned_clusters),
            }
            all_suspected.update(clustering_result.suspected_indices)
        else:
            results["clustering"] = {"score": 0, "n_suspected": 0}

        # 3. Influence Estimation
        if request.run_influence:
            influence = SimplifiedInfluenceEstimator()
            influence_result = influence.estimate(dataset.data, dataset.labels)
            results["influence"] = {
                "score": influence_result.poisoning_score,
                "n_suspected": len(influence_result.suspected_indices),
                "top_harmful": influence_result.harmful_samples[:5],
            }
            all_suspected.update(influence_result.suspected_indices)
        else:
            results["influence"] = {"score": 0, "n_suspected": 0}

        # 4. Trigger Detection
        if request.run_trigger:
            trigger = UniversalTriggerDetector()
            trigger_result = trigger.detect(
                dataset.data, dataset.labels, request.dataset_type
            )
            results["trigger"] = {
                "score": trigger_result.poisoning_score,
                "n_triggers": len(trigger_result.detected_triggers),
                "patterns": trigger_result.suspicious_patterns,
            }
        else:
            results["trigger"] = {"score": 0, "n_triggers": 0}

        # Compute overall score
        scores = [
            results[k]["score"]
            for k in ["spectral", "clustering", "influence", "trigger"]
        ]
        overall_score = sum(scores) / len(scores)

        # Compute detection accuracy
        suspected_list = sorted(all_suspected)
        accuracy = compute_detection_accuracy(
            ground_truth, suspected_list, request.n_samples
        )

        return DetectResponse(
            poisoning_score=overall_score,
            suspected_indices=suspected_list,
            spectral_result=results["spectral"],
            clustering_result=results["clustering"],
            influence_result=results["influence"],
            trigger_result=results["trigger"],
            ground_truth_poison_indices=ground_truth,
            detection_accuracy=accuracy,
        )

    except Exception as e:
        logger.error(f"Detection failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def compute_detection_accuracy(
    ground_truth: List[int], detected: List[int], total: int
) -> Dict[str, float]:
    """Compute detection accuracy metrics."""
    gt_set = set(ground_truth)
    det_set = set(detected)

    if not gt_set:
        return {"precision": 1.0, "recall": 1.0, "f1": 1.0, "false_positive_rate": 0.0}

    true_positives = len(gt_set & det_set)
    false_positives = len(det_set - gt_set)
    false_negatives = len(gt_set - det_set)
    true_negatives = total - len(gt_set | det_set)

    precision = true_positives / max(1, true_positives + false_positives)
    recall = true_positives / max(1, true_positives + false_negatives)
    f1 = 2 * precision * recall / max(0.001, precision + recall)
    fpr = false_positives / max(1, false_positives + true_negatives)

    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "false_positive_rate": fpr,
    }
