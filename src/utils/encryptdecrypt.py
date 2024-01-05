import hashlib
import base64
import json
from secrets import token_bytes
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad, unpad
import requests
import pytz
import datetime
from dateutil.relativedelta import relativedelta
import uuid

# from src.config import Settings

# CAMSPAY_ID = Settings.CAMSPAY_CREDENTIALS.get("CAMSPAY_ID")
# URL_HOST = Settings.CAMSPAY_CREDENTIALS.get("URL_HOST")
# MERCHANT_ID = Settings.CAMSPAY_CREDENTIALS.get("MERCHANT_ID")
# SUBBILLER_ID = Settings.CAMSPAY_CREDENTIALS.get("SUBBILLER_ID")
# CAMSPAY_ENCRYPTION_KEY = Settings.CAMSPAY_CREDENTIALS.get("CAMSPAY_ENCRYPTION_KEY")

CAMSPAY_ENCRYPTION_KEY = "k5c5pi7X5OZN8hEW"
MERCHANT_ID = "991324"
SUBBILLER_ID = "771442"
CAMSPAY_ID = "8a2384a44979075371a81bdf490140c1a051d198ccc0fc68bad986a9034328b0"
URL_HOST = "https://cppro1.camspay.com/api/v1"


# extracting secret key
BLOCK_SIZE = 16


def get_secret_key():
    hashing_iv = hashlib.sha256(CAMSPAY_ENCRYPTION_KEY.encode()).hexdigest()
    secret_key = hashing_iv[0:32].encode("utf8")
    return secret_key


def encrypt(plaintext, key, iv):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    c = cipher.encrypt(pad(plaintext.encode("utf8"), BLOCK_SIZE))
    enc = base64.b64encode(c).decode("utf8")
    output = enc.replace("+", "-").replace("/", "_")
    return output


def decrypt(ciphertext, key, iv):
    iv = bytes.fromhex(iv)
    response = (ciphertext).replace("-", "+").replace("_", "/")
    cipher = AES.new(key, AES.MODE_CBC, iv)
    response = base64.b64decode(response)
    c = cipher.decrypt(response)
    output = unpad(c, BLOCK_SIZE).decode("utf8")
    return output


def get_iv():
    return token_bytes(16)


def get_ist_date():
    ist = pytz.timezone("Asia/Kolkata")

    # Get the current time in IST
    ist_time = datetime.datetime.now(ist)

    # Return the date in ddmmyyyy format
    return ist_time.strftime("%d%m%Y")


def get_ist_date_plus_one_month():
    # Define the IST timezone
    ist = pytz.timezone("Asia/Kolkata")

    # Get the current time in IST
    ist_time = datetime.datetime.now(ist)

    # Add one month to the current date
    one_month_later = ist_time + relativedelta(months=1)

    # Return the date in ddmmyyyy format
    return one_month_later.strftime("%d%m%Y")


def get_next_recur_date_daily():
    ist = pytz.timezone("Asia/Kolkata")

    # Get the current time in IST
    ist_time = datetime.datetime.now(ist)

    # Add one month to the current date
    one_day_later = ist_time + relativedelta(days=1)

    # Return the date in ddmmyyyy format
    return ist_time.strftime("%d%m%Y")


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


def make_request(url, req_data):
    print("url", url)
    iv = get_iv()
    secret_key = get_secret_key()
    encrypted_request = encrypt(json.dumps(req_data), secret_key, iv)
    encrypted_body = {"param": f"{CAMSPAY_ID}.{iv.hex()}.{encrypted_request}"}
    print("encrypted_body:", encrypted_body)
    res = requests.post(url=url, data=encrypted_body)
    print("status_code", res.status_code)
    res = json.loads(res.text)
    encrypted_resp = res["res"].split(".")
    # encrypted_resp[1] is camspay response
    # encrypted_resp[0] is camspay iv
    print("encrypted_resp", encrypted_resp)
    decrypted_resp = decrypt(encrypted_resp[1], secret_key, encrypted_resp[0])
    decrypted_resp = json.loads(decrypted_resp)
    return decrypted_resp


def validate_vpa(vpa):
    url = f"{URL_HOST}/validvpa"
    raw_json = {"vpa": vpa, "merchantid": MERCHANT_ID, "subbillerid": SUBBILLER_ID}
    resp = make_request(url, raw_json)
    print(resp)
    # add response validator
    return resp


