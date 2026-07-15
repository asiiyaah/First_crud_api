from pydantic import BaseModel , Field

class TaskCreate(BaseModel):
    title : str = Field(...,min_length=1)
    