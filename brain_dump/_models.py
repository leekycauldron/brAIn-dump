from pydantic import BaseModel
from typing import Optional

class Date(BaseModel):
    year: int
    month: int
    day: int