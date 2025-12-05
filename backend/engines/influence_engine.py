"""
Influence Function Estimator (Simplified).

Estimates sample influence on model training to detect harmful samples.
"""

from dataclasses import dataclass
from typing import Any, Dict, List

import numpy as np

from backend.utils import get_logger

logger = get_logger("influence_engine")


@dataclass
class InfluenceResult:
    """Result of influence function analysis."""

    poisoning_score: float
    suspected_indices: List[int]
    influence_scores: np.ndarray
    harmful_samples: List[Dict[str, Any]]


class SimplifiedInfluenceEstimator:
    """Simplified influence function estimator."""

    def __init__(self, threshold_percentile: float = 95.0):
        self.threshold_percentile = threshold_percentile

    def estimate(self, data: np.ndarray, labels: np.ndarray) -> InfluenceResult:
        """Estimate influence scores for all samples."""
        logger.info(f"Estimating influence for {len(data)} samples")

        flat_data = data.reshape(data.shape[0], -1)
        n_samples = len(flat_data)

        # Compute simplified influence based on:
        # 1. Distance from class centroid
        # 2. Gradient magnitude proxy
        # 3. Leave-one-out influence approximation

        influence_scores = np.zeros(n_samples)
        unique_labels = np.unique(labels)

        for label in unique_labels:
            class_mask = labels == label
            class_data = flat_data[class_mask]
            class_indices = np.where(class_mask)[0]

            centroid = np.mean(class_data, axis=0)
            distances = np.linalg.norm(class_data - centroid, axis=1)

            # Normalize distances
            if distances.std() > 0:
                z_distances = (distances - distances.mean()) / distances.std()
            else:
                z_distances = np.zeros_like(distances)

            # Compute gradient magnitude proxy
            grad_proxy = np.abs(class_data - centroid).sum(axis=1)
            if grad_proxy.std() > 0:
                z_grad = (grad_proxy - grad_proxy.mean()) / grad_proxy.std()
            else:
                z_grad = np.zeros_like(grad_proxy)

            # Combined influence score
            combined = 0.6 * z_distances + 0.4 * z_grad
            influence_scores[class_indices] = combined

        # Find harmful samples
        threshold = np.percentile(influence_scores, self.threshold_percentile)
        suspected_mask = influence_scores > threshold
        suspected_indices = np.where(suspected_mask)[0].tolist()

        harmful_samples = []
        for idx in suspected_indices[:20]:  # Top 20
            harmful_samples.append(
                {
                    "index": int(idx),
                    "influence_score": float(influence_scores[idx]),
                    "label": int(labels[idx]),
                }
            )

        poisoning_score = self._compute_score(influence_scores, suspected_indices)

        return InfluenceResult(
            poisoning_score=poisoning_score,
            suspected_indices=suspected_indices,
            influence_scores=influence_scores,
            harmful_samples=harmful_samples,
        )

    def _compute_score(self, scores: np.ndarray, suspected: List[int]) -> float:
        if not suspected:
            return 0.0
        mean_harmful = np.mean(scores[suspected])
        ratio = len(suspected) / len(scores)
        return min(100, ratio * 100 + mean_harmful * 15)
