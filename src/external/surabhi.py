import requests
from src.constants.common import GST


def _format_surabhi_response(response: str):
    response_l = response.split("\t")
    applied_gst = round(float(response_l[4]) * (GST / 100), 2)
    response_dict = {
        "product_id": int(response_l[1]),
        "product_name": response_l[2],
        "gold_24_carat_w_gst": float(response_l[4]),
        "applied_gst": applied_gst,
        "gold_24_carat_wo_gst": round(float(response_l[4]) - applied_gst, 2),
    }
    return response_dict


def get_latest_gold_price():
    url = "http://bcast.surabibullion.net:7767/VOTSBroadcastStreaming/Services/xml/GetLiveRateOfScrip/2932"

    payload = {}
    headers = {
        "Accept": "text/plain, */*; q=0.01",
        "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
        "Connection": "keep-alive",
        "DNT": "1",
        "Origin": "http://www.surabibullion.com",
        "Referer": "http://www.surabibullion.com/",
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36",
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    """
    Initialzie Repository object
    objct with data
    
    """

    return _format_surabhi_response(response.text)


if __name__ == "__main__":
    print(get_latest_gold_price())
