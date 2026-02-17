from pydantic import BaseModel, EmailStr, ConfigDict
from uuid import UUID
from datetime import datetime

# Lo que recibimos cuando alguien se registra
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

# Lo que devolvemos al cliente (sin el password)
class UserOut(BaseModel):
    id: UUID
    username: str
    email: EmailStr
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)