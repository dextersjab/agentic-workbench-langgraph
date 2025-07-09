import pytest, json, csv, os, requests

BASE = os.getenv("API_BASE", "http://localhost:8000")

def test_classification():
    resp = requests.post(f"{BASE}/classify", json={"subject": "VPN issue", "description": "VPN cannot connect"})
    assert resp.status_code == 200
    payload = resp.json()
    assert "category" in payload
    assert "confidence" in payload

def test_routing():
    resp = requests.post(f"{BASE}/route", json={"subject": "Password reset", "description": "I cannot reset my password"})
    assert resp.status_code == 200
    payload = resp.json()
    assert payload["priority"] in ["P1","P2","P3"]