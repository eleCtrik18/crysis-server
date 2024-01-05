from fastapi import APIRouter, Depends, status, Response
from sqlalchemy.orm import Session
from src.db.session import get_db, get_cache
from src.schema.common import APIResponse
from src.schema.auth import SendOTPRequest, VerifyOTPRequest
from src.services.auth import AuthenticationService

router = APIRouter()


@router.post("/send-otp", response_model=APIResponse, tags=["auth"])
async def send_otp(
    response: Response,
    request_data: SendOTPRequest,
    db: Session = Depends(get_db),
    cache=Depends(get_cache),
):
    """
    Send OTP to the user
    """
    resp = await AuthenticationService().send_otp(request_data, cache)
    response.status_code = status.HTTP_200_OK
    if not resp.success:
        response.status_code = status.HTTP_400_BAD_REQUEST
    return resp


@router.post("/verify-otp", response_model=APIResponse, tags=["auth"])
async def verify_otp(
    response: Response,
    request_data: VerifyOTPRequest,
    db: Session = Depends(get_db),
    cache=Depends(get_cache),
):
    """
    Send OTP to the user
    """
    resp = await AuthenticationService().verify_otp(request_data, cache, db)
    response.status_code = status.HTTP_200_OK
    if not resp.success:
        response.status_code = status.HTTP_400_BAD_REQUEST
    return resp
