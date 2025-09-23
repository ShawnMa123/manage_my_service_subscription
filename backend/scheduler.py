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
    """Check for subscriptions that need reminders and send batch Telegram notification"""
    logger.info("Starting subscription reminder check")

    # Reinitialize Telegram service to get latest settings
    await telegram_service.initialize()

    today = datetime.now().date()
    reminders_to_send = []

    with Session(engine) as session:
        # Get all subscriptions
        stmt = select(Subscription)
        subscriptions = session.exec(stmt).all()

        for subscription in subscriptions:
            days_until_due = (subscription.next_due_date - today).days

            # Collect subscriptions that need reminders (overdue, due today, or due within 3 days)
            if days_until_due <= 3:  # Includes overdue (negative), today (0), and upcoming (1-3)
                reminders_to_send.append(subscription)
                logger.info(f"Added to reminder batch: {subscription.name} (due in {days_until_due} days)")

        # Send batch reminder if there are any subscriptions to remind about
        if reminders_to_send:
            success = await telegram_service.send_batch_reminders(reminders_to_send)
            if success:
                logger.info(f"Batch reminder sent successfully for {len(reminders_to_send)} subscriptions")
            else:
                logger.error(f"Failed to send batch reminder for {len(reminders_to_send)} subscriptions")
        else:
            logger.info("No subscriptions require reminders at this time")

    logger.info("Subscription reminder check completed")


class SchedulerService:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()

    def start(self):
        """Start the scheduler with hourly reminder check"""
        # Run every hour at minute 0
        self.scheduler.add_job(
            check_subscription_reminders,
            CronTrigger(minute=0),
            id="subscription_reminder_check",
            name="Hourly subscription reminder check",
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