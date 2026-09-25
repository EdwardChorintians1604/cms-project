from datetime import date, datetime
from typing import Optional
from pydantic import AliasChoices, BaseModel, EmailStr, ConfigDict, Field

class UserBase(BaseModel):
    full_name: str = Field(validation_alias=AliasChoices("full_name", "fullName"))
    username: str
    email: EmailStr
    birth_place: Optional[str] = Field(default=None, validation_alias=AliasChoices("birth_place", "birthPlace"))
    birth_date: Optional[date] = Field(default=None, validation_alias=AliasChoices("birth_date", "birthDate"))
    nik: Optional[str] = None
    no_ktp: Optional[str] = Field(default=None, validation_alias=AliasChoices("no_ktp", "noKtp"))
    gender: Optional[str] = None
    education: Optional[str] = None
    church_domisili: Optional[str] = None
    church_central: Optional[str] = None
    married: Optional[str] = None
    chatecication: Optional[str] = None
    phone: Optional[str] = None
    origin: Optional[str] = None
    address: Optional[str] = None
    photo_url: Optional[str] = Field(default=None, validation_alias=AliasChoices("photo_url", "photoUrl"))
    church_id: Optional[int] = None
    role: Optional[str] = "jemaat"
    is_active: Optional[bool] = True

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

class UserCreate(UserBase):
    birth_place: str = Field(validation_alias=AliasChoices("birth_place", "birthPlace"))
    birth_date: date = Field(validation_alias=AliasChoices("birth_date", "birthDate"))
    nik: str
    gender: str
    education: str
    church_domisili: str
    church_central: str
    married: str
    chatecication: str
    phone: str
    origin: str
    address: str
    password: str
    confirm_password: Optional[str] = Field(default=None, validation_alias=AliasChoices("confirm_password", "confirmPassword"))

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    birth_place: Optional[str] = None
    birth_date: Optional[date] = None
    nik: Optional[str] = None
    no_ktp: Optional[str] = None
    gender: Optional[str] = None
    education: Optional[str] = None
    church_domisili: Optional[str] = None
    church_central: Optional[str] = None
    married: Optional[str] = None
    chatecication: Optional[str] = None
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    phone: Optional[str] = None
    origin: Optional[str] = None
    address: Optional[str] = None
    photo_url: Optional[str] = None
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    id: int
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
