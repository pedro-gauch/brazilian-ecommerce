# Brazilian E-Commerce Analytics

An end-to-end data pipeline built on the
[Olist Brazilian E-Commerce dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce),
demonstrating SQL fluency, dbt data modeling, batch processing simulation,
and business insight extraction from a real relational dataset.

## Business Questions

1. **Seller performance** — which sellers deliver on time, earn good reviews,
and drive revenue?
2. **Delivery and satisfaction** — what is the relationship between delivery
delay and customer review scores?
3. **Revenue and complaints by category** — which product categories are most
valuable, and which generate the most dissatisfaction?

## Architecture

| Layer | Tool |
|---|---|
| Source | Kaggle API (Olist dataset) |
| Ingestion | Python (kaggle, duckdb, python-dotenv) |
| Storage | MotherDuck (cloud-hosted DuckDB) |
| Transformation | dbt Core with dbt-duckdb adapter |
| SQL Linting | SQLFluff 3.5.0 (duckdb dialect) |

### Batch Processing Simulation

The dataset is static, but the pipeline is designed to simulate a real-world
dynamic database where new records arrive daily. Each pipeline run processes
only the records that fall within the current batch window, controlled by a
watermark date. This demonstrates how production incremental pipelines
operate in practice.

> A production version of this pipeline would use a managed EL tool such as
> Meltano or Airbyte for the ingestion layer.

## Project Structure
```
brazilian-ecommerce/
├── ingestion/        # Python scripts: Kaggle API → MotherDuck
├── transform/        # dbt project: staging, intermediate, marts
└── docs/             # Architecture diagrams and decision records
```

## Setup

### Prerequisites

- Python 3.11.15
- A [MotherDuck](https://motherduck.com) account and access token
- A [Kaggle](https://www.kaggle.com) account and API token

### Installation
```bash
# Clone the repository
git clone https://github.com/pedro-gauch/brazilian-ecommerce.git
cd brazilian-ecommerce

# Create and activate virtual environment
python3.11 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Configure credentials
cp .env.example .env
# Edit .env and fill in your tokens
```

### Environment Variables

| Variable | Description |
|---|---|
| `KAGGLE_API_TOKEN` | Kaggle API token from account settings |
| `MOTHERDUCK_TOKEN` | MotherDuck access token |

## Branch Strategy

| Branch | Purpose |
|---|---|
| `main` | Stable milestones only — merged via PR from dev |
| `dev` | Primary working branch |
| `feature/<description>` | One per piece of work, branched from dev |

## Coding Standards

- **SQL** — enforced by SQLFluff 3.5.0
- **dbt** — dbt coding conventions
- **Python** — Google Python Style Guide (80 char limit, type hints, docstrings)

## Future Extensions

- Predictive modeling and ML on seller performance and customer satisfaction
- Dashboard / BI serving layer
