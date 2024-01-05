from fastapi import APIRouter, Depends, status, Response, Request
from sqlalchemy.orm import Session
from src.db.session import get_db
from src.schema.common import APIResponse
from src.scripts.priceupdater import update_gold_price
from src.repositories.prices import Gold24PriceRepository
from src.deps.auth import get_current_user


router = APIRouter()


@router.get("/prices", response_model=APIResponse, tags=["data", "prices"])
async def get_price(
    request: Request, response: Response, db: Session = Depends(get_db)
):
    product = request.query_params.get("product")
    if product is None or product == "" or product not in ["24KGOLD"]:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return APIResponse(
            success=False,
            message="Product is required",
        )
    if product == "24KGOLD":
        price = Gold24PriceRepository(db).get_latest_price()
        if price is None:
            response.status_code = status.HTTP_424_FAILED_DEPENDENCY
            return APIResponse(
                success=False,
                message="Price not found",
            )
        response.status_code = status.HTTP_200_OK
        return APIResponse(
            success=True, message="Product is required", data=price.__dict__
        )


@router.get("/cron/update-prices", response_model=APIResponse, tags=["cron", "prices"])
async def update_price(
    request: Request, response: Response, db: Session = Depends(get_db)
):
    product = request.query_params.get("product")
    if product is None or product == "" or product not in ["24KGOLD"]:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return APIResponse(
            success=False,
            message="Product is required",
        )
    if product == "24KGOLD":
        try:
            update_gold_price(db)
        except Exception as e:
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return APIResponse(
                success=False,
                message=str(e),
            )
        response.status_code = status.HTTP_200_OK
        return APIResponse(success=True, message="", data={})


@router.get("/convert", response_model=APIResponse, tags=["prices"])
async def get_converted_price(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    block_id = request.query_params.get("block_id")
    price_type = request.query_params.get("price_type")
    input_val = request.query_params.get("input_val")
    input_type = request.query_params.get("input_type")

    if not block_id or not price_type or not input_val or not input_type:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return APIResponse(
            success=False,
            message="block_id, price_type, input_val, input_type are required",
        )
    resp = Gold24PriceRepository(db).get_conversions(
        block_id=int(block_id),
        price_type=price_type,
        input_val=float(input_val),
        input_type=input_type,
    )
    response.status_code = status.HTTP_200_OK
    return APIResponse(success=True, message="", data=resp)
