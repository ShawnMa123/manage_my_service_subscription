import asyncio
import logging
from typing import Optional, List
from datetime import datetime
from telegram import Bot
from telegram.error import TelegramError
from sqlmodel import Session, select
from database import engine
from models import Setting, Subscription

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

    async def send_test_message(self) -> bool:
        """Send a test message to verify Telegram configuration"""
        await self.initialize()  # Re-initialize to get latest settings
        test_message = "🔔 测试通知\n\n这是来自订阅管理系统的测试消息。如果您收到此消息，说明 Telegram 通知配置正确！"
        return await self.send_message(test_message)

    async def send_batch_reminders(self, subscriptions: List[Subscription]) -> bool:
        """Send batch reminder message for multiple subscriptions"""
        if not subscriptions:
            return True

        # Group subscriptions by urgency
        today = datetime.now().date()
        overdue = []
        due_today = []
        due_soon = []

        for sub in subscriptions:
            days_until_due = (sub.next_due_date - today).days
            if days_until_due < 0:
                overdue.append(sub)
            elif days_until_due == 0:
                due_today.append(sub)
            else:
                due_soon.append(sub)

        # Construct batch message
        message_parts = ["🔔 订阅提醒汇总"]
        message_parts.append(f"📅 检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        message_parts.append("")

        if overdue:
            message_parts.append("🚨 已过期:")
            for sub in overdue:
                days_overdue = abs((sub.next_due_date - today).days)
                message_parts.append(f"  • {sub.name} - 已过期 {days_overdue} 天")
                message_parts.append(f"    💰 {sub.price} {sub.currency} | 周期: {self._get_cycle_text(sub.cycle)}")
            message_parts.append("")

        if due_today:
            message_parts.append("⏰ 今日到期:")
            for sub in due_today:
                message_parts.append(f"  • {sub.name}")
                message_parts.append(f"    💰 {sub.price} {sub.currency} | 周期: {self._get_cycle_text(sub.cycle)}")
            message_parts.append("")

        if due_soon:
            message_parts.append("📋 即将到期:")
            for sub in due_soon:
                days_until_due = (sub.next_due_date - today).days
                message_parts.append(f"  • {sub.name} - {days_until_due} 天后到期")
                message_parts.append(f"    💰 {sub.price} {sub.currency} | 周期: {self._get_cycle_text(sub.cycle)}")
            message_parts.append("")

        # Add summary
        total_count = len(subscriptions)
        total_amount = sum(sub.price for sub in subscriptions)
        message_parts.append(f"📊 总计: {total_count} 个订阅需要关注")
        if total_amount > 0:
            # Group by currency for summary
            currency_totals = {}
            for sub in subscriptions:
                if sub.currency not in currency_totals:
                    currency_totals[sub.currency] = 0
                currency_totals[sub.currency] += sub.price

            amount_texts = [f"{amount:.2f} {currency}" for currency, amount in currency_totals.items()]
            message_parts.append(f"💳 涉及金额: {', '.join(amount_texts)}")

        message = "\n".join(message_parts)
        return await self.send_message(message)

    async def send_operation_notification(self, operation: str, subscription: Subscription, old_data: dict = None) -> bool:
        """Send real-time operation notification"""
        emoji_map = {
            "created": "➕",
            "updated": "✏️",
            "deleted": "🗑️",
            "renewed": "🔄"
        }

        operation_map = {
            "created": "新建订阅",
            "updated": "更新订阅",
            "deleted": "删除订阅",
            "renewed": "续费订阅"
        }

        emoji = emoji_map.get(operation, "🔔")
        operation_text = operation_map.get(operation, operation)

        message_parts = [f"{emoji} {operation_text}"]
        message_parts.append(f"⏰ 操作时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        message_parts.append("")

        if operation == "deleted":
            message_parts.append(f"📝 订阅名称: {subscription.name}")
            message_parts.append(f"💰 价格: {subscription.price} {subscription.currency}")
        else:
            message_parts.append(f"📝 订阅名称: {subscription.name}")
            message_parts.append(f"💰 价格: {subscription.price} {subscription.currency}")
            message_parts.append(f"🔄 周期: {self._get_cycle_text(subscription.cycle)}")
            message_parts.append(f"📅 下次续费: {subscription.next_due_date}")

            if subscription.notes:
                notes_preview = subscription.notes[:50] + "..." if len(subscription.notes) > 50 else subscription.notes
                message_parts.append(f"📝 备注: {notes_preview}")

        if operation == "updated" and old_data:
            message_parts.append("")
            message_parts.append("🔄 变更内容:")

            changes = []
            if old_data.get("name") != subscription.name:
                changes.append(f"  • 名称: {old_data.get('name')} → {subscription.name}")
            if old_data.get("price") != subscription.price:
                changes.append(f"  • 价格: {old_data.get('price')} → {subscription.price}")
            if old_data.get("cycle") != subscription.cycle:
                old_cycle_text = self._get_cycle_text(old_data.get('cycle'))
                new_cycle_text = self._get_cycle_text(subscription.cycle)
                changes.append(f"  • 周期: {old_cycle_text} → {new_cycle_text}")
            if str(old_data.get("next_due_date")) != str(subscription.next_due_date):
                changes.append(f"  • 续费日期: {old_data.get('next_due_date')} → {subscription.next_due_date}")

            if changes:
                message_parts.extend(changes)
            else:
                message_parts.append("  • 仅更新了备注信息")

        message = "\n".join(message_parts)
        return await self.send_message(message)

    def _get_cycle_text(self, cycle: str) -> str:
        """Convert cycle enum to Chinese text"""
        cycle_map = {
            "monthly": "月度",
            "quarterly": "季度",
            "yearly": "年度"
        }
        return cycle_map.get(cycle, cycle)


# Global instance
telegram_service = TelegramService()