def create_daily_mandate(vpa=None, amount="02.00"):
    # may need: instaauth, instaamount, redirecturl, debiturl
    url = f"{URL_HOST}/mandatecreate"
    if vpa:
        vpa_details = validate_vpa(vpa=vpa)
        print(vpa_details)
        if vpa_details["is_autopay_eligible"] != "Y":
            return "Account is not eligible for Autopay"
        payer_name = vpa_details["payer_name"]

    req_data = {
        "trxnno": generate_transaction_id(),
        "amount": str(amount),
        "pattern": "ASPRESENTED",
        "mandatestartdate": get_ist_date(),
        "mandateenddate": get_ist_date_plus_one_month(),
        "merchantid": MERCHANT_ID,
        "subbillerid": SUBBILLER_ID,
        "revokeable": "Y",
        # "payervpa": vpa,
        "payername": "Shivam Singhal",
        "authorize": "Y",
        "authorizerevoke": "Y",
        "intent": "Y",
        "redirecturl": "https://api.auragold.in/mandatesuccess",
    }
    print("req_data ", req_data)
    resp = make_request(url, req_data)
    print("resp: ", resp)
    """
    {'cp_mdt_ref_no': 'MAAT66TESTP478YUAT989MAND1000054922', 'status': 'PENDING', 
    'deeplink': 'upi://mandate?pa=cpupisi@indus&pn=TestCams&mn=TESTMANDATE&tid=202308112022488cd8330ce4e54ad794&tr=MAAT66TESTP478YUAT989MAND1000054922&validitystart=11082023&validityend=11092023&am=02.00&amrule=MAX&recur=ASPRESENTED&cu=INR&mc=6211&tn=Subscription&purpose=14&rev=Y&mode=01&sign=MGQCMBt8tD5FRyNMtzDKJPaK03iBvZFaCvOq0NtQsJw9BQV/t2T+KLdQ30RFbsSB9jMB0wIwDV7ibvDOdhdNsw0CFhq8+uznjj28/EzhD1AS9m+LpO0OblXsx94jlcX5bmoFHo6B&orgid=159234', 'msg': 'Mandate Intent URL generated successfully', 'errCode': '1111', 'errDesc': 'Mandate Intent URL generated successfully', 'res': {'trxnno': '202308112022488cd8330ce4e54ad794', 'amount': '02.00', 'pattern': 'DAILY', 'mandatestartdate': '11082023', 'mandateenddate': '11092023', 'merchantid': '884663', 'subbillerid': '661608', 'revokeable': 'Y', 'payervpa': '9503182221@paytm', 'payername': 'Shivam Singhal', 'authorize': 'Y', 'authorizerevoke': 'Y', 'intent': 'Y', 'redirecturl': 'https://api.auragold.in/mandatesuccess', 'autoExecute': 'Y', 'instaauth': 'N'}}
    """
    return resp


def revoke_mandate(mandate_ref_no):
    req_data = {"refno": mandate_ref_no}
    url = f"{URL_HOST}/mandaterevoke"
    resp = make_request(url=url, req_data=req_data)
    print(resp)
    return resp


def check_mandate_status(mandate_ref_no, txn_no):
    url = f"{URL_HOST}/mandatestatus"
    req_data = {
        "trxnno": txn_no,
        "refno": mandate_ref_no,
        "actiontype": "MANDATE_STATUS",
        "merchantid": MERCHANT_ID,
        "subbillerid": SUBBILLER_ID,
    }
    print("req_data:", req_data)
    resp = make_request(url, req_data=req_data)
    print("resp", resp)
    """
    {'merchantid': '884663', 'subbillerid': '661608', 'cp_mdt_ref_no': 'MAAT66TESTP478YUAT989MAND1000054923', 'umn': 'PTM50b5b5d154866932ad90bfe70f3c6@paytm', 'trxnno': '202308112029553f8fcefcd2e24260b4', 'amount': '2.00', 'status': 'ACTIVE', 'statusdesc': '00-APPROVED OR COMPLETED SUCCESSFULLY', 'pattern': 'DAILY'}
    """
    return resp


def check_transaction_status(mandate_ref_no, txn_no):
    url = f"{URL_HOST}/mandatestatus"
    req_data = {
        "trxnno": txn_no,
        "refno": mandate_ref_no,
        "actiontype": "TRANSACTION_STATUS",
        "merchantid": MERCHANT_ID,
        "subbillerid": SUBBILLER_ID,
    }
    print("req_data:", req_data)
    resp = make_request(url, req_data=req_data)
    print(resp)
    """
    [{'merchantid': '884663', 'subbillerid': '661608', 'executionrefno': 'TO122927', 'trxnno': '2023081123052901aeb23dab3c4788a1', 'amount': '1.00', 'bankrrn': '322361923490', 'cp_mdt_ref_no': 'MAAT66TESTP478YUAT989MAND1000054924', 'trxndate': '2023-08-11 23:05:31', 'trxn_status': 'FAILED', 'status_desc': 'Address resolution is failed', 'bank_name': 'HDFC Bank', 'account_no': '50100372427008', 'acc_holder_name': 'Shivam Singhal', 'ifsc': 'HDFC0009228', 'payerpva': '9503182221@paytm'}]   
      """
    return resp


