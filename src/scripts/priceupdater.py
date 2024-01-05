from src.external.surabhi import get_latest_gold_price
from src.models.prices import Gold24Price
from src.constants.common import GOLD24_BUY_SPREAD_PERC, GOLD24_SELL_SPREAD_PERC, GST
from src.logging import logger as external_logger


def update_gold_price(db, logger=None):
    if not logger:
        logger = external_logger
    try:
        latest_gold_price = get_latest_gold_price()
        aura_buy_price = round(
            latest_gold_price["gold_24_carat_wo_gst"]
            * (1 + GOLD24_BUY_SPREAD_PERC / 100),
            2,
        )

        aura_sell_price = round(
            latest_gold_price["gold_24_carat_wo_gst"]
            * (1 - GOLD24_SELL_SPREAD_PERC / 100),
            2,
        )
        applied_gst = round((GST / 100) * aura_buy_price, 2)

        data = {
            "src_price_w_gst": latest_gold_price["gold_24_carat_w_gst"],
            "src_price_wo_gst": latest_gold_price["gold_24_carat_wo_gst"],
            "product_id": latest_gold_price["product_id"],
            "source": "surabi",
            "product_name": latest_gold_price["product_name"],
            "price_w_gst": aura_buy_price + applied_gst,
            "price_wo_gst": aura_buy_price,
            "applied_gst": applied_gst,
            "aura_buy_price": aura_buy_price,
            "aura_sell_price": aura_sell_price,
        }
    except Exception as e:
        if logger:
            logger.error(
                f"Error while fetching gold price from surabi, updating with last fetched: {e}"
            )
        last_price = (
            db.query(Gold24Price).order_by(Gold24Price.created_at.desc()).first()
        )
        if last_price:
            latest_gold_price = last_price.__dict__
            data = {
                "src_price_w_gst": latest_gold_price["src_price_w_gst"],
                "src_price_wo_gst": latest_gold_price["src_price_wo_gst"],
                "product_id": latest_gold_price["product_id"],
                "source": "surabi",
                "product_name": latest_gold_price["product_name"],
                "price_w_gst": latest_gold_price["price_w_gst"],
                "price_wo_gst": latest_gold_price["price_wo_gst"],
                "applied_gst": latest_gold_price["applied_gst"],
                "aura_buy_price": latest_gold_price["aura_buy_price"],
                "aura_sell_price": latest_gold_price["aura_sell_price"],
            }
        else:
            raise Exception("No gold price found in DB")

    gold_price_rec = Gold24Price(**data)
    if logger:
        logger.info(f"Adding new gold price record: {data}")
    db.add(gold_price_rec)
    db.commit()
