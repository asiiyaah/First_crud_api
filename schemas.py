from pydantic import BaseModel , Field
from typing import Optional

class TaskCreate(BaseModel):
    title : str = Field(...,min_length=1)


class TaskResponse(BaseModel):
    id: int
    title:str
    done:bool

class TaskUpdate(BaseModel):
    title : Optional[str] = None
    done : Optional[bool] = None