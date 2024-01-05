from fastapi import APIRouter, Depends, status, Response
from sqlalchemy.orm import Session
from src.db.session import get_db
from src.schema.common import APIResponse
from src.schema.auth import PartnerAuthRequest
from src.services.auth import AuthenticationService
from src.schema.profile import PartnerCreateUserRequest
from src.deps.auth import get_current_partner
from src.services.profile import PartnerUserProfile

router = APIRouter()


@router.post("/auth", response_model=APIResponse, tags=["partner"])
async def authenticate_partner(
    response: Response,
    request_data: PartnerAuthRequest,
    db: Session = Depends(get_db),
):
    """
    Authenticate partner
    """
    resp = await AuthenticationService().auth_partner(request_data, db)
    response.status_code = status.HTTP_200_OK
    if not resp.success:
        response.status_code = status.HTTP_400_BAD_REQUEST
    return resp


@router.post("/user", response_model=APIResponse, tags=["partner"])
def create_new_user_via_partner(
    response: Response,
    request_data: PartnerCreateUserRequest,
    db: Session = Depends(get_db),
    current_partner=Depends(get_current_partner),
):
    created = PartnerUserProfile(db, current_partner).create_new_user(request_data)
    if created.success:
        response.status_code = status.HTTP_200_OK
    else:
        response.status_code = status.HTTP_400_BAD_REQUEST
    return created
