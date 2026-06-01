import os
import requests
from dotenv import load_dotenv

load_dotenv()

CHAPA_SECRET_KEY = os.getenv("CHAPA_SECRET_KEY")
CHAPA_BASE_URL = "https://api.chapa.co/v1"


def initialize_payment(
    tx_ref: str,
    amount: float,
    email: str,
    first_name: str,
    last_name: str,
    callback_url: str,
    return_url: str,
    description: str = "TaxiMela Featured Listing Subscription",
) -> dict:
    """
    Initializes a Chapa payment and returns the checkout URL.
    """
    response = requests.post(
        f"{CHAPA_BASE_URL}/transaction/initialize",
        headers={
            "Authorization": f"Bearer {CHAPA_SECRET_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "amount": str(amount),
            "currency": "ETB",
            "email": email,
            "first_name": first_name,
            "last_name": last_name or "N/A",
            "tx_ref": tx_ref,
            "callback_url": callback_url,
            "return_url": return_url,
            "description": description,
        },
    )

    data = response.json()

    if response.status_code != 200 or data.get("status") != "success":
        raise Exception(f"Chapa initialization failed: {data.get('message', 'Unknown error')}")

    return {
        "checkout_url": data["data"]["checkout_url"],
        "tx_ref": tx_ref,
    }


def verify_payment(tx_ref: str) -> dict:
    """
    Verifies a Chapa payment by tx_ref.
    Returns the full Chapa response data.
    """
    response = requests.get(
        f"{CHAPA_BASE_URL}/transaction/verify/{tx_ref}",
        headers={
            "Authorization": f"Bearer {CHAPA_SECRET_KEY}",
        },
    )

    data = response.json()

    if response.status_code != 200:
        raise Exception(f"Chapa verification failed: {data.get('message', 'Unknown error')}")

    return data
