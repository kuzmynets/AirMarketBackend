from pydantic import BaseModel
from typing import List, Optional

class CreateAd(BaseModel):
    title: str
    description: str
    price: float
    images: List[str]

class UpdateAd(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    images: Optional[List[str]] = None