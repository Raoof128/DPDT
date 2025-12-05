# Security Policy

## Supported Versions

| Version | Supported          | Notes |
| ------- | ------------------ | ----- |
| 1.0.x   | ✅ Actively supported | Current stable release |
| < 1.0   | ❌ Not supported | Pre-release versions |

---

## Reporting a Vulnerability

We take the security of the Data Poisoning Detection Tool seriously. If you discover a security vulnerability, please follow these guidelines:

### 🚨 DO NOT report security vulnerabilities through public GitHub issues.

### Reporting Process

1. **Email**: Send details to the maintainer (check repository for contact)
2. **Include**:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact assessment
   - Any suggested fixes (optional)

3. **Response Timeline**:
   - **Initial Response**: Within 48 hours
   - **Assessment**: Within 7 days
   - **Resolution**: Depends on severity

### What to Expect

- Acknowledgment of your report
- Regular updates on progress
- Credit in the security advisory (if desired)
- Coordinated disclosure timeline

---

## Security Design Principles

This tool is designed with security as a priority:

### 1. Synthetic Data Only

```
✅ All data is synthetically generated
✅ No real datasets are processed or stored
✅ No external data downloads
❌ No real malware or attacks
```

### 2. Input Validation

All user inputs are validated using Pydantic schemas:

```python
class DetectRequest(BaseModel):
    dataset_type: Literal["image", "text", "tabular"]
    n_samples: int = Field(ge=10, le=50000)
    poison_ratio: float = Field(ge=0.0, le=0.5)
```

### 3. No Code Execution

- The tool performs static analysis only
- No user-provided code is executed
- No arbitrary file access
- No shell command execution

### 4. Safe Defaults

- Reasonable limits on all parameters
- Validation before processing
- Controlled resource usage

---

## Safety Guidelines

This tool is designed for **educational and defensive purposes only**.

### ✅ Acceptable Use

- Learning about data poisoning attacks
- Testing detection algorithms
- Research and academic purposes
- Defending ML pipelines

### ❌ Prohibited Use

- Generating real malicious payloads
- Attacking production systems
- Creating actual malware
- Any illegal activities

---

## Security Features

| Feature | Implementation |
|---------|----------------|
| **Input Validation** | Pydantic models with strict typing |
| **Safe Execution** | Synthetic data only, no file access |
| **Logging** | Structured logs without sensitive data |
| **Dependencies** | Regular security scanning |
| **CORS** | Configurable cross-origin policy |

---

## Dependency Security

We monitor dependencies for vulnerabilities:

- **Dependabot**: Automated dependency updates
- **Safety**: Python dependency vulnerability scanning
- **Bandit**: Static security analysis

### Running Security Checks

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run security scan
make security

# Or manually
bandit -r backend/
safety check
```

---

## Incident Response Process

1. **Triage**: Verify and assess the vulnerability report
2. **Classification**: Determine severity (Critical, High, Medium, Low)
3. **Investigation**: Identify root cause and scope
4. **Remediation**: Develop and test a fix
5. **Release**: Deploy patched version
6. **Disclosure**: Notify community and credit reporter

### Severity Classification

| Severity | Description | Response Time |
|----------|-------------|---------------|
| **Critical** | Immediate risk, exploitable | 24 hours |
| **High** | Significant risk | 72 hours |
| **Medium** | Moderate risk | 1 week |
| **Low** | Minor risk | 2 weeks |

---

## Best Practices for Users

### When Deploying

1. **Use HTTPS** in production
2. **Implement authentication** for public deployments
3. **Set restrictive CORS** policies
4. **Monitor logs** for suspicious activity
5. **Keep dependencies updated**

### Example Secure Deployment

```python
from fastapi import FastAPI, Depends
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")

async def verify_api_key(api_key: str = Depends(api_key_header)):
    if api_key != os.getenv("API_KEY"):
        raise HTTPException(status_code=403)
    return api_key

@app.post("/detect_poison")
async def detect(request: DetectRequest, _: str = Depends(verify_api_key)):
    ...
```

---

## Contact

For security-related inquiries that don't involve vulnerabilities, please open a GitHub issue or discussion.

---

## Acknowledgments

We thank all security researchers who help improve the security of this project through responsible disclosure.
