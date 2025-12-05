# Usage Examples

Practical examples demonstrating how to use the Data Poisoning Detection Tool.

## Table of Contents

- [Quick Start](#quick-start)
- [Python SDK Examples](#python-sdk-examples)
- [API Examples with cURL](#api-examples-with-curl)
- [Detection Pipeline Examples](#detection-pipeline-examples)
- [Integration Examples](#integration-examples)

---

## Quick Start

### 1. Start the Server

```bash
# Using Make
make dev

# Or directly with uvicorn
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Open the Dashboard

Navigate to http://localhost:8000/dashboard in your browser.

### 3. Run Your First Scan

```bash
curl -X POST http://localhost:8000/scan \
  -H "Content-Type: application/json" \
  -d '{"dataset_type": "image", "n_samples": 100}'
```

---

## Python SDK Examples

### Basic Detection

```python
"""Example: Basic poison detection on a synthetic dataset."""

import requests

API_URL = "http://localhost:8000"

# Generate and scan a dataset
response = requests.post(f"{API_URL}/detect_poison", json={
    "dataset_type": "image",
    "n_samples": 1000,
    "poison_ratio": 0.1,
    "run_spectral": True,
    "run_clustering": True,
    "run_trigger": True,
})

result = response.json()

print(f"Poisoning Score: {result['poisoning_score']:.2f}/100")
print(f"Suspected Samples: {len(result['suspected_indices'])}")
print(f"Detection Precision: {result['detection_accuracy']['precision']:.2%}")
```

### Using the Engines Directly

```python
"""Example: Using detection engines directly in Python."""

from backend.engines import (
    DatasetGenerator,
    SpectralSignaturesDetector,
    ActivationClusteringDetector,
    UniversalTriggerDetector,
    CollapseRiskEngine,
)

# Generate synthetic dataset with 10% poisoning
generator = DatasetGenerator()
dataset = generator.generate_image_dataset(
    n_samples=1000,
    n_classes=10,
    poison_ratio=0.1,
    seed=42
)

print(f"Dataset shape: {dataset.data.shape}")
print(f"Poisoned indices: {dataset.metadata['poison_indices'][:10]}...")

# Run spectral analysis
spectral = SpectralSignaturesDetector(n_components=10)
spectral_result = spectral.analyze(dataset.data, dataset.labels)
print(f"\nSpectral Score: {spectral_result.poisoning_score:.2f}")
print(f"Suspected by Spectral: {len(spectral_result.suspected_indices)}")

# Run clustering analysis
clustering = ActivationClusteringDetector(n_clusters=10)
clustering_result = clustering.analyze(dataset.data, dataset.labels)
print(f"\nClustering Score: {clustering_result.poisoning_score:.2f}")
print(f"Misaligned Clusters: {len(clustering_result.suspicious_clusters)}")

# Run trigger detection
trigger = UniversalTriggerDetector()
trigger_result = trigger.detect(dataset.data, dataset.labels, "image")
print(f"\nTrigger Score: {trigger_result.poisoning_score:.2f}")
print(f"Detected Triggers: {len(trigger_result.detected_triggers)}")

# Assess collapse risk
risk_engine = CollapseRiskEngine()
risk_result = risk_engine.assess(
    dataset.data, 
    dataset.labels,
    poisoning_info={
        "suspected_indices": spectral_result.suspected_indices,
        "trigger_score": trigger_result.poisoning_score
    }
)
print(f"\nCollapse Risk: {risk_result.collapse_risk_score:.2f}")
print(f"Risk Level: {risk_result.risk_level.value}")
print("Recommendations:")
for rec in risk_result.recommendations:
    print(f"  - {rec}")
```

### Dataset Cleaning Example

```python
"""Example: Cleaning a poisoned dataset."""

from backend.engines import (
    DatasetGenerator,
    DatasetCleanser,
    CleansingMode,
    SpectralSignaturesDetector,
)

# Generate poisoned dataset
generator = DatasetGenerator()
dataset = generator.generate_tabular_dataset(
    n_samples=1000,
    n_features=20,
    poison_ratio=0.15,
    seed=42
)

# Detect poison
detector = SpectralSignaturesDetector()
detection = detector.analyze(dataset.data, dataset.labels)
print(f"Detected {len(detection.suspected_indices)} suspicious samples")

# Clean in SAFE mode (removes high-confidence only)
cleanser = DatasetCleanser(
    mode=CleansingMode.SAFE,
    confidence_threshold=0.7
)

result = cleanser.clean(
    dataset.data,
    dataset.labels,
    suspected_indices=detection.suspected_indices,
    confidence_scores=detection.confidence_scores
)

print(f"\nCleaning Summary:")
print(f"  Original samples: {result.summary['original_samples']}")
print(f"  Removed samples: {result.summary['removed_samples']}")
print(f"  Remaining samples: {result.summary['remaining_samples']}")
print(f"  Removal ratio: {result.summary['removal_ratio']:.2%}")

# Check relabel suggestions
if result.relabel_suggestions:
    print(f"\nRelabel Suggestions (top 5):")
    for suggestion in result.relabel_suggestions[:5]:
        print(f"  Sample {suggestion['index']}: "
              f"{suggestion['current_label']} → {suggestion['suggested_label']} "
              f"(conf: {suggestion['confidence']:.2f})")
```

---

## API Examples with cURL

### Scan Different Dataset Types

```bash
# Image dataset
curl -X POST http://localhost:8000/scan \
  -H "Content-Type: application/json" \
  -d '{"dataset_type": "image", "n_samples": 500}'

# Text dataset
curl -X POST http://localhost:8000/scan \
  -H "Content-Type: application/json" \
  -d '{"dataset_type": "text", "n_samples": 500}'

# Tabular dataset
curl -X POST http://localhost:8000/scan \
  -H "Content-Type: application/json" \
  -d '{"dataset_type": "tabular", "n_samples": 500}'
```

### Full Detection Pipeline

```bash
# Run all detection methods
curl -X POST http://localhost:8000/detect_poison \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_type": "image",
    "n_samples": 1000,
    "poison_ratio": 0.1,
    "run_spectral": true,
    "run_clustering": true,
    "run_influence": true,
    "run_trigger": true
  }' | python -m json.tool

# Run only spectral analysis (faster)
curl -X POST http://localhost:8000/detect_poison \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_type": "tabular",
    "n_samples": 5000,
    "run_spectral": true,
    "run_clustering": false,
    "run_influence": false,
    "run_trigger": false
  }'
```

### Cleaning Modes

```bash
# STRICT mode - removes all flagged samples
curl -X POST http://localhost:8000/clean \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_type": "image",
    "n_samples": 1000,
    "poison_ratio": 0.1,
    "mode": "strict"
  }'

# SAFE mode - removes only high-confidence detections
curl -X POST http://localhost:8000/clean \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_type": "image",
    "n_samples": 1000,
    "poison_ratio": 0.1,
    "mode": "safe",
    "confidence_threshold": 0.8
  }'

# REVIEW mode - suggestions only, no removal
curl -X POST http://localhost:8000/clean \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_type": "image",
    "n_samples": 1000,
    "poison_ratio": 0.1,
    "mode": "review"
  }'
