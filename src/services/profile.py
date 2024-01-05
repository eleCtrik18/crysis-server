from src.schema.common import APIResponse
from src.schema.profile import UpdateUserProfileRequest, PanVerifyRequest
from src.repositories.users import UserRepository
from src.repositories.wallet import WalletRepository
from src.repositories.kyc import KycRepository
from src.external.idfy import get_request_idfy, verify_pan_idfy
from uuid import uuid4
from datetime import datetime
from src.logging import logger
import time


class UserProfile:
    def __init__(self, db, user_obj) -> None:
        self.db = db
        self.user_id = user_obj.id

    def get_user_profile(
        self,
    ):
        try:
            userDetails = UserRepository(self.db).get_user_profile(self.user_id)
            return APIResponse(
                success=True, message="User Details fetched", data={"user": userDetails}
            )
        except Exception as e:
            return APIResponse(success=False, error=str(e))

    def update_profile(self, user_data: UpdateUserProfileRequest):
        try:
            UserRepository(self.db).update_user_profile(self.user_id, user_data.dict())
            return APIResponse(success=True, message="Profile updated successfully.")
        except Exception as e:
            return APIResponse(success=False, error=str(e))


    def verify_pan(self, request_data: PanVerifyRequest):
        try:
            user_kyc_status = UserRepository(self.db).get_kyc_status(self.user_id)
            check_pan = ""
            if user_kyc_status["is_kyc_verified"]:
                return APIResponse(success=False, message="Kyc already verified")
            pan_number = request_data.pan.strip().lower()
            dob_provided = request_data.dob
            logger.info(f"Verification request of Pan number {pan_number} for user {self.user_id}")
            check_kyc = KycRepository(self.db).get_kyc_details(pan_number)
            if check_kyc:
                check_user = UserRepository(self.db).get_kyc_status(check_kyc.user_id)
                if check_user and check_user["is_kyc_verified"]:
                    logger.info(f"Pan number {pan_number} already verified for user {check_kyc.user_id}")
                    return APIResponse(
                        success=False,
                        message="The pan provided already exist in our system, please provide another to continue",
                    )
            if (
                check_kyc
                and check_kyc.kyc_request_id
                and check_kyc.user_id == self.user_id
            ):
                logger.info(f"Existing request id {check_kyc.kyc_request_id} for Pan number {pan_number} found")
                check_pan = get_request_idfy(check_kyc.kyc_request_id)
            else:
                id = str(uuid4())
                req_id = verify_pan_idfy(pan_number, id)
                logger.info(f"New req id {req_id} for pan {pan_number} generated")
                KycRepository(self.db).create_kyc_pan(self.user_id, req_id, pan_number)
                check_pan = get_request_idfy(req_id)
                # TODO REMOVE TIMEOUT
                time.sleep(5)
                if check_pan and check_pan["status"] == "in_progress":
                    logger.info(f"New Pan fetched Data is in progress, retrying: {pan_number}")
                    check_pan = get_request_idfy(req_id)

            if check_pan and check_pan.get("result", False):
                KycRepository(self.db).update_kyc_data(
                    check_pan["result"], self.user_id
                )
            if check_pan and check_pan["status"] == "failed":
                return APIResponse(
                    success=False,
                    message="The pan number provided could not be verified. Please try with different pan number",
                )

            if check_pan and check_pan["status"] == "in_progress":
                return APIResponse(
                    success=False,
                    message="This is taking unusually long, please try again later with same pan number",
                )

            status = check_pan["result"]["source_output"]
            if status:
                parsed_date = datetime.strptime(dob_provided, "%d-%m-%Y")
                formatted_date = datetime.strftime(parsed_date, "%Y-%m-%d")
                dob_pan = status["dob"]
                if dob_pan == formatted_date:
                    UserRepository(self.db).update_kyc_status(self.user_id)
                    # TODO update name according to pan
                    UserRepository(self.db).update_profile_wrt_kyc(
                        self.user_id, status["full_name_split"],dob_provided
                    )
                    KycRepository(self.db).update_pan(pan_number, self.user_id)
                    return APIResponse(
                        success=True, message="PAN verified successfully"
                    )
                else:
                    return APIResponse(
                        success=False,
                        message="Date of birth provided does not match,PAN card",
                    )

        except Exception as e:
            return APIResponse(success=False, message=str(e))


class PartnerUserProfile:
    def __init__(self, db, partner_obj) -> None:
        self.db = db
        self.partner_obj = partner_obj

    def create_new_user(self, user_data):
        user_repo = UserRepository(self.db)
        # check if user already exists
        user = user_repo.get_user_by_phone_number(user_data.phone_number)
        if not user:
            # create user
            user_id = user_repo.create_user_w_data(
                user_data.dict(), self.partner_obj.id
            )
            WalletRepository(self.db).create_wallet(user_id)
            return APIResponse(
                success=True,
                message="User created successfully.",
                data={"user_id": user_id},
            )

        return APIResponse(success=False, error="User already exists.")
