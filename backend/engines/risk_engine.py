"""
Model Collapse Risk Engine.

Computes training-time risk scores for dataset quality.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List

import numpy as np

from backend.utils import get_logger

logger = get_logger("risk_engine")


class RiskLevel(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class RiskResult:
    """Result of risk assessment."""

    collapse_risk_score: float
    risk_level: RiskLevel
    risk_factors: Dict[str, float]
    recommendations: List[str]
    details: Dict[str, Any] = field(default_factory=dict)


class CollapseRiskEngine:
    """Compute model collapse risk from dataset characteristics."""

    def __init__(self):
        self.risk_weights = {
            "overfit_potential": 0.2,
            "representation_collapse": 0.25,
            "class_boundary_distortion": 0.2,
            "poisoning_density": 0.25,
            "trigger_confidence": 0.1,
        }

    def assess(
        self,
        data: np.ndarray,
        labels: np.ndarray,
        poisoning_info: Dict[str, Any] = None,
    ) -> RiskResult:
        """Assess collapse risk for dataset."""
        logger.info(f"Assessing collapse risk for {len(data)} samples")

        flat_data = data.reshape(data.shape[0], -1)

        risk_factors = {}

        # 1. Overfit Potential
        risk_factors["overfit_potential"] = self._compute_overfit_risk(
            flat_data, labels
        )

        # 2. Representation Collapse
        risk_factors["representation_collapse"] = self._compute_collapse_risk(flat_data)

        # 3. Class Boundary Distortion
        risk_factors["class_boundary_distortion"] = self._compute_boundary_risk(
            flat_data, labels
        )

        # 4. Poisoning Density
        if poisoning_info:
            risk_factors["poisoning_density"] = self._compute_poison_density(
                poisoning_info, len(data)
            )
        else:
            risk_factors["poisoning_density"] = 0.0

        # 5. Trigger Confidence
        if poisoning_info and "trigger_score" in poisoning_info:
            risk_factors["trigger_confidence"] = poisoning_info["trigger_score"] / 100.0
        else:
            risk_factors["trigger_confidence"] = 0.0

        # Compute weighted score
        collapse_risk_score = sum(
            risk_factors[k] * self.risk_weights[k] * 100 for k in self.risk_weights
        )
        collapse_risk_score = min(100, max(0, collapse_risk_score))

        # Determine risk level
        risk_level = self._get_risk_level(collapse_risk_score)

        # Generate recommendations
        recommendations = self._generate_recommendations(risk_factors, risk_level)

        return RiskResult(
            collapse_risk_score=collapse_risk_score,
            risk_level=risk_level,
            risk_factors=risk_factors,
            recommendations=recommendations,
            details={"n_samples": len(data), "n_classes": len(np.unique(labels))},
        )

    def _compute_overfit_risk(self, data: np.ndarray, labels: np.ndarray) -> float:
        """Compute overfitting risk based on data characteristics."""
        n_samples, n_features = data.shape
        n_classes = len(np.unique(labels))

        # Risk increases with high dimensionality and low samples
        samples_per_feature = n_samples / n_features
        samples_per_class = n_samples / n_classes

        risk = 0.0
        if samples_per_feature < 10:
            risk += 0.3
        if samples_per_class < 50:
            risk += 0.3

        # Check for class imbalance
        _, counts = np.unique(labels, return_counts=True)
        imbalance = counts.max() / counts.min()
        if imbalance > 5:
            risk += 0.4

        return min(1.0, risk)

    def _compute_collapse_risk(self, data: np.ndarray) -> float:
        """Compute representation collapse risk."""
        # Check variance across features
        feature_vars = data.var(axis=0)
        low_var_ratio = (feature_vars < 0.01).sum() / len(feature_vars)

        # Check effective rank
        try:
            U, s, Vt = np.linalg.svd(data[: min(1000, len(data))], full_matrices=False)
            total_var = (s**2).sum()
            cumvar = np.cumsum(s**2) / total_var
            effective_rank = np.searchsorted(cumvar, 0.95) + 1
            rank_ratio = effective_rank / min(data.shape)
        except:
            rank_ratio = 1.0

        risk = low_var_ratio * 0.5 + (1 - rank_ratio) * 0.5
        return min(1.0, risk)

    def _compute_boundary_risk(self, data: np.ndarray, labels: np.ndarray) -> float:
        """Compute class boundary distortion risk."""
        try:
            # Simple heuristic for boundary distortion
            # Measure overlap between class distributions
            unique_labels = np.unique(labels)
            if len(unique_labels) < 2:
                return 0.0

            centroids = []
            for label in unique_labels:
                centroids.append(np.mean(data[labels == label], axis=0))

            centroids = np.array(centroids)
            # Average distance between centroids
            dists = np.linalg.norm(centroids[:, None] - centroids, axis=2)
            avg_dist = np.mean(dists[dists > 0])

            # Normalize (heuristic)
            score = max(0.0, 100.0 - avg_dist * 10)
            return min(100.0, score)

        except Exception:
            return 50.0

    def _compute_poison_density(
        self, poisoning_info: Dict[str, Any], n_samples: int
    ) -> float:
        """Compute risk from poisoning density.

        Args:
            poisoning_info: Dictionary containing suspected_indices.
            n_samples: Total number of samples in dataset.

        Returns:
            Poisoning density risk score (0-1 scale).
        """
        if not poisoning_info:
            return 0.0

        n_suspected = len(poisoning_info.get("suspected_indices", []))
        ratio = n_suspected / n_samples if n_samples > 0 else 0

        # Normalize to 0-1 scale (high risk if > 10% is suspected)
        return min(1.0, ratio * 10)

    def _get_risk_level(self, score: float) -> RiskLevel:
        if score >= 75:
            return RiskLevel.CRITICAL
        elif score >= 50:
            return RiskLevel.HIGH
        elif score >= 25:
            return RiskLevel.MEDIUM
        return RiskLevel.LOW

    def _generate_recommendations(
        self, factors: Dict[str, float], risk_level: RiskLevel
    ) -> List[str]:
        """Generate actionable recommendations based on risk factors and level.

        Args:
            factors: Dictionary of risk factor scores (0-1 scale).
            risk_level: Overall risk level classification.

        Returns:
            List of actionable recommendation strings.
        """
        recs = []

        # Add risk-level specific warnings
        if risk_level == RiskLevel.CRITICAL:
            recs.append(
                "⚠️ CRITICAL: Dataset is unsafe for training. Immediate intervention required."
            )
        elif risk_level == RiskLevel.HIGH:
            recs.append(
                "⚠️ HIGH RISK: Significant dataset issues detected. Review before training."
            )

        if factors["overfit_potential"] > 0.7:
            recs.append(
                "Increase dataset size or apply regularization to prevent overfitting."
            )

        if factors["representation_collapse"] > 0.7:
            recs.append("Check for duplicate samples or low-variance features.")

        if factors["class_boundary_distortion"] > 70:  # This one uses 0-100 scale
            recs.append(
                "Classes are poorly separated. Review label quality and feature selection."
            )

        if factors["poisoning_density"] > 0.5:
            recs.append(
                "High concentration of suspected poisoning. Run 'Clean' module immediately."
            )

        if factors["trigger_confidence"] > 0.5:
            recs.append(
                "Strong indicators of backdoor triggers. Inspect high-confidence samples."
            )

        if not recs:
            recs.append("✅ Dataset appears healthy. Proceed with training.")

        return recs
