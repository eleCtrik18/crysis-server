import pytz
import datetime
import uuid


def generate_transaction_id():
    ist = pytz.timezone("Asia/Kolkata")

    # Get the current time in IST
    ist_time = datetime.datetime.now(ist)

    # Return the datetime in the format YYYYMMDDHHMMSS (14 characters)
    ist_time_str = ist_time.strftime("%Y%m%d%H%M%S")

    # Generate a random UUID without dashes
    random_id = uuid.uuid4().hex

    # Get the first 18 characters from the random UUID (32 - 14 = 18)
    random_part = random_id[:18]

    # Combine the IST datetime string with the random part
    transaction_id = ist_time_str + random_part

    return transaction_id
