# 🛡️ Data Poisoning Detection Tool (DPDT)

[![CI](https://github.com/Raoof128/DPDT/actions/workflows/ci.yml/badge.svg)](https://github.com/Raoof128/DPDT/actions/workflows/ci.yml)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A **production-grade** platform for detecting training data poisoning attacks, backdoor triggers, and assessing model collapse risk in machine learning pipelines.

> ⚠️ **Safety Notice**: All data is **SYNTHETIC** and **SAFE** for educational purposes. No real malware, attacks, or PII.

---

## 📋 Table of Contents

- [Features](#-features)
- [Quick Start](#-quick-start)
- [API Reference](#-api-endpoints)
- [Project Structure](#-project-structure)
- [Detection Methods](#-detection-theory)
- [Configuration](#-configuration)
- [Testing](#-testing)
- [Docker](#-docker)
- [Contributing](#-contributing)
- [License](#-license)

---

## ✨ Features

### 🔬 Detection Engines

| Engine | Description | Use Case |
|--------|-------------|----------|
| **Spectral Signatures** | PCA/SVD-based outlier detection using singular vector analysis | Backdoor attacks creating separable subspaces |
| **Activation Clustering** | Neural activation analysis with K-Means/DBSCAN | Label-flipping and targeted misclassification |
| **Influence Functions** | Simplified harmful sample estimation | High-impact poisoned samples |
| **Trigger Detection** | Pixel patches, watermarks, text sequences | Visual and textual backdoor triggers |

### 📊 Risk Assessment

- **Overfit Potential**: Dimensionality vs sample ratio analysis
- **Representation Collapse**: Feature variance and rank analysis
- **Class Boundary Distortion**: Inter-class distance metrics
- **Poisoning Density**: Suspicious sample concentration estimation

### 🧹 Dataset Cleaning Modes

| Mode | Description | Best For |
|------|-------------|----------|
| **STRICT** | Remove all flagged samples | High-security scenarios |
| **SAFE** | Remove high-confidence detections only | Balanced approach |
| **REVIEW** | Generate suggestions without removal | Human-in-the-loop workflows |

### 📈 Reporting & Compliance

- HTML/PDF report generation
- NIST AI RMF compliance mapping
- ISO/IEC 42001 alignment
- OAIC ADM transparency support

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- pip or conda

### Installation

```bash
# Clone the repository
git clone https://github.com/Raoof128/DPDT.git
cd DPDT

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Or install as package
pip install -e .
```

### Run the Server

```bash
# Using Make (recommended)
make dev

# Or directly with uvicorn
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# Or using Python
python -m backend.main
```

### Access Points

| Endpoint | URL | Description |
|----------|-----|-------------|
| **Dashboard** | http://localhost:8000/dashboard | Interactive web UI |
| **API Docs** | http://localhost:8000/docs | Swagger/OpenAPI documentation |
| **Health Check** | http://localhost:8000/health | Service status |

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | API information |
| `GET` | `/health` | Health check |
| `GET` | `/dashboard` | Web dashboard |
| `POST` | `/scan` | Validate dataset quality |
| `POST` | `/detect_poison` | Run detection pipeline |
| `POST` | `/clean` | Clean poisoned dataset |
| `POST` | `/collapse_risk` | Assess training risk |
| `POST` | `/report` | Generate HTML report |

### Example: Detect Poisoning

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

### Example Response

```json
{
  "poisoning_score": 45.5,
  "suspected_indices": [12, 45, 89, 123, 456],
  "detection_accuracy": {
    "precision": 0.83,
    "recall": 0.75,
    "f1": 0.79
  }
}
```

> 📚 See [docs/API.md](docs/API.md) for complete API documentation.

---

## 🏗️ Project Structure

```
DPDT/
├── backend/
│   ├── main.py                 # FastAPI application entry point
│   ├── api/                    # REST API endpoints
│   │   ├── scan.py             # Dataset validation
│   │   ├── poison.py           # Poisoning detection
│   │   ├── clean.py            # Dataset cleaning
│   │   ├── collapse.py         # Risk assessment
│   │   └── report.py           # Report generation
│   ├── engines/                # Detection algorithms
│   │   ├── ingest_engine.py    # Data generation & validation
│   │   ├── spectral_engine.py  # Spectral signatures
│   │   ├── activation_clustering.py
│   │   ├── influence_engine.py
│   │   ├── trigger_detector.py
│   │   ├── risk_engine.py
│   │   └── cleanser.py
│   └── utils/                  # Shared utilities
│       ├── logger.py           # Logging
│       ├── hash_utils.py       # Dataset fingerprinting
│       ├── visuals.py          # Visualization
│       └── pdf_export.py       # Report export
├── frontend/                   # Web dashboard
│   ├── index.html
│   ├── styles.css
│   └── dashboard.js
├── tests/                      # Test suite
│   ├── conftest.py             # Shared fixtures
│   ├── test_engines.py
│   └── test_api.py
├── docs/                       # Documentation
│   ├── API.md
│   ├── ARCHITECTURE.md
│   └── EXAMPLES.md
├── .github/                    # CI/CD workflows
│   ├── workflows/
│   └── ISSUE_TEMPLATE/
├── requirements.txt            # Production dependencies
├── requirements-dev.txt        # Development dependencies
├── pyproject.toml              # Project configuration
├── Makefile                    # Development commands
├── Dockerfile                  # Container image
└── docker-compose.yml          # Container orchestration
```

---

## 📖 Detection Theory

### Spectral Signatures

Based on [Tran et al., NeurIPS 2018], poisoned samples create separable subspaces in representation space.

```
Algorithm:
1. Center data matrix X
2. Compute SVD: X = UΣV^T
3. Project samples onto top-k singular vectors
4. Flag samples with |projection| > threshold (z-score based)
```

### Activation Clustering

Poisoned samples cluster separately from clean samples in activation space:

1. Extract intermediate activations (simulated)
2. Apply K-Means/DBSCAN per class
3. Identify minority clusters as suspicious
4. Cross-reference with label distribution

### Influence Functions

Estimates the impact of removing each training sample:

1. Compute gradient-based influence scores
2. Identify samples with high negative influence
3. Flag as potentially harmful

---

## ⚙️ Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `LOG_LEVEL` | `info` | Logging level (debug, info, warning, error) |
| `HOST` | `0.0.0.0` | Server host |
| `PORT` | `8000` | Server port |

### Makefile Commands

```bash
make help          # Show all commands
make install       # Install production deps
make install-dev   # Install dev deps
make dev           # Start dev server
make test          # Run tests
make coverage      # Run tests with coverage
make lint          # Run linters
make format        # Format code
make clean         # Clean build artifacts
make docker-build  # Build Docker image
```

---

## 🧪 Testing

```bash
# Run all tests
make test

# Run with coverage report
make coverage

# Run specific test file
pytest tests/test_engines.py -v

# Run fast tests only
pytest tests/ -m "not slow" -v
```

### Test Coverage

| Module | Coverage |
|--------|----------|
| Engines | ~80% |
| API | ~90% |
| Utils | ~70% |
| **Overall** | **~77%** |

---

## 🐳 Docker

### Build and Run

```bash
# Build image
docker build -t dpdt:latest .

# Run container
docker run -p 8000:8000 dpdt:latest

# Using docker-compose
docker-compose up -d
```

### Docker Compose Services

```bash
# Start production service
docker-compose up detector

# Start development service with hot reload
docker-compose --profile dev up detector-dev
```

---

## 📋 Compliance Mapping

| Framework | Coverage |
|-----------|----------|
| **NIST AI RMF** | Govern, Map, Measure, Manage functions |
| **ISO/IEC 42001** | AI management system requirements |
| **OAIC ADM** | Automated decision-making transparency |

---

## 🔒 Safety Rules

1. ✅ Only synthetic datasets - no real data processing
2. ✅ No real malicious triggers or payloads
3. ✅ No attack methodology instructions
4. ✅ All examples are benign simulations
5. ✅ Educational and defensive purposes only

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'feat: add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- **Spectral Signatures**: Tran et al., "Spectral Signatures in Backdoor Attacks" (NeurIPS 2018)
- **FastAPI**: Sebastián Ramírez
- **scikit-learn**: The scikit-learn developers

---

## 📬 Support

- 📖 [Documentation](docs/)
- 🐛 [Issue Tracker](https://github.com/Raoof128/DPDT/issues)
- 💬 [Discussions](https://github.com/Raoof128/DPDT/discussions)

---

**Built with 🛡️ for AI Safety**
