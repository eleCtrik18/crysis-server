import requests
import json
from src.config import settings
from src.logging import logger
from src.schema.common import APIResponse


def credit_gold_to_user(code, amount, phone, txn_id=None):
    url = f"{settings.MOIHOST_URL}/api/v1/payment/deposit_gold_v2"

    payload = json.dumps(
        {
            "amount": amount,
            "secret_key": settings.MOIAPI_SECRET_KEY,
            "phone_number": phone,
            "code": code,
        }
    )
    logger.info(
        f"credit_gold_to_user {phone}, amount: {amount} code: {code}, txn_id: {txn_id}"
    )
    headers = {
        "Content-Type": "application/json",
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    if response.status_code == 200:
        return APIResponse(success=True, error="", data={})
    else:
        logger.error(
            f"FAILED: to credit_gold_to_user {phone}, amount: {amount} code: {code}, txn_id: {txn_id}"
        )
        return APIResponse(
            success=False, error="NON_200", data={"status_code": response.status_code}
        )
