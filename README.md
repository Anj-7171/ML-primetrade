# Primetrade MLOps Engineering Task 0 Assessment

This repository contains a minimal MLOps-style batch job in Python that demonstrates reproducibility, observability, and deployment readiness on financial data.

## Files
- `run.py`: The main batch job execution script.
- `config.yaml`: Configuration containing `seed`, `window`, and `version`.
- `data.csv`: Source OHLCV data for computation.
- `requirements.txt`: Python package requirements.
- `Dockerfile`: Container configuration for isolation and deployment.
- `generate_data.py`: A helper script used to generate an initial 10,000 rows `data.csv`.

## Local Run Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Execute Script
Run the script exactly as below:
```bash
python run.py --input data.csv --config config.yaml --output metrics.json --log-file run.log
```

## Docker Build & Run

Ensure you have Docker installed. The command will automatically build an image and run it.

### 1. Build Image
```bash
docker build -t mlops-task .
```

### 2. Run Container
```bash
docker run --rm mlops-task
```

The metrics JSON will be printed to your console confirming success.

## Example `metrics.json`
```json
{
  "version": "v1",
  "rows_processed": 10000,
  "metric": "signal_rate",
  "value": 0.5373,
  "latency_ms": 61,
  "seed": 42,
  "status": "success"
}
```
