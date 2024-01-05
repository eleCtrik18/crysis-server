import pytz
import datetime
from dateutil.relativedelta import relativedelta


def get_current_datetime_obj(string=False):
    ist = pytz.timezone("Asia/Kolkata")

    # Get the current time in IST
    ist_time = datetime.datetime.now(ist)
    if string:
        return ist_time.__str__()

    return ist_time


def get_next_recur_date_daily(return_obj=False, format="%d%m%Y"):
    ist = pytz.timezone("Asia/Kolkata")

    # Get the current time in IST
    ist_time = datetime.datetime.now(ist)

    # Add one month to the current date
    one_day_later = ist_time + relativedelta(days=1)

    # Return the date in ddmmyyyy format
    if return_obj:
        return one_day_later
    return one_day_later.strftime("%d%m%Y")


def get_ist_date_plus_x_month(x):
    # Define the IST timezone
    ist = pytz.timezone("Asia/Kolkata")

    # Get the current time in IST
    ist_time = datetime.datetime.now(ist)

    # Add one month to the current date
    one_month_later = ist_time + relativedelta(months=x)

    # Return the date in ddmmyyyy format
    return one_month_later.strftime("%d%m%Y")


def get_current_date_minus_x_days_obj(x):
    # Define the IST timezone
    ist = pytz.timezone("Asia/Kolkata")

    # Get the current time in IST
    ist_time = datetime.datetime.now(ist)

    # Subtract x days to the current date
    x_days_ago = ist_time - relativedelta(days=x)

    # Return the date in ddmmyyyy format
    return x_days_ago


def get_current_date_minus_x_minutes_obj(x):
    # Define the IST timezone
    ist = pytz.timezone("Asia/Kolkata")

    # Get the current time in IST
    ist_time = datetime.datetime.now(ist)

    # Subtract x mins to the current date
    x_mins_ago = ist_time - relativedelta(minutes=x)

    return x_mins_ago


def get_ist_date():
    ist = pytz.timezone("Asia/Kolkata")

    # Get the current time in IST
    ist_time = datetime.datetime.now(ist)

    # Return the date in ddmmyyyy format
    return ist_time.strftime("%d%m%Y")
