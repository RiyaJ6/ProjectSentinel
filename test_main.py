from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

auth_headers = {"Authorization": "valid-emirates-hcc-token"}

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
    response = client.post("/api/v1/telemetry", json=payload, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["status"] == "logged"

def test_telemetry_anomaly_detection():
    payload = {
        "flight_id": "EK412",
        "sensor_type": "CATERING",
        "status": "DELAYED",
        "delay_minutes": 20
    }
    response = client.post("/api/v1/telemetry", json=payload, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["status"] == "anomaly_detected"

def test_mitigation_generation():
    response = client.post("/api/v1/mitigate?flight_id=EK412&issue=Catering_Delay", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["status"] == "mitigation_deployed"
    assert "Reroute ground tugs" in response.json()["agentic_action"]

def test_post_quantum_circuit_breaker_isolation():
    # 5th Test: Verifies security perimeter drops structural poisoning attempts
    payload = {
        "flight_id": "EK412",
        "sensor_type": "CATERING",
        "status": "STALLED",
        "delay_minutes": 99
    }
    
    # Merge auth token with the malicious cryptographic state token
    security_headers = {
        **auth_headers,
        "X-State-Token": "EXPIRED_OR_MALICIOUS_LATTICE_SIGNATURE"
    }
    
    response = client.post("/api/v1/telemetry", json=payload, headers=security_headers)
    assert response.status_code == 400
    assert "Circuit Breaker Active" in response.json()["detail"]

