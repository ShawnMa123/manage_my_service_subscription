"""
趋势分析服务模块
提供订阅数据的各种统计分析功能
"""
from datetime import datetime, date, timedelta
from typing import List, Dict
from collections import defaultdict
from dateutil.relativedelta import relativedelta
from sqlmodel import Session, select
from models import (
    Subscription, SubscriptionAnalytics, PriceTrend, CycleAnalysis,
    MonthlySpending, TimelineData, TrendAnalysis
)


class AnalyticsService:
    """趋势分析服务类"""

    def __init__(self, session: Session):
        self.session = session

    def get_all_subscriptions(self) -> List[Subscription]:
        """获取所有订阅数据"""
        stmt = select(Subscription)
        return list(self.session.exec(stmt).all())

    def calculate_monthly_cost(self, subscription: Subscription) -> float:
        """计算单个订阅的月度成本"""
        if subscription.cycle == "monthly":
            return subscription.price
        elif subscription.cycle == "quarterly":
            return subscription.price / 3
        elif subscription.cycle == "yearly":
            return subscription.price / 12
        return 0.0

    def calculate_yearly_cost(self, subscription: Subscription) -> float:
        """计算单个订阅的年度成本"""
        if subscription.cycle == "monthly":
            return subscription.price * 12
        elif subscription.cycle == "quarterly":
            return subscription.price * 4
        elif subscription.cycle == "yearly":
            return subscription.price
        return 0.0

    def get_subscription_analytics(self) -> SubscriptionAnalytics:
        """获取订阅数据综合分析"""
        subscriptions = self.get_all_subscriptions()

        # 基础统计
        total_subscriptions = len(subscriptions)
        active_subscriptions = total_subscriptions  # 所有存储的订阅都是活跃的

        # 成本计算
        total_monthly_cost = sum(self.calculate_monthly_cost(sub) for sub in subscriptions)
        total_yearly_cost = sum(self.calculate_yearly_cost(sub) for sub in subscriptions)

        # 周期分析
        cycle_stats = defaultdict(lambda: {'count': 0, 'total_amount': 0.0})
        for sub in subscriptions:
            cycle_stats[sub.cycle]['count'] += 1
            cycle_stats[sub.cycle]['total_amount'] += sub.price

        cycle_breakdown = []
        for cycle, stats in cycle_stats.items():
            cycle_breakdown.append(CycleAnalysis(
                cycle=cycle,
                count=stats['count'],
                total_amount=stats['total_amount'],
                average_price=stats['total_amount'] / stats['count'] if stats['count'] > 0 else 0.0
            ))

        # 即将到期的订阅（30天内）
        upcoming_date = date.today() + timedelta(days=30)
        upcoming_renewals = [
            sub for sub in subscriptions
            if sub.next_due_date <= upcoming_date
        ]

        # 价格区间统计
        price_ranges = self._calculate_price_ranges(subscriptions)

        return SubscriptionAnalytics(
            total_subscriptions=total_subscriptions,
            active_subscriptions=active_subscriptions,
            total_monthly_cost=total_monthly_cost,
            total_yearly_cost=total_yearly_cost,
            cycle_breakdown=cycle_breakdown,
            upcoming_renewals=upcoming_renewals,
            price_ranges=price_ranges
        )

    def _calculate_price_ranges(self, subscriptions: List[Subscription]) -> Dict[str, int]:
        """计算价格区间分布"""
        ranges = {
            "0-50": 0,
            "50-100": 0,
            "100-300": 0,
            "300-500": 0,
            "500+": 0
        }

        for sub in subscriptions:
            if sub.price < 50:
                ranges["0-50"] += 1
            elif sub.price < 100:
                ranges["50-100"] += 1
            elif sub.price < 300:
                ranges["100-300"] += 1
            elif sub.price < 500:
                ranges["300-500"] += 1
            else:
                ranges["500+"] += 1

        return ranges

    def get_price_trend(self) -> PriceTrend:
        """获取价格趋势分析"""
        subscriptions = self.get_all_subscriptions()

        # 生成最近12个月的月度支出统计
        monthly_spending = []
        today = date.today()

        # 按货币分组统计
        currency_stats = defaultdict(lambda: {'monthly': 0.0, 'yearly': 0.0})

        for i in range(12):
            month_date = today.replace(day=1) - relativedelta(months=i)
            month_str = month_date.strftime("%Y-%m")

            # 计算该月的总支出（基于当前活跃订阅）
            month_total = 0.0
            month_count = 0

            for sub in subscriptions:
                # 只计算在该月之前或该月创建的订阅
                if sub.created_at.date() <= month_date:
                    monthly_cost = self.calculate_monthly_cost(sub)
                    month_total += monthly_cost
                    month_count += 1

                    # 累计货币统计
                    currency_stats[sub.currency]['monthly'] += monthly_cost
                    currency_stats[sub.currency]['yearly'] += self.calculate_yearly_cost(sub)

            monthly_spending.append(MonthlySpending(
                month=month_str,
                total_amount=month_total,
                currency="CNY",  # 主要货币，后续可以支持多货币
                subscription_count=month_count
            ))

        # 反转列表，使时间顺序正确
        monthly_spending.reverse()

        # 计算总成本
        total_monthly = sum(self.calculate_monthly_cost(sub) for sub in subscriptions)
        total_yearly = sum(self.calculate_yearly_cost(sub) for sub in subscriptions)

        return PriceTrend(
            monthly_spending=monthly_spending,
            total_monthly=total_monthly,
            total_yearly=total_yearly,
            currency_breakdown=dict(currency_stats)
        )

    def get_creation_timeline(self) -> List[TimelineData]:
        """获取订阅创建时间线"""
        subscriptions = self.get_all_subscriptions()

        # 按月分组统计创建的订阅
        timeline_stats = defaultdict(lambda: {'count': 0, 'amount': 0.0})

        for sub in subscriptions:
            month_key = sub.created_at.strftime("%Y-%m")
            timeline_stats[month_key]['count'] += 1
            timeline_stats[month_key]['amount'] += sub.price

        # 转换为时间线数据
        timeline_data = []
        for month, stats in sorted(timeline_stats.items()):
            timeline_data.append(TimelineData(
                date=month,
                count=stats['count'],
                amount=stats['amount']
            ))

        return timeline_data

    def get_renewal_timeline(self) -> List[TimelineData]:
        """获取续费时间线（预测未来12个月）"""
        subscriptions = self.get_all_subscriptions()

        # 预测未来12个月的续费情况
        timeline_stats = defaultdict(lambda: {'count': 0, 'amount': 0.0})
        today = date.today()

        for i in range(12):
            month_date = today + relativedelta(months=i)
            month_start = month_date.replace(day=1)
            month_end = (month_start + relativedelta(months=1)) - timedelta(days=1)
            month_key = month_date.strftime("%Y-%m")

            for sub in subscriptions:
                # 检查订阅在该月是否有续费
                current_due = sub.next_due_date

                # 模拟续费周期，计算该月可能的续费
                while current_due <= month_end:
                    if month_start <= current_due <= month_end:
                        timeline_stats[month_key]['count'] += 1
                        timeline_stats[month_key]['amount'] += sub.price
                        break

                    # 计算下一个续费日期
                    if sub.cycle == "monthly":
                        current_due += relativedelta(months=1)
                    elif sub.cycle == "quarterly":
                        current_due += relativedelta(months=3)
                    elif sub.cycle == "yearly":
                        current_due += relativedelta(years=1)
                    else:
                        break

        # 转换为时间线数据
        timeline_data = []
        for month, stats in sorted(timeline_stats.items()):
            timeline_data.append(TimelineData(
                date=month,
                count=stats['count'],
                amount=stats['amount']
            ))

        return timeline_data

    def get_comprehensive_analysis(self) -> TrendAnalysis:
        """获取综合趋势分析"""
        return TrendAnalysis(
            subscription_analytics=self.get_subscription_analytics(),
            price_trend=self.get_price_trend(),
            creation_timeline=self.get_creation_timeline(),
            renewal_timeline=self.get_renewal_timeline()
        )