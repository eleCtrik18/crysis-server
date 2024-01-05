from sqlalchemy import Column
from sqlalchemy.orm import subqueryload, joinedload
from src.models.users import User, Partner


class UserRepository:
    def __init__(self, db) -> None:
        self.db = db

    def get_user_by_phone_number(self, phone) -> User:
        return self.db.query(User).filter(User.phone_number == phone).first()

    def create_first_login_user(self, phone_number, jwt_token) -> User:
        user = User()
        user.phone_number = phone_number
        user.jwt_token = jwt_token
        user.first_name = phone_number
        user.email_verified = False
        with self.db as session:
            try:
                session.add(user)
                session.commit()
                session.refresh(user)
                return user
            except Exception:
                session.rollback()
                raise

    def update_user_profile(self, user_id, user_data) -> User:
        UserObj = self.db.query(User).filter(User.id == user_id).first()
        if not UserObj:
            raise Exception("User not found")
        if user_data.get("first_name"):
            UserObj.first_name = user_data.get("first_name")
        if user_data.get("last_name"):
            UserObj.last_name = user_data.get("last_name")
        if user_data.get("email"):
            UserObj.email = user_data.get("email")
        if user_data.get("dob"):
            UserObj.dob = user_data.get("dob")

        # if user_data.get("first_name", "") or user_data.get("last_name", ""):
        #     UserObj.display_name = (
        #         user_data.get("first_name", "") + " " + user_data.get("last_name", "")
        #     )

        with self.db as session:
            try:
                session.add(UserObj)
                session.commit()
                session.refresh(UserObj)
                return UserObj
            except Exception:
                session.rollback()
                raise

    def get_user_profile(self, user_id):
        UserObj = self.db.query(User).filter(User.id == user_id).first()
        if not UserObj:
            raise Exception("User not found")
        return {
            "first_name": UserObj.first_name,
            "email": UserObj.email or "",
            "phone_number": UserObj.phone_number,
            "last_name": UserObj.last_name or "",
            "display_name": UserObj.first_name + (UserObj.last_name or ""),
        }

    def create_user_w_data(self, user_data, partner_id) -> Column[int]:
        user = User()
        user.phone_number = user_data.get("phone_number")
        user.first_name = user_data.get("first_name")
        user.last_name = user_data.get("last_name")
        user.email = user_data.get("email")
        user.country_code = user_data.get("country_code")
        user.partner_id = partner_id
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user.id

    def get_kyc_status(self, user_id):
        UserObj = self.db.query(User).filter(User.id == user_id).first()
        if not UserObj:
            raise Exception("User not found")
        return {
            "is_kyc_verified": UserObj.kyc_verified,
        }

    def update_kyc_status(self, user_id):
        UserObj = self.db.query(User).filter(User.id == user_id).first()
        if not UserObj:
            raise Exception("User not found")
        UserObj.kyc_verified = True
        with self.db as session:
            try:
                session.add(UserObj)
                session.commit()
                session.refresh(UserObj)
            except Exception:
                session.rollback()
                raise

    def update_profile_wrt_kyc(self, user_id, full_name, dob):
        UserObj = self.db.query(User).filter(User.id == user_id).first()
        if not UserObj:
            raise
        UserObj.first_name = full_name[0]
        UserObj.middle_name = full_name[1]
        UserObj.last_name = full_name[2]
        UserObj.dob = dob
        with self.db as session:
            try:
                session.add(UserObj)
                session.commit()
                session.refresh(UserObj)
            except Exception:
                session.rollback()
                raise

    
class PartnerRepository:
    def __init__(self, db):
        self.db = db

    def get_partner_by_username(self, username) -> Partner:
        return self.db.query(Partner).filter(Partner.username == username).first()
