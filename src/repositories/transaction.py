from src.models.transaction import Transaction
from src.models.wallet import Wallet
from src.utils.mathutils import truncate_to_4_decimal


class TransactionRepository:
    def __init__(self, db, user_id):
        self.db = db
        self.user_id = user_id

    def process_transaction(self, TransactionObj: Transaction):
        with self.db as session:  # using Unit of Work pattern
            try:
                txn: Transaction = TransactionObj
                txn.user_id = self.user_id

                session.add(txn)
                if TransactionObj.txn_status == "SUCCESS":
                    wallet_obj = (
                        session.query(Wallet)
                        .filter(Wallet.user_id == self.user_id)
                        .with_for_update()
                        .first()
                    )

                    if wallet_obj is None:
                        wallet_obj = Wallet(
                            **{
                                "user_id": self.user_id,
                                "qty_g": truncate_to_4_decimal(TransactionObj.qty_g),
                            }
                        )
                    else:
                        if txn.txn_type == "BUY":
                            wallet_obj.qty_g = truncate_to_4_decimal(
                                TransactionObj.qty_g + wallet_obj.qty_g
                            )
                        else:
                            if wallet_obj.qty_g < TransactionObj.qty_g:
                                raise Exception("Insufficient balance.")
                            else:
                                wallet_obj.qty_g = truncate_to_4_decimal(
                                    wallet_obj.qty_g - TransactionObj.qty_g
                                )

                    session.add(wallet_obj)
                session.commit()
                session.refresh(txn)
                return txn
            except Exception:
                session.rollback()
                raise

    def get_transactions(self, limit: int = 100, offset: int = 0):
        with self.db as session:
            try:
                transactions = (
                    session.query(Transaction)
                    .filter(Transaction.user_id == self.user_id)
                    .order_by(Transaction.created_at.desc())
                    .limit(limit)
                    .offset(offset)
                    .all()
                )
                return transactions
            except Exception:
                session.rollback()
                raise

    def get_transaction(self, txn_id: int):
        with self.db as session:
            try:
                transaction = (
                    session.query(Transaction).filter(Transaction.id == txn_id).first()
                )
                return transaction
            except Exception:
                raise

    def get_transaction_by_external_id(self, ext_transaction_id: str):
        with self.db as session:
            try:
                transaction = (
                    session.query(Transaction)
                    .filter(
                        Transaction.external_txn_id == ext_transaction_id,
                    )
                    .first()
                )
                return transaction
            except Exception:
                raise

    def attach_invoice(self, TransactionObj: Transaction, invoice_id):
        with self.db as session:
            try:
                TransactionObj.invoice_id = invoice_id
                session.add(TransactionObj)
                session.commit()
                session.refresh(TransactionObj)
                return TransactionObj
            except Exception:
                session.rollback()
                raise

    def transaction_object(self) -> Transaction:
        return Transaction()
