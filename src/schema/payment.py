from pydantic import BaseModel, Field, validator


class DailyMandateRequest(BaseModel):
    amount_rs: str = Field(..., example="1.0")
    phone: str = Field(..., example="9402930102")

    @validator("amount_rs")
    def validate_amount(cls, v):
        if v is not None:
            post_decimal = v.split(".")[1]
            pre_decimal = int(v.split(".")[0])
            if post_decimal != "00":
                raise ValueError("Decimal values should be 00")

            if pre_decimal < 1 or pre_decimal > 5000:
                raise ValueError("amount should be in between 1 and 5000")

        return v
