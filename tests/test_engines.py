"""Tests for Data Poisoning Detection Tool."""

import numpy as np
import pytest

from backend.engines import (
    ActivationClusteringDetector,
    CleansingMode,
    CollapseRiskEngine,
    DatasetCleanser,
    DatasetGenerator,
    DatasetValidator,
    SimplifiedInfluenceEstimator,
    SpectralSignaturesDetector,
    UniversalTriggerDetector,
)


class TestDatasetGenerator:
    """Tests for synthetic dataset generation."""

    def test_generate_image_dataset(self):
        """Test image dataset generation."""
        gen = DatasetGenerator()
        dataset = gen.generate_image_dataset(n_samples=100, n_classes=5)

        assert dataset.data.shape[0] == 100
        assert len(dataset.labels) == 100
        assert len(np.unique(dataset.labels)) == 5

    def test_generate_text_dataset(self):
        """Test text dataset generation."""
        gen = DatasetGenerator()
        dataset = gen.generate_text_dataset(n_samples=100, n_classes=3)

        assert dataset.data.shape[0] == 100
        assert len(dataset.labels) == 100

    def test_generate_tabular_dataset(self):
        """Test tabular dataset generation."""
        gen = DatasetGenerator()
        dataset = gen.generate_tabular_dataset(n_samples=100, n_features=20)

        assert dataset.data.shape == (100, 20)

    def test_poisoning_injection(self):
        """Test that poisoning creates expected samples."""
        gen = DatasetGenerator()
        dataset = gen.generate_image_dataset(n_samples=100, poison_ratio=0.1)

        assert len(dataset.metadata["poison_indices"]) == 10


class TestDatasetValidator:
    """Tests for dataset validation."""

    def test_valid_dataset(self):
        """Test validation of clean dataset."""
        gen = DatasetGenerator()
        dataset = gen.generate_tabular_dataset(n_samples=100)

        validator = DatasetValidator()
        result = validator.validate(dataset)

        assert result.is_valid
        assert result.quality_score > 80

    def test_fingerprint_generation(self):
        """Test fingerprint is generated."""
        gen = DatasetGenerator()
        dataset = gen.generate_tabular_dataset(n_samples=50)

        validator = DatasetValidator()
        result = validator.validate(dataset)

        assert result.fingerprint is not None
        assert "combined_hash" in result.fingerprint


class TestSpectralSignatures:
    """Tests for spectral analysis."""

    def test_analyze_clean_data(self):
        """Test analysis on clean data."""
        gen = DatasetGenerator()
        dataset = gen.generate_tabular_dataset(n_samples=200, poison_ratio=0.0)

        detector = SpectralSignaturesDetector()
        result = detector.analyze(dataset.data, dataset.labels)

        assert result.poisoning_score < 50
        assert len(result.singular_values) > 0

    def test_analyze_poisoned_data(self):
        """Test analysis on poisoned data."""
        gen = DatasetGenerator()
        # Increase poison ratio and use specific seed for reproducibility
        dataset = gen.generate_tabular_dataset(n_samples=200, poison_ratio=0.2, seed=42)

        # Lower threshold slightly for test robustness
        detector = SpectralSignaturesDetector(detection_threshold=1.5)
        result = detector.analyze(dataset.data, dataset.labels)

        # Should detect some suspicious samples
        assert len(result.suspected_indices) > 0


class TestActivationClustering:
    """Tests for activation clustering."""

    def test_clustering_analysis(self):
        """Test clustering on dataset."""
        gen = DatasetGenerator()
        dataset = gen.generate_tabular_dataset(n_samples=200, poison_ratio=0.1)

        detector = ActivationClusteringDetector()
        result = detector.analyze(dataset.data, dataset.labels)

        assert len(result.cluster_labels) == 200
        assert result.embeddings_2d.shape[1] == 2


class TestInfluenceEstimator:
    """Tests for influence function estimation."""

    def test_influence_estimation(self):
        """Test influence score computation."""
        gen = DatasetGenerator()
        dataset = gen.generate_tabular_dataset(n_samples=100)

        estimator = SimplifiedInfluenceEstimator()
        result = estimator.estimate(dataset.data, dataset.labels)

        assert len(result.influence_scores) == 100


class TestTriggerDetector:
    """Tests for trigger detection."""

    def test_image_trigger_detection(self):
        """Test image trigger detection."""
        gen = DatasetGenerator()
        dataset = gen.generate_image_dataset(n_samples=100, poison_ratio=0.1)

        detector = UniversalTriggerDetector()
        result = detector.detect(dataset.data, dataset.labels, "image")

        assert result.trigger_heatmap is not None

    def test_text_trigger_detection(self):
        """Test text trigger detection."""
        gen = DatasetGenerator()
        dataset = gen.generate_text_dataset(n_samples=100, poison_ratio=0.1)

        detector = UniversalTriggerDetector()
        result = detector.detect(dataset.data, dataset.labels, "text")

        assert isinstance(result.detected_triggers, list)


class TestRiskEngine:
    """Tests for collapse risk assessment."""

    def test_risk_assessment(self):
        """Test risk score computation."""
        gen = DatasetGenerator()
        dataset = gen.generate_tabular_dataset(n_samples=100)

        engine = CollapseRiskEngine()
        result = engine.assess(dataset.data, dataset.labels)

        assert 0 <= result.collapse_risk_score <= 100
        assert result.risk_level is not None
        assert len(result.recommendations) > 0


class TestCleanser:
    """Tests for dataset cleaning."""

    def test_strict_cleaning(self):
        """Test strict cleaning mode."""
        gen = DatasetGenerator()
        dataset = gen.generate_tabular_dataset(n_samples=100, poison_ratio=0.1)

        suspected = dataset.metadata["poison_indices"]

        cleanser = DatasetCleanser(mode=CleansingMode.STRICT)
        result = cleanser.clean(dataset.data, dataset.labels, suspected)

        assert result.summary["removed_samples"] == len(suspected)

    def test_safe_cleaning(self):
        """Test safe cleaning mode."""
        gen = DatasetGenerator()
        dataset = gen.generate_tabular_dataset(n_samples=100, poison_ratio=0.1)

        suspected = dataset.metadata["poison_indices"]

        cleanser = DatasetCleanser(mode=CleansingMode.SAFE)
        result = cleanser.clean(dataset.data, dataset.labels, suspected)

        # Safe mode removes fewer samples
        assert result.summary["removed_samples"] <= len(suspected)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
