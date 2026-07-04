# 🛡️ CloudSentinel-CSPM

> A Cloud Security Posture Management (CSPM) platform for Google Cloud that discovers cloud assets, detects security misconfigurations, calculates risk scores, and maintains historical security posture.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green)
![Google%20Cloud](https://img.shields.io/badge/Google%20Cloud-GCP-orange)
![Status](https://img.shields.io/badge/Status-Active-success)

---

# Overview

CloudSentinel is an extensible Cloud Security Posture Management (CSPM) platform built to continuously assess Google Cloud environments for security risks.

It automatically:

- Discovers cloud assets
- Detects security misconfigurations
- Calculates risk scores
- Maps findings to CIS Benchmarks
- Maps findings to MITRE ATT&CK
- Maintains an asset inventory
- Stores historical scan results
- Provides REST APIs for dashboards and reporting

The project is designed with a modular architecture so additional cloud services and cloud providers can be added with minimal changes.

---

# Current Features

## Google Cloud Resource Discovery

- ✅ IAM Service Accounts
- ✅ Cloud Storage Buckets
- ✅ Compute Engine Virtual Machines

---

## Security Analysis

- ✅ Rule-based security scanning
- ✅ Risk scoring engine
- ✅ CIS Benchmark mapping
- ✅ MITRE ATT&CK mapping
- ✅ Evidence collection
- ✅ Remediation recommendations

---

## Persistence

- ✅ Findings Database
- ✅ Asset Inventory
- ✅ Historical Scan Tracking

---

## API

- ✅ FastAPI REST API
- ✅ Swagger Documentation
- ✅ Modular Provider Architecture

---

# Architecture

```text
                Google Cloud APIs
                        │
                        ▼
                Resource Collectors
                        │
                        ▼
                 Resource Normalizers
                        │
                        ▼
                  Rule Evaluation
                        │
                        ▼
                   Risk Engine
                        │
                        ▼
                 Scan Result Model
                        │
          ┌─────────────┼──────────────┐
          ▼             ▼              ▼
     Findings DB   Asset Inventory   Scan History
          │
          ▼
      FastAPI REST API
          │
          ▼
     React Dashboard (Upcoming)
```

---

# Supported Resources

| Service | Status |
|----------|--------|
| IAM Service Accounts | ✅ |
| Cloud Storage Buckets | ✅ |
| Compute Engine VMs | ✅ |

---

# Example Findings

Current security checks include:

### IAM

- Default Service Account Detected
- Least Privilege Recommendations

### Storage

- Bucket Versioning Disabled

### Compute

- Public IP Exposure
- Default Compute Service Account Attached

Each finding contains:

- Severity
- Risk Score
- Evidence
- Recommendation
- CIS Benchmark Reference
- MITRE ATT&CK Technique

---

# Technology Stack

## Backend

- Python
- FastAPI
- SQLAlchemy
- SQLite

## Google Cloud

- IAM API
- Cloud Storage API
- Compute Engine API

## Security

- Rule Engine
- Risk Engine
- CIS Benchmark Mapping
- MITRE ATT&CK Mapping

---

# Project Structure

```text
CloudSentinel-CSPM/

backend/
│
├── api/
├── collectors/
├── database/
├── integrations/
├── models/
├── normalizers/
├── providers/
├── rules/
├── scheduler/
├── services/
├── utils/
└── main.py

frontend/

tests/

ROADMAP.md
CHANGELOG.md
README.md
requirements.txt
docker-compose.yml
```

---

# Running Locally

## Clone

```bash
git clone https://github.com/Andro-ux/CloudSentinel-CSPM.git

cd CloudSentinel-CSPM
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Configure Credentials

Place your Google Cloud service account credentials in:

```text
backend/credentials/
```

Create a `.env` file with your configuration.

---

## Start the API

```bash
uvicorn backend.main:app --reload
```

Swagger UI:

```
http://127.0.0.1:8000/docs
```

---

# Database

CloudSentinel currently persists:

- Findings
- Asset Inventory
- Scan History

using SQLite through SQLAlchemy.

---

# Roadmap

## Dashboard

- [ ] Dashboard Summary
- [ ] Findings API
- [ ] Asset Inventory API
- [ ] Scan History API
- [ ] React Dashboard

---

## Google Cloud Coverage

### Identity

- [x] Service Accounts
- [ ] IAM Policies
- [ ] IAM Bindings
- [ ] Custom Roles
- [ ] Service Account Keys

### Compute

- [x] Virtual Machines
- [ ] Disks
- [ ] Snapshots
- [ ] Images
- [ ] Instance Groups

### Networking

- [ ] Firewall Rules
- [ ] VPC Networks
- [ ] Subnets
- [ ] Routes
- [ ] Cloud NAT
- [ ] Load Balancers
- [ ] Cloud Armor

### Storage

- [x] Buckets
- [ ] Bucket IAM
- [ ] Lifecycle Rules
- [ ] CMEK
- [ ] Logging
- [ ] Public Objects

### Databases

- [ ] Cloud SQL
- [ ] Firestore
- [ ] Memorystore

### Containers

- [ ] GKE
- [ ] Node Pools
- [ ] RBAC

### Serverless

- [ ] Cloud Run
- [ ] Cloud Functions
- [ ] App Engine

### Secrets

- [ ] Secret Manager
- [ ] Cloud KMS

---

## AI Features

- [ ] AI Risk Explanation
- [ ] AI Remediation
- [ ] Executive Reports
- [ ] Risk Prioritization

---

## Multi-Cloud

- [ ] AWS
- [ ] Azure

---

# Future Vision

CloudSentinel is being developed into a complete Cloud Security Posture Management platform featuring:

- Multi-cloud support
- Continuous scanning
- Historical risk analysis
- Compliance reporting
- Attack-path correlation
- AI-assisted remediation
- Executive dashboards

---

# Contributing

Contributions, feature requests, and security improvements are welcome.

Please open an Issue before submitting major changes.

---

# License

This project is licensed under the MIT License.

---

**⭐ If you find this project useful, consider starring the repository!**