from pydantic import BaseModel

class TaskCreate(BaseModel):
    title: str
    is_completed: bool = False

class TaskUpdate(BaseModel):
    title: str | None = None
    is_completed: bool | None = None

class TaskResponse(BaseModel):
    id: int
    title: str
    is_completed: bool

class MessageResponse(BaseModel):
    message: str