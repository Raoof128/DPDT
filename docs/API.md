# API Reference

Comprehensive API documentation for the Data Poisoning Detection Tool.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, the API does not require authentication. For production deployments, consider adding API key or JWT authentication.

---

## Endpoints

### Health & Info

#### `GET /`
Returns API information and available endpoints.

**Response:**
```json
{
  "name": "Data Poisoning Detection Tool",
  "version": "1.0.1",
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
Health check endpoint for monitoring.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.1",
  "service": "Data Poisoning Detection Tool"
}
```

---

#### `GET /dashboard`
Serves the web-based dashboard UI.

**Response:** HTML page

---

### Dataset Scanning

#### `POST /scan`
Validates and fingerprints a synthetic dataset.

**Request Body:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `dataset_type` | string | Yes | One of: `image`, `text`, `tabular` |
| `n_samples` | integer | No | Number of samples (10-100000, default: 1000) |
| `n_classes` | integer | No | Number of classes (2-1000, default: 10) |
| `poison_ratio` | float | No | Ratio of poisoned samples (0.0-0.5, default: 0.0) |
| `seed` | integer | No | Random seed (default: 42) |

**Example Request:**
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

**Response:**
```json
{
  "is_valid": true,
  "quality_score": 95.5,
  "n_samples": 1000,
  "n_classes": 10,
  "anomalies": [],
  "warnings": [],
  "fingerprint": {
    "data_hash": "abc123...",
    "labels_hash": "def456...",
    "combined_hash": "ghi789..."
  },
  "stats": {
    "n_samples": 1000,
    "data_shape": [1000, 28, 28, 1],
    "data_mean": 0.45,
    "data_std": 0.22
  }
}
```

---

### Poison Detection

#### `POST /detect_poison`
Runs the full poisoning detection pipeline.

**Request Body:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `dataset_type` | string | Yes | One of: `image`, `text`, `tabular` |
| `n_samples` | integer | No | Number of samples (10-50000, default: 1000) |
| `n_classes` | integer | No | Number of classes (2-100, default: 10) |
| `poison_ratio` | float | No | Ratio of poisoned samples (0.0-0.5, default: 0.1) |
| `seed` | integer | No | Random seed (default: 42) |
| `run_spectral` | boolean | No | Run spectral signatures (default: true) |
| `run_clustering` | boolean | No | Run activation clustering (default: true) |
| `run_influence` | boolean | No | Run influence estimation (default: true) |
| `run_trigger` | boolean | No | Run trigger detection (default: true) |

**Example Request:**
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

**Response:**
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

---

### Dataset Cleaning

#### `POST /clean`
Removes or flags suspected poisoned samples.

**Request Body:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `dataset_type` | string | No | One of: `image`, `tabular` (default: `image`) |
| `n_samples` | integer | No | Number of samples (10-50000, default: 1000) |
| `n_classes` | integer | No | Number of classes (2-100, default: 10) |
| `poison_ratio` | float | No | Ratio of poisoned samples (0.0-0.5, default: 0.1) |
| `seed` | integer | No | Random seed (default: 42) |
| `mode` | string | No | Cleaning mode: `strict`, `safe`, `review` (default: `safe`) |
| `confidence_threshold` | float | No | Confidence threshold (0.0-1.0, default: 0.7) |

**Cleaning Modes:**
- **strict**: Remove all flagged samples
- **safe**: Remove only high-confidence detections
- **review**: Generate suggestions without removal

**Response:**
```json
{
  "original_samples": 1000,
  "removed_samples": 85,
  "remaining_samples": 915,
  "removal_ratio": 0.085,
  "removed_indices": [12, 45, 89, ...],
  "relabel_suggestions": [
    {"index": 234, "current_label": 3, "suggested_label": 5, "confidence": 0.82}
  ],
  "mode": "safe"
}
```

---

### Risk Assessment

#### `POST /collapse_risk`
Evaluates model training collapse risk.

**Request Body:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `dataset_type` | string | No | One of: `image`, `tabular` (default: `image`) |
| `n_samples` | integer | No | Number of samples (10-50000, default: 1000) |
| `n_classes` | integer | No | Number of classes (2-100, default: 10) |
| `poison_ratio` | float | No | Ratio of poisoned samples (0.0-0.5, default: 0.1) |
| `seed` | integer | No | Random seed (default: 42) |

**Response:**
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
    "Dataset appears healthy. Proceed with training."
  ],
  "details": {
    "n_samples": 1000,
    "n_classes": 10
  }
}
```

**Risk Levels:**
- **LOW** (0-24): Safe to proceed
- **MEDIUM** (25-49): Review recommended
- **HIGH** (50-74): Significant issues detected
- **CRITICAL** (75-100): Unsafe for training

---

### Report Generation

#### `POST /report`
Generates a comprehensive HTML analysis report.

**Request Body:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `dataset_type` | string | No | One of: `image`, `tabular` (default: `image`) |
| `n_samples` | integer | No | Number of samples (10-10000, default: 500) |
| `n_classes` | integer | No | Number of classes (2-50, default: 5) |
| `poison_ratio` | float | No | Ratio of poisoned samples (0.0-0.5, default: 0.1) |
| `seed` | integer | No | Random seed (default: 42) |
| `dataset_name` | string | No | Name for the report (default: `synthetic_dataset`) |

**Response:** HTML document with:
- Executive summary
- Detection results table
- Risk assessment
- Recommendations
- Compliance mapping (NIST AI RMF, ISO/IEC 42001, OAIC ADM)
- Technical appendix

---

## Error Responses

All errors follow this format:

```json
{
  "detail": "Error message describing the issue"
}
```

### HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request - Invalid input |
| 422 | Validation Error - Missing required fields |
| 500 | Internal Server Error |

---

## Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
