from pydantic import BaseModel, Field
from typing import Optional

txn_subtype_options = ["COUPON", "CASH", "REFERRAL"]
txn_type_options = ["BUY", "SELL"]
txn_status_options = [
    "SUCCESS",
    "FAILED",
    "REFUNDED",
    "REFUND_INITIATED",
    "IN_PROGRESS",
]
product_name_options = ["GOLD24", "GOLD22", "SILVER"]
platform_options = ["android", "ios", "web", "api"]
version_options = ["Aura 1.0.0", "Moi 1.0.0"]
show_in_app_options = [True, False]


class TransactionRequestSchema(BaseModel):
    amount_rs: float = Field(..., example=1.0)
    price_block_id: int = Field(..., example=1)
    txn_type: str = Field(..., example="buy", options=txn_type_options)
    txn_subtype: str = Field(..., example="COUPON", options=txn_subtype_options)
    product_name: str = Field(..., example="GOLD24", options=product_name_options)
    platform: str = Field(..., example="android", options=platform_options)
    version: str = Field(..., example="Aura 1.0.0", options=version_options)
    attached_coupon_code: Optional[str] = None
    payment_mode: str= Field(..., example="upi")   
    phone: str = Field(..., example="9019019829")
    external_txn_id: str = Field(..., example="some uuid")
