from datetime import datetime, date
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict, EmailStr
import re

PHONE_REGEX = re.compile(r"^\+?\d{1,3}?[-.\s]?\(?\d{1,4}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}$")

class ContactBase(BaseModel):
    firstname: str = Field(max_length=50)
    lastname: str = Field(max_length=50)
    email: EmailStr = Field(max_length=255)
    phone: str = Field(max_length=16)
    birthday: date
    description: str = Field(max_length=255)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        if not PHONE_REGEX.match(value):
            raise ValueError("Invalid phone number format")
        return value

class ContactModel(ContactBase):
    pass

class ContactUpdate(ContactModel):
    done: bool

class ContactStatusUpdate(BaseModel):
    done: bool

class ContactResponse(ContactBase):
    id: int
    done: bool
    created_at: datetime | None
    updated_at: Optional[datetime] | None

    model_config = ConfigDict(from_attributes=True)

class User(BaseModel):
    id: int
    username: str
    email: str
    avatar: str | None

    model_config = ConfigDict(from_attributes=True)

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class RequestEmail(BaseModel):
    email: EmailStr
    