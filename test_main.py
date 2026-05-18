from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "nominal"

def test_telemetry_nominal():
    payload = {
        "flight_id": "EK412",
        "sensor_type": "FUELING",
        "status": "ON_TIME",
        "delay_minutes": 0
    }
    response = client.post("/api/v1/telemetry", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "logged"

def test_telemetry_anomaly_detection():
    payload = {
        "flight_id": "EK412",
        "sensor_type": "CATERING",
        "status": "DELAYED",
        "delay_minutes": 20
    }
    response = client.post("/api/v1/telemetry", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "anomaly_detected"

def test_mitigation_generation():
    response = client.post("/api/v1/mitigate?flight_id=EK412&issue=Catering_Delay")
    assert response.status_code == 200
    assert response.json()["status"] == "mitigation_deployed"
    assert "Reroute ground tugs" in response.json()["agentic_action"]
