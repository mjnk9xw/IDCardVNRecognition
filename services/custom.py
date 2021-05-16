from typing import Optional

from pydantic import BaseModel


class CustomerBase(BaseModel):
    idc: str
    fullname: str
    dob: str
    address: str
    country: str
    sex: Optional[str]
    ethnicity: Optional[str]
    national: Optional[str]


class CustomerResponse(CustomerBase):
    pass


class CustomerRequestBase64(BaseModel):
    file: str
