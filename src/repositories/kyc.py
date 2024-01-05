from src.models.users import UserKycDetail
import json


class KycRepository:
    def __init__(self, db) -> None:
        self.db = db

    def get_user_kyc(self, user_id) -> UserKycDetail:
        return (
            self.db.query(UserKycDetail)
            .filter(UserKycDetail.user_id == user_id)
            .first()
        )

    def get_kyc_details(self, pan):
        return (
            self.db.query(UserKycDetail).filter(UserKycDetail.kyc_number == pan).first()
        )

    def create_kyc_pan(self, user_id, kyc_req_id, pan):
        kyc = UserKycDetail()
        kyc.kyc_request_id = kyc_req_id
        kyc.kyc_number = pan
        kyc.user_id = user_id
        kyc.kyc_verified_by="PAN"
        with self.db as session:
            try:
                session.add(kyc)
                session.commit()
                session.refresh(kyc)
            except Exception:
                raise
        return kyc

    def update_kyc_data(self, data, user_id):
        kyc = self.get_user_kyc(user_id)
        kyc.kyc_data =  data
        with self.db as session:
            try:
                session.add(kyc)
                session.commit()
                session.refresh(kyc)
            except Exception:
                raise
    def update_pan(self,pan,user_id):
        kyc = self.get_user_kyc(user_id)
        kyc.kyc_number = pan
        with self.db as session:
            try:
                session.add(kyc)
                session.commit()
                session.refresh(kyc)
            except Exception:
                raise
