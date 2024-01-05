import requests
import json


def send_otp_via_cm(phone_number: str, otp: str, country_code=91):
    product_token = "664be4fc-6622-49b0-a718-7e0389ebdaf2"
    url = "https://gw.cmtelecom.com/v1.0/message"

    if not otp or not phone_number or not country_code:
        raise Exception("Invalid input on sending OTP via CM.com")

    payload = json.dumps(
        {
            "messages": {
                "authentication": {"producttoken": product_token},
                "msg": [
                    {
                        "allowedChannels": ["SMS"],
                        "from": "AURAPP",
                        "to": [{"number": f"00{country_code}{phone_number}"}],
                        "minimumNumberOfMessageParts": 1,
                        "maximumNumberOfMessageParts": 8,
                        "body": {
                            "type": "auto",
                            "content": f"Hello, Your OTP for authentication is {otp} "
                            + "Please do not share it with anyone. -Aura Gold",
                        },
                    }
                ],
            }
        }
    )
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.request("POST", url, headers=headers, data=payload)
        if response.status_code == 200:
            response_data = response.json()
            if response_data["messages"][0]["status"] == "Accepted":
                return True
        raise Exception(
            f"Failed to send OTP via CM.com, error_code: {response.status_code}"
        )
    except Exception as e:
        raise e
