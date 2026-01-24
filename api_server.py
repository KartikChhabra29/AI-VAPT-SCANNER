from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import subprocess
import json
import re

app = FastAPI()

# Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "AI VAPT Scanner API Running"}

# -----------------------------
# SCAN ENDPOINT
# -----------------------------
@app.get("/scan")
def run_scan(target: str):
    try:
        # Run scanner_core.py with target argument
        result = subprocess.run(
            ["python", "scanner_core.py", target],
            capture_output=True,
            text=True
        )

        output = result.stdout
        print("\n=== RAW OUTPUT ===\n", output)

        # Extract JSON inside { ... }
        match = re.search(r"{.*}", output, re.DOTALL)
        if not match:
            return {"status": "error", "message": "JSON not found in scanner output"}

        json_text = match.group(0)
        report = json.loads(json_text)

        return {
            "status": "success",
            "report": report
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}


# -----------------------------
# PDF DOWNLOAD ENDPOINT
# -----------------------------
@app.get("/download")
def download_pdf():
    return FileResponse(
        "scan_report.pdf",  # Path in backend folder
        media_type="application/pdf",
        filename="scan_report.pdf"
    )
