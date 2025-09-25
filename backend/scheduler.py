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

    try:
        # Reinitialize Telegram service to get latest settings
        await telegram_service.initialize()

        today = datetime.now().date()
        three_days_from_now = today + timedelta(days=3)

        with Session(engine) as session:
            # Optimized query: Only get subscriptions that are due within 3 days
            # This eliminates the N+1 problem by filtering at the database level
            stmt = select(Subscription).where(
                Subscription.next_due_date <= three_days_from_now
            ).order_by(Subscription.next_due_date)

            due_subscriptions = session.exec(stmt).all()

            if due_subscriptions:
                logger.info(f"Found {len(due_subscriptions)} subscriptions requiring reminders")

                # Log details for each subscription
                for subscription in due_subscriptions:
                    days_until_due = (subscription.next_due_date - today).days
                    logger.info(f"Reminder needed: {subscription.name} (due in {days_until_due} days)")

                # Send batch reminder
                success = await telegram_service.send_batch_reminders(due_subscriptions)
                if success:
                    logger.info(f"Batch reminder sent successfully for {len(due_subscriptions)} subscriptions")
                else:
                    logger.error(f"Failed to send batch reminder for {len(due_subscriptions)} subscriptions")
            else:
                logger.info("No subscriptions require reminders at this time")

    except Exception as e:
        logger.error(f"Error during subscription reminder check: {e}")
        raise

    logger.info("Subscription reminder check completed")


class SchedulerService:
    def __init__(self):
        self.scheduler = AsyncIOScheduler(
            timezone="UTC",  # Explicit timezone setting
            job_defaults={
                'coalesce': True,  # Combine multiple pending executions
                'max_instances': 1,  # Prevent overlapping executions
                'misfire_grace_time': 30  # Allow 30 seconds grace for missed jobs
            }
        )

    def start(self):
        """Start the scheduler with optimized configuration"""
        try:
            # Run every hour at minute 0
            self.scheduler.add_job(
                check_subscription_reminders,
                CronTrigger(minute=0),
                id="subscription_reminder_check",
                name="Hourly subscription reminder check",
                replace_existing=True
            )

            self.scheduler.start()
            logger.info("Scheduler started successfully with optimized settings")

        except Exception as e:
            logger.error(f"Failed to start scheduler: {e}")
            raise

    def stop(self):
        """Stop the scheduler gracefully"""
        try:
            if self.scheduler.running:
                self.scheduler.shutdown(wait=True)
                logger.info("Scheduler stopped gracefully")
            else:
                logger.info("Scheduler was not running")
        except Exception as e:
            logger.error(f"Error stopping scheduler: {e}")


# Global instance
scheduler_service = SchedulerService()