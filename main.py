"""
Benchmark Dashboard Web Application
Receives aggregated benchmark results, stores them, and serves interactive visualizations.
"""
from fastapi import FastAPI, Request, HTTPException, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from uuid import uuid4
from typing import Optional
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
async def upload_results(
    file: Optional[UploadFile] = None,
    config_file: Optional[UploadFile] = None,
):
    """
    Upload benchmark results.
    Supports:
    - Multipart upload with 'file' (JSON report) and optional 'config_file' (ZIP)
    """
    try:
        # Handle report file
        if not file:
             raise HTTPException(status_code=400, detail="Missing report file")
        
        contents = await file.read()
        try:
            data = json.loads(contents)
        except json.JSONDecodeError:
             raise HTTPException(status_code=400, detail="Invalid JSON report file")
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Generate short UUID (last 12 characters)
    uuid = str(uuid4())[-12:]
    filepath = os.path.join(DATA_DIR, f"{uuid}.json")

    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)

    # Save config ZIP if provided
    if config_file:
        config_path = os.path.join(DATA_DIR, f"{uuid}_config.zip")
        with open(config_path, "wb") as f:
            f.write(await config_file.read())

    # Also save as latest
    latest_path = os.path.join(DATA_DIR, "latest.json")
    with open(latest_path, "w") as f:
        json.dump(data, f, indent=2)
    
    # If config exists, also save as latest_config.zip
    if config_file:
         latest_config_path = os.path.join(DATA_DIR, "latest_config.zip")
         # We need to re-read or copy. Since we already wrote it to disk, let's copy
         import shutil
         shutil.copy2(os.path.join(DATA_DIR, f"{uuid}_config.zip"), latest_config_path)

    # Build full URL (using request is tricky if not passed, but we can simplify return)
    # We'll just return relative path or constructed ID
    link = f"/benchmarks/{uuid}"

    return {"link": link, "uuid": uuid}


@app.get("/benchmarks/{uuid}", response_class=HTMLResponse)
async def view_benchmark(uuid: str):
    """Serve the dashboard HTML for viewing benchmark results."""
    dashboard_path = os.path.join(TEMPLATES_DIR, "dashboard.html")
    if not os.path.exists(dashboard_path):
        raise HTTPException(status_code=500, detail="Dashboard template not found")
    
    with open(dashboard_path, "r") as f:
        return HTMLResponse(f.read())


@app.get("/api/benchmarks/{uuid}")
async def get_benchmark_data(uuid: str):
    """Return benchmark JSON data for the given UUID."""
    filepath = os.path.join(DATA_DIR, f"{uuid}.json")
    
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Results not found")
    
    with open(filepath, "r") as f:
        data = json.load(f)
    
    # Check if config exists and add a flag to the response
    config_path = os.path.join(DATA_DIR, f"{uuid}_config.zip")
    if os.path.exists(config_path):
        data["has_config"] = True
        
    return data


@app.get("/api/benchmarks/{uuid}/config")
async def get_benchmark_config(uuid: str):
    """Download the configuration ZIP for the given UUID."""
    filename = f"{uuid}_config.zip"
    filepath = os.path.join(DATA_DIR, filename)
    
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Configuration not found")
        
    from fastapi.responses import FileResponse
    return FileResponse(filepath, media_type="application/zip", filename=f"pma_config_{uuid}.zip")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
