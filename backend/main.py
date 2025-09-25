import logging
from contextlib import asynccontextmanager
from typing import List
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from database import create_db_and_tables, get_session
from models import (
    Subscription, SubscriptionCreate, SubscriptionUpdate,
    Setting, SettingCreate, SettingUpdate,
    TrendAnalysis, SubscriptionAnalytics, PriceTrend
)
from scheduler import scheduler_service, check_subscription_reminders
from telegram_service import telegram_service
from analytics import AnalyticsService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    create_db_and_tables()
    await telegram_service.initialize()
    scheduler_service.start()
    logger.info("Application started")
    yield
    # Shutdown
    scheduler_service.stop()
    logger.info("Application shutdown")


app = FastAPI(
    title="Subscription Management API",
    description="API for managing subscription services with Telegram reminders",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Subscription endpoints
@app.get("/api/subscriptions", response_model=List[Subscription])
def get_subscriptions(session: Session = Depends(get_session)):
    """Get all subscriptions"""
    stmt = select(Subscription).order_by(Subscription.next_due_date)
    subscriptions = session.exec(stmt).all()
    return subscriptions


@app.post("/api/subscriptions", response_model=Subscription)
async def create_subscription(
    subscription: SubscriptionCreate,
    session: Session = Depends(get_session)
):
    """Create a new subscription"""
    db_subscription = Subscription(**subscription.model_dump())
    session.add(db_subscription)
    session.commit()
    session.refresh(db_subscription)

    # Send real-time notification
    try:
        await telegram_service.send_operation_notification("created", db_subscription)
    except Exception as e:
        logger.warning(f"Failed to send creation notification: {e}")

    return db_subscription


@app.get("/api/subscriptions/{subscription_id}", response_model=Subscription)
def get_subscription(subscription_id: int, session: Session = Depends(get_session)):
    """Get a specific subscription by ID"""
    subscription = session.get(Subscription, subscription_id)
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return subscription


@app.put("/api/subscriptions/{subscription_id}", response_model=Subscription)
async def update_subscription(
    subscription_id: int,
    subscription_update: SubscriptionUpdate,
    session: Session = Depends(get_session)
):
    """Update a specific subscription"""
    subscription = session.get(Subscription, subscription_id)
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")

    # Store old data for change tracking
    old_data = {
        "name": subscription.name,
        "price": subscription.price,
        "currency": subscription.currency,
        "cycle": subscription.cycle,
        "next_due_date": subscription.next_due_date,
        "notes": subscription.notes
    }

    update_data = subscription_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(subscription, key, value)

    session.add(subscription)
    session.commit()
    session.refresh(subscription)

    # Send real-time notification with change details
    try:
        await telegram_service.send_operation_notification("updated", subscription, old_data)
    except Exception as e:
        logger.warning(f"Failed to send update notification: {e}")

    return subscription


@app.delete("/api/subscriptions/{subscription_id}")
async def delete_subscription(subscription_id: int, session: Session = Depends(get_session)):
    """Delete a specific subscription"""
    subscription = session.get(Subscription, subscription_id)
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")

    # Store subscription data before deletion for notification
    subscription_data = Subscription(
        id=subscription.id,
        name=subscription.name,
        price=subscription.price,
        currency=subscription.currency,
        cycle=subscription.cycle,
        next_due_date=subscription.next_due_date,
        notes=subscription.notes,
        created_at=subscription.created_at
    )

    session.delete(subscription)
    session.commit()

    # Send real-time notification
    try:
        await telegram_service.send_operation_notification("deleted", subscription_data)
    except Exception as e:
        logger.warning(f"Failed to send deletion notification: {e}")

    return {"message": "Subscription deleted successfully"}


@app.post("/api/subscriptions/{subscription_id}/renew", response_model=Subscription)
async def renew_subscription(subscription_id: int, session: Session = Depends(get_session)):
    """Renew a subscription by extending the next due date based on its cycle"""
    subscription = session.get(Subscription, subscription_id)
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")

    # Store old due date for notification
    old_due_date = subscription.next_due_date

    # Calculate the new due date based on cycle
    current_due_date = subscription.next_due_date

    if subscription.cycle == "monthly":
        new_due_date = current_due_date + relativedelta(months=1)
    elif subscription.cycle == "quarterly":
        new_due_date = current_due_date + relativedelta(months=3)
    elif subscription.cycle == "yearly":
        new_due_date = current_due_date + relativedelta(years=1)
    else:
        raise HTTPException(status_code=400, detail="Invalid subscription cycle")

    subscription.next_due_date = new_due_date
    session.add(subscription)
    session.commit()
    session.refresh(subscription)

    # Send real-time notification
    try:
        await telegram_service.send_operation_notification("renewed", subscription, {"next_due_date": old_due_date})
    except Exception as e:
        logger.warning(f"Failed to send renewal notification: {e}")

    return subscription


# Settings endpoints
@app.get("/api/settings", response_model=List[Setting])
def get_settings(session: Session = Depends(get_session)):
    """Get all settings"""
    stmt = select(Setting)
    settings = session.exec(stmt).all()
    return settings


@app.post("/api/settings")
def update_settings(
    settings: List[SettingCreate],
    session: Session = Depends(get_session)
):
    """Update multiple settings"""
    for setting_data in settings:
        # Check if setting exists
        existing_setting = session.get(Setting, setting_data.key)
        if existing_setting:
            existing_setting.value = setting_data.value
            session.add(existing_setting)
        else:
            new_setting = Setting(**setting_data.model_dump())
            session.add(new_setting)

    session.commit()
    return {"message": "Settings updated successfully"}


@app.get("/api/settings/{key}", response_model=Setting)
def get_setting(key: str, session: Session = Depends(get_session)):
    """Get a specific setting by key"""
    setting = session.get(Setting, key)
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    return setting


@app.put("/api/settings/{key}", response_model=Setting)
def update_setting(
    key: str,
    setting_update: SettingUpdate,
    session: Session = Depends(get_session)
):
    """Update a specific setting"""
    setting = session.get(Setting, key)
    if not setting:
        # Create new setting if it doesn't exist
        setting = Setting(key=key, value=setting_update.value)
    else:
        setting.value = setting_update.value

    session.add(setting)
    session.commit()
    session.refresh(setting)
    return setting


# Telegram test endpoint
@app.post("/api/telegram/test")
async def test_telegram_notification():
    """Send a test message to verify Telegram configuration"""
    try:
        success = await telegram_service.send_test_message()
        if success:
            return {"status": "success", "message": "Test message sent successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to send test message")
    except Exception as e:
        logger.error(f"Error sending test message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Manual reminder check endpoint
@app.post("/api/reminders/check")
async def check_reminders():
    """Manually trigger reminder check for testing"""
    try:
        await check_subscription_reminders()
        return {"status": "success", "message": "Reminder check completed"}
    except Exception as e:
        logger.error(f"Error checking reminders: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# 趋势分析端点
@app.get("/api/analytics/comprehensive", response_model=TrendAnalysis)
def get_comprehensive_analytics(session: Session = Depends(get_session)):
    """获取综合趋势分析数据"""
    try:
        analytics_service = AnalyticsService(session)
        return analytics_service.get_comprehensive_analysis()
    except Exception as e:
        logger.error(f"Error getting comprehensive analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analytics/subscription", response_model=SubscriptionAnalytics)
def get_subscription_analytics(session: Session = Depends(get_session)):
    """获取订阅数据分析"""
    try:
        analytics_service = AnalyticsService(session)
        return analytics_service.get_subscription_analytics()
    except Exception as e:
        logger.error(f"Error getting subscription analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analytics/price-trend", response_model=PriceTrend)
def get_price_trend(session: Session = Depends(get_session)):
    """获取价格趋势分析"""
    try:
        analytics_service = AnalyticsService(session)
        return analytics_service.get_price_trend()
    except Exception as e:
        logger.error(f"Error getting price trend: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analytics/timeline/creation")
def get_creation_timeline(session: Session = Depends(get_session)):
    """获取订阅创建时间线"""
    try:
        analytics_service = AnalyticsService(session)
        return analytics_service.get_creation_timeline()
    except Exception as e:
        logger.error(f"Error getting creation timeline: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analytics/timeline/renewal")
def get_renewal_timeline(session: Session = Depends(get_session)):
    """获取续费时间线预测"""
    try:
        analytics_service = AnalyticsService(session)
        return analytics_service.get_renewal_timeline()
    except Exception as e:
        logger.error(f"Error getting renewal timeline: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Health check endpoint
@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)