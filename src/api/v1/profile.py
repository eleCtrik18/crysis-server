"""
Write APIs related to profile here. 
example: CRUD profile
"""
from fastapi import APIRouter, Depends, status, Response, Request
from sqlalchemy.orm import Session
from src.db.session import get_db
from src.schema.common import APIResponse
from src.schema.profile import UpdateUserProfileRequest, PanVerifyRequest
from src.deps.auth import get_current_user
from src.services.profile import UserProfile

router = APIRouter()


@router.get("/profile", tags=["profile"])
def get_user_profile(
    response: Response,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    user = UserProfile(db, current_user).get_user_profile()
    if user.success:
        response.status_code = status.HTTP_200_OK
    else:
        response.status_code = status.HTTP_400_BAD_REQUEST
    return user


@router.post("/update", response_model=APIResponse, tags=["profile"])
def update_user_profile(
    response: Response,
    request_data: UpdateUserProfileRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    updated = UserProfile(db, current_user).update_profile(request_data)
    if updated.success:
        response.status_code = status.HTTP_200_OK
    else:
        response.status_code = status.HTTP_400_BAD_REQUEST
    return updated


@router.post("/verify-kyc",response_model=APIResponse,tags=["profile"])
def verify_pan(
    response: Response,
    request_data:PanVerifyRequest,
    db:Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    verified = UserProfile(db,current_user).verify_pan(request_data)
    if verified.success:
        response.status_code = status.HTTP_200_OK
    else:
        response.status_code = status.HTTP_400_BAD_REQUEST
    return verified