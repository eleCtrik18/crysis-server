from src.config import settings
from src.utils.datetimeutils import get_current_datetime_obj
from src.tasks import make_slack_request


def send_slack_message(message):
    token = "xoxb-5050041441440-5824580913447-OPrFSJo6ChXxngY3Tpi17KZr"
    api_url = "https://slack.com/api/chat.postMessage"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    if settings.ENV == "production":
        channel = "C050KPKT97Y"
    else:
        channel = "C05RCRBATUG"
    message = (
        get_current_datetime_obj(string=True)
        + "\n"
        + str(message)
        + "\n"
        + "-----------"
    )
    payload = {"channel": channel, "text": message}
    try:
        make_slack_request.delay(api_url, headers, payload)

    except Exception as e:
        print(f"An error occurred: {str(e)}")
