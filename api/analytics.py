from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
import numpy as np

app = FastAPI()

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
file_path = os.path.join(BASE_DIR, "q-vercel-latency.json")

with open(file_path) as f:
    data = json.load(f)

@app.post("/api/analytics")
async def analytics(payload: dict):
    regions = payload.get("regions", [])
    threshold = payload.get("threshold_ms", 0)

    result = {}

    for region in regions:
        region_records = [r for r in data if r["region"] == region]

        latencies = [r["latency_ms"] for r in region_records]
        uptimes = [r["uptime"] for r in region_records]

        if not latencies:
            continue

        avg_latency = sum(latencies) / len(latencies)
        p95_latency = np.percentile(latencies, 95)
        avg_uptime = sum(uptimes) / len(uptimes)
        breaches = sum(1 for l in latencies if l > threshold)

        result[region] = {
            "avg_latency": round(avg_latency, 2),
            "p95_latency": round(float(p95_latency), 2),
            "avg_uptime": round(avg_uptime, 4),
            "breaches": breaches
        }

    return result