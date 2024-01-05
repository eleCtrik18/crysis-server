from src.models.invoice import Invoice
from datetime import datetime


class InvoiceRepository:
    def __init__(self, db, user_id) -> None:
        self.db = db
        self.user_id = user_id

    def put_invoice(self, download_url):
        invoice = Invoice()
        invoice.download_url = download_url
        invoice.user_id = self.user_id
        with self.db as session:
            try:
                session.add(invoice)
                session.commit()
                session.refresh(invoice)
                return invoice.id
            except Exception:
                session.rollback()
                raise

    def get_invoice(self, invoice_id):
        with self.db as session:
            try:
                invoice = (
                    session.query(Invoice).filter(Invoice.id == invoice_id).first()
                )
                invoice.last_downloaded = datetime.now()
                session.add(invoice)
                session.commit()
                session.refresh(invoice)
                return {"downloadLink": invoice.download_url}
            except Exception:
                session.rollback()
                raise Exception("No invoice Found")
