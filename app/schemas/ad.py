from pydantic import BaseModel
from typing import Optional

class AdBase(BaseModel):
    title: str
    description: str
    price: float

class AdCreate(AdBase):
    pass

class AdUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None

class AdOut(AdBase):
    id: str
    owner_email: str