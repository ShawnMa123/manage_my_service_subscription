import asyncio
import logging
from typing import Optional
from telegram import Bot
from telegram.error import TelegramError
from sqlmodel import Session, select
from database import engine
from models import Setting

logger = logging.getLogger(__name__)


class TelegramService:
    def __init__(self):
        self.bot: Optional[Bot] = None
        self.chat_id: Optional[str] = None

    async def initialize(self):
        """Initialize Telegram bot with settings from database"""
        with Session(engine) as session:
            # Get Telegram bot token
            token_stmt = select(Setting).where(Setting.key == "telegram_token")
            token_setting = session.exec(token_stmt).first()

            # Get chat ID
            chat_id_stmt = select(Setting).where(Setting.key == "telegram_chat_id")
            chat_id_setting = session.exec(chat_id_stmt).first()

            if token_setting and chat_id_setting:
                self.bot = Bot(token=token_setting.value)
                self.chat_id = chat_id_setting.value
                logger.info("Telegram service initialized successfully")
            else:
                logger.warning("Telegram settings not found in database")

    async def send_message(self, message: str) -> bool:
        """Send message via Telegram bot"""
        if not self.bot or not self.chat_id:
            logger.error("Telegram bot not properly initialized")
            return False

        try:
            await self.bot.send_message(chat_id=self.chat_id, text=message)
            logger.info(f"Message sent successfully: {message[:50]}...")
            return True
        except TelegramError as e:
            logger.error(f"Failed to send Telegram message: {e}")
            return False


# Global instance
telegram_service = TelegramService()