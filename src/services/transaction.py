from src.repositories.transaction import TransactionRepository
from src.schema.transaction import TransactionRequestSchema
from src.schema.common import APIResponse
from src.repositories.prices import Gold24PriceRepository
from src.services.invoice import Invoice
from src.repositories.users import UserRepository
from uuid import uuid4
from src.constants.common import GST
import math


class TransactionService:
    def __init__(self, db, user_id) -> None:
        self.db = db
        self.user_id = user_id

    @staticmethod
    def calculate_transaction_qty(
        txn_type: str, rate_per_g_wo_gst: float, amount_rs: float
    ):
        qty_g = math.floor((amount_rs / rate_per_g_wo_gst) * 10000) / 10000
        if txn_type == "BUY":
            included_gst = round(amount_rs * (GST / 100), 2)

            obj = {
                "rate_per_g_wo_gst": rate_per_g_wo_gst,
                "gst_rs": included_gst,
                "total_value_rs": round(amount_rs, 2),
                "value_wo_gst_rs": round(amount_rs - included_gst, 2),
                "qty_g": qty_g,
            }
        else:
            obj = {
                "rate_per_g_wo_gst": rate_per_g_wo_gst,
                "gst_rs": 0,
                "total_value_rs": round(amount_rs, 2),
                "value_wo_gst_rs": round(amount_rs, 2),
                "qty_g": qty_g,
            }
        return obj

    @staticmethod
    def calulate_discount(
        txn_type: str, total_value_rs: float, attached_coupon_code=None
    ):
        if attached_coupon_code is None:
            return 0
        disc_perc_map = {"TESTAURACOUPON": 3}
        if txn_type == "BUY":
            # coupon = CouponRepository(self.db).get_coupon(attached_coupon_code)
            # if coupon is None:
            #     raise Exception("Coupon not found")
            # if coupon.is_valid is False:
            #     raise Exception("Coupon is not valid")
            discount_rs = round(
                total_value_rs * disc_perc_map.get(attached_coupon_code, 0) / 100, 2
            )
        else:
            discount_rs = 0
        return discount_rs

    def generate_unique_transaction_id(self, user_id: int):
        return str(user_id) + "_" + (str(uuid4())[0:8]).upper()

    def process_failed_transaction(
        self, transaction_obj, price_obj, uuid, status, message=None
    ):
        txn_repo = TransactionRepository(self.db, self.user_id)

        txn_obj = txn_repo.transaction_object()

        data = {
            **transaction_obj.dict(),
            **price_obj,
            "uuid": uuid,
            "txn_status": status,
        }

        for key in data:
            if hasattr(txn_obj, key):
                setattr(txn_obj, key, data[key])

        txn = txn_repo.process_transaction(txn_obj)
        return txn

    def process_success_transaction(
        self, transaction_obj: TransactionRequestSchema
    ) -> APIResponse:
        """
        #TODO:
            1. Add checks on qty which can be bought/sold
            2. Integrate coupon code
            3. Integrate referral code
        """
        resp = APIResponse(success=False, message="Failed to process transaction")
        uuid = self.generate_unique_transaction_id(self.user_id)
        price_repo = Gold24PriceRepository(self.db)
        price_valid = price_repo.is_block_id_valid(transaction_obj.price_block_id)
        txn_repo = TransactionRepository(self.db, self.user_id)

        try:
            if transaction_obj.product_name == "GOLD24":
                if transaction_obj.txn_type == "BUY":
                    rate_per_g_wo_gst = price_repo.get_buy_price_by_id(
                        block_id=transaction_obj.price_block_id
                    )
                else:
                    rate_per_g_wo_gst = price_repo.get_sell_price_by_id(
                        block_id=transaction_obj.price_block_id
                    )
                if not rate_per_g_wo_gst:
                    raise Exception("Price block not found/expired")
            else:
                raise Exception("Product not found")

            prices_obj = self.calculate_transaction_qty(
                txn_type=transaction_obj.txn_type,
                rate_per_g_wo_gst=rate_per_g_wo_gst,
                amount_rs=transaction_obj.amount_rs,
            )
            prices_obj["discount_rs"] = self.calulate_discount(
                txn_type=transaction_obj.txn_type,
                total_value_rs=prices_obj["total_value_rs"],
                attached_coupon_code=transaction_obj.attached_coupon_code,
            )

            if not price_valid:
                txn = self.process_failed_transaction(
                    transaction_obj,
                    prices_obj,
                    uuid,
                    status="FAILED",
                    message="Price block not found/expired",
                )
                resp.success = False
                resp.message = "Transaction Failed, Price expired."
                resp.data = txn.__dict__
                return resp

            txn_obj = txn_repo.transaction_object()

            data = {
                **transaction_obj.dict(),
                **prices_obj,
                "uuid": uuid,
                "txn_status": "SUCCESS",
            }

            for key in data:
                if hasattr(txn_obj, key):
                    setattr(txn_obj, key, data[key])

            txn = txn_repo.process_transaction(txn_obj)
            resp.success = True
            resp.message = "Transaction processed successfully"
            self.attach_invoice_to_txn(txn_id=txn.id)  # background task
            resp.data = txn.__dict__
        except Exception as e:
            resp.success = False
            resp.message = "Failed to process transaction"
            resp.error = str(e)
        return resp

    # this will be a background task
    def attach_invoice_to_txn(self, txn_id):
        txn_repo = TransactionRepository(self.db, self.user_id)
        txn_obj = txn_repo.get_transaction(txn_id)
        user_data = UserRepository(self.db).get_user_profile(self.user_id)
        if txn_obj.txn_type == "BUY":
            gst = txn_obj.gst_rs
        else:
            gst = "NA"
        invoice_data = {
            "date": txn_obj.created_at.date(),
            "user_name": user_data["first_name"].title()
            + " "
            + user_data["last_name"].title(),
            "user_id": self.user_id,
            "hsn": txn_obj.txn_type,
            "qty": txn_obj.qty_g,
            "price": txn_obj.rate_per_g_wo_gst,
            "gst": gst,
            "amount_w_gst": txn_obj.total_value_rs,
            "amount_wo_gst": txn_obj.value_wo_gst_rs,
            "txn_id": txn_obj.uuid,
            "payment_mode": txn_obj.payment_mode,
        }

        invoice_id = Invoice(self.db, self.user_id).generate(invoice_data)
        txn_repo.attach_invoice(txn_obj, invoice_id=invoice_id)