def notify_user_about_next_debit(mandate_ref_no, amount):
    url = f"{URL_HOST}/mandatePreDebit"
    req_data = {
        "refno": mandate_ref_no,
        "amount": str(amount),
        "nextRecurDate": get_next_recur_date_daily(),
    }
    print("req_data={}".format(req_data))
    resp = make_request(url, req_data=req_data)
    print("resp", resp)
    """
    {'bank_error_code': '00', 'bank_error_desc': 'APPROVED OR COMPLETED SUCCESSFULLY', 'bank_res_code': '00', 'bank_res_desc': 'APPROVED OR COMPLETED SUCCESSFULLY', 'status': 'Success', 'statusdesc': 'Request Processed Successfully', 'cp_mandate_ref_no': 'MAAT66TESTP478YUAT989MAND1000054923', 'seqno': 2}    
    """
    return resp


def execute_mandate(mandate_ref_no, amount, seq_no):
    url = f"{URL_HOST}/mandateExecute"
    req_data = {
        "refno": mandate_ref_no,
        "amount": str(amount),
        "seqno": seq_no,
        "trxnno": generate_transaction_id(),
    }
    print("req_data={}".format(req_data))
    resp = make_request(url, req_data=req_data)
    print("resp", resp)
    return resp


def decrypt_response(res):
    secret_key = get_secret_key()
    encrypted_resp = res.split(".")
    decrypted_resp = decrypt(encrypted_resp[1], secret_key, encrypted_resp[0])
    decrypted_resp = json.loads(decrypted_resp)
    return decrypted_resp


# validate_vpa("9503182221@icici")

# create_daily_mandate(None, "01.00")

# DAILY MANDATE:
mandate_ref_no = "NAMT66TESPROD8YUAT989DNAMYAP2690591"
txn_no = "202308112029553f8fcefcd2e24260b4"
seqno = "2"
amount = "10.00"


# ASPRESENTED MANDATE
# mandate_ref_no = "MAAT66TESTP478YUAT989MAND1000054924"
# txn_no = "20230811223844b4cd9262f3614a5aa6"
# seqno = "5"
# amount = "01.00"
"""
transactions
txn_id = "2023081123052901aeb23dab3c4788a1" :: FAILED
{'status': 'INITIATED', 'statusdesc': 'Mandate Execution initiated to NPCI', 'executionrefno': 'TO122927', 'cp_mandate_ref_no': 'MAAT66TESTP478YUAT989MAND1000054924', 'bankrrn': '322361923490', 'trxnno': '2023081123052901aeb23dab3c4788a1', 'siptrxnno': ''}
"""
# mandate_ref_no = "MAAT66TESTP478YUAT989MAND1000056339"
# txn_no = "20230821123015f7e0a0a35a2c44ab8e"
# seqno = "3"
# amount = "01.00"


# check_mandate_status(mandate_ref_no="NAMT66TESPROD8YUAT989DNAMYAP2812358", txn_no="20230908105543acf2b5772c4e42a3b4")


# notify_user_about_next_debit(mandate_ref_no, "01.00")

# execute_mandate(mandate_ref_no, amount, seqno)

# revoke_mandate(mandate_ref_no)

# check_transaction_status(
#     "NAMT66TESPROD8YUAT989DNAMYAP2752969", "20230902182000c549111bdb6d4081ab"
# )
# SUCCESS Transaction
# [{'merchantid': '884663', 'subbillerid': '661608', 'executionrefno': 'TO122959', 'trxnno': '202308132340507ea033a241af4fa4a3', 'amount': '1.00', 'bankrrn': '322562118170', 'cp_mdt_ref_no': 'MAAT66TESTP478YUAT989MAND1000054924', 'trxndate': '2023-08-13 23:40:53', 'trxn_status': 'CAPTURED', 'status_desc': 'Transaction Completed Successfully', 'bank_name': 'HDFC Bank', 'account_no': '50100372427008', 'acc_holder_name': 'Shivam Singhal', 'ifsc': 'HDFC0009228', 'payerpva': '9503182221@paytm'}]
