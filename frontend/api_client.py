# api_client.py
import requests

def upload_pdf(file, upload_url: str):
    files = {
        "file": (file.name, file, "application/pdf")
    }
    response = requests.post(upload_url, files=files)
    response.raise_for_status()
    return response.json()


def query_rag(payload: dict, query_url: str):
    response = requests.post(query_url, json=payload)
    response.raise_for_status()
    return response.json()
