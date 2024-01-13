from fastapi import APIRouter, Request, Depends, Response, status
from sqlalchemy.orm import Session
from src.schema.common import APIResponse
from src.deps.auth import get_current_user
from src.db.session import get_db
from src.services.wallet import WalletService

router = APIRouter()


@router.get("/", tags=["wallet"])
def get_wallet(
    req: Request,
    response: Response,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    wallet_service = WalletService(db, current_user)
    combined_response = wallet_service.get_wallet_with_conversion()

    print(combined_response)

    if combined_response.success:
        response.status_code = status.HTTP_200_OK
    else:
        response.status_code = status.HTTP_400_BAD_REQUEST

    return combined_response
