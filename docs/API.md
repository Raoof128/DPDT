# API Reference

Comprehensive API documentation for the Data Poisoning Detection Tool v1.0.2.

## Table of Contents

- [Overview](#overview)
- [Base URL](#base-url)
- [Authentication](#authentication)
- [Endpoints](#endpoints)
  - [Health & Info](#health--info)
  - [Dataset Scanning](#dataset-scanning)
  - [Poison Detection](#poison-detection)
  - [Dataset Cleaning](#dataset-cleaning)
  - [Risk Assessment](#risk-assessment)
  - [Report Generation](#report-generation)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)

---

## Overview

The Data Poisoning Detection Tool API provides RESTful endpoints for:

- Validating and fingerprinting datasets
- Detecting poisoning attacks using multiple algorithms
- Cleaning contaminated datasets
- Assessing training collapse risk
- Generating compliance reports

All endpoints accept JSON payloads and return JSON responses (except report generation which returns HTML).

---

## Base URL

```
http://localhost:8000
```

For production deployments, replace with your domain:
```
https://api.yourdomain.com
```

---

## Authentication

> **Note**: The current version does not require authentication. For production deployments, consider implementing:
> - API Key authentication (`X-API-Key` header)
> - JWT Bearer tokens
> - OAuth 2.0

---

## Endpoints

### Health & Info

#### `GET /`

Returns API information and available endpoints.

**Response** `200 OK`:
```json
{
  "name": "Data Poisoning Detection Tool",
  "version": "1.0.2",
  "endpoints": {
    "docs": "/docs",
    "health": "/health",
    "dashboard": "/dashboard",
    "scan": "/scan",
    "detect_poison": "/detect_poison",
    "clean": "/clean",
    "collapse_risk": "/collapse_risk",
    "report": "/report"
  },
  "safety_notice": "All data is synthetic. No real attacks or PII."
}
```

---

#### `GET /health`

Health check endpoint for monitoring and load balancers.

**Response** `200 OK`:
```json
{
  "status": "healthy",
  "version": "1.0.2",
  "service": "Data Poisoning Detection Tool"
}
```

**Use Case**: Kubernetes liveness/readiness probes, uptime monitoring.

---

#### `GET /dashboard`

Serves the interactive web-based dashboard UI.

**Response**: HTML page

---

### Dataset Scanning

#### `POST /scan`

Validates and fingerprints a synthetic dataset for integrity and quality.

**Request Body**:

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `dataset_type` | string | ✅ | - | One of: `image`, `text`, `tabular` |
| `n_samples` | integer | ❌ | 1000 | Number of samples (10-100,000) |
| `n_classes` | integer | ❌ | 10 | Number of classes (2-1,000) |
| `poison_ratio` | float | ❌ | 0.0 | Ratio of poisoned samples (0.0-0.5) |
| `seed` | integer | ❌ | 42 | Random seed for reproducibility |

**Example Request**:
```bash
curl -X POST http://localhost:8000/scan \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_type": "image",
    "n_samples": 1000,
    "n_classes": 10,
    "poison_ratio": 0.0
  }'
```

**Response** `200 OK`:
```json
{
  "is_valid": true,
  "quality_score": 95.5,
  "n_samples": 1000,
  "n_classes": 10,
  "anomalies": [],
  "warnings": [],
  "fingerprint": {
    "data_hash": "a1b2c3d4e5f6...",
    "labels_hash": "f6e5d4c3b2a1...",
    "shape": "(1000, 28, 28, 1)",
    "dtype": "float64",
    "n_samples": 1000,
    "n_classes": 10,
    "combined_hash": "9f8e7d6c5b4a..."
  },
  "stats": {
    "n_samples": 1000,
    "data_shape": [1000, 28, 28, 1],
    "data_mean": 0.45,
    "data_std": 0.22,
    "labels_distribution": {"0": 100, "1": 100, ...}
  }
}
```

**Response Fields**:
- `is_valid`: Whether the dataset passes all validation checks
- `quality_score`: Overall quality score (0-100)
- `fingerprint`: Cryptographic fingerprint for provenance tracking
- `anomalies`: List of detected data anomalies
- `warnings`: Non-critical issues found

---

### Poison Detection

#### `POST /detect_poison`

Runs the full poisoning detection pipeline with multiple algorithms.

**Request Body**:

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `dataset_type` | string | ✅ | - | One of: `image`, `text`, `tabular` |
| `n_samples` | integer | ❌ | 1000 | Number of samples (10-50,000) |
| `n_classes` | integer | ❌ | 10 | Number of classes (2-100) |
| `poison_ratio` | float | ❌ | 0.1 | Ratio of poisoned samples (0.0-0.5) |
| `seed` | integer | ❌ | 42 | Random seed |
| `run_spectral` | boolean | ❌ | true | Enable spectral signatures analysis |
| `run_clustering` | boolean | ❌ | true | Enable activation clustering |
| `run_influence` | boolean | ❌ | true | Enable influence estimation |
| `run_trigger` | boolean | ❌ | true | Enable trigger detection |

**Example Request**:
```bash
curl -X POST http://localhost:8000/detect_poison \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_type": "image",
    "n_samples": 1000,
    "n_classes": 10,
    "poison_ratio": 0.1,
    "run_spectral": true,
    "run_clustering": true,
    "run_influence": true,
    "run_trigger": true
  }'
```

**Response** `200 OK`:
```json
{
  "poisoning_score": 45.5,
  "suspected_indices": [12, 45, 89, 123, 456],
  "spectral_result": {
    "score": 35.0,
    "n_suspected": 8
  },
  "clustering_result": {
    "score": 42.0,
    "n_suspected": 6,
    "n_misaligned": 2
  },
  "influence_result": {
    "score": 55.0,
    "n_suspected": 5,
    "top_harmful": [
      {"index": 12, "influence_score": 3.5, "label": 0}
    ]
  },
  "trigger_result": {
    "score": 50.0,
    "n_triggers": 3,
    "patterns": [{"type": "pixel_patch", "count": 3}]
  },
  "ground_truth_poison_indices": [12, 45, 89, 123, 456, 789],
  "detection_accuracy": {
    "precision": 0.83,
    "recall": 0.75,
    "f1": 0.79,
    "false_positive_rate": 0.02
  }
}
```

**Detection Algorithms**:

| Algorithm | Description | Best For |
|-----------|-------------|----------|
| Spectral | SVD-based outlier detection | Backdoor attacks |
| Clustering | Activation-based clustering | Label-flipping |
| Influence | Impact estimation | High-influence samples |
| Trigger | Pattern detection | Visual/textual triggers |

---

### Dataset Cleaning

#### `POST /clean`

Removes or flags suspected poisoned samples from the dataset.

**Request Body**:

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `dataset_type` | string | ❌ | `image` | One of: `image`, `tabular` |
| `n_samples` | integer | ❌ | 1000 | Number of samples (10-50,000) |
| `n_classes` | integer | ❌ | 10 | Number of classes (2-100) |
| `poison_ratio` | float | ❌ | 0.1 | Ratio of poisoned samples |
| `seed` | integer | ❌ | 42 | Random seed |
| `mode` | string | ❌ | `safe` | Cleaning mode (see below) |
| `confidence_threshold` | float | ❌ | 0.7 | Confidence threshold (0.0-1.0) |

**Cleaning Modes**:

| Mode | Description | Removes |
|------|-------------|---------|
| `strict` | Aggressive cleaning | All flagged samples |
| `safe` | Balanced approach | High-confidence detections |
| `review` | Manual review | None (suggestions only) |

**Response** `200 OK`:
```json
{
  "original_samples": 1000,
  "removed_samples": 85,
  "remaining_samples": 915,
  "removal_ratio": 0.085,
  "removed_indices": [12, 45, 89, ...],
  "relabel_suggestions": [
    {
      "index": 234,
      "current_label": 3,
      "suggested_label": 5,
      "confidence": 0.82
    }
  ],
  "mode": "safe"
}
```

---

### Risk Assessment

#### `POST /collapse_risk`

Evaluates model training collapse risk for a dataset.

**Request Body**:

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `dataset_type` | string | ❌ | `image` | One of: `image`, `tabular` |
| `n_samples` | integer | ❌ | 1000 | Number of samples |
| `n_classes` | integer | ❌ | 10 | Number of classes |
| `poison_ratio` | float | ❌ | 0.1 | Ratio of poisoned samples |
| `seed` | integer | ❌ | 42 | Random seed |

**Response** `200 OK`:
```json
{
  "collapse_risk_score": 35.5,
  "risk_level": "MEDIUM",
  "risk_factors": {
    "overfit_potential": 0.3,
    "representation_collapse": 0.2,
    "class_boundary_distortion": 45.0,
    "poisoning_density": 0.15,
    "trigger_confidence": 0.25
  },
  "recommendations": [
    "Consider regularization techniques",
    "Monitor training loss carefully"
  ],
  "details": {
    "n_samples": 1000,
    "n_classes": 10,
    "poison_ratio": 0.1
  }
}
```

**Risk Levels**:

| Level | Score | Recommendation |
|-------|-------|----------------|
| LOW | 0-24 | Safe to proceed with training |
| MEDIUM | 25-49 | Review dataset before training |
| HIGH | 50-74 | Significant issues - cleaning recommended |
| CRITICAL | 75-100 | Unsafe for training - do not proceed |

---

### Report Generation

#### `POST /report`

Generates a comprehensive HTML analysis report.

**Request Body**:

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `dataset_type` | string | ❌ | `image` | One of: `image`, `tabular` |
| `n_samples` | integer | ❌ | 500 | Number of samples |
| `n_classes` | integer | ❌ | 5 | Number of classes |
| `poison_ratio` | float | ❌ | 0.1 | Ratio of poisoned samples |
| `seed` | integer | ❌ | 42 | Random seed |
| `dataset_name` | string | ❌ | `synthetic_dataset` | Name for report |

**Response**: HTML document containing:

- 📊 Executive Summary
- 🔍 Detection Results Table
- ⚠️ Risk Assessment
- 💡 Recommendations
- ✅ Compliance Mapping (NIST AI RMF, ISO/IEC 42001, OAIC ADM)
- 📎 Technical Appendix

---

## Error Handling

### Error Response Format

```json
{
  "detail": "Error message describing the issue"
}
```

### HTTP Status Codes

| Code | Description | Common Causes |
|------|-------------|---------------|
| 200 | Success | Request completed successfully |
| 400 | Bad Request | Invalid parameter values |
| 422 | Unprocessable Entity | Missing required fields, validation error |
| 500 | Internal Server Error | Server-side error |

### Validation Errors

```json
{
  "detail": [
    {
      "loc": ["body", "n_samples"],
      "msg": "ensure this value is greater than or equal to 10",
      "type": "value_error.number.not_ge"
    }
  ]
}
```

---

## Rate Limiting

> **Note**: Rate limiting is not implemented in the current version. For production deployments, consider:
> - Request rate limiting (e.g., 100 requests/minute)
> - Payload size limits
> - Concurrent request limits

---

## Interactive Documentation

For interactive API exploration:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## SDK Examples

### Python

```python
import requests

# Detect poisoning
response = requests.post(
    "http://localhost:8000/detect_poison",
    json={
        "dataset_type": "image",
        "n_samples": 1000,
        "poison_ratio": 0.1
    }
)
result = response.json()
print(f"Poisoning score: {result['poisoning_score']}")
```

### JavaScript

```javascript
const response = await fetch('http://localhost:8000/detect_poison', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    dataset_type: 'image',
    n_samples: 1000,
    poison_ratio: 0.1
  })
});
const result = await response.json();
console.log(`Poisoning score: ${result.poisoning_score}`);
```

---

## Changelog

See [CHANGELOG.md](../CHANGELOG.md) for API version history.
