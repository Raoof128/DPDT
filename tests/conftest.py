"""Pytest configuration and shared fixtures.

This module provides reusable test fixtures for the Data Poisoning Detection Tool.
"""

import numpy as np
import pytest

from backend.engines import DatasetGenerator


@pytest.fixture(scope="session")
def generator() -> DatasetGenerator:
    """Create a shared DatasetGenerator instance."""
    return DatasetGenerator()


@pytest.fixture(scope="session")
def clean_image_dataset(generator: DatasetGenerator):
    """Generate a clean image dataset (no poisoning)."""
    return generator.generate_image_dataset(
        n_samples=200,
        n_classes=5,
        poison_ratio=0.0,
        seed=42,
    )


@pytest.fixture(scope="session")
def poisoned_image_dataset(generator: DatasetGenerator):
    """Generate a poisoned image dataset (10% poisoning)."""
    return generator.generate_image_dataset(
        n_samples=200,
        n_classes=5,
        poison_ratio=0.1,
        seed=42,
    )


@pytest.fixture(scope="session")
def clean_tabular_dataset(generator: DatasetGenerator):
    """Generate a clean tabular dataset (no poisoning)."""
    return generator.generate_tabular_dataset(
        n_samples=200,
        n_features=20,
        n_classes=3,
        poison_ratio=0.0,
        seed=42,
    )


@pytest.fixture(scope="session")
def poisoned_tabular_dataset(generator: DatasetGenerator):
    """Generate a poisoned tabular dataset (10% poisoning)."""
    return generator.generate_tabular_dataset(
        n_samples=200,
        n_features=20,
        n_classes=3,
        poison_ratio=0.1,
        seed=42,
    )


@pytest.fixture(scope="session")
def clean_text_dataset(generator: DatasetGenerator):
    """Generate a clean text dataset (no poisoning)."""
    return generator.generate_text_dataset(
        n_samples=100,
        n_classes=3,
        poison_ratio=0.0,
        seed=42,
    )


@pytest.fixture(scope="session")
def poisoned_text_dataset(generator: DatasetGenerator):
    """Generate a poisoned text dataset (10% poisoning)."""
    return generator.generate_text_dataset(
        n_samples=100,
        n_classes=3,
        poison_ratio=0.1,
        seed=42,
    )


@pytest.fixture
def sample_array() -> np.ndarray:
    """Generate a simple sample array for testing."""
    np.random.seed(42)
    return np.random.randn(100, 10).astype(np.float32)


@pytest.fixture
def sample_labels() -> np.ndarray:
    """Generate sample labels for testing."""
    np.random.seed(42)
    return np.random.randint(0, 3, size=100)


@pytest.fixture
def high_dimensional_data() -> np.ndarray:
    """Generate high-dimensional data for stress testing."""
    np.random.seed(42)
    return np.random.randn(50, 500).astype(np.float32)


# Markers for test categorization
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "security: marks tests as security tests")


# Skip slow tests by default in CI unless explicitly requested
def pytest_collection_modifyitems(config, items):
    """Modify test collection based on markers."""
    if config.getoption("-m"):
        # Don't modify if user specified markers
        return

    skip_slow = pytest.mark.skip(reason="slow test - use -m slow to run")
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip_slow)
