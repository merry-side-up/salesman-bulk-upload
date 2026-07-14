import requests
from config import API_URL, JWT_TOKEN


def create_visit(payload):

    headers = {
        "Authorization": JWT_TOKEN,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    response = requests.post(
        API_URL,
        headers=headers,
        json=payload
    )

    return response