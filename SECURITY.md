# Security Policy

## Supported Versions

Use this section to tell people about which versions of your project are currently being supported with security updates.

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take the security of this project seriously. If you find any security vulnerability, please report it to us as described below.

### **DO NOT report security vulnerabilities through public GitHub issues.**

Instead, please report them via email to `security@example.com` (replace with actual contact if available, or instruct to use private disclosure).

You should receive a response within 48 hours. If for some reason you do not, please follow up via email to ensure we received your original message.

## Safety Guidelines

This tool is designed for **educational and defensive purposes only**.

1. **Synthetic Data Only**: Do not use this tool to generate real malicious payloads or attacks against production systems.
2. **No Malware**: The codebase does not contain and should not be used to generate actual malware.
3. **Ethical Use**: Users are responsible for using this software in compliance with all applicable laws and regulations.

## Security Features

- **Input Validation**: All API inputs are validated using Pydantic models.
- **Safe Execution**: No execution of arbitrary code from inputs.
- **Dependency Scanning**: We regularly scan dependencies for known vulnerabilities.

## Incident Response Process

1. **Triage**: Verify the vulnerability report.
2. **Assessment**: Determine the impact and severity.
3. **Fix**: Develop and test a patch.
4. **Disclosure**: Release the fix and notify the community.
