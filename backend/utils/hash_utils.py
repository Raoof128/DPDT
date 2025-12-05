"""
Hash Utilities for Dataset Fingerprinting.

Provides cryptographic hashing for dataset integrity verification
and provenance tracking.
"""

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np


def compute_sha256(data: bytes) -> str:
    """
    Compute SHA-256 hash of binary data.

    Args:
        data: Binary data to hash

    Returns:
        Hexadecimal hash string
    """
    return hashlib.sha256(data).hexdigest()


def compute_file_hash(file_path: Path) -> str:
    """
    Compute SHA-256 hash of a file.

    Args:
        file_path: Path to file

    Returns:
        Hexadecimal hash string
    """
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()


def compute_array_hash(array: np.ndarray) -> str:
    """
    Compute hash of a NumPy array.

    Args:
        array: NumPy array to hash

    Returns:
        Hexadecimal hash string
    """
    return compute_sha256(array.tobytes())


def compute_dataset_fingerprint(
    data: np.ndarray, labels: np.ndarray, metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, str]:
    """
    Compute comprehensive fingerprint for a dataset.

    Args:
        data: Dataset features/samples
        labels: Dataset labels
        metadata: Optional metadata dictionary

    Returns:
        Dictionary containing fingerprint components
    """
    fingerprint = {
        "data_hash": compute_array_hash(data),
        "labels_hash": compute_array_hash(labels),
        "shape": str(data.shape),
        "dtype": str(data.dtype),
        "n_samples": int(data.shape[0]),
        "n_classes": int(len(np.unique(labels))),
    }

    if metadata:
        metadata_str = json.dumps(metadata, sort_keys=True)
        fingerprint["metadata_hash"] = compute_sha256(metadata_str.encode())

    # Combined fingerprint
    combined = "|".join(f"{k}:{v}" for k, v in sorted(fingerprint.items()))
    fingerprint["combined_hash"] = compute_sha256(combined.encode())

    return fingerprint


def verify_fingerprint(
    data: np.ndarray, labels: np.ndarray, expected_hash: str
) -> bool:
    """
    Verify dataset against expected fingerprint.

    Args:
        data: Dataset features
        labels: Dataset labels
        expected_hash: Expected combined hash

    Returns:
        True if fingerprint matches
    """
    current = compute_dataset_fingerprint(data, labels)
    return current["combined_hash"] == expected_hash


class FingerprintLog:
    """Maintains a log of dataset fingerprints for provenance tracking."""

    def __init__(self, log_path: Path):
        """
        Initialize fingerprint log.

        Args:
            log_path: Path to JSON log file
        """
        self.log_path = Path(log_path)
        self._log: List[Dict[str, Any]] = []
        self._load()

    def _load(self) -> None:
        """Load existing log from file."""
        if self.log_path.exists():
            with open(self.log_path, "r") as f:
                self._log = json.load(f)

    def _save(self) -> None:
        """Save log to file."""
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.log_path, "w") as f:
            json.dump(self._log, f, indent=2)

    def add_entry(
        self,
        dataset_name: str,
        fingerprint: Dict[str, str],
        operation: str = "scan",
        notes: Optional[str] = None,
    ) -> None:
        """
        Add a fingerprint entry to the log.

        Args:
            dataset_name: Name/identifier of dataset
            fingerprint: Fingerprint dictionary
            operation: Operation performed (scan, clean, etc.)
            notes: Optional notes
        """
        from datetime import datetime

        entry = {
            "timestamp": datetime.now().isoformat(),
            "dataset_name": dataset_name,
            "operation": operation,
            "fingerprint": fingerprint,
            "notes": notes,
        }
        self._log.append(entry)
        self._save()

    def get_history(self, dataset_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get fingerprint history.

        Args:
            dataset_name: Filter by dataset name (optional)

        Returns:
            List of fingerprint entries
        """
        if dataset_name:
            return [e for e in self._log if e["dataset_name"] == dataset_name]
        return self._log.copy()
