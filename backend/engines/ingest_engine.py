"""
Dataset Ingestion & Validation Engine.

Supports image, text, and tabular datasets with comprehensive validation.
All data is synthetic for educational purposes.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from scipy import stats

from backend.utils import compute_dataset_fingerprint, get_logger

logger = get_logger("ingest_engine")


class DatasetType(Enum):
    """Supported dataset types."""

    IMAGE = "image"
    TEXT = "text"
    TABULAR = "tabular"


@dataclass
class ValidationResult:
    """Result of dataset validation."""

    is_valid: bool
    quality_score: float  # 0-100
    anomalies: List[Dict[str, Any]] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    fingerprint: Optional[Dict[str, str]] = None
    stats: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SyntheticDataset:
    """Container for synthetic dataset."""

    data: np.ndarray
    labels: np.ndarray
    dataset_type: DatasetType
    metadata: Dict[str, Any] = field(default_factory=dict)


class DatasetGenerator:
    """
    Synthetic Dataset Generator.

    Generates SAFE, SYNTHETIC datasets for educational/testing purposes.
    NO real data is used.
    """

    @staticmethod
    def generate_image_dataset(
        n_samples: int = 1000,
        n_classes: int = 10,
        image_size: Tuple[int, int, int] = (28, 28, 1),
        poison_ratio: float = 0.0,
        seed: int = 42,
    ) -> SyntheticDataset:
        """
        Generate synthetic image dataset (MNIST-like).

        Args:
            n_samples: Number of samples
            n_classes: Number of classes
            image_size: Image dimensions (H, W, C)
            poison_ratio: Ratio of poisoned samples (0-1)
            seed: Random seed

        Returns:
            SyntheticDataset with image data
        """
        np.random.seed(seed)

        h, w, c = image_size
        data = np.random.randn(n_samples, h, w, c).astype(np.float32)
        labels = np.random.randint(0, n_classes, n_samples)

        # Add class-specific patterns (synthetic digit-like features)
        for i in range(n_samples):
            class_idx = labels[i]
            # Create synthetic class pattern
            pattern = np.zeros((h, w, c))
            # Add class-specific strokes
            row_start = (class_idx * 2) % (h - 5)
            col_start = (class_idx * 3) % (w - 5)
            pattern[row_start : row_start + 5, col_start : col_start + 5, :] = 1.0
            data[i] += pattern * 0.5

        # Normalize to [0, 1]
        data = (data - data.min()) / (data.max() - data.min() + 1e-8)

        # Add synthetic poisoning if requested
        n_poison = int(n_samples * poison_ratio)
        poison_indices = []

        if n_poison > 0:
            poison_indices = np.random.choice(
                n_samples, n_poison, replace=False
            ).tolist()
            for idx in poison_indices:
                # Add synthetic trigger pattern (small square in corner)
                data[idx, 0:4, 0:4, :] = 1.0  # White patch trigger
                # Flip label to target class
                labels[idx] = (labels[idx] + 1) % n_classes

        metadata = {
            "n_samples": n_samples,
            "n_classes": n_classes,
            "image_size": image_size,
            "poison_ratio": poison_ratio,
            "poison_indices": poison_indices,
            "seed": seed,
            "is_synthetic": True,
        }

        logger.info(
            f"Generated synthetic image dataset: {n_samples} samples, {n_classes} classes"
        )

        return SyntheticDataset(
            data=data, labels=labels, dataset_type=DatasetType.IMAGE, metadata=metadata
        )

    @staticmethod
    def generate_text_dataset(
        n_samples: int = 1000,
        n_classes: int = 5,
        max_length: int = 100,
        poison_ratio: float = 0.0,
        seed: int = 42,
    ) -> SyntheticDataset:
        """
        Generate synthetic text dataset.

        Args:
            n_samples: Number of samples
            n_classes: Number of classes
            max_length: Maximum sequence length
            poison_ratio: Ratio of poisoned samples
            seed: Random seed

        Returns:
            SyntheticDataset with text embeddings
        """
        np.random.seed(seed)

        # Generate synthetic word embeddings (simulating tokenized text)
        vocab_size = 1000

        data = np.random.randint(0, vocab_size, (n_samples, max_length))
        labels = np.random.randint(0, n_classes, n_samples)

        # Add class-specific token patterns
        for i in range(n_samples):
            class_idx = labels[i]
            # Insert class-specific tokens
            class_tokens = [100 + class_idx * 10 + j for j in range(5)]
            data[i, :5] = class_tokens

        # Convert to float for processing
        data = data.astype(np.float32)

        # Add synthetic text poisoning
        n_poison = int(n_samples * poison_ratio)
        poison_indices = []

        if n_poison > 0:
            poison_indices = np.random.choice(
                n_samples, n_poison, replace=False
            ).tolist()
            # Synthetic trigger: specific token sequence
            trigger_tokens = [999, 998, 997]  # Rare token trigger
            for idx in poison_indices:
                data[idx, -3:] = trigger_tokens
                labels[idx] = 0  # Target class

        metadata = {
            "n_samples": n_samples,
            "n_classes": n_classes,
            "max_length": max_length,
            "vocab_size": vocab_size,
            "poison_ratio": poison_ratio,
            "poison_indices": poison_indices,
            "seed": seed,
            "is_synthetic": True,
        }

        logger.info(
            f"Generated synthetic text dataset: {n_samples} samples, {n_classes} classes"
        )

        return SyntheticDataset(
            data=data, labels=labels, dataset_type=DatasetType.TEXT, metadata=metadata
        )

    @staticmethod
    def generate_tabular_dataset(
        n_samples: int = 1000,
        n_features: int = 20,
        n_classes: int = 3,
        poison_ratio: float = 0.0,
        seed: int = 42,
    ) -> SyntheticDataset:
        """
        Generate synthetic tabular dataset.

        Args:
            n_samples: Number of samples
            n_features: Number of features
            n_classes: Number of classes
            poison_ratio: Ratio of poisoned samples
            seed: Random seed

        Returns:
            SyntheticDataset with tabular data
        """
        np.random.seed(seed)

        # Generate class-conditional data
        data = np.zeros((n_samples, n_features), dtype=np.float32)
        labels = np.random.randint(0, n_classes, n_samples)

        for i in range(n_samples):
            class_idx = labels[i]
            # Class-specific mean
            mean = np.zeros(n_features)
            mean[
                class_idx
                * (n_features // n_classes) : (class_idx + 1)
                * (n_features // n_classes)
            ] = 1.0
            data[i] = np.random.randn(n_features) * 0.5 + mean

        # Add synthetic poisoning
        n_poison = int(n_samples * poison_ratio)
        poison_indices = []

        if n_poison > 0:
            poison_indices = np.random.choice(
                n_samples, n_poison, replace=False
            ).tolist()
            for idx in poison_indices:
                # Add outlier pattern
                data[idx, -3:] = 10.0  # Extreme values as trigger
                labels[idx] = (labels[idx] + 1) % n_classes

        metadata = {
            "n_samples": n_samples,
            "n_features": n_features,
            "n_classes": n_classes,
            "poison_ratio": poison_ratio,
            "poison_indices": poison_indices,
            "seed": seed,
            "is_synthetic": True,
        }

        logger.info(
            f"Generated synthetic tabular dataset: {n_samples} samples, {n_features} features"
        )

        return SyntheticDataset(
            data=data,
            labels=labels,
            dataset_type=DatasetType.TABULAR,
            metadata=metadata,
        )


class DatasetValidator:
    """
    Comprehensive Dataset Validator.

    Validates schema, labels, distributions, and detects anomalies.
    """

    def __init__(self, strict_mode: bool = False):
        """
        Initialize validator.

        Args:
            strict_mode: Enable strict validation rules
        """
        self.strict_mode = strict_mode
        self.logger = get_logger("validator")

    def validate(self, dataset: SyntheticDataset) -> ValidationResult:
        """
        Perform comprehensive dataset validation.

        Args:
            dataset: Dataset to validate

        Returns:
            ValidationResult with scores and anomalies
        """
        anomalies = []
        warnings = []
        scores = []

        # 1. Schema Validation
        schema_score, schema_issues = self._validate_schema(dataset)
        scores.append(schema_score)
        anomalies.extend(schema_issues)

        # 2. Label Consistency
        label_score, label_issues = self._validate_labels(dataset)
        scores.append(label_score)
        anomalies.extend(label_issues)

        # 3. Missing Values
        missing_score, missing_issues = self._check_missing_values(dataset)
        scores.append(missing_score)
        anomalies.extend(missing_issues)

        # 4. Duplicates
        dup_score, dup_issues = self._check_duplicates(dataset)
        scores.append(dup_score)
        anomalies.extend(dup_issues)

        # 5. Distribution Analysis
        dist_score, dist_issues = self._analyze_distribution(dataset)
        scores.append(dist_score)
        anomalies.extend(dist_issues)

        # 6. Class Imbalance
        balance_score, balance_issues = self._check_class_balance(dataset)
        scores.append(balance_score)
        warnings.extend(balance_issues)

        # Compute overall quality score
        quality_score = np.mean(scores)

        # Compute fingerprint
        fingerprint = compute_dataset_fingerprint(
            dataset.data, dataset.labels, dataset.metadata
        )

        # Compute statistics
        stats = self._compute_statistics(dataset)

        is_valid = quality_score >= (80 if self.strict_mode else 60)

        self.logger.info(
            f"Validation complete: quality_score={quality_score:.1f}, valid={is_valid}"
        )

        return ValidationResult(
            is_valid=bool(is_valid),
            quality_score=float(quality_score),
            anomalies=anomalies,
            warnings=warnings,
            fingerprint=fingerprint,
            stats=stats,
        )

    def _validate_schema(
        self, dataset: SyntheticDataset
    ) -> Tuple[float, List[Dict[str, Any]]]:
        """Validate data schema and structure."""
        issues = []
        score = 100.0

        # Check data shape
        if len(dataset.data.shape) < 2:
            issues.append(
                {
                    "type": "schema_error",
                    "severity": "high",
                    "message": "Data must have at least 2 dimensions",
                }
            )
            score -= 30

        # Check labels shape
        if len(dataset.labels.shape) != 1:
            issues.append(
                {
                    "type": "schema_error",
                    "severity": "high",
                    "message": "Labels must be 1-dimensional",
                }
            )
            score -= 30

        # Check sample count match
        if dataset.data.shape[0] != len(dataset.labels):
            issues.append(
                {
                    "type": "schema_error",
                    "severity": "critical",
                    "message": f"Sample count mismatch: {dataset.data.shape[0]} vs {len(dataset.labels)}",
                }
            )
            score -= 50

        # Check data type
        if not np.issubdtype(dataset.data.dtype, np.floating):
            issues.append(
                {
                    "type": "schema_warning",
                    "severity": "low",
                    "message": f"Data type {dataset.data.dtype} is not floating point",
                }
            )
            score -= 5

        return max(0, score), issues

    def _validate_labels(
        self, dataset: SyntheticDataset
    ) -> Tuple[float, List[Dict[str, Any]]]:
        """Validate label consistency."""
        issues = []
        score = 100.0

        unique_labels = np.unique(dataset.labels)

        # Check for negative labels
        if np.any(dataset.labels < 0):
            issues.append(
                {
                    "type": "label_error",
                    "severity": "high",
                    "message": "Negative label values detected",
                }
            )
            score -= 20

        # Check for non-contiguous labels
        expected_labels = np.arange(len(unique_labels))
        if not np.array_equal(np.sort(unique_labels), expected_labels):
            issues.append(
                {
                    "type": "label_warning",
                    "severity": "medium",
                    "message": "Non-contiguous label values",
                }
            )
            score -= 10

        return max(0, score), issues

    def _check_missing_values(
        self, dataset: SyntheticDataset
    ) -> Tuple[float, List[Dict[str, Any]]]:
        """Check for missing values (NaN, Inf)."""
        issues = []
        score = 100.0

        nan_count: int = int(np.sum(np.isnan(dataset.data)))
        inf_count: int = int(np.sum(np.isinf(dataset.data)))

        if nan_count > 0:
            ratio = nan_count / dataset.data.size
            issues.append(
                {
                    "type": "missing_values",
                    "severity": "high" if ratio > 0.01 else "medium",
                    "message": f"Found {nan_count} NaN values ({ratio*100:.2f}%)",
                }
            )
            score -= min(50, ratio * 500)

        if inf_count > 0:
            ratio = inf_count / dataset.data.size
            issues.append(
                {
                    "type": "infinite_values",
                    "severity": "high",
                    "message": f"Found {inf_count} infinite values ({ratio*100:.2f}%)",
                }
            )
            score -= min(50, ratio * 500)

        return max(0, score), issues

    def _check_duplicates(
        self, dataset: SyntheticDataset
    ) -> Tuple[float, List[Dict[str, Any]]]:
        """Check for duplicate samples."""
        issues = []
        score = 100.0

        # Flatten samples for comparison
        flat_data = dataset.data.reshape(dataset.data.shape[0], -1)

        # Use random sampling for large datasets
        n_samples = min(1000, len(flat_data))
        sample_indices = np.random.choice(len(flat_data), n_samples, replace=False)
        sample_data = flat_data[sample_indices]

        # Check for near-duplicates using correlation
        n_checked = 0
        n_duplicates = 0

        for i in range(min(100, len(sample_data))):
            for j in range(i + 1, min(100, len(sample_data))):
                n_checked += 1
                if np.allclose(sample_data[i], sample_data[j], rtol=1e-5):
                    n_duplicates += 1

        if n_duplicates > 0:
            dup_ratio = n_duplicates / max(1, n_checked)
            issues.append(
                {
                    "type": "duplicates",
                    "severity": "medium",
                    "message": f"Detected ~{n_duplicates} near-duplicate pairs in sample",
                }
            )
            score -= min(30, dup_ratio * 100)

        return max(0, score), issues

    def _analyze_distribution(
        self, dataset: SyntheticDataset
    ) -> Tuple[float, List[Dict[str, Any]]]:
        """Analyze data distribution for anomalies."""
        issues = []
        score = 100.0

        flat_data = dataset.data.flatten()

        # Check for outliers using IQR
        q1 = np.percentile(flat_data, 25)
        q3 = np.percentile(flat_data, 75)
        iqr = q3 - q1
        lower_bound = q1 - 3 * iqr
        upper_bound = q3 + 3 * iqr

        outlier_count: int = int(np.sum((flat_data < lower_bound) | (flat_data > upper_bound)))
        outlier_ratio = outlier_count / len(flat_data)

        if outlier_ratio > 0.05:
            issues.append(
                {
                    "type": "distribution_anomaly",
                    "severity": "high" if outlier_ratio > 0.1 else "medium",
                    "message": f"High outlier ratio: {outlier_ratio*100:.2f}%",
                }
            )
            score -= min(30, outlier_ratio * 200)

        # Check for extreme skewness
        try:
            skewness = stats.skew(flat_data)
            if abs(skewness) > 2:
                issues.append(
                    {
                        "type": "distribution_skew",
                        "severity": "low",
                        "message": f"High skewness: {skewness:.2f}",
                    }
                )
                score -= 5
        except Exception:
            pass

        return max(0, score), issues

    def _check_class_balance(
        self, dataset: SyntheticDataset
    ) -> Tuple[float, List[str]]:
        """Check class balance."""
        warnings = []
        score = 100.0

        unique, counts = np.unique(dataset.labels, return_counts=True)
        ratios = counts / counts.sum()

        # Check for severe imbalance
        if ratios.max() / ratios.min() > 10:
            warnings.append(
                f"Severe class imbalance detected: ratio {ratios.max()/ratios.min():.1f}:1"
            )
            score -= 20
        elif ratios.max() / ratios.min() > 3:
            warnings.append(
                f"Class imbalance detected: ratio {ratios.max()/ratios.min():.1f}:1"
            )
            score -= 10

        return max(0, score), warnings

    def _compute_statistics(self, dataset: SyntheticDataset) -> Dict[str, Any]:
        """Compute dataset statistics."""
        flat_data = dataset.data.reshape(dataset.data.shape[0], -1)
        unique_labels, label_counts = np.unique(dataset.labels, return_counts=True)

        return {
            "n_samples": int(dataset.data.shape[0]),
            "data_shape": list(dataset.data.shape),
            "data_dtype": str(dataset.data.dtype),
            "data_mean": float(np.mean(dataset.data)),
            "data_std": float(np.std(dataset.data)),
            "data_min": float(np.min(dataset.data)),
            "data_max": float(np.max(dataset.data)),
            "n_classes": int(len(unique_labels)),
            "class_distribution": {
                int(k): int(v) for k, v in zip(unique_labels, label_counts)
            },
            "feature_dim": int(flat_data.shape[1]),
        }
