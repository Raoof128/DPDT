"""
Dataset Cleanser / Scrubber.

Provides automatic and manual cleaning of poisoned datasets.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

import numpy as np

from backend.utils import get_logger

logger = get_logger("cleanser")


class CleansingMode(Enum):
    STRICT = "strict"  # Remove all flagged
    SAFE = "safe"  # Remove high confidence only
    REVIEW = "review"  # Manual review mode


@dataclass
class CleansingResult:
    """Result of dataset cleansing."""

    cleaned_data: np.ndarray
    cleaned_labels: np.ndarray
    removed_indices: List[int]
    kept_indices: List[int]
    relabel_suggestions: List[Dict[str, Any]]
    summary: Dict[str, Any]


class DatasetCleanser:
    """Clean poisoned datasets."""

    def __init__(
        self,
        mode: CleansingMode = CleansingMode.SAFE,
        confidence_threshold: float = 0.7,
    ):
        self.mode = mode
        self.confidence_threshold = confidence_threshold

    def clean(
        self,
        data: np.ndarray,
        labels: np.ndarray,
        suspected_indices: List[int],
        confidence_scores: Optional[np.ndarray] = None,
    ) -> CleansingResult:
        """Clean dataset by removing suspected samples."""
        logger.info(f"Cleaning dataset with {len(suspected_indices)} suspected samples")

        n_samples = len(data)
        remove_indices = set()

        if self.mode == CleansingMode.STRICT:
            remove_indices = set(suspected_indices)
        elif self.mode == CleansingMode.SAFE:
            if confidence_scores is not None:
                for idx in suspected_indices:
                    if confidence_scores[idx] >= self.confidence_threshold:
                        remove_indices.add(idx)
            else:
                # Remove top 50% by default
                remove_indices = set(suspected_indices[: len(suspected_indices) // 2])
        else:  # REVIEW mode
            remove_indices = set()  # Nothing auto-removed

        kept_indices = [i for i in range(n_samples) if i not in remove_indices]
        removed_indices = sorted(remove_indices)

        cleaned_data = data[kept_indices]
        cleaned_labels = labels[kept_indices]

        # Generate relabel suggestions
        relabel_suggestions = self._generate_relabel_suggestions(
            data, labels, suspected_indices, remove_indices
        )

        summary = {
            "original_samples": n_samples,
            "removed_samples": len(removed_indices),
            "remaining_samples": len(kept_indices),
            "removal_ratio": len(removed_indices) / n_samples,
            "mode": self.mode.value,
        }

        return CleansingResult(
            cleaned_data=cleaned_data,
            cleaned_labels=cleaned_labels,
            removed_indices=removed_indices,
            kept_indices=kept_indices,
            relabel_suggestions=relabel_suggestions,
            summary=summary,
        )

    def _generate_relabel_suggestions(
        self, data: np.ndarray, labels: np.ndarray, suspected: List[int], removed: set
    ) -> List[Dict[str, Any]]:
        """Generate relabeling suggestions for samples not removed."""
        suggestions = []
        flat_data = data.reshape(data.shape[0], -1)
        unique_labels = np.unique(labels)

        # Compute class centroids
        centroids = {}
        for label in unique_labels:
            class_data = flat_data[labels == label]
            centroids[label] = class_data.mean(axis=0)

        for idx in suspected:
            if idx in removed:
                continue

            current_label = labels[idx]
            sample = flat_data[idx]

            # Find nearest centroid
            distances = {}
            for label, centroid in centroids.items():
                distances[label] = np.linalg.norm(sample - centroid)

            nearest_label = min(distances, key=distances.get)

            if nearest_label != current_label:
                suggestions.append(
                    {
                        "index": idx,
                        "current_label": int(current_label),
                        "suggested_label": int(nearest_label),
                        "confidence": 1.0
                        - distances[nearest_label] / sum(distances.values()),
                    }
                )

        return suggestions[:50]


class TriggerRemover:
    """Remove trigger patterns from data."""

    def remove_image_triggers(
        self, images: np.ndarray, trigger_info: Dict[str, Any]
    ) -> np.ndarray:
        """Remove detected triggers from images."""
        logger.info("Removing image triggers")
        cleaned = images.copy()

        for trigger in trigger_info.get("detected_triggers", []):
            if trigger["type"] in ["pixel_trigger", "corner_trigger"]:
                row, col = trigger["location"]
                size = trigger.get("size", 5)

                for idx in trigger.get("sample_indices", []):
                    if idx < len(cleaned):
                        # Replace trigger region with local mean
                        region = cleaned[
                            idx,
                            max(0, row - size) : row + 2 * size,
                            max(0, col - size) : col + 2 * size,
                        ]
                        mean_val = region.mean()
                        cleaned[idx, row : row + size, col : col + size] = mean_val

        return cleaned

    def remove_text_triggers(
        self, texts: np.ndarray, trigger_info: Dict[str, Any]
    ) -> np.ndarray:
        """Remove detected triggers from text."""
        logger.info("Removing text triggers")
        cleaned = texts.copy()

        for trigger in trigger_info.get("detected_triggers", []):
            if trigger["type"] == "token_trigger":
                pos = trigger["position"]
                token = trigger["token_id"]
                mask = cleaned[:, pos] == token
                cleaned[mask, pos] = 0  # Replace with padding token

        return cleaned
