import jinja2
from src.repositories.invoice import InvoiceRepository
from src.utils.pdfutils import html_to_pdf
from src.schema.common import APIResponse
import os
from src.utils.aws import upload_to_s3
from src.repositories.transaction import TransactionRepository


class Invoice:
    def __init__(self, db, user_id):
        self.db = db
        self.user_id = user_id

    def upload_invoice(self, file_name):
        return upload_to_s3(file_name)

    def generate(self, data):
        templateLoader = jinja2.FileSystemLoader(searchpath="./src/templates")
        templateEnv = jinja2.Environment(loader=templateLoader)
        TEMPLATE_FILE = "invoice.html"
        template = templateEnv.get_template(TEMPLATE_FILE)
        outputText = template.render(data)
        file_name = f"{data['txn_id']}"  # update
        html_file_name = f"invoices/{data['txn_id']}.html"
        with open(html_file_name, mode="w", encoding="utf-8") as message:
            message.write(outputText)

        # convert html to pdf
        pdf_file = html_to_pdf(html_file_name, f"{file_name}.pdf")
        os.remove(html_file_name)
        invoice_url = self.upload_invoice(pdf_file)
        if not invoice_url:
            raise Exception("Invoice upload failed")
        os.remove(pdf_file)
        invoice_repo = InvoiceRepository(self.db, self.user_id)
        invoice_id = invoice_repo.put_invoice(invoice_url)
        return invoice_id

    def get_invoice(self, ext_txn_id):
        txn_repo = TransactionRepository(self.db, self.user_id)
        txn_obj = txn_repo.get_transaction_by_external_id(ext_txn_id)
        if not txn_obj:
            return APIResponse(success=False, message="Invalid Transaction id")
        invoice_id = txn_obj.invoice_id
        try:
            invoice = InvoiceRepository(self.db, self.user_id).get_invoice(invoice_id)
            return APIResponse(success=True, message="Invoice Retrieved", data=invoice)
        except Exception as e:
            return APIResponse(success=False, message="No invoice found", error=str(e))
