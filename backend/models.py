from datetime import datetime, date
from enum import Enum
from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import Text
from pydantic import BaseModel


class CycleEnum(str, Enum):
    monthly = "monthly"
    quarterly = "quarterly"
    yearly = "yearly"


class Subscription(SQLModel, table=True):
    __tablename__ = "subscriptions"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    price: float
    currency: str = Field(default="CNY")
    cycle: CycleEnum
    next_due_date: date
    notes: Optional[str] = Field(default=None, sa_column=Text)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class SubscriptionCreate(BaseModel):
    name: str
    price: float
    currency: str = "CNY"
    cycle: CycleEnum
    next_due_date: date
    notes: Optional[str] = None


class SubscriptionUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    currency: Optional[str] = None
    cycle: Optional[CycleEnum] = None
    next_due_date: Optional[date] = None
    notes: Optional[str] = None


class Setting(SQLModel, table=True):
    __tablename__ = "settings"

    key: str = Field(primary_key=True)
    value: str


class SettingCreate(BaseModel):
    key: str
    value: str


class SettingUpdate(BaseModel):
    value: str