from pydantic import BaseModel, Field, validator
from typing import Optional


class UpdateUserProfileRequest(BaseModel):
    first_name: Optional[str] = Field(None, example="John")
    last_name: Optional[str] = Field(None, example="Abraham")
    dob: Optional[str] = Field(None, example="Abraham")
    email: Optional[str] = Field(None, example="Johnny@gmail.com")

    @validator("dob")
    def validate_dob(cls, v):
        if v is not None:
            if len(str(v)) != 10:
                raise ValueError("DOB must be 10 digits")
            if v[2] != "-" or v[5] != "-":
                raise ValueError("DOB must be in DD-MM-YYYY format")
            if int(v[3:5]) > 12 or int(v[3:5]) < 1:
                raise ValueError("Month should be between 1 and 12")
            if int(v[0:2]) > 31 or int(v[0:2]) < 1:
                raise ValueError("Day should be between 1 and 31")
            if int(v[6:]) > 2020 or int(v[6:]) < 1920:
                raise ValueError("Year should be between 1920 and 2020")
        return v

    @validator("email")
    def validate_email(cls, v):
        if v is not None:
            if "@" not in v:
                raise ValueError("Invalid email")
        return v

    class Config:
        schema_extra = {
            "example": {
                "first_name": "John",
                "last_name": "Abraham",
                "dob": "21-02-1994",
                "email": "john@text.com",
            }
        }


class PartnerCreateUserRequest(BaseModel):
    first_name: str = Field(..., example="Shivam")
    middle_name: Optional[str] = Field(None, example="Kumar")
    last_name: Optional[str] = Field(None, example="Singhal")
    country_code: Optional[str] = "91"
    phone_number: str = Field(..., example="1234567890")



class PanVerifyRequest(UpdateUserProfileRequest):
    pan: str = Field(..., example = "eesspp2015n")
    dob: str = Field(..., example="Abraham")