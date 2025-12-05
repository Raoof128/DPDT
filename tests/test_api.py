"""API Endpoint Tests for Data Poisoning Detection Tool.

Tests the FastAPI endpoints using httpx async client.
"""

import pytest
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


class TestHealthEndpoint:
    """Tests for health check endpoint."""

    def test_health_check(self) -> None:
        """Test health endpoint returns correct status."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data

    def test_root_endpoint(self) -> None:
        """Test root endpoint returns API info."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "endpoints" in data


class TestScanEndpoint:
    """Tests for dataset scan endpoint."""

    def test_scan_image_dataset(self) -> None:
        """Test scanning an image dataset."""
        response = client.post(
            "/scan",
            json={
                "dataset_type": "image",
                "n_samples": 100,
                "n_classes": 5,
                "poison_ratio": 0.0,
                "seed": 42,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_valid"] is True
        assert data["n_samples"] == 100
        assert "quality_score" in data
        assert "fingerprint" in data

    def test_scan_text_dataset(self) -> None:
        """Test scanning a text dataset."""
        response = client.post(
            "/scan",
            json={
                "dataset_type": "text",
                "n_samples": 50,
                "n_classes": 3,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_valid"] is True

    def test_scan_tabular_dataset(self) -> None:
        """Test scanning a tabular dataset."""
        response = client.post(
            "/scan",
            json={
                "dataset_type": "tabular",
                "n_samples": 100,
                "n_classes": 3,
            },
        )
        assert response.status_code == 200

    def test_scan_invalid_type(self) -> None:
        """Test scanning with invalid dataset type returns error."""
        response = client.post(
            "/scan",
            json={
                "dataset_type": "invalid_type",
                "n_samples": 100,
            },
        )
        assert response.status_code == 400


class TestDetectPoisonEndpoint:
    """Tests for poison detection endpoint."""

    def test_detect_poison_image(self) -> None:
        """Test poison detection on image dataset."""
        response = client.post(
            "/detect_poison",
            json={
                "dataset_type": "image",
                "n_samples": 100,
                "n_classes": 5,
                "poison_ratio": 0.1,
                "seed": 42,
                "run_spectral": True,
                "run_clustering": True,
                "run_influence": True,
                "run_trigger": True,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "poisoning_score" in data
        assert "suspected_indices" in data
        assert "detection_accuracy" in data
        # With poison_ratio=0.1 and 100 samples, should have ~10 ground truth
        assert len(data["ground_truth_poison_indices"]) == 10

    def test_detect_poison_selective_methods(self) -> None:
        """Test poison detection with only spectral method."""
        response = client.post(
            "/detect_poison",
            json={
                "dataset_type": "tabular",
                "n_samples": 50,
                "poison_ratio": 0.0,
                "run_spectral": True,
                "run_clustering": False,
                "run_influence": False,
                "run_trigger": False,
            },
        )
        assert response.status_code == 200
        data = response.json()
        # With no poisoning, score should be low
        assert data["poisoning_score"] < 50


class TestCleanEndpoint:
    """Tests for dataset cleaning endpoint."""

    def test_clean_strict_mode(self) -> None:
        """Test cleaning in strict mode."""
        response = client.post(
            "/clean",
            json={
                "dataset_type": "image",
                "n_samples": 100,
                "n_classes": 5,
                "poison_ratio": 0.1,
                "seed": 42,
                "mode": "strict",
                "confidence_threshold": 0.5,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["original_samples"] == 100
        assert data["mode"] == "strict"
        assert "removed_indices" in data

    def test_clean_safe_mode(self) -> None:
        """Test cleaning in safe mode."""
        response = client.post(
            "/clean",
            json={
                "dataset_type": "tabular",
                "n_samples": 100,
                "poison_ratio": 0.1,
                "mode": "safe",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["mode"] == "safe"

    def test_clean_review_mode(self) -> None:
        """Test cleaning in review mode (no removal)."""
        response = client.post(
            "/clean",
            json={
                "dataset_type": "image",
                "n_samples": 100,
                "poison_ratio": 0.1,
                "mode": "review",
            },
        )
        assert response.status_code == 200
        data = response.json()
        # Review mode should not remove any samples
        assert data["removed_samples"] == 0


class TestCollapseRiskEndpoint:
    """Tests for collapse risk assessment endpoint."""

    def test_collapse_risk_low(self) -> None:
        """Test collapse risk with healthy dataset."""
        response = client.post(
            "/collapse_risk",
            json={
                "dataset_type": "tabular",
                "n_samples": 500,
                "n_classes": 5,
                "poison_ratio": 0.0,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "collapse_risk_score" in data
        assert "risk_level" in data
        assert "recommendations" in data
        assert data["risk_level"] in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

    def test_collapse_risk_with_poisoning(self) -> None:
        """Test collapse risk with poisoned dataset."""
        response = client.post(
            "/collapse_risk",
            json={
                "dataset_type": "image",
                "n_samples": 200,
                "n_classes": 10,
                "poison_ratio": 0.2,
            },
        )
        assert response.status_code == 200
        data = response.json()
        # Higher poisoning should increase risk
        assert 0 <= data["collapse_risk_score"] <= 100


class TestReportEndpoint:
    """Tests for report generation endpoint."""

    def test_generate_report(self) -> None:
        """Test HTML report generation."""
        response = client.post(
            "/report",
            json={
                "dataset_type": "image",
                "n_samples": 50,
                "n_classes": 3,
                "poison_ratio": 0.1,
                "dataset_name": "test_dataset",
            },
        )
        assert response.status_code == 200
        # Should return HTML content
        assert "<!DOCTYPE html>" in response.text
        assert "Data Poisoning" in response.text


class TestDashboard:
    """Tests for dashboard serving."""

    def test_dashboard_exists(self) -> None:
        """Test dashboard is served."""
        response = client.get("/dashboard")
        assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
