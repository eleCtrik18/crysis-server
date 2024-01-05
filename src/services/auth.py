from src.external.cm import send_otp_via_cm
from src.schema.auth import SendOTPRequest, VerifyOTPRequest, PartnerAuthRequest
from src.schema.common import APIResponse
import random
from uuid import uuid4
from src.utils.auth import create_access_token, create_refresh_token
from src.repositories.users import UserRepository, PartnerRepository
from src.repositories.wallet import WalletRepository
from src.config import settings


class AuthenticationService:
    def __init__(self) -> None:
        pass

    def is_test_number(self, phone_number):
        return phone_number.startswith("0000")

    async def send_otp(self, request_data: SendOTPRequest, cache) -> APIResponse:
        otp = random.randint(111111, 999999)
        request_id = str(uuid4())
        try:
            if self.is_test_number(request_data.phone):
                otp = 909090
                sent = True
            else:
                sent = send_otp_via_cm(
                    phone_number=request_data.phone, otp=otp.__str__()
                )
            if sent:
                # cache.set(request_id, otp, ex=60 * 5)  # use this for Aura 2.0 app
                cache.set(request_data.phone, str(otp), ex=60 * 5)  # 5 minutes
        except Exception as e:
            return APIResponse(
                success=False,
                message="Failed to send OTP, please try again in some time",
                error=str(e),
            )
        request_data.dict()["requestId"] = request_id
        return APIResponse(
            success=True, message="OTP sent successfully", data=request_data.dict()
        )

    async def verify_otp(self, request_data: VerifyOTPRequest, cache, db):
        otp_b = cache.get(request_data.phone)
        if not otp_b:
            return APIResponse(success=False, message="OTP expired. Please resend OTP")

        otp = str(otp_b, encoding="ascii", errors="ignore")
        if otp == request_data.otp:
            access_token = create_access_token(request_data.phone)
            refresh_token = create_refresh_token(request_data.phone)

            # get user instance to check first time login
            user = UserRepository(db).get_user_by_phone_number(request_data.phone)
            if not user and request_data.source != "partner":
                # create user
                user = UserRepository(db).create_first_login_user(
                    request_data.phone, access_token
                )
                WalletRepository(db).create_wallet(user.id)

            cache.delete(request_data.phone)

            return APIResponse(
                success=True,
                message="OTP verified successfully",
                data={"access_token": access_token, "refresh_token": refresh_token},
            )
        return APIResponse(success=False, message="Invalid OTP/ OTP expired")

    async def auth_partner(self, request_data: PartnerAuthRequest, db):
        partner_obj = PartnerRepository(db).get_partner_by_username(
            request_data.username
        )
        if not partner_obj:
            return APIResponse(success=False, error="Invalid username")

        if partner_obj.password != request_data.password:  # type: ignore
            return APIResponse(success=False, error="Invalid password")

        if partner_obj.is_active is False:
            return APIResponse(success=False, error="Partner is not active")

        if partner_obj.api_key != request_data.api_key:
            return APIResponse(success=False, error="Invalid api key")

        access_token = create_access_token(
            partner_obj.username, secret_key=settings.PARTNER_JWT_SECRET_KEY
        )

        return APIResponse(
            success=True,
            message="Partner authenticated successfully",
            data={"access_token": access_token},
        )
