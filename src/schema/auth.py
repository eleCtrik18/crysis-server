from pydantic import BaseModel, Field, validator
from typing import Optional


class SendOTPRequest(BaseModel):
    countryCode: str = Field(..., example="91")
    phone: str = Field(..., example="1234567890")

    @validator("phone")
    def phone_must_be_10_digits(cls, v):
        if len(str(v)) != 10:
            raise ValueError("Phone number must be 10 digits")
        return v

    @validator("phone")
    def phone_must_starts_with_6_7_8_9(cls, v):
        if str(v)[0] not in ["0", "6", "7", "8", "9"]:
            raise ValueError("Phone number must starts with 6, 7, 8 or 9")
        return v

    @validator("countryCode")
    def country_code_must_be_2_digits(cls, v):
        if len(str(v)) != 2:
            raise ValueError("Country code must be 2 digits")
        return v

    @validator("countryCode")
    def country_code_supported(cls, v):
        if str(v) != "91":
            raise ValueError("Only country code 91 is supported (India)")
        return v

    class Config:
        schema_extra = {"example": {"countryCode": "91", "phone": "9503182221"}}


class VerifyOTPRequest(BaseModel):
    requestId: Optional[str] = None
    otp: str = Field(..., example="123456")
    phone: str = Field(..., example="1234567890")
    source: str = Field(None, example="1234567890")

    @validator("otp")
    def otp_must_be_6_digits(cls, v):
        if len(str(v)) != 6:
            raise ValueError("OTP must be 6 digits")
        return v


class PartnerAuthRequest(BaseModel):
    username: str = Field(..., example="username")
    password: str = Field(..., example="password")
    api_key: str = Field(..., example="api_key")
