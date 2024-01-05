from src.models.prices import Gold24Price
from datetime import datetime, timedelta, timezone
import pytz
from src.utils.mathutils import format_amt, format_qty


class Gold24PriceRepository:
    def __init__(self, db):
        self.db = db

    def get_latest_price(self) -> Gold24Price:
        return self.db.query(Gold24Price).order_by(Gold24Price.id.desc()).first()

    def get_price_by_id(self, block_id: int) -> Gold24Price:
        return self.db.query(Gold24Price).filter(Gold24Price.id == block_id).first()

    def get_buy_price_by_id(self, block_id: int) -> float:
        return (
            self.db.query(Gold24Price)
            .filter(Gold24Price.id == block_id)
            .first()
            .aura_buy_price
        )

    def get_sell_price_by_id(self, block_id: int) -> float:
        return (
            self.db.query(Gold24Price)
            .filter(Gold24Price.id == block_id)
            .first()
            .aura_sell_price
        )

    def is_block_id_valid(self, block_id: int) -> bool:
        block_creation_obj = (
            self.db.query(Gold24Price).filter(Gold24Price.id == block_id).first()
        )
        if not block_creation_obj:
            return False
        block_creation_time = block_creation_obj.created_at

        current_datetime = datetime.now().astimezone(timezone.utc)

        if block_creation_time.tzinfo.__str__() == "UTC+05:30":
            block_creation_time = block_creation_time.replace(tzinfo=pytz.UTC)

        if current_datetime - block_creation_time > timedelta(minutes=15):
            return False
        return True

    def get_conversions(
        self, block_id: int, price_type: str, input_val: float, input_type: str
    ):
        """
        To convert gold qty to amt inc gst:
        lets say qty comes as : 1.5 grams, price is 5867.11
        first multiply 1 gm with price_wo_gst  8800.665
        add GST: 3% by amount to it 9064.68



        Now user enters the amount, lets say 9064.68
        deduct the GST(2.912%) first : 8800.71
        divide it by price_wo_gst: 1.5

        """
        block_obj = self.get_price_by_id(block_id)
        resp = {
            "block_id": block_id,
            "price_type": price_type,
            "input_val": input_val,
            "input_type": input_type,
            "output_val": None,
            "gst": 0,
        }
        if price_type == "buy":
            if input_type == "qty":
                amt_wo_gst = input_val * block_obj.aura_buy_price
                resp["output_val"] = format_amt(
                    amt_wo_gst + (amt_wo_gst * 0.03)
                )  # GST is added
                resp["gst"] = format_amt(amt_wo_gst * 0.03)
            elif input_type == "amt":
                gst_removed_amt = input_val - (input_val * 0.0291)
                resp["output_val"] = format_qty(
                    gst_removed_amt / block_obj.aura_buy_price
                )
                resp["gst"] = format_amt(input_val * 0.0291)
        elif price_type == "sell":
            if input_type == "qty":
                resp["output_val"] = format_amt(input_val * block_obj.aura_sell_price)
            elif input_type == "amt":
                resp["output_val"] = format_qty(input_val / block_obj.aura_sell_price)
        else:
            raise Exception("Invalid price type")
        return resp
