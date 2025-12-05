"""
Trigger Pattern Detector.

Detects synthetic backdoor triggers in images, text, and tabular data.
"""

from typing import Any, Dict, List, Optional

import numpy as np

from backend.utils import get_logger

logger = get_logger("trigger_detector")


class TriggerResult:
    """Result of trigger detection analysis."""

    def __init__(
        self,
        poisoning_score: float,
        detected_triggers: List[Dict[str, Any]],
        suspicious_patterns: List[str],
        trigger_heatmap: Optional[np.ndarray] = None,
    ):
        """Initialize result."""
        self.poisoning_score = poisoning_score
        self.detected_triggers = detected_triggers
        self.suspicious_patterns = suspicious_patterns
        self.trigger_heatmap = trigger_heatmap


class ImageTriggerDetector:
    """Detect visual triggers in image data."""

    def __init__(
        self, patch_sizes: List[int] = [3, 4, 5], intensity_threshold: float = 0.8
    ):
        self.patch_sizes = patch_sizes
        self.intensity_threshold = intensity_threshold

    def detect(self, images: np.ndarray, labels: np.ndarray) -> TriggerResult:
        """Detect trigger patterns in images."""
        logger.info(f"Scanning {len(images)} images for triggers")

        if len(images.shape) == 3:
            images = images[..., np.newaxis]

        n_samples, h, w, c = images.shape
        trigger_heatmap = np.zeros((h, w))
        detected_triggers = []
        suspicious_indices = []

        # Scan for patch-based triggers
        for patch_size in self.patch_sizes:
            for i in range(h - patch_size + 1):
                for j in range(w - patch_size + 1):
                    patches = images[:, i : i + patch_size, j : j + patch_size, :]
                    result = self._analyze_patch(patches, labels, i, j, patch_size)
                    if result:
                        detected_triggers.append(result)
                        trigger_heatmap[i : i + patch_size, j : j + patch_size] += 1
                        suspicious_indices.extend(result.get("sample_indices", []))

        # Check corner regions specifically (common trigger location)
        corners = [(0, 0), (0, w - 5), (h - 5, 0), (h - 5, w - 5)]
        for ci, cj in corners:
            if ci + 5 <= h and cj + 5 <= w:
                corner_patches = images[:, ci : ci + 5, cj : cj + 5, :]
                result = self._analyze_corner(corner_patches, labels, ci, cj)
                if result:
                    detected_triggers.append(result)
                    trigger_heatmap[ci : ci + 5, cj : cj + 5] += 2

        trigger_heatmap = trigger_heatmap / max(1, trigger_heatmap.max())

        poisoning_score = self._compute_score(detected_triggers, len(images))

        return TriggerResult(
            poisoning_score=poisoning_score,
            detected_triggers=detected_triggers,
            trigger_heatmap=trigger_heatmap,
            suspicious_patterns=[
                {"type": "pixel_patch", "count": len(detected_triggers)}
            ],
        )

    def _analyze_patch(
        self, patches: np.ndarray, labels: np.ndarray, row: int, col: int, size: int
    ) -> Optional[Dict[str, Any]]:
        """Analyze a patch region for trigger patterns."""
        flat_patches = patches.reshape(len(patches), -1)

        # Check for high-intensity uniform patches
        mean_intensity = flat_patches.mean(axis=1)
        high_intensity_mask = mean_intensity > self.intensity_threshold

        if high_intensity_mask.sum() < 5:
            return None

        # Check if high-intensity samples have unusual label distribution
        high_labels = labels[high_intensity_mask]
        unique, counts = np.unique(high_labels, return_counts=True)

        if len(unique) > 0:
            dominant_ratio = counts.max() / counts.sum()
            if dominant_ratio > 0.8 and high_intensity_mask.sum() >= 5:
                return {
                    "type": "pixel_trigger",
                    "location": (row, col),
                    "size": size,
                    "intensity": float(mean_intensity[high_intensity_mask].mean()),
                    "dominant_label": int(unique[counts.argmax()]),
                    "sample_indices": np.where(high_intensity_mask)[0].tolist()[:10],
                }
        return None

    def _analyze_corner(
        self, patches: np.ndarray, labels: np.ndarray, row: int, col: int
    ) -> Optional[Dict[str, Any]]:
        """Specifically analyze corner regions."""
        flat_patches = patches.reshape(len(patches), -1)
        std_per_sample = flat_patches.std(axis=1)

        # Low variance = uniform patch = potential trigger
        low_var_mask = std_per_sample < 0.1
        if low_var_mask.sum() >= 5:
            return {
                "type": "corner_trigger",
                "location": (row, col),
                "n_suspicious": int(low_var_mask.sum()),
                "sample_indices": np.where(low_var_mask)[0].tolist()[:10],
            }
        return None

    def _compute_score(self, triggers: List[Dict], total: int) -> float:
        if not triggers:
            return 0.0
        return min(100, len(triggers) * 15)


