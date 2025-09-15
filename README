# SmartPay

SmartPay is an automated compliance validation and advisory tool for transaction data, designed to support payment industry participants in optimizing interchange fees and ensuring scheme compliance (Visa, Mastercard). The platform combines Machine Learning (InterQ Advisor) and rules-based (Compliance Checker) approaches, providing actionable insights and clear, auditable reporting via a modern web interface.

---

## Solution Flow

This flow diagram shows our solution for the hackathon:

**From the user perspective:**
- Everything starts on the landing page, where users can choose between two features: **InterQ Advisor** and **Compliance Checker**.

### InterQ Advisor Path

- The user uploads a transaction CSV (in a predefined format).
- After validation and brand (Visa/Mastercard) detection, a Machine Learning model processes the data.
- The model generates a data-driven report, highlighting:
  - Main factors influencing interchange fees
  - Comparison between predicted and actual outcomes
  - Identified downgrade cases
  - Clear recommendations to reduce risks and optimize processes

### Compliance Checker Path

- The user uploads raw transaction files (CSV).
- Files are normalized into a common schema and enriched with derived facts (region, channel, cross-border status, SCA, etc.).
- A rules engine applies both general and scheme-specific checks.
- Each transaction is tagged with:
  - Findings
  - Remediation advice
  - Estimated financial impact
  - A risk level (from LOW to CRITICAL)
- Results are returned as compliance reports.

**Data Storage:**  
Both uploaded CSVs and generated reports are stored in the database for easy monitoring and decision-making.

---

## Features

- **InterQ Advisor:** ML-powered interchange optimization advice and downgrade detection
- **Compliance Checker:** Automated, customizable scheme compliance validation and reporting
- **Modern Dashboard:** Upload, search, sort, and view/download results
- **Data Storage:** All inputs and outputs are stored for tracking and audit

---

## Tech Stack

### Web Development

**Frontend**
- React
- TypeScript
- TailwindCSS + Radix UI

**Backend**
- FastAPI (Python)
- MySQL
- pandas

### Data & Business Value

**AI / ML**
- XGBoost Regressor
- scikit-learn + numpy
- SHAP (Shapley Additive Explanations)

### DevOps & Management

- Docker
- GitHub
- Miro

---

## Quick Start

### Prerequisites

- Node.js (v18+)
- Python (3.11+)
- Docker (recommended for full stack)

### Running with Docker

1. Build and run all services:
   ```bash
   docker-compose up --build
   ```
2. Access the web interface at [http://localhost:8080](http://localhost:8080)

### Manual Setup

#### Backend

```bash
cd compliance_service
pip install -r requirements.txt
python main.py --input path/to/transactions.csv --out results.csv
```

#### Frontend

```bash
cd view
npm install
npm run dev
```

---

## Usage

- Go to the dashboard.
- Upload your transaction file.
- Select either **InterQ Advisor** or **Compliance Checker** as needed.
- View detailed results, including risk levels, findings, and recommendations.
- Download compliance and advisory reports as CSV.

---

## Project Structure

- `view/`: Frontend React app
- `compliance_service/`: Python backend for compliance checking
- `model/`: Database models
- `init-db/`: Database initialization scripts
- `hackathon_mastercard_regressor/`: (Experimental) Model explainability and feature analysis

