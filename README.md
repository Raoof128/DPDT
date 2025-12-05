# 🛡️ Data Poisoning Detection Tool

A **production-grade** platform for detecting training data poisoning attacks, backdoor triggers, and assessing model collapse risk.

> ⚠️ **Safety Notice**: All data is **SYNTHETIC** and **SAFE** for educational purposes. No real malware, attacks, or PII.

---

## ✨ Features

### 🔬 Detection Engines

| Engine | Description |
|--------|-------------|
| **Spectral Signatures** | PCA/SVD-based outlier detection using singular vector analysis |
| **Activation Clustering** | Neural activation analysis with K-Means/DBSCAN |
| **Influence Functions** | Simplified harmful sample estimation |
| **Trigger Detection** | Pixel patches, watermarks, text sequences |

### 📊 Risk Assessment

- **Overfit Potential**: Dimensionality vs sample ratio
- **Representation Collapse**: Feature variance analysis
- **Class Boundary Distortion**: Inter-class distance metrics
- **Poisoning Density**: Suspicious sample concentration

### 🧹 Dataset Cleaning

- **STRICT**: Remove all flagged samples
- **SAFE**: Remove high-confidence detections only
- **REVIEW**: Generate suggestions without removal

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- pip or conda

### Installation

```bash
# Clone or navigate to project
cd data-poisoning-detector

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Run the Server

```bash
# Start FastAPI server
python -m backend.main

# Or with uvicorn directly
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### Access

- **Dashboard**: http://localhost:8000/dashboard
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/scan` | Validate dataset quality |
| `POST` | `/detect_poison` | Run full detection pipeline |
| `POST` | `/clean` | Clean poisoned dataset |
| `POST` | `/collapse_risk` | Assess training risk |
| `POST` | `/report` | Generate HTML report |
| `GET`  | `/health` | Health check |
| `GET`  | `/dashboard` | Web dashboard |

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

---

## 🏗️ Project Structure

```
data-poisoning-detector/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── api/
│   │   ├── scan.py             # Dataset scanning
│   │   ├── poison.py           # Poisoning detection
│   │   ├── clean.py            # Dataset cleaning
│   │   ├── collapse.py         # Risk assessment
│   │   └── report.py           # Report generation
│   ├── engines/
│   │   ├── ingest_engine.py    # Data ingestion & validation
│   │   ├── spectral_engine.py  # Spectral signatures
│   │   ├── activation_clustering.py
│   │   ├── influence_engine.py
│   │   ├── trigger_detector.py
│   │   ├── risk_engine.py
│   │   └── cleanser.py
│   └── utils/
│       ├── logger.py           # Logging utilities
│       ├── hash_utils.py       # Dataset fingerprinting
│       ├── visuals.py          # Visualization
│       └── pdf_export.py       # Report export
├── frontend/
│   ├── index.html              # Dashboard UI
│   ├── styles.css              # Premium dark theme
│   └── dashboard.js            # Interactive features
├── tests/
├── logs/
├── models/
├── requirements.txt
└── README.md
```

---

## 📖 Detection Theory

### Spectral Signatures

Based on [Tran et al., NeurIPS 2018], poisoned samples create separable subspaces in representation space. By analyzing projections onto top singular vectors, we identify outliers.

```
1. Center data matrix X
2. Compute SVD: X = UΣV^T
3. Project samples onto top-k singular vectors
4. Flag samples with high projection magnitudes (z-score > threshold)
```

### Activation Clustering

Poisoned samples often cluster separately from clean samples in activation space:

1. Extract intermediate activations
2. Apply K-Means/DBSCAN per class
3. Identify minority clusters as suspicious
4. Cross-reference with label distribution

---

## 📋 Compliance Mapping

| Framework | Coverage |
|-----------|----------|
| **NIST AI RMF** | Govern, Map, Measure, Manage functions |
| **ISO/IEC 42001** | AI management system requirements |
| **OAIC ADM** | Automated decision-making transparency |

---

## 🧪 Testing

```bash
# Run tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=backend --cov-report=html
```

---

## 🔒 Safety Rules

1. ✅ Only synthetic datasets
2. ✅ No real malicious triggers
3. ✅ No attack instructions
4. ✅ All examples are benign
5. ✅ Educational purposes only

---

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- Spectral Signatures: Tran et al., "Spectral Signatures in Backdoor Attacks"
- FastAPI: Sebastián Ramírez
- scikit-learn: The scikit-learn developers

---

**Built with 🛡️ for AI Safety**
