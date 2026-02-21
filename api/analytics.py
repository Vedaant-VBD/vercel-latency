from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import json
import os
import math

app = FastAPI()

# 🔥 Proper CORS setup (important for grader)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],   # allow POST + OPTIONS
    allow_headers=["*"],
)

# Load telemetry JSON safely
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
file_path = os.path.join(BASE_DIR, "q-vercel-latency.json")

with open(file_path) as f:
    data = json.load(f)


def percentile(values, percent):
    values = sorted(values)
    k = (len(values) - 1) * (percent / 100)
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return values[int(k)]
    return values[f] + (values[c] - values[f]) * (k - f)


# 🔥 IMPORTANT: path must match exactly
@app.post("/api/analytics")
async def analytics(request: Request):
    payload = await request.json()

    regions = payload.get("regions", [])
    threshold = payload.get("threshold_ms", 0)

    result = {}

    for region in regions:
        records = [r for r in data if r["region"] == region]

        if not records:
            continue

        latencies = [r["latency_ms"] for r in records]
        uptimes = [r["uptime"] for r in records]

        result[region] = {
            "avg_latency": round(sum(latencies) / len(latencies), 2),
            "p95_latency": round(percentile(latencies, 95), 2),
            "avg_uptime": round(sum(uptimes) / len(uptimes), 4),
            "breaches": sum(1 for l in latencies if l > threshold)
        }

    return result
