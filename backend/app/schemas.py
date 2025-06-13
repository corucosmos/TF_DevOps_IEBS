from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str

class UserResponse(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str

    class Config:
        from_attributes = True