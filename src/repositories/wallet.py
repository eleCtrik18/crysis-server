from sqlalchemy import func
from src.models.transaction import Transaction
from src.models.wallet import Wallet
from src.utils.mathutils import truncate_to_4_decimal


class WalletRepository:
    def __init__(self, db) -> None:
        self.db = db

    def create_wallet(self, user_id) -> Wallet:
        wallet = Wallet()
        wallet.user_id = user_id
        with self.db as session:
            try:
                session.add(wallet)
                session.commit()
                session.refresh(wallet)
            except Exception:
                session.rollback()
                raise
        return wallet

    def get_user_wallet(self, user_id) -> dict:
        WalletObj = self.db.query(Wallet).filter(Wallet.user_id == user_id).first()
        if not WalletObj:
            raise Exception("User Wallet not found")
        return {"quantity": truncate_to_4_decimal(WalletObj.qty_g)}
    
    def get_total_invested_value_for_user(self, user_id: str) -> float:
        try:
            total_value = (
                self.db.query(func.sum(Transaction.total_value_rs))
                .filter(
                    Transaction.user_id == user_id,
                    Transaction.txn_status == 'SUCCESS',
                    Transaction.txn_type == 'BUY'
                )
                .scalar() or 0.0
            )
            return total_value
        except Exception as e:
            # Handle exceptions (e.g., log or raise)
            raise
