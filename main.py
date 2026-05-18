from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional
import datetime
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("SentinelOps")

app = FastAPI(title="Project Sentinel Core API", version="1.0.0")

class TelemetryPayload(BaseModel):
    flight_id: str = Field(..., example="EK412")
    sensor_type: str = Field(..., example="CATERING")
    status: str = Field(..., example="DELAYED")
    delay_minutes: int = Field(..., ge=0, example=5)
    timestamp: Optional[str] = None

class MitigationResponse(BaseModel):
    status: str
    agentic_action: str
    timestamp: str

def verify_jwt_token(token: str = "valid-emirates-hcc-token"):
    if token != "valid-emirates-hcc-token":
        logger.warning("Unauthorized access attempt intercepted.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    return True

@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "nominal", "timestamp": datetime.datetime.utcnow().isoformat()}

@app.post("/api/v1/telemetry", tags=["Data Ingestion"])
async def ingest_telemetry(payload: TelemetryPayload, authorized: bool = Depends(verify_jwt_token)):
    logger.info(f"Ingesting telemetry for {payload.flight_id} - {payload.sensor_type}")
    
    if payload.delay_minutes > 15:
        logger.error(f"Critical delay detected on {payload.flight_id}. Escalating to LLM layer.")
        return {"status": "anomaly_detected", "system_action": "escalating to Agentic AI"}
    
    return {"status": "logged", "delay_minutes": payload.delay_minutes}

@app.post("/api/v1/mitigate", response_model=MitigationResponse, tags=["Agentic AI"])
async def generate_mitigation(flight_id: str, issue: str, authorized: bool = Depends(verify_jwt_token)):
    logger.info(f"Generating mitigation protocol for {flight_id}.")
    mitigation_logic = f"Reroute ground tugs for {flight_id} due to {issue}. Alert Gate Agents to stagger boarding to protect ATC slot."
    
    return MitigationResponse(
        status="mitigation_deployed",
        agentic_action=mitigation_logic,
        timestamp=datetime.datetime.utcnow().isoformat()
    )
