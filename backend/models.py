from datetime import datetime, date
from enum import Enum
from typing import Optional, List
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


# 趋势分析相关的数据模型
class MonthlySpending(BaseModel):
    """月度支出统计"""
    month: str  # YYYY-MM格式
    total_amount: float
    currency: str
    subscription_count: int


class PriceTrend(BaseModel):
    """价格趋势数据"""
    monthly_spending: List[MonthlySpending]
    total_monthly: float
    total_yearly: float
    currency_breakdown: dict  # 按货币分组的统计


class CycleAnalysis(BaseModel):
    """订阅周期分析"""
    cycle: str
    count: int
    total_amount: float
    average_price: float


class SubscriptionAnalytics(BaseModel):
    """订阅数据分析"""
    total_subscriptions: int
    active_subscriptions: int
    total_monthly_cost: float
    total_yearly_cost: float
    cycle_breakdown: List[CycleAnalysis]
    upcoming_renewals: List[Subscription]  # 即将到期的订阅
    price_ranges: dict  # 价格区间统计


class TimelineData(BaseModel):
    """时间线数据"""
    date: str
    count: int
    amount: float


class TrendAnalysis(BaseModel):
    """综合趋势分析"""
    subscription_analytics: SubscriptionAnalytics
    price_trend: PriceTrend
    creation_timeline: List[TimelineData]  # 订阅创建时间线
    renewal_timeline: List[TimelineData]  # 续费时间线