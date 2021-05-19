from typing import Optional

from pydantic import BaseModel


class CustomerBase(BaseModel):
    # urlimg: str
    idc: str
    fullname: str
    dob: str
    address: str
    country: str
    sex: Optional[str]
    # ethnicity: Optional[str]
    national: Optional[str]
    score: float
    typekyc: str
    totaltime: float


class CustomerResponse(CustomerBase):
    pass


class CustomerRequestBase64(BaseModel):
    file: str