```

### Generate Report

```bash
# Generate HTML report and save to file
curl -X POST http://localhost:8000/report \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_type": "image",
    "n_samples": 500,
    "poison_ratio": 0.1,
    "dataset_name": "production_training_v2"
  }' > report.html

# Open in browser (macOS)
open report.html
```

---

## Detection Pipeline Examples

### Comparing Detection Methods

```python
"""Example: Compare effectiveness of different detection methods."""

from backend.engines import (
    DatasetGenerator,
    SpectralSignaturesDetector,
    ActivationClusteringDetector,
    SimplifiedInfluenceEstimator,
    UniversalTriggerDetector,
)
import numpy as np

# Generate dataset with known poisoning
generator = DatasetGenerator()
dataset = generator.generate_image_dataset(
    n_samples=1000,
    n_classes=10,
    poison_ratio=0.1,
    seed=42
)

ground_truth = set(dataset.metadata["poison_indices"])
print(f"Ground truth poisoned: {len(ground_truth)} samples")

# Run each detector
detectors = [
    ("Spectral", SpectralSignaturesDetector()),
    ("Clustering", ActivationClusteringDetector()),
    ("Influence", SimplifiedInfluenceEstimator()),
    ("Trigger", UniversalTriggerDetector()),
]

print("\n" + "="*60)
print(f"{'Method':<15} {'Score':>8} {'Detected':>10} {'Precision':>10} {'Recall':>8}")
print("="*60)

for name, detector in detectors:
    if name == "Trigger":
        result = detector.detect(dataset.data, dataset.labels, "image")
        # Trigger detection returns different structure
        detected = set()
        for trigger in result.detected_triggers:
            detected.update(trigger.get("sample_indices", []))
    else:
        result = detector.analyze(dataset.data, dataset.labels) if name != "Influence" \
                 else detector.estimate(dataset.data, dataset.labels)
        detected = set(result.suspected_indices)
    
    true_positives = len(detected & ground_truth)
    precision = true_positives / len(detected) if detected else 0
    recall = true_positives / len(ground_truth) if ground_truth else 0
    
    print(f"{name:<15} {result.poisoning_score:>8.1f} {len(detected):>10} "
          f"{precision:>10.2%} {recall:>8.2%}")
