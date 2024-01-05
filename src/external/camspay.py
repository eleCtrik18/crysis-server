from src.utils.encryptdecrypt import encrypt, decrypt, get_iv, get_secret_key
import json
import requests
from src.utils.payment import (
    generate_transaction_id,
)
from src.utils.datetimeutils import get_ist_date, get_ist_date_plus_x_month
from src.logging import logger
from src.config import Settings
from src.models.logging import VendorApiLog
from src.db.session import get_task_db


CAMSPAY_ID = Settings.CAMSPAY_CREDENTIALS.get("CAMSPAY_ID")
URL_HOST = Settings.CAMSPAY_CREDENTIALS.get("URL_HOST")
MERCHANT_ID = Settings.CAMSPAY_CREDENTIALS.get("MERCHANT_ID")
SUBBILLER_ID = Settings.CAMSPAY_CREDENTIALS.get("SUBBILLER_ID")
AURA_HOST = Settings.AURA_HOST


def make_camspay_request(url, req_data, server_req_id=None, user_id=None):
    logger.info(
        f"camspay req data url: {url}, req_data: {req_data}, server_req_id, {server_req_id}"
        f"user_id: {user_id}"
    )
    secret_key = get_secret_key()
    iv = get_iv()
    encrypted_request = encrypt(json.dumps(req_data), secret_key, iv)
    encrypted_body = {"param": f"{CAMSPAY_ID}.{iv.hex()}.{encrypted_request}"}
    res = requests.post(url=url, data=encrypted_body)
    status_code = res.status_code
    logger.info(f"camspay api {url} response: {res.status_code}")
    res = json.loads(res.text)
    encrypted_resp = res["res"].split(".")
    decrypted_resp = decrypt(encrypted_resp[1], secret_key, encrypted_resp[0])
    decrypted_resp = json.loads(decrypted_resp)
    logger.info(f"camspay url {url} decrypted_resp {decrypted_resp}")
    try:
        obj = VendorApiLog()
        obj.user_id = user_id
        obj.vendor = "camspay"
        obj.encrypted_request_data = encrypted_body
        obj.request_data = req_data
        obj.response_code = status_code
        obj.request_id = server_req_id
        obj.encrypted_response_data = res
        obj.response_data = decrypted_resp
        obj.url = url
        with get_task_db() as db_session:
            db_session.add(obj)
            db_session.commit()
    except Exception as e:
        logger.error(f"camspay url {url} error: {e}")

    return decrypted_resp


def validate_vpa(vpa, user_id):
    url = f"{URL_HOST}/validvpa"
    raw_json = {"vpa": vpa, "merchantid": MERCHANT_ID, "subbillerid": SUBBILLER_ID}
    resp = make_camspay_request(url, raw_json, user_id=user_id)
    # print(resp)
    # add response validator
    return resp


def setup_daily_mandate(amount: str, payer_name, vpa=None, user_id=None):
    url = f"{URL_HOST}/mandatecreate"
    if vpa:
        vpa_details = validate_vpa(vpa=vpa, user_id=user_id)
        if vpa_details["is_autopay_eligible"] != "Y":
            return "Account is not eligible for Autopay"
        payer_name = vpa_details["payer_name"]
    txn_no = generate_transaction_id()
    start_date = get_ist_date()
    end_date = get_ist_date_plus_x_month(x=24)
    req_data = {
        "trxnno": txn_no,
        "amount": str(amount),
        "pattern": "ASPRESENTED",
        "mandatestartdate": start_date,
        "mandateenddate": end_date,
        "merchantid": MERCHANT_ID,
        "subbillerid": SUBBILLER_ID,
        "revokeable": "Y",
        # "payervpa": vpa,
        "payername": payer_name,
        "authorize": "Y",
        "authorizerevoke": "Y",
        "intent": "Y",
        "redirecturl": f"{AURA_HOST}/api/payment/v1/mandate/response",
        # "debiturl": f"{AURA_HOST}/api/payment/v1/mandate/response",
        "mandateexpirytime": 5,
    }
    resp = make_camspay_request(url, req_data, user_id=user_id)
    """
    {'cp_mdt_ref_no': 'MAAT66TESTP478YUAT989MAND1000054922', 'status': 'PENDING', 
    'deeplink': 'upi://mandate?pa=cpupisi@indus&pn=TestCams&mn=TESTMANDATE&tid=202308112022488cd8330ce4e54ad794&tr=MAAT66TESTP478YUAT989MAND1000054922&validitystart=11082023&validityend=11092023&am=02.00&amrule=MAX&recur=ASPRESENTED&cu=INR&mc=6211&tn=Subscription&purpose=14&rev=Y&mode=01&sign=MGQCMBt8tD5FRyNMtzDKJPaK03iBvZFaCvOq0NtQsJw9BQV/t2T+KLdQ30RFbsSB9jMB0wIwDV7ibvDOdhdNsw0CFhq8+uznjj28/EzhD1AS9m+LpO0OblXsx94jlcX5bmoFHo6B&orgid=159234', 'msg': 'Mandate Intent URL generated successfully', 'errCode': '1111', 'errDesc': 'Mandate Intent URL generated successfully', 'res': {'trxnno': '202308112022488cd8330ce4e54ad794', 'amount': '02.00', 'pattern': 'DAILY', 'mandatestartdate': '11082023', 'mandateenddate': '11092023', 'merchantid': '884663', 'subbillerid': '661608', 'revokeable': 'Y', 'payervpa': '9503182221@paytm', 'payername': 'Shivam Singhal', 'authorize': 'Y', 'authorizerevoke': 'Y', 'intent': 'Y', 'redirecturl': 'https://api.auragold.in/mandatesuccess', 'autoExecute': 'Y', 'instaauth': 'N'}}
    """
    _resp = {
        "mandate_ref": resp["cp_mdt_ref_no"],
        "txn_no": txn_no,
        "deeplink": resp["deeplink"],
        "msg": resp["msg"],
        "status": resp["status"],
        "start_date": start_date,
        "end_date": end_date,
        "meta_data": resp,
    }
    return _resp


