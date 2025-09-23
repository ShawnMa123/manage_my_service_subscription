import asyncio
import logging
import aiohttp
from typing import Dict, Optional
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)


class CurrencyService:
    """货币转换服务 - 使用免费汇率API"""

    def __init__(self):
        # 使用 exchangerate-api.com 的免费API
        self.base_url = "https://api.exchangerate-api.com/v4/latest"
        self.fallback_url = "https://api.fixer.io/latest"  # 备用API
        self.cache: Dict[str, Dict] = {}
        self.cache_duration = timedelta(hours=1)  # 缓存1小时

    async def get_exchange_rates(self, base_currency: str = "USD") -> Dict[str, float]:
        """获取汇率数据，带缓存机制"""
        cache_key = f"rates_{base_currency}"
        now = datetime.now()

        # 检查缓存
        if cache_key in self.cache:
            cached_data = self.cache[cache_key]
            if now - cached_data["timestamp"] < self.cache_duration:
                logger.info(f"Using cached exchange rates for {base_currency}")
                return cached_data["rates"]

        # 获取新的汇率数据
        try:
            rates = await self._fetch_rates(base_currency)
            # 缓存数据
            self.cache[cache_key] = {
                "rates": rates,
                "timestamp": now
            }
            logger.info(f"Fetched and cached exchange rates for {base_currency}")
            return rates
        except Exception as e:
            logger.error(f"Failed to fetch exchange rates: {e}")
            # 如果有缓存数据，即使过期也使用
            if cache_key in self.cache:
                logger.warning("Using expired cache due to API failure")
                return self.cache[cache_key]["rates"]
            # 返回默认汇率
            return self._get_fallback_rates()

    async def _fetch_rates(self, base_currency: str) -> Dict[str, float]:
        """从API获取汇率数据"""
        urls = [
            f"{self.base_url}/{base_currency}",
            f"https://open.er-api.com/v6/latest/{base_currency}",  # 另一个免费API
        ]

        async with aiohttp.ClientSession() as session:
            for url in urls:
                try:
                    async with session.get(url, timeout=10) as response:
                        if response.status == 200:
                            data = await response.json()
                            rates = data.get("rates", {})
                            if rates:
                                return rates
                except Exception as e:
                    logger.warning(f"Failed to fetch from {url}: {e}")
                    continue

        raise Exception("All exchange rate APIs failed")

    def _get_fallback_rates(self) -> Dict[str, float]:
        """提供备用汇率（大致准确的静态汇率）"""
        logger.warning("Using fallback exchange rates")
        return {
            "CNY": 7.2,    # 1 USD = 7.2 CNY
            "EUR": 0.85,   # 1 USD = 0.85 EUR
            "GBP": 0.73,   # 1 USD = 0.73 GBP
            "JPY": 110.0,  # 1 USD = 110 JPY
            "USD": 1.0,    # 基准货币
            "HKD": 7.8,    # 1 USD = 7.8 HKD
            "SGD": 1.35,   # 1 USD = 1.35 SGD
            "KRW": 1200.0, # 1 USD = 1200 KRW
        }

    async def convert_to_cny(self, amount: float, from_currency: str) -> float:
        """将指定货币金额转换为人民币"""
        if from_currency.upper() == "CNY":
            return amount

        try:
            # 先转换为USD，再转换为CNY
            if from_currency.upper() == "USD":
                usd_amount = amount
            else:
                # 获取以USD为基准的汇率
                usd_rates = await self.get_exchange_rates("USD")
                from_rate = usd_rates.get(from_currency.upper())
                if not from_rate:
                    logger.warning(f"Unknown currency: {from_currency}, using amount as-is")
                    return amount
                usd_amount = amount / from_rate

            # 转换USD到CNY
            usd_rates = await self.get_exchange_rates("USD")
            cny_rate = usd_rates.get("CNY", 7.2)  # 默认汇率
            cny_amount = usd_amount * cny_rate

            logger.info(f"Converted {amount} {from_currency} to {cny_amount:.2f} CNY")
            return cny_amount

        except Exception as e:
            logger.error(f"Currency conversion failed: {e}")
            # 如果转换失败，返回原金额
            return amount

    async def convert_multiple_to_cny(self, amounts: Dict[str, float]) -> float:
        """将多种货币的金额转换为CNY总额"""
        total_cny = 0.0
        conversion_details = []

        for currency, amount in amounts.items():
            cny_amount = await self.convert_to_cny(amount, currency)
            total_cny += cny_amount
            conversion_details.append(f"{amount:.2f} {currency} → {cny_amount:.2f} CNY")

        logger.info(f"Multi-currency conversion: {'; '.join(conversion_details)} = {total_cny:.2f} CNY")
        return total_cny

    def get_currency_symbol(self, currency: str) -> str:
        """获取货币符号"""
        symbols = {
            "CNY": "¥",
            "USD": "$",
            "EUR": "€",
            "GBP": "£",
            "JPY": "¥",
            "HKD": "HK$",
            "SGD": "S$",
            "KRW": "₩"
        }
        return symbols.get(currency.upper(), currency.upper())


# 全局实例
currency_service = CurrencyService()