from src.services.transaction import TransactionService
from fastapi import APIRouter, Depends, status, Response, Request
from sqlalchemy.orm import Session
from src.db.session import get_db
from src.schema.common import APIResponse
from src.schema.transaction import TransactionRequestSchema
from src.services.invoice import Invoice
from src.deps.auth import get_current_partner
from src.repositories.users import UserRepository


router = APIRouter()


@router.post("/new", response_model=APIResponse, tags=["transaction"])
async def create_transaction(
    response: Response,
    request_data: TransactionRequestSchema,
    db: Session = Depends(get_db),
    current_partner=Depends(get_current_partner),
):
    user_repo = UserRepository(db)
    user_obj = user_repo.get_user_by_phone_number(request_data.phone)
    if not user_obj:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"success": False, "error": "invalid user details"}
    user_id = user_obj.id
    resp: APIResponse = TransactionService(
        db, user_id=user_id
    ).process_success_transaction(request_data)

    if resp.error not in [None, ""] or resp.success is False:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return resp
    response.status_code = status.HTTP_200_OK
    return resp


@router.get("/invoice", response_model=APIResponse)
async def get_invoice(
    response: Response,
    request: Request,
    db=Depends(get_db),
    current_partner=Depends(get_current_partner),
):
    ext_txn_id = request.query_params.get("txn_id")
    if ext_txn_id is None:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return APIResponse(success=False, message="Invalid Invoice ID or User ID")
    invoice = Invoice(db, None).get_invoice(ext_txn_id)
    if invoice.success:
        response.status_code = status.HTTP_200_OK
    else:
        response.status_code = status.HTTP_400_BAD_REQUEST
    return invoice
