import requests
import json
from src.config import settings

headers = {
    "api-key": settings.IDFY_KEY,
    "account-id": settings.IDFY_ACC,
    "Content-Type": "application/json",
}


def get_request_idfy(req_id):
    base_url = (
        settings.IDFY_REQ_TEST_URL
        if settings.ENV == "development"
        else settings.IDFY_REQ_URL
    )
    url = f"{base_url}{req_id}"

    try:
        response = requests.request("GET", url=url, headers=headers)
        if response.status_code == 200:
            resp_json = response.json()
            return resp_json[0]
    except Exception as e:
        raise e


def verify_pan_idfy(pan, id):
    print(settings.ENV)
    base_url = (
        settings.IDFY_VERIFY_TEST_URL
        if settings.ENV == "development"
        else settings.IDFY_VERIFY_URL
    )
    url = f"{base_url}"
    payload = json.dumps(
        {"task_id": id, "group_id": settings.IDFY_GROUP_ID, "data": {"id_number": pan}}
    )
    try:
        response = requests.request("POST", url=url, headers=headers, data=payload)
        if response.status_code == 202:
            resp_json = response.json()
            return resp_json["request_id"]
    except Exception as e:
        raise e
