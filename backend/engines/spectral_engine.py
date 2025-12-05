"""
Spectral Signatures Engine.

Implements spectral signatures analysis for poisoning detection.
"""

from typing import Any, Dict, List

import numpy as np
from scipy import stats
from sklearn.decomposition import PCA, TruncatedSVD
from sklearn.preprocessing import StandardScaler

from backend.utils import get_logger

logger = get_logger("spectral_engine")


class SpectralResult:
    """Result of spectral signatures analysis."""

    def __init__(
        self,
        poisoning_score: float,
        suspected_indices: List[int],
        outlier_scores: np.ndarray,
        singular_values: np.ndarray,
        analysis_details: Dict[str, Any],
    ):
        """Initialize result."""
        self.poisoning_score = poisoning_score
        self.suspected_indices = suspected_indices
        self.outlier_scores = outlier_scores
        self.singular_values = singular_values
        self.analysis_details = analysis_details


class SpectralSignaturesDetector:
    """
    Detects poisoned samples using spectral signatures.

    Based on the principle that poisoned samples often form a separable
    subspace in the feature representation.
    """

    def __init__(self, n_components: int = 10, detection_threshold: float = 2.0):
        """
        Initialize detector.

        Args:
            n_components: Number of singular vectors to analyze.
            detection_threshold: Z-score threshold for outlier detection.
        """
        self.n_components = n_components
        self.detection_threshold = detection_threshold

    def analyze(self, data: np.ndarray, labels: np.ndarray) -> SpectralResult:
        """
        Perform spectral signatures analysis.

        Args:
            data: Feature matrix (n_samples, n_features).
            labels: Label array (n_samples,).

        Returns:
            SpectralResult containing scores and suspected indices.
        """
        logger.info(f"Starting spectral analysis on {len(data)} samples")

        # Flatten image data if needed
        if len(data.shape) > 2:
            flat_data = data.reshape(data.shape[0], -1)
        else:
            flat_data = data

        # Normalize data
        scaler = StandardScaler()
        normalized_data = scaler.fit_transform(flat_data)

        # Compute SVD
        # Use RandomizedSVD (via TruncatedSVD) for efficiency on large datasets
        svd = TruncatedSVD(
            n_components=min(self.n_components, flat_data.shape[1] - 1), random_state=42
        )
        svd.fit(normalized_data)
        singular_values = svd.singular_values_

        # Analyze per class
        suspected_indices: List[int] = []
        outlier_scores = np.zeros(len(data))
        details: Dict[str, Any] = {}

        unique_labels = np.unique(labels)
        for label in unique_labels:
            class_mask = labels == label
            class_indices = np.where(class_mask)[0]
            class_data = normalized_data[class_mask]

            if len(class_data) < 5:
                continue

            # Compute class mean
            class_mean = np.mean(class_data, axis=0)
            centered_data = class_data - class_mean

            # Project onto top singular vector of the class
            pca = PCA(n_components=1, random_state=42)
            projections = pca.fit_transform(centered_data).flatten()

            # Calculate outlier scores (distance from center in projection)
            scores = np.abs(projections)
            z_scores = np.abs(stats.zscore(scores))

            # Flag outliers
            outliers = np.where(z_scores > self.detection_threshold)[0]
            global_indices = class_indices[outliers]
            suspected_indices.extend(global_indices)

            # Store scores
            outlier_scores[class_indices] = z_scores

            details[str(label)] = {
                "n_samples": len(class_indices),
                "n_suspected": len(outliers),
            }

        # Calculate overall poisoning score (0-100)
        poison_ratio = len(suspected_indices) / len(data) if len(data) > 0 else 0
        poisoning_score = min(100.0, poison_ratio * 500)  # Scale up for visibility

        return SpectralResult(
            poisoning_score=poisoning_score,
            suspected_indices=sorted(list(set(suspected_indices))),
            outlier_scores=outlier_scores,
            singular_values=singular_values,
            analysis_details=details,
        )
