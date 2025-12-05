"""
Visualization Utilities.

Generate charts, heatmaps, and clustering visualizations.
"""

import base64
from io import BytesIO
from typing import Dict, List, Optional

import numpy as np

# Conditional matplotlib import
try:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.figure import Figure

    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False


def create_spectral_plot(
    singular_values: np.ndarray, title: str = "Singular Values"
) -> str:
    """Create spectral signature plot."""
    if not HAS_MATPLOTLIB:
        return ""

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(range(len(singular_values)), singular_values, color="steelblue", alpha=0.8)
    ax.set_xlabel("Component Index")
    ax.set_ylabel("Singular Value")
    ax.set_title(title)
    ax.grid(True, alpha=0.3)

    return _fig_to_base64(fig)


def create_scatter_plot(
    embeddings: np.ndarray,
    labels: np.ndarray,
    suspected: Optional[List[int]] = None,
    title: str = "2D Projection",
) -> str:
    """Create 2D scatter plot with suspected samples highlighted."""
    if not HAS_MATPLOTLIB:
        return ""

    fig, ax = plt.subplots(figsize=(10, 8))

    unique_labels = np.unique(labels)
    colors = plt.cm.tab10(np.linspace(0, 1, len(unique_labels)))  # type: ignore[attr-defined]

    for i, label in enumerate(unique_labels):
        mask = labels == label
        ax.scatter(
            embeddings[mask, 0],
            embeddings[mask, 1],
            c=[colors[i]],
            label=f"Class {label}",
            alpha=0.6,
            s=30,
        )

    if suspected:
        ax.scatter(
            embeddings[suspected, 0],
            embeddings[suspected, 1],
            c="red",
            marker="x",
            s=100,
            linewidths=2,
            label="Suspected",
        )

    ax.set_xlabel("Component 1")
    ax.set_ylabel("Component 2")
    ax.set_title(title)
    ax.legend(loc="upper right")
    ax.grid(True, alpha=0.3)

    return _fig_to_base64(fig)


def create_heatmap(matrix: np.ndarray, title: str = "Heatmap") -> str:
    """Create heatmap visualization."""
    if not HAS_MATPLOTLIB:
        return ""

    fig, ax = plt.subplots(figsize=(10, 8))
    im = ax.imshow(matrix, cmap="hot", aspect="auto")
    plt.colorbar(im, ax=ax)
    ax.set_title(title)

    return _fig_to_base64(fig)


def create_risk_gauge(score: float, title: str = "Collapse Risk") -> str:
    """Create risk score gauge chart."""
    if not HAS_MATPLOTLIB:
        return ""

    fig, ax = plt.subplots(figsize=(8, 4))

    # Create horizontal bar
    colors = ["green", "yellow", "orange", "red"]
    bounds = [0, 25, 50, 75, 100]

    for i, (start, end) in enumerate(zip(bounds[:-1], bounds[1:])):
        ax.barh(0, end - start, left=start, height=0.5, color=colors[i], alpha=0.3)

    # Add score marker
    ax.axvline(x=score, color="black", linewidth=3)
    ax.scatter([score], [0], s=200, color="black", zorder=5)

    ax.set_xlim(0, 100)
    ax.set_ylim(-0.5, 0.5)
    ax.set_xlabel("Risk Score")
    ax.set_title(f"{title}: {score:.1f}")
    ax.set_yticks([])

    return _fig_to_base64(fig)


def create_bar_chart(values: Dict[str, float], title: str = "Scores") -> str:
    """Create bar chart for scores."""
    if not HAS_MATPLOTLIB:
        return ""

    fig, ax = plt.subplots(figsize=(10, 6))

    names = list(values.keys())
    scores = list(values.values())
    colors = plt.cm.viridis(np.linspace(0.2, 0.8, len(names)))  # type: ignore[attr-defined]

    bars = ax.bar(names, scores, color=colors)
    ax.set_ylabel("Score")
    ax.set_title(title)
    ax.set_xticklabels(names, rotation=45, ha="right")

    for bar, score in zip(bars, scores):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.5,
            f"{score:.1f}",
            ha="center",
            va="bottom",
        )

    plt.tight_layout()
    return _fig_to_base64(fig)


def _fig_to_base64(fig: "Figure") -> str:
    """Convert matplotlib figure to base64 string."""
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=100, bbox_inches="tight")
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode("utf-8")
    plt.close(fig)
    return f"data:image/png;base64,{img_str}"