```

### Batch Processing

```python
"""Example: Batch processing multiple datasets."""

import requests
from concurrent.futures import ThreadPoolExecutor
import time

API_URL = "http://localhost:8000"

# Define datasets to process
datasets = [
    {"name": "training_images_v1", "type": "image", "samples": 1000},
    {"name": "validation_images", "type": "image", "samples": 500},
    {"name": "user_text_data", "type": "text", "samples": 2000},
    {"name": "sensor_readings", "type": "tabular", "samples": 5000},
]

def process_dataset(config):
    """Process a single dataset."""
    start = time.time()
    
    response = requests.post(f"{API_URL}/detect_poison", json={
        "dataset_type": config["type"],
        "n_samples": config["samples"],
        "poison_ratio": 0.1,
    })
    
    result = response.json()
    elapsed = time.time() - start
    
    return {
        "name": config["name"],
        "score": result["poisoning_score"],
        "suspected": len(result["suspected_indices"]),
        "time": elapsed,
    }

# Process in parallel
with ThreadPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(process_dataset, datasets))

# Print summary
print("\n" + "="*70)
print("Batch Processing Results")
print("="*70)
print(f"{'Dataset':<25} {'Score':>10} {'Suspected':>12} {'Time':>10}")
print("-"*70)
for r in results:
    print(f"{r['name']:<25} {r['score']:>10.1f} {r['suspected']:>12} {r['time']:>10.2f}s")
```

---

## Integration Examples

### CI/CD Pipeline Integration

```yaml
# .github/workflows/dataset-check.yml
name: Dataset Quality Check

on:
  push:
    paths:
      - 'data/**'

jobs:
  poison-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Start Detection Server
        run: |
          pip install data-poisoning-detector
          uvicorn backend.main:app --port 8000 &
          sleep 5
      
      - name: Check Training Data
        run: |
          RESULT=$(curl -s -X POST http://localhost:8000/detect_poison \
            -H "Content-Type: application/json" \
            -d '{"dataset_type": "image", "n_samples": 1000, "poison_ratio": 0.0}')
          
          SCORE=$(echo $RESULT | jq '.poisoning_score')
          echo "Poisoning Score: $SCORE"
          
          if (( $(echo "$SCORE > 25" | bc -l) )); then
            echo "::error::Dataset poisoning score too high: $SCORE"
            exit 1
          fi
```

### Docker Compose Setup

```yaml
# docker-compose.yml
version: '3.8'

services:
  detector:
    build: .
    ports:
      - "8000:8000"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    environment:
      - LOG_LEVEL=info
      - PYTHONUNBUFFERED=1
    volumes:
      - ./logs:/app/logs
      - ./reports:/app/reports
```

### MLflow Integration

```python
"""Example: Logging detection results to MLflow."""

import mlflow
import requests

API_URL = "http://localhost:8000"

# Start MLflow run
with mlflow.start_run(run_name="dataset_quality_check"):
    # Run detection
    response = requests.post(f"{API_URL}/detect_poison", json={
        "dataset_type": "image",
        "n_samples": 10000,
        "poison_ratio": 0.0,
    })
    result = response.json()
    
    # Log metrics
    mlflow.log_metric("poisoning_score", result["poisoning_score"])
    mlflow.log_metric("spectral_score", result["spectral_result"]["score"])
    mlflow.log_metric("clustering_score", result["clustering_result"]["score"])
    mlflow.log_metric("detection_precision", result["detection_accuracy"]["precision"])
    mlflow.log_metric("detection_recall", result["detection_accuracy"]["recall"])
    
    # Log parameters
    mlflow.log_param("dataset_type", "image")
    mlflow.log_param("n_samples", 10000)
    
    # Set tags
    if result["poisoning_score"] > 50:
        mlflow.set_tag("quality", "SUSPICIOUS")
    else:
        mlflow.set_tag("quality", "HEALTHY")
    
    print(f"MLflow Run ID: {mlflow.active_run().info.run_id}")
```

---

## Troubleshooting

### Common Issues

**1. Connection Refused**
```bash
# Ensure server is running
curl http://localhost:8000/health

# Check if port is in use
lsof -i :8000
```

**2. Slow Detection**
- Reduce `n_samples` for faster testing
- Disable unnecessary detection methods
- Use tabular data (fastest for testing)

**3. Memory Issues**
- Process large datasets in batches
- Monitor memory with `top` or `htop`
- Consider using smaller sample sizes

---

## Next Steps

- Read the [API Reference](API.md) for complete endpoint documentation
- Check out [Architecture](ARCHITECTURE.md) to understand the system design
- Join our community discussions on GitHub
