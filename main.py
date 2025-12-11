"""
Benchmark Dashboard Web Application
Receives aggregated benchmark results, stores them, and serves interactive visualizations.
"""
from fastapi import FastAPI, Request, HTTPException, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from uuid import uuid4
import os
import json

app = FastAPI(title="Benchmark Dashboard")

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
DATA_DIR = os.path.join(BASE_DIR, "data")

os.makedirs(DATA_DIR, exist_ok=True)


@app.get("/", response_class=RedirectResponse)
async def root():
    """Redirect to latest benchmark."""
    return RedirectResponse(url="/benchmarks/latest")


@app.post("/api/upload")
async def upload_results(file: UploadFile, request: Request):
    """
    Upload benchmark results JSON.
    Returns a link to view the results.
    """
    try:
        contents = await file.read()
        data = json.loads(contents)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON file")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Generate short UUID (last 12 characters)
    run_id = str(uuid4())[-12:]
    filepath = os.path.join(DATA_DIR, f"{run_id}.json")

    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)

    # Also save as latest
    latest_path = os.path.join(DATA_DIR, "latest.json")
    with open(latest_path, "w") as f:
        json.dump(data, f, indent=2)

    # Build full URL
    base_url = str(request.base_url).rstrip("/")
    link = f"{base_url}/benchmarks/{run_id}"

    return {"link": link}


@app.get("/benchmarks/{run_id}", response_class=HTMLResponse)
async def view_benchmark(run_id: str):
    """Serve the dashboard HTML for viewing benchmark results."""
    dashboard_path = os.path.join(TEMPLATES_DIR, "dashboard.html")
    if not os.path.exists(dashboard_path):
        raise HTTPException(status_code=500, detail="Dashboard template not found")
    
    with open(dashboard_path, "r") as f:
        return HTMLResponse(f.read())


@app.get("/api/benchmarks/{run_id}")
async def get_benchmark_data(run_id: str):
    """Return benchmark JSON data for the given run ID."""
    filepath = os.path.join(DATA_DIR, f"{run_id}.json")
    
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Results not found")
    
    with open(filepath, "r") as f:
        return json.load(f)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
