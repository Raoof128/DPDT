"""
Activation Clustering Engine.

Detects poisoning by analyzing intermediate neural network activations
and finding clusters misaligned with labels.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import numpy as np
from sklearn.cluster import DBSCAN, KMeans
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE

from backend.utils import get_logger

logger = get_logger("activation_clustering")


@dataclass
class ClusteringResult:
    """Result of activation clustering analysis."""

    poisoning_score: float
    suspected_indices: List[int]
    cluster_labels: np.ndarray
    misaligned_clusters: List[Dict[str, Any]]
    embeddings_2d: np.ndarray
    analysis_details: Dict[str, Any] = field(default_factory=dict)


class SimpleFeatureExtractor:
    """Simple feature extractor simulating neural network activations."""

    def __init__(self, hidden_dim: int = 128, seed: int = 42) -> None:
        self.hidden_dim = hidden_dim
        self.seed = seed
        np.random.seed(seed)
        self.projection: Optional[np.ndarray] = None

    def fit(self, data: np.ndarray, labels: np.ndarray) -> "SimpleFeatureExtractor":
        """Fit the feature extractor."""
        flat_data = data.reshape(data.shape[0], -1)
        input_dim = flat_data.shape[1]
        self.projection = np.random.randn(input_dim, self.hidden_dim) * 0.1
        return self

    def extract(self, data: np.ndarray) -> np.ndarray:
        """Extract activation features."""
        flat_data = data.reshape(data.shape[0], -1)
        if self.projection is None:
            self.projection = np.random.randn(flat_data.shape[1], self.hidden_dim) * 0.1
        activations = np.tanh(flat_data @ self.projection)
        return activations


class ActivationClusteringDetector:
    """Detect poisoning via activation clustering analysis."""

    def __init__(
        self,
        n_clusters: int = 2,
        use_dbscan: bool = False,
        eps: float = 0.5,
        min_samples: int = 5,
    ):
        self.n_clusters = n_clusters
        self.use_dbscan = use_dbscan
        self.eps = eps
        self.min_samples = min_samples
        self.feature_extractor = SimpleFeatureExtractor()

    def analyze(self, data: np.ndarray, labels: np.ndarray) -> ClusteringResult:
        """Perform activation clustering analysis."""
        logger.info(f"Starting activation clustering on {len(data)} samples")

        # Extract features
        self.feature_extractor.fit(data, labels)
        activations = self.feature_extractor.extract(data)

        all_suspected = []
        all_misaligned = []

        # Analyze each class
        unique_labels = np.unique(labels)
        for label in unique_labels:
            class_mask = labels == label
            class_indices = np.where(class_mask)[0]
            class_activations = activations[class_mask]

            if len(class_activations) < 10:
                continue

            result = self._cluster_class(class_activations, class_indices)
            all_suspected.extend(result["suspected"])
            if result["misaligned"]:
                all_misaligned.append({"class": int(label), **result["misaligned"]})

        # Compute 2D embeddings for visualization
        pca = PCA(n_components=min(50, activations.shape[1]))
        reduced = pca.fit_transform(activations)
        if len(reduced) > 200:
            tsne = TSNE(
                n_components=2, random_state=42, perplexity=min(30, len(reduced) - 1)
            )
            embeddings_2d = tsne.fit_transform(reduced[:200])
            embeddings_2d = np.vstack([embeddings_2d, reduced[200:, :2]])
        else:
            embeddings_2d = reduced[:, :2]

        # Get overall cluster labels
        if self.use_dbscan:
            clusterer = DBSCAN(eps=self.eps, min_samples=self.min_samples)
        else:
            clusterer = KMeans(
                n_clusters=min(self.n_clusters * len(unique_labels), len(data) // 10),
                random_state=42,
                n_init=10,
            )
        cluster_labels = clusterer.fit_predict(activations)

        poisoning_score = self._compute_score(all_suspected, all_misaligned, len(data))

        return ClusteringResult(
            poisoning_score=poisoning_score,
            suspected_indices=sorted(set(all_suspected)),
            cluster_labels=cluster_labels,
            misaligned_clusters=all_misaligned,
            embeddings_2d=embeddings_2d,
            analysis_details={
                "n_classes": len(unique_labels),
                "n_misaligned": len(all_misaligned),
            },
        )

    def _cluster_class(
        self, activations: np.ndarray, indices: np.ndarray
    ) -> Dict[str, Any]:
        """Cluster activations within a class to find poisoned subset."""
        if self.use_dbscan:
            clusterer = DBSCAN(eps=self.eps, min_samples=self.min_samples)
        else:
            clusterer = KMeans(n_clusters=self.n_clusters, random_state=42, n_init=10)

        cluster_labels = clusterer.fit_predict(activations)
        unique_clusters = [c for c in np.unique(cluster_labels) if c != -1]

        if len(unique_clusters) < 2:
            return {"suspected": [], "misaligned": None}

        # Find smallest cluster (likely poisoned)
        cluster_sizes: List[tuple] = [
            (c, int(np.sum(cluster_labels == c))) for c in unique_clusters
        ]
        cluster_sizes.sort(key=lambda x: x[1])
        smallest_cluster = cluster_sizes[0][0]
        smallest_size = cluster_sizes[0][1]

        # Check if smallest cluster is anomalous
        total = len(activations)
        ratio = smallest_size / total

        if ratio < 0.3:  # Minority cluster
            suspected_local = np.where(cluster_labels == smallest_cluster)[0]
            suspected_global = indices[suspected_local].tolist()
            return {
                "suspected": suspected_global,
                "misaligned": {
                    "cluster_size": smallest_size,
                    "ratio": ratio,
                    "indices": suspected_global,
                },
            }

        return {"suspected": [], "misaligned": None}

    def _compute_score(
        self, suspected: List[int], misaligned: List[Dict], total: int
    ) -> float:
        if not suspected:
            return 0.0
        ratio = len(suspected) / total
        n_misaligned = len(misaligned)
        return min(100, ratio * 150 + n_misaligned * 10)
