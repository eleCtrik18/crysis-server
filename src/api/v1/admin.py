from fastapi import APIRouter, Depends, status, Response, Request
from sqlalchemy.orm import Session
from src.db.session import get_db
from src.schema.common import APIResponse
from src.deps.auth import get_current_partner
from src.scripts.mandate import execute_mandates, update_mandate_transaction_status
from src.logging import logger


router = APIRouter()


@router.get("/mandate/execute", tags=["mandates"])
def execute_mandate_via_admin(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    current_partner=Depends(get_current_partner),
):
    user_id = request.query_params.get("user_id", "").strip()
    if not user_id:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return APIResponse(success=False, message="Invalid User ID")
    executed = execute_mandates(db=db, logger=logger, user_id=user_id)
    if executed:
        response.status_code = status.HTTP_200_OK
    else:
        response.status_code = status.HTTP_400_BAD_REQUEST


@router.get("/mandate/txn-status", tags=["mandates"])
def fetch_and_update_mandate_transaction_status(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    current_partner=Depends(get_current_partner),
):
    txn_id = request.query_params.get("txn_id", "").strip()
    if not txn_id:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return APIResponse(success=False, message="Invalid txn_id")
    executed = update_mandate_transaction_status(db=db, logger=logger, txn_id=txn_id)
    if executed:
        response.status_code = status.HTTP_200_OK
    else:
        response.status_code = status.HTTP_400_BAD_REQUEST
