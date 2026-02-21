# Moniepoint Analytics API

**Author:** Tijani Ahmed

A REST API that processes merchant activity logs and exposes business insights.

---

## Assumptions

- CSV files are in the `data/` directory at the project root.
- Malformed or unparseable rows are skipped gracefully without aborting the import.
- "Product adoption" counts any merchant with at least one event per product (any status).
- Failure rate excludes PENDING: `FAILED / (SUCCESS + FAILED) * 100`.
- All 5 endpoint responses are cached in memory after first request (dataset is static).

---

## Prerequisites

- Python 3.11+
- PostgreSQL (running locally)

---

## Setup & Run

### 1. Clone the repo
```bash
git clone <your-repo-url>
cd moniepoint-analytics
```

### 2. Create and activate virtual environment
```bash
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Create PostgreSQL database
```sql
CREATE DATABASE moniepoint;
```

### 5. Configure environment
Edit `.env` with your database credentials:
```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=moniepoint
DB_USER=postgres
DB_PASSWORD=your_password
```

### 6. Add CSV files
Place all `activities_YYYYMMDD.csv` files into the `data/` folder.

### 7. Import data (run once)
```bash
python scripts/ingest.py
```

### 8. Start the API
```bash
uvicorn src.app.main:app --host 0.0.0.0 --port 8080
```

---

## Test the endpoints
```bash
curl http://localhost:8080/analytics/top-merchant
curl http://localhost:8080/analytics/monthly-active-merchants
curl http://localhost:8080/analytics/product-adoption
curl http://localhost:8080/analytics/kyc-funnel
curl http://localhost:8080/analytics/failure-rates
```

Or visit **http://localhost:8080/docs** for interactive API docs.