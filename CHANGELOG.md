# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.2] - 2025-12-05

### Added

#### Documentation
- **docs/API.md**: Comprehensive API reference with all endpoints, request/response schemas, and examples
- **docs/EXAMPLES.md**: Practical usage examples including Python SDK, cURL commands, and integration patterns
- **.github/ISSUE_TEMPLATE/bug_report.yml**: Structured bug report template with relevant fields
- **.github/ISSUE_TEMPLATE/feature_request.yml**: Feature request template with prioritization
- **.github/PULL_REQUEST_TEMPLATE.md**: PR template with checklists and structured sections

#### CI/CD
- **.github/workflows/release.yml**: Automated release workflow for GitHub releases and Docker images
- **.github/dependabot.yml**: Automated dependency updates for Python, GitHub Actions, and Docker
- Enhanced CI workflow with linting, type checking, security scanning, and multi-version testing

#### Development Configuration
- **requirements-dev.txt**: Comprehensive development dependencies
- **docker-compose.yml**: Production-ready Docker Compose with health checks and resource limits
- **.devcontainer/**: VS Code Dev Container configuration with extensions and settings
- **.flake8**: Flake8 configuration with sensible defaults
- **.pre-commit-config.yaml**: Pre-commit hooks for formatting, linting, and security
- **tests/conftest.py**: Shared pytest fixtures for datasets and custom markers
- **backend/py.typed**: PEP 561 type marker for IDE support

#### Configuration Enhancements
- Enhanced **pyproject.toml** with bandit security config, coverage settings, and comprehensive tool configs
- Expanded **Makefile** with comprehensive commands, colored output, and organized sections
- Improved **.gitignore** with complete patterns for Python, IDEs, testing, and project-specific files

### Changed
- Updated CI workflow to use latest GitHub Actions (v4/v5) with caching and parallel jobs
- Improved test configuration with strict markers and branch coverage
- Enhanced Dockerfile configuration in dev container

## [1.0.1] - 2025-12-05

### Fixed
- **Critical Bug**: Fixed `_generate_recommendations()` method signature mismatch in `risk_engine.py` that caused test failures.
- **API Bug**: Fixed `ScanResponse` model type mismatch - fingerprint now correctly accepts `Dict[str, Any]` instead of `Dict[str, str]`.
- **Exception Handling**: Fixed error handling in scan endpoint to properly re-raise `HTTPException` with correct status codes.

### Added
- **API Tests**: Added comprehensive test suite for all API endpoints (`tests/test_api.py`) with 15 new tests.
- **Improved Recommendations**: Risk recommendations now include risk-level-specific warnings for CRITICAL and HIGH levels.

### Changed
- **Code Quality**: Reformatted entire codebase with `black` and `isort` for PEP 8 compliance.
- **Import Ordering**: Fixed import order violations across all API modules.
- **Test Coverage**: Improved test coverage from 55% to 80%.

### Removed
- **Dead Code**: Removed unused `_assess_trigger_confidence()` method from `CollapseRiskEngine`.

## [1.0.0] - 2025-12-05

### Added
- **Core Engine**: Initial release of the Data Poisoning Detection Tool.
- **Spectral Signatures**: PCA/SVD-based outlier detection for identifying poisoned samples.
- **Activation Clustering**: Neural network activation analysis using K-Means/DBSCAN.
- **Influence Functions**: Simplified influence estimation to detect harmful training samples.
- **Trigger Detection**: Detectors for pixel patches, watermarks, text sequences, and tabular outliers.
- **Collapse Risk Engine**: Assessment of model training risks (overfitting, representation collapse).
- **Dataset Cleanser**: Tools to remove or relabel flagged samples (Strict, Safe, Review modes).
- **API**: FastAPI backend with endpoints for scanning, detection, cleaning, and reporting.
- **Dashboard**: Modern, dark-themed web interface for interaction and visualization.
- **Reporting**: HTML/PDF report generation with compliance mapping (NIST, ISO).
- **Synthetic Data**: Built-in generator for safe, synthetic image, text, and tabular datasets.

### Security
- Implemented input validation using Pydantic.
- Enforced synthetic-only data generation to prevent real-world harm.
- Added security policy and safe usage guidelines.
