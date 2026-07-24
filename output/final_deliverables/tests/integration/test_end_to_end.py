import requests


def test_fastapi_running():
    r = requests.get("http://127.0.0.1:8000/api/v1/health")
    assert r.status_code == 200


def test_streamlit_running():
    r = requests.get("http://127.0.0.1:8501")
    assert r.status_code == 200


def test_api_returns_company():
    r = requests.get("http://127.0.0.1:8000/api/v1/companies/TCS")
    assert r.status_code == 200
