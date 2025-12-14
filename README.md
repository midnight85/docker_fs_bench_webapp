# Filesystem and Docker Storage Driver Benchmark Dashboard

A FastAPI-based web application for aggregating, visualizing, and sharing benchmark results from the Filesystem and Docker Storage Driver Benchmark Suites.

## Features

- **Interactive Visualization**: Dynamic charts using Plotly.js to compare filesystem performance.
- **Detailed Metrics**: Breakdown of IOPS, Bandwidth, Latency, and system resource usage (CPU, RAM).
- **Configuration Sharing**: Automatically bundles and serves the benchmark configuration (Ansible vars) used for each run.
- **System Monitoring**: Correlates benchmark scores with Docker stats and iostat metrics over time.

## Project Structure

```
webapp/
├── data/               # Stores benchmark results (*.json) and configs (*.zip)
├── templates/
│   └── dashboard.html  # Main frontend dashboard
├── main.py            # FastAPI backend application
└── requirements.txt   # Python dependencies
```

## Installation & Running Locally

### Prerequisites
- Python 3.9+
- pip

### 1. Setup Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Server
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
The dashboard will be available at `http://localhost:8000`.

## API Endpoints

### Upload Results
`POST /api/upload`
Accepts `multipart/form-data`:
- `file`: The `aggregated_report.json` file.
- `config_file` (Optional): A zip archive of the configuration directory.

Returns: `{ "link": "/benchmarks/{uuid}", "uuid": "{uuid}" }`

### View Dashboard
`GET /benchmarks/{uuid}`
Returns the HTML dashboard for a specific run.

### Get Config
`GET /api/benchmarks/{uuid}/config`
Downloads the configuration ZIP file associated with the run.

### Get Raw Data
`GET /api/benchmarks/{uuid}`
Returns the raw JSON data for the benchmark run.

## Deployment on Render.com

This project includes a `render.yaml` for automatic deployment.
1. Create a **Web Service** on Render.
2. Connect your repository.
3. Select "Python 3" runtime.
4. Build Command: `pip install -r requirements.txt`
5. Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

> **Note**: On the Free tier, the filesystem is ephemeral. Uploaded results will disappear if the service restarts. For calling persistence, upgrade to a paid plan with a persistent disk.
