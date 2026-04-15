import argparse
import yaml
import pandas as pd
import numpy as np
import json
import logging
import time
import sys
import os

def setup_logging(log_file):
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

def write_error_metrics(output_file, version, error_message):
    metrics = {
        "version": version,
        "status": "error",
        "error_message": error_message
    }
    with open(output_file, 'w') as f:
        json.dump(metrics, f, indent=2)
    print(json.dumps(metrics, indent=2))

def write_success_metrics(output_file, version, rows_processed, signal_rate, latency_ms, seed):
    metrics = {
        "version": version,
        "rows_processed": rows_processed,
        "metric": "signal_rate",
        "value": float(signal_rate),
        "latency_ms": latency_ms,
        "seed": seed,
        "status": "success"
    }
    with open(output_file, 'w') as f:
        json.dump(metrics, f, indent=2)
    print(json.dumps(metrics, indent=2))

def main():
    start_time = time.time()
    
    parser = argparse.ArgumentParser(description='MLOps Batch Job')
    parser.add_argument('--input', required=True, help='Input CSV file')
    parser.add_argument('--config', required=True, help='Config YAML file')
    parser.add_argument('--output', required=True, help='Output metrics JSON file')
    parser.add_argument('--log-file', required=True, help='Log file')
    
    args = parser.parse_args()

    # We must try to get version from config, but if it fails, default to "v1" for error reporting
    version = "v1"

    # Minimal setup for logger if the config isn't loaded yet
    # but we need to log right away as per requirements
    try:
        logger = setup_logging(args.log_file)
        logger.info("Job started")
    except Exception as e:
        # If we can't even configure logging, write an error metric and exit
        write_error_metrics(args.output, version, f"Failed to setup logging: {str(e)}")
        sys.exit(1)

    try:
        # 1) Load + validate config
        if not os.path.exists(args.config):
            raise FileNotFoundError(f"Config file {args.config} not found")
        
        with open(args.config, 'r') as f:
            config = yaml.safe_load(f)
            
        if not isinstance(config, dict):
            raise ValueError("Invalid config structure: must be a dictionary")
            
        required_keys = ['seed', 'window', 'version']
        missing_keys = [k for k in required_keys if k not in config]
        if missing_keys:
            raise ValueError(f"Config missing required fields: {', '.join(missing_keys)}")
            
        version = config['version']
        seed = int(config['seed'])
        window = int(config['window'])
        
        logger.info(f"Config loaded and validated: seed={seed}, window={window}, version={version}")
        
        np.random.seed(seed)

        # 2) Load + validate dataset
        if not os.path.exists(args.input):
            raise FileNotFoundError(f"Input file {args.input} not found")
            
        if os.path.getsize(args.input) == 0:
            raise ValueError("Input CSV file is empty")
            
        try:
            df = pd.read_csv(args.input)
        except Exception as e:
            raise ValueError(f"Invalid CSV format: {str(e)}")
            
        if df.empty:
            raise ValueError("Loaded dataset is empty")
            
        if 'close' not in df.columns:
            raise ValueError("Dataset missing required column: 'close'")
            
        rows_processed = len(df)
        logger.info(f"Loaded {rows_processed} rows from {args.input}")

        # 3) Rolling mean
        logger.info("Computing rolling mean...")
        # handling the first window-1 rows with NaNs by default pandas rolling behavior
        rolling_mean = df['close'].rolling(window=window).mean()
        
        # 4) Signal
        logger.info("Generating signals...")
        # signal = 1 if close > rolling_mean, else 0
        # If rolling_mean is NaN, close > NaN is False, so signal = 0. This is consistent.
        signal = (df['close'] > rolling_mean).astype(int)

        # 5) Metrics + timing
        signal_rate = signal.mean()
        
        end_time = time.time()
        latency_ms = int((end_time - start_time) * 1000)
        
        logger.info("Writing metrics summary...")
        write_success_metrics(
            output_file=args.output,
            version=version,
            rows_processed=rows_processed,
            signal_rate=signal_rate,
            latency_ms=latency_ms,
            seed=seed
        )
        
        logger.info("Job ended successfully")
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"Job failed: {str(e)}")
        write_error_metrics(args.output, version, str(e))
        sys.exit(1)

if __name__ == "__main__":
    main()