def send_mandate_notification(mandate_ref_no, amount, debit_date, user_id):
    url = f"{URL_HOST}/mandatePreDebit"
    req_data = {
        "refno": mandate_ref_no,
        "amount": str(amount),
        "nextRecurDate": debit_date,
    }
    resp = make_camspay_request(url, req_data=req_data, user_id=user_id)
    """
    {'bank_error_code': '00', 'bank_error_desc': 'APPROVED OR COMPLETED SUCCESSFULLY', 'bank_res_code': '00', 'bank_res_desc': 'APPROVED OR COMPLETED SUCCESSFULLY', 'status': 'Success', 'statusdesc': 'Request Processed Successfully', 'cp_mandate_ref_no': 'MAAT66TESTP478YUAT989MAND1000054923', 'seqno': 2}    
    """
    _resp = {
        "status": (
            "SENT"
            if resp["status"] == "Success"
            and resp["bank_error_desc"] == "APPROVED OR COMPLETED SUCCESSFULLY"
            else resp["status"]
        ),
        "seq_no": resp.get("seqno"),
        "meta_data": resp,
        "status_desc": resp.get("statusdesc"),
    }
    return _resp


def check_mandate_status(mandate_ref_no, txn_no, user_id):
    url = f"{URL_HOST}/mandatestatus"
    req_data = {
        "trxnno": txn_no,
        "refno": mandate_ref_no,
        "actiontype": "MANDATE_STATUS",
        "merchantid": MERCHANT_ID,
        "subbillerid": SUBBILLER_ID,
    }
    resp = make_camspay_request(url, req_data=req_data, user_id=user_id)
    """
    {'merchantid': '884663', 'subbillerid': '661608', 'cp_mdt_ref_no': 'MAAT66TESTP478YUAT989MAND1000054923', 'umn': 'PTM50b5b5d154866932ad90bfe70f3c6@paytm', 'trxnno': '202308112029553f8fcefcd2e24260b4', 'amount': '2.00', 'status': 'ACTIVE', 'statusdesc': '00-APPROVED OR COMPLETED SUCCESSFULLY', 'pattern': 'DAILY'}
    """
    _resp = {
        "status": resp["status"],
        "meta_data": resp,
        "mandate_ref": resp["cp_mdt_ref_no"],
    }
    return _resp


def execute_mandate_at_camspay(mandate_ref_no, amount, seq_no, user_id):
    url = f"{URL_HOST}/mandateExecute"
    req_data = {
        "refno": mandate_ref_no,
        "amount": str(amount),
        "seqno": seq_no,
        "trxnno": generate_transaction_id(),
    }
    resp = make_camspay_request(url, req_data=req_data, user_id=user_id)
    # {
    #     "status": "INITIATED",
    #     "statusdesc": "Mandate Execution initiated to NPCI",
    #     "executionrefno": "TO122927",
    #     "cp_mandate_ref_no": "MAAT66TESTP478YUAT989MAND1000054924",
    #     "bankrrn": "322361923490",
    #     "trxnno": "2023081123052901aeb23dab3c4788a1",
    #     "siptrxnno": "",
    # }
    _resp = {
        "status": resp["status"],
        "execution_ref": resp["executionrefno"],
        "txn_no": resp["trxnno"],
        "bank_rrn": resp["bankrrn"],
        "meta_data": resp,
        "status_desc": resp["statusdesc"],
    }
    return _resp


def revoke_mandate(mandate_ref_no, user_id):
    req_data = {"refno": mandate_ref_no}
    url = f"{URL_HOST}/mandaterevoke"
    resp = make_camspay_request(url=url, req_data=req_data, user_id=user_id)
    print(resp)
    return resp


def check_transaction_status(mandate_ref_no, txn_no, user_id):
    url = f"{URL_HOST}/mandatestatus"
    req_data = {
        "trxnno": txn_no,
        "refno": mandate_ref_no,
        "actiontype": "TRANSACTION_STATUS",
        "merchantid": MERCHANT_ID,
        "subbillerid": SUBBILLER_ID,
    }
    resp = make_camspay_request(url, req_data=req_data, user_id=user_id)
    """
    [{'merchantid': '884663', 'subbillerid': '661608', 'executionrefno': 'TO122927', 'trxnno': '2023081123052901aeb23dab3c4788a1', 'amount': '1.00', 'bankrrn': '322361923490', 'cp_mdt_ref_no': 'MAAT66TESTP478YUAT989MAND1000054924', 'trxndate': '2023-08-11 23:05:31', 'trxn_status': 'FAILED', 'status_desc': 'Address resolution is failed', 'bank_name': 'HDFC Bank', 'account_no': '50100372427008', 'acc_holder_name': 'Shivam Singhal', 'ifsc': 'HDFC0009228', 'payerpva': '9503182221@paytm'}]   
      """
    _resp = {
        "status": resp[0]["trxn_status"],
        "status_desc": resp[0]["status_desc"],
        "meta_data": resp[0],
    }
    return _resp
