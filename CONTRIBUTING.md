# Contributing to Data Poisoning Detection Tool

Thank you for your interest in contributing to the Data Poisoning Detection Tool! This document provides guidelines and instructions for contributing.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)

---

## Code of Conduct

This project adheres to a [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to the maintainers.

---

## Getting Started

### Prerequisites

- Python 3.9 or higher
- pip or conda package manager
- Git

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/data-poisoning-detector.git
   cd data-poisoning-detector
   ```
3. Add the upstream remote:
   ```bash
   git remote add upstream https://github.com/ORIGINAL_OWNER/data-poisoning-detector.git
   ```

---

## Development Setup

### Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Install Dependencies

```bash
# Install production dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt

# Or use make
make install-dev
```

### Verify Setup

```bash
# Run tests
make test

# Run linting
make lint

# Start development server
make dev
```

---

## How to Contribute

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates.

**Bug Report Template:**

```markdown
**Description**
A clear description of the bug.

**Steps to Reproduce**
1. Go to '...'
2. Click on '...'
3. See error

**Expected Behavior**
What you expected to happen.

**Actual Behavior**
What actually happened.

**Environment**
- OS: [e.g., macOS 14.0]
- Python: [e.g., 3.11.0]
- Version: [e.g., 1.0.0]

**Additional Context**
Any other relevant information.
```

### Suggesting Features

Feature requests are welcome! Please provide:

1. **Use case**: Why is this feature needed?
2. **Proposed solution**: How should it work?
3. **Alternatives considered**: Other approaches you've thought of
4. **Additional context**: Mockups, diagrams, or examples

### Contributing Code

1. **Check existing issues** for related work
2. **Open an issue first** for significant changes
3. **Create a feature branch** from `main`
4. **Write tests** for new functionality
5. **Update documentation** as needed
6. **Submit a pull request**

---

## Pull Request Process

### Branch Naming

Use descriptive branch names:

- `feature/add-new-detector`
- `fix/spectral-analysis-bug`
- `docs/update-api-reference`
- `refactor/clean-engine-code`

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Formatting, no code change
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(engines): add DBSCAN clustering option
fix(spectral): correct singular value computation
docs(api): update endpoint documentation
```

### Pull Request Checklist

Before submitting:

- [ ] Code follows project style guidelines
- [ ] All tests pass (`make test`)
- [ ] Linting passes (`make lint`)
- [ ] Type checking passes (`make typecheck`)
- [ ] Documentation is updated
- [ ] CHANGELOG.md is updated (for significant changes)
- [ ] Commit messages follow conventions

### Review Process

1. Automated checks must pass
2. At least one maintainer approval required
3. All review comments addressed
4. Branch is up-to-date with `main`

---

## Coding Standards

### Python Style

We follow [PEP 8](https://pep8.org/) with these tools:

- **Formatter**: Black (line length: 88)
- **Linter**: Flake8
- **Type Checker**: mypy
- **Import Sorter**: isort

### Code Quality Rules

1. **Type Hints**: All functions must have type annotations
2. **Docstrings**: All public functions/classes need docstrings (Google style)
3. **Error Handling**: Use specific exceptions, not bare `except`
4. **Logging**: Use the project logger, not `print()`
5. **Constants**: Use UPPER_CASE for constants
6. **No Magic Numbers**: Define named constants

### Example Code Style

```python
"""Module docstring describing purpose."""

from typing import List, Optional

from backend.utils import get_logger

logger = get_logger(__name__)

# Constants
DEFAULT_THRESHOLD = 0.5
MAX_ITERATIONS = 100


def analyze_dataset(
    data: np.ndarray,
    labels: np.ndarray,
    threshold: float = DEFAULT_THRESHOLD,
) -> AnalysisResult:
    """
    Analyze dataset for poisoning indicators.

    Args:
        data: Feature matrix of shape (n_samples, n_features).
        labels: Label array of shape (n_samples,).
        threshold: Detection threshold (0.0 to 1.0).

    Returns:
        AnalysisResult containing detection scores and flagged indices.

    Raises:
        ValueError: If data and labels have mismatched lengths.
    """
    if len(data) != len(labels):
        raise ValueError(f"Length mismatch: {len(data)} vs {len(labels)}")

    logger.info(f"Analyzing {len(data)} samples with threshold {threshold}")
    
    # Implementation here
    ...
```

---

## Testing Guidelines

### Test Structure

```
tests/
├── __init__.py
├── conftest.py          # Shared fixtures
├── test_engines.py      # Engine tests
├── test_api.py          # API endpoint tests
├── test_utils.py        # Utility tests
└── integration/         # Integration tests
    └── test_pipeline.py
```

### Writing Tests

Use pytest with descriptive test names:

```python
import pytest
from backend.engines import SpectralSignaturesDetector


class TestSpectralSignaturesDetector:
    """Tests for SpectralSignaturesDetector class."""

    def test_analyze_returns_valid_score_range(self):
        """Poisoning score should be between 0 and 100."""
        detector = SpectralSignaturesDetector()
        result = detector.analyze(sample_data, sample_labels)
        
        assert 0 <= result.poisoning_score <= 100

    def test_analyze_with_clean_data_has_low_score(self):
        """Clean data should have poisoning score below 25."""
        detector = SpectralSignaturesDetector()
        result = detector.analyze(clean_data, clean_labels)
        
        assert result.poisoning_score < 25

    @pytest.mark.parametrize("poison_ratio", [0.05, 0.1, 0.2])
    def test_detects_various_poison_ratios(self, poison_ratio):
        """Should detect poisoning at various contamination levels."""
        # Test implementation
        ...
```

### Running Tests

```bash
# Run all tests
make test

# Run with coverage
make coverage

# Run specific test file
pytest tests/test_engines.py -v

# Run specific test
pytest tests/test_engines.py::TestSpectralSignaturesDetector -v
```

---

## Documentation

### Docstring Format

Use Google-style docstrings:

```python
def function_name(param1: str, param2: int = 10) -> bool:
    """
    Short description of function.

    Longer description if needed, explaining the purpose,
    algorithm, or important details.

    Args:
        param1: Description of param1.
        param2: Description of param2. Defaults to 10.

    Returns:
        Description of return value.

    Raises:
        ValueError: When param1 is empty.
        TypeError: When param2 is not an integer.

    Example:
        >>> result = function_name("test", param2=5)
        >>> print(result)
        True
    """
```

### Updating Documentation

1. Update docstrings when changing function signatures
2. Update README.md for user-facing changes
3. Update API docs in `docs/` for endpoint changes
4. Add examples for new features

---

## Questions?

If you have questions, feel free to:

1. Open a GitHub Discussion
2. Check existing issues and documentation
3. Reach out to maintainers

Thank you for contributing! 🎉
