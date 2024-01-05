from fastapi import APIRouter, Depends, status, Response, Request
from sqlalchemy.orm import Session
from src.db.session import get_db
from src.schema.common import APIResponse
from src.deps.auth import get_current_partner
from src.repositories.users import UserRepository
from src.repositories.payment import MandateRepository
from src.services.payment import UpiAutopayService
from src.schema.payment import DailyMandateRequest
from src.utils.encryptdecrypt import decrypt_response
from src.models.logging import WebhookLog
from src.utils.logging_utils import send_slack_message
from src.config import settings

router = APIRouter()


@router.get("/mandate/active", response_model=APIResponse, tags=["payment"])
async def get_all_active_mandates(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    current_partner=Depends(get_current_partner),
):
    phone_no = request.query_params.get("phone_no", "").strip()
    if phone_no in ["", None]:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "success": False,
            "error": "invalid request, need mandate_id and phone_no",
        }
    user_repo = UserRepository(db)
    user_obj = user_repo.get_user_by_phone_number(phone_no)
    if not user_obj:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"success": False, "error": "invalid user details"}
    user_id = user_obj.id

    mandate_repo = MandateRepository(db=db, user_id=user_id)
    mandates = mandate_repo.get_active_mandates_by_user_id()
    response.status_code = status.HTTP_200_OK
    _resp = {"mandates": []}

    for mandate_obj in mandates:
        resp = {
            "mandate_id": mandate_obj.id,
            "madate_ref": mandate_obj.mandate_ref,
            "status": mandate_obj.status,
            "amount": mandate_obj.amount,
            "start_date": mandate_obj.start_date,
            "attached_bank": mandate_obj.bank,
            "recurrence": mandate_obj.recurrence,
        }
        _resp["mandates"].append(resp)

    return APIResponse(success=True, data=_resp, error="")


@router.post("/mandate/daily", response_model=APIResponse, tags=["payment"])
async def create_daily_mandate(
    response: Response,
    request_data: DailyMandateRequest,
    db: Session = Depends(get_db),
    current_partner=Depends(get_current_partner),
):
    user_repo = UserRepository(db)
    user_obj = user_repo.get_user_by_phone_number(request_data.phone)
    if not user_obj:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"success": False, "error": "invalid user details"}
    user_id = user_obj.id
    resp: APIResponse = UpiAutopayService(
        db, user_id=user_id
    ).setup_upi_autopay_daily_mandate(request_data.amount_rs)

    if resp.error not in [None, ""] or resp.success is False:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return resp
    response.status_code = status.HTTP_200_OK
    return resp


@router.get("/mandate", response_model=APIResponse, tags=["payment"])
async def get_mandate_data(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    current_partner=Depends(get_current_partner),
):
    mandate_id = request.query_params.get("mandate_id", "").strip()
    phone_no = request.query_params.get("phone_no", "").strip()
    if phone_no in ["", None] or mandate_id in ["", None]:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "success": False,
            "error": "invalid request, need mandate_id and phone_no",
        }
    user_repo = UserRepository(db)
    user_obj = user_repo.get_user_by_phone_number(phone_no)
    if not user_obj:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"success": False, "error": "invalid user details"}
    user_id = user_obj.id

    mandate_obj = MandateRepository(db=db, user_id=user_id).get_mandate_by_id(
        mandate_id=mandate_id
    )
    if not mandate_obj:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"success": False, "error": "invalid mandate_id"}

    resp = {
        "mandate_id": mandate_id,
        "madate_ref": mandate_obj.mandate_ref,
        "status": mandate_obj.status,
        "amount": mandate_obj.amount,
        "start_date": mandate_obj.start_date,
        "attached_bank": mandate_obj.bank,
        "recurrence": mandate_obj.recurrence,
    }
    response.status_code = status.HTTP_200_OK
    api_resp = APIResponse(
        success=True, message="fetched mandate details", error="", data=resp
    )
    return api_resp


@router.post("/mandate/response", tags=["payment"])
async def camspay_mandate_webhook(
    request: Request, response: Response, db: Session = Depends(get_db)
):
    req = await request.json()
    is_decrypted = request.query_params.get("is_decrypted", "0").strip()
    if is_decrypted == "1" and settings.ENV == "development":
        decrypted_resp = req
    else:
        res = req["res"]
        decrypted_resp = decrypt_response(res)
    send_slack_message(f"Received webhook: {decrypted_resp}")

    obj = WebhookLog(vendor="camspay", request_data=decrypted_resp)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    try:
        resp: APIResponse = UpiAutopayService(db, user_id=None).update_mandate_status(
            decrypted_resp
        )
    except Exception as e:
        raise
        obj.server_response_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        obj.error = str(e)
        db.add(obj)
        db.commit()
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"success": False, "error": f"internal server error: {e}"}

    obj.server_response_code = 200
    db.add(obj)
    db.commit()
    response.status_code = status.HTTP_200_OK
    return {"success": True, "error": None}


@router.get("/mandate/execute", tags=["payment"])
async def camspay_mandate_execute(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    current_partner=Depends(get_current_partner),
):
    notif_id = int(request.query_params.get("notif_id", "0").strip())
    if notif_id == 0:
        return {"success": False, "error": "notif_id"}
    resp: APIResponse = UpiAutopayService(db, user_id=None).execute_mandate(
        notif_id=notif_id
    )
    response.status_code = status.HTTP_200_OK
    return resp
