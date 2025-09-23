import asyncio
import logging
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlmodel import Session, select
from database import engine
from models import Subscription
from telegram_service import telegram_service

logger = logging.getLogger(__name__)


async def check_subscription_reminders():
    """Check for subscriptions that need reminders and send Telegram notifications"""
    logger.info("Starting subscription reminder check")

    # Reinitialize Telegram service to get latest settings
    await telegram_service.initialize()

    today = datetime.now().date()

    with Session(engine) as session:
        # Get all subscriptions
        stmt = select(Subscription)
        subscriptions = session.exec(stmt).all()

        for subscription in subscriptions:
            days_until_due = (subscription.next_due_date - today).days

            # Send reminder for 7, 3, and 1 days before due date
            if days_until_due in [7, 3, 1]:
                message = f"🔔 订阅提醒\n\n" \
                         f"服务名称: {subscription.name}\n" \
                         f"价格: {subscription.price} {subscription.currency}\n" \
                         f"续费日期: {subscription.next_due_date}\n" \
                         f"剩余天数: {days_until_due} 天\n"

                if subscription.notes:
                    message += f"备注: {subscription.notes}\n"

                success = await telegram_service.send_message(message)
                if success:
                    logger.info(f"Reminder sent for subscription: {subscription.name}")
                else:
                    logger.error(f"Failed to send reminder for subscription: {subscription.name}")

    logger.info("Subscription reminder check completed")


class SchedulerService:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()

    def start(self):
        """Start the scheduler with daily reminder check"""
        # Run every day at 1:00 AM
        self.scheduler.add_job(
            check_subscription_reminders,
            CronTrigger(hour=1, minute=0),
            id="subscription_reminder_check",
            name="Daily subscription reminder check",
            replace_existing=True
        )

        self.scheduler.start()
        logger.info("Scheduler started successfully")

    def stop(self):
        """Stop the scheduler"""
        self.scheduler.shutdown()
        logger.info("Scheduler stopped")


# Global instance
scheduler_service = SchedulerService()