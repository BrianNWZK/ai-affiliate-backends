import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from decimal import Decimal
import random

logger = logging.getLogger("ArielMatrix.RewardManager")

class RewardManager:
    def __init__(self):
        self.reward_pool = Decimal('100000.00')  # $100K initial pool
        self.distributed_rewards = Decimal('0.00')
        self.reward_history = []
        self.performance_bonuses = []
        self.milestone_rewards = {}
        
    async def manage_rewards(self, revenue_generated: float) -> Dict:
        """Manage reward distribution based on revenue"""
        logger.info(f"💎 Managing rewards for ${revenue_generated:,.2f} revenue...")
        
        try:
            revenue_decimal = Decimal(str(revenue_generated))
            
            # Calculate performance bonus
            performance_bonus = await self._calculate_performance_bonus(revenue_decimal)
            
            # Check for milestone rewards
            milestone_reward = await self._check_milestone_rewards(revenue_decimal)
            
            # Distribute rewards
            total_rewards = performance_bonus + milestone_reward
            
            if total_rewards > 0:
                await self._distribute_rewards(total_rewards, revenue_decimal)
            
            # Update reward pool
            await self._update_reward_pool(revenue_decimal)
            
            reward_result = {
                "performance_bonus": float(performance_bonus),
                "milestone_reward": float(milestone_reward),
                "total_rewards": float(total_rewards),
                "reward_pool_balance": float(self.reward_pool),
                "distributed_total": float(self.distributed_rewards),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            logger.info(f"💎 Rewards managed: ${total_rewards:,.2f} distributed")
            return reward_result
            
        except Exception as e:
            logger.error(f"Reward management failed: {e}")
            return {"error": str(e)}
    
    async def _calculate_performance_bonus(self, revenue: Decimal) -> Decimal:
        """Calculate performance-based bonus"""
        try:
            # Base bonus: 1% of revenue
            base_bonus = revenue * Decimal('0.01')
            
            # Performance multiplier based on revenue size
            if revenue >= Decimal('100000'):  # $100K+
                multiplier = Decimal('2.0')
            elif revenue >= Decimal('50000'):   # $50K+
                multiplier = Decimal('1.5')
            elif revenue >= Decimal('10000'):   # $10K+
                multiplier = Decimal('1.2')
            else:
                multiplier = Decimal('1.0')
            
            performance_bonus = base_bonus * multiplier
            
            # Cap bonus at 5% of revenue
            max_bonus = revenue * Decimal('0.05')
            performance_bonus = min(performance_bonus, max_bonus)
            
            return performance_bonus
            
        except Exception as e:
            logger.error(f"Performance bonus calculation failed: {e}")
            return Decimal('0.00')
    
    async def _check_milestone_rewards(self, total_revenue: Decimal) -> Decimal:
        """Check for milestone-based rewards"""
        try:
            milestones = [
                (Decimal('100000'), Decimal('5000')),    # $100K -> $5K reward
                (Decimal('1000000'), Decimal('50000')),   # $1M -> $50K reward
                (Decimal('10000000'), Decimal('500000')), # $10M -> $500K reward
                (Decimal('100000000'), Decimal('5000000')), # $100M -> $5M reward
                (Decimal('1000000000'), Decimal('50000000')), # $1B -> $50M reward
            ]
            
            milestone_reward = Decimal('0.00')
            
            for milestone_amount, reward_amount in milestones:
                if total_revenue >= milestone_amount and milestone_amount not in self.milestone_rewards:
                    milestone_reward += reward_amount
                    self.milestone_rewards[milestone_amount] = {
                        "achieved_at": datetime.utcnow().isoformat(),
                        "reward_amount": float(reward_amount)
                    }
                    
                    logger.info(f"🎉 Milestone achieved: ${milestone_amount:,.2f} - Reward: ${reward_amount:,.2f}")
            
            return milestone_reward
            
        except Exception as e:
            logger.error(f"Milestone reward check failed: {e}")
            return Decimal('0.00')
    
    async def _distribute_rewards(self, reward_amount: Decimal, revenue: Decimal):
        """Distribute rewards"""
        try:
            if reward_amount <= 0:
                return
            
            # Check if sufficient funds in reward pool
            if reward_amount > self.reward_pool:
                logger.warning(f"Insufficient reward pool: ${self.reward_pool} < ${reward_amount}")
                reward_amount = self.reward_pool
            
            # Distribute reward
            self.reward_pool -= reward_amount
            self.distributed_rewards += reward_amount
            
            # Record reward distribution
            reward_record = {
                "amount": float(reward_amount),
                "revenue_generated": float(revenue),
                "distributed_at": datetime.utcnow().isoformat(),
                "reward_type": "performance_and_milestone"
            }
            
            self.reward_history.append(reward_record)
            
            # Keep only recent history
            if len(self.reward_history) > 1000:
                self.reward_history = self.reward_history[-1000:]
            
            logger.info(f"💰 Reward distributed: ${reward_amount:,.2f}")
            
        except Exception as e:
            logger.error(f"Reward distribution failed: {e}")
    
    async def _update_reward_pool(self, revenue: Decimal):
        """Update reward pool with new revenue"""
        try:
            # Add 2% of revenue to reward pool
            pool_contribution = revenue * Decimal('0.02')
            self.reward_pool += pool_contribution
            
            # Cap reward pool at $10M
            max_pool = Decimal('10000000.00')
            if self.reward_pool > max_pool:
                self.reward_pool = max_pool
            
        except Exception as e:
            logger.error(f"Reward pool update failed: {e}")
    
    async def update_rewards(self, total_revenue: float):
        """Update rewards based on total revenue"""
        return await self.manage_rewards(total_revenue)
    
    async def get_reward_summary(self) -> Dict:
        """Get reward system summary"""
        try:
            recent_rewards = self.reward_history[-10:] if self.reward_history else []
            
            return {
                "reward_pool_balance": float(self.reward_pool),
                "total_distributed": float(self.distributed_rewards),
                "milestones_achieved": len(self.milestone_rewards),
                "recent_rewards": recent_rewards,
                "milestone_rewards": self.milestone_rewards,
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Reward summary failed: {e}")
            return {"error": str(e)}
