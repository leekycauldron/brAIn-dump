from pydantic import BaseModel

class Date(BaseModel):
    year: int
    month: int
    day: int