class TextTriggerDetector:
    """Detect text-based triggers."""

    def __init__(self, min_pattern_freq: int = 5):
        self.min_pattern_freq = min_pattern_freq

    def detect(self, texts: np.ndarray, labels: np.ndarray) -> TriggerResult:
        """Detect trigger patterns in text data."""
        logger.info(f"Scanning {len(texts)} text samples for triggers")

        detected_triggers = []

        # Convert to int tokens if float
        if texts.dtype in [np.float32, np.float64]:
            texts = texts.astype(int)

        n_samples, seq_len = texts.shape

        # Check for rare token sequences at end (common trigger placement)
        for pos in [seq_len - 3, seq_len - 2, seq_len - 1]:
            if pos >= 0:
                result = self._check_position(texts, labels, pos)
                if result:
                    detected_triggers.append(result)

        # Check for repeated subsequences
        result = self._check_repeated_patterns(texts, labels)
        detected_triggers.extend(result)

        poisoning_score = self._compute_score(detected_triggers)

        return TriggerResult(
            poisoning_score=poisoning_score,
            detected_triggers=detected_triggers,
            trigger_heatmap=None,
            suspicious_patterns=[
                {"type": "text_sequence", "count": len(detected_triggers)}
            ],
        )

    def _check_position(
        self, texts: np.ndarray, labels: np.ndarray, pos: int
    ) -> Optional[Dict[str, Any]]:
        """Check specific position for trigger tokens."""
        tokens_at_pos = texts[:, pos]
        unique_tokens, counts = np.unique(tokens_at_pos, return_counts=True)

        # Look for rare tokens that appear frequently
        for token, count in zip(unique_tokens, counts):
            if count >= self.min_pattern_freq and token > 900:  # Rare token range
                token_mask = tokens_at_pos == token
                token_labels = labels[token_mask]
                unique_labels, label_counts = np.unique(
                    token_labels, return_counts=True
                )

                if len(unique_labels) > 0:
                    dominant_ratio = label_counts.max() / label_counts.sum()
                    if dominant_ratio > 0.7:
                        return {
                            "type": "token_trigger",
                            "position": pos,
                            "token_id": int(token),
                            "frequency": int(count),
                            "dominant_label": int(unique_labels[label_counts.argmax()]),
                        }
        return None

    def _check_repeated_patterns(
        self, texts: np.ndarray, labels: np.ndarray
    ) -> List[Dict[str, Any]]:
        """Check for repeated suspicious patterns."""
        triggers = []
        len(texts)

        # Check last 5 tokens as potential trigger sequence
        if texts.shape[1] >= 5:
            last_5 = texts[:, -5:]
            pattern_map = {}

            for i, pattern in enumerate(last_5):
                key = tuple(pattern.tolist())
                if key not in pattern_map:
                    pattern_map[key] = []
                pattern_map[key].append(i)

            for pattern, indices in pattern_map.items():
                if len(indices) >= self.min_pattern_freq:
                    pattern_labels = labels[indices]
                    unique, counts = np.unique(pattern_labels, return_counts=True)
                    if len(unique) > 0 and counts.max() / counts.sum() > 0.8:
                        triggers.append(
                            {
                                "type": "sequence_trigger",
                                "pattern": list(pattern),
                                "frequency": len(indices),
                                "dominant_label": int(unique[counts.argmax()]),
                            }
                        )
        return triggers

    def _compute_score(self, triggers: List[Dict]) -> float:
        if not triggers:
            return 0.0
        return min(100, len(triggers) * 20)


class UniversalTriggerDetector:
    """Universal trigger detector for any data type."""

    def __init__(self):
        self.image_detector = ImageTriggerDetector()
        self.text_detector = TextTriggerDetector()

    def detect(
        self, data: np.ndarray, labels: np.ndarray, data_type: str
    ) -> TriggerResult:
        """Detect triggers based on data type."""
        if data_type == "image":
            return self.image_detector.detect(data, labels)
        elif data_type == "text":
            return self.text_detector.detect(data, labels)
        else:
            # Generic detection for tabular
            return self._detect_tabular(data, labels)

    def _detect_tabular(self, data: np.ndarray, labels: np.ndarray) -> TriggerResult:
        """Detect triggers in tabular data."""
        detected = []

        # Check for extreme values in specific columns
        for col in range(data.shape[1]):
            col_data = data[:, col]
            z_scores = np.abs((col_data - col_data.mean()) / (col_data.std() + 1e-8))
            extreme_mask = z_scores > 3

            if extreme_mask.sum() >= 5:
                extreme_labels = labels[extreme_mask]
                unique, counts = np.unique(extreme_labels, return_counts=True)
                if counts.max() / counts.sum() > 0.8:
                    detected.append(
                        {
                            "type": "extreme_value_trigger",
                            "column": col,
                            "n_samples": int(extreme_mask.sum()),
                        }
                    )

        return TriggerResult(
            poisoning_score=min(100, len(detected) * 15),
            detected_triggers=detected,
            trigger_heatmap=None,
            suspicious_patterns=[{"type": "tabular", "count": len(detected)}],
        )
