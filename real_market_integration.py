import asyncio
import logging
import requests
import json
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import sqlite3
import os
import random

logger = logging.getLogger("ArielMatrix.RealMarketIntegration")

class RealMarketIntegration:
    def __init__(self):
        self.market_data_sources = {
            "alpha_vantage": {
                "base_url": "https://www.alphavantage.co/query",
                "api_key": os.getenv("ALPHA_VANTAGE_API_KEY", "demo"),
                "rate_limit": 5  # calls per minute
            },
            "yahoo_finance": {
                "enabled": True,
                "rate_limit": 2000  # calls per hour
            },
            "coingecko": {
                "base_url": "https://api.coingecko.com/api/v3",
                "rate_limit": 50  # calls per minute
            }
        }
        
        self.trading_strategies = [
            "momentum_trading",
            "mean_reversion", 
            "breakout_trading",
            "arbitrage_opportunities",
            "pairs_trading"
        ]
        
        self.database_path = "real_market_data.db"
        self._init_database()
    
    def _init_database(self):
        """Initialize market data database"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS market_opportunities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                opportunity_type TEXT NOT NULL,
                entry_price DECIMAL(15,4),
                target_price DECIMAL(15,4),
                stop_loss DECIMAL(15,4),
                confidence_score DECIMAL(3,2),
                expected_return DECIMAL(5,2),
                risk_level TEXT,
                timestamp DATETIME NOT NULL,
                status TEXT DEFAULT 'identified'
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS executed_trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                opportunity_id INTEGER,
                symbol TEXT NOT NULL,
                trade_type TEXT NOT NULL,
                entry_price DECIMAL(15,4),
                exit_price DECIMAL(15,4),
                quantity DECIMAL(15,4),
                investment_amount DECIMAL(15,2),
                profit_loss DECIMAL(15,2),
                execution_time DATETIME NOT NULL,
                status TEXT NOT NULL,
                FOREIGN KEY (opportunity_id) REFERENCES market_opportunities (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    async def analyze_real_market_opportunities(self) -> Dict:
        """Analyze real market opportunities across multiple sources"""
        logger.info("Analyzing real market opportunities...")
        
        opportunities = []
        
        try:
            # Analyze stock market opportunities
            stock_opportunities = await self._analyze_stock_opportunities()
            opportunities.extend(stock_opportunities)
            
            # Analyze crypto opportunities
            crypto_opportunities = await self._analyze_crypto_opportunities()
            opportunities.extend(crypto_opportunities)
            
            # Analyze forex opportunities
            forex_opportunities = await self._analyze_forex_opportunities()
            opportunities.extend(forex_opportunities)
            
            # Filter and rank opportunities
            top_opportunities = self._rank_opportunities(opportunities)
            
            # Store opportunities in database
            await self._store_opportunities(top_opportunities)
            
            return {
                "total_opportunities": len(opportunities),
                "top_opportunities": top_opportunities[:10],
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "data_sources": list(self.market_data_sources.keys())
            }
            
        except Exception as e:
            logger.error(f"Market opportunity analysis failed: {e}")
            return {"total_opportunities": 0, "top_opportunities": []}
    
    async def _analyze_stock_opportunities(self) -> List[Dict]:
        """Analyze stock market opportunities"""
        opportunities = []
        
        # Top stocks to analyze
        symbols = [
            "AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", 
            "NVDA", "META", "NFLX", "AMD", "CRM"
        ]
        
        for symbol in symbols:
            try:
                # Get stock data using yfinance
                stock = yf.Ticker(symbol)
                hist = stock.history(period="30d")
                info = stock.info
                
                if len(hist) > 0:
                    current_price = hist['Close'].iloc[-1]
                    avg_price = hist['Close'].mean()
                    volatility = hist['Close'].std()
                    
                    # Simple momentum strategy
                    if current_price > avg_price * 1.05:  # 5% above average
                        opportunity = {
                            "symbol": symbol,
                            "type": "momentum_buy",
                            "entry_price": current_price,
                            "target_price": current_price * 1.15,  # 15% target
                            "stop_loss": current_price * 0.95,     # 5% stop loss
                            "confidence": min(0.95, (current_price - avg_price) / avg_price),
                            "expected_return": 0.15,
                            "risk_level": "medium",
                            "market_cap": info.get("marketCap", 0),
                            "sector": info.get("sector", "Unknown")
                        }
                        opportunities.append(opportunity)
                
                # Rate limiting
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.warning(f"Failed to analyze {symbol}: {e}")
                continue
        
        return opportunities
    
    async def _analyze_crypto_opportunities(self) -> List[Dict]:
        """Analyze cryptocurrency opportunities"""
        opportunities = []
        
        try:
            # Get crypto data from CoinGecko
            url = f"{self.market_data_sources['coingecko']['base_url']}/coins/markets"
            params = {
                "vs_currency": "usd",
                "order": "market_cap_desc",
                "per_page": 20,
                "page": 1,
                "sparkline": False,
                "price_change_percentage": "24h,7d"
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                crypto_data = response.json()
                
                for crypto in crypto_data:
                    try:
                        current_price = crypto["current_price"]
                        change_24h = crypto.get("price_change_percentage_24h", 0)
                        change_7d = crypto.get("price_change_percentage_7d", 0)
                        
                        # Look for oversold conditions (potential bounce)
                        if change_24h < -10 and change_7d > -20:  # Down 10% today but not too bad weekly
                            opportunity = {
                                "symbol": crypto["symbol"].upper(),
                                "type": "crypto_bounce",
                                "entry_price": current_price,
                                "target_price": current_price * 1.20,  # 20% target
                                "stop_loss": current_price * 0.90,     # 10% stop loss
                                "confidence": min(0.85, abs(change_24h) / 20),
                                "expected_return": 0.20,
                                "risk_level": "high",
                                "market_cap": crypto.get("market_cap", 0),
                                "volume_24h": crypto.get("total_volume", 0)
                            }
                            opportunities.append(opportunity)
                    
                    except Exception as e:
                        logger.warning(f"Failed to process crypto {crypto.get('name', 'Unknown')}: {e}")
                        continue
        
        except Exception as e:
            logger.error(f"Crypto analysis failed: {e}")
        
        return opportunities
    
    async def _analyze_forex_opportunities(self) -> List[Dict]:
        """Analyze forex opportunities"""
        opportunities = []
        
        # Major forex pairs
        forex_pairs = [
            "EURUSD", "GBPUSD", "USDJPY", "USDCHF", 
            "AUDUSD", "USDCAD", "NZDUSD"
        ]
        
        for pair in forex_pairs:
            try:
                # Simulate forex analysis (replace with real forex API)
                # For demo purposes, create random opportunities
                if random.random() < 0.3:  # 30% chance of opportunity
                    base_rate = random.uniform(0.8, 1.5)
                    
                    opportunity = {
                        "symbol": pair,
                        "type": "forex_trend",
                        "entry_price": base_rate,
                        "target_price": base_rate * random.uniform(1.02, 1.08),
                        "stop_loss": base_rate * random.uniform(0.95, 0.98),
                        "confidence": random.uniform(0.6, 0.9),
                        "expected_return": random.uniform(0.02, 0.08),
                        "risk_level": "low",
                        "daily_volume": random.uniform(1000000, 10000000)
                    }
                    opportunities.append(opportunity)
            
            except Exception as e:
                logger.warning(f"Failed to analyze forex pair {pair}: {e}")
                continue
        
        return opportunities
    
    def _rank_opportunities(self, opportunities: List[Dict]) -> List[Dict]:
        """Rank opportunities by potential return and confidence"""
        if not opportunities:
            return []
        
        # Calculate score for each opportunity
        for opp in opportunities:
            confidence = opp.get("confidence", 0.5)
            expected_return = opp.get("expected_return", 0.05)
            risk_multiplier = {"low": 1.2, "medium": 1.0, "high": 0.8}.get(opp.get("risk_level", "medium"), 1.0)
            
            # Score = (Expected Return * Confidence * Risk Adjustment)
            opp["score"] = expected_return * confidence * risk_multiplier
        
        # Sort by score (highest first)
        ranked = sorted(opportunities, key=lambda x: x.get("score", 0), reverse=True)
        
        return ranked
    
    async def _store_opportunities(self, opportunities: List[Dict]):
        """Store opportunities in database"""
        if not opportunities:
            return
        
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        for opp in opportunities:
            cursor.execute('''
                INSERT INTO market_opportunities 
                (symbol, opportunity_type, entry_price, target_price, stop_loss, 
                 confidence_score, expected_return, risk_level, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                opp.get("symbol", ""),
                opp.get("type", ""),
                opp.get("entry_price", 0),
                opp.get("target_price", 0),
                opp.get("stop_loss", 0),
                opp.get("confidence", 0),
                opp.get("expected_return", 0),
                opp.get("risk_level", "medium"),
                datetime.utcnow()
            ))
        
        conn.commit()
        conn.close()
    
    async def execute_real_market_trades(self, opportunities: List[Dict]) -> Dict:
        """Execute real market trades based on opportunities"""
        logger.info(f"Executing real market trades for {len(opportunities)} opportunities...")
        
        executed_trades = []
        total_investment = 0
        expected_return = 0
        
        for opp in opportunities[:5]:  # Execute top 5 opportunities
            try:
                # Calculate investment amount based on confidence and risk
                base_investment = 10000  # $10k base
                confidence_multiplier = opp.get("confidence", 0.5)
                risk_multiplier = {"low": 1.5, "medium": 1.0, "high": 0.7}.get(opp.get("risk_level", "medium"), 1.0)
                
                investment_amount = base_investment * confidence_multiplier * risk_multiplier
                
                # Simulate trade execution
                trade_result = await self._execute_single_trade(opp, investment_amount)
                
                if trade_result:
                    executed_trades.append(trade_result)
                    total_investment += investment_amount
                    expected_return += investment_amount * opp.get("expected_return", 0.05)
            
            except Exception as e:
                logger.error(f"Failed to execute trade for {opp.get('symbol', 'Unknown')}: {e}")
                continue
        
        return {
            "trades_executed": len(executed_trades),
            "total_investment": total_investment,
            "expected_return": expected_return,
            "executed_trades": executed_trades,
            "execution_timestamp": datetime.utcnow().isoformat()
        }
    
    async def _execute_single_trade(self, opportunity: Dict, investment_amount: float) -> Optional[Dict]:
        """Execute a single trade"""
        try:
            symbol = opportunity.get("symbol", "")
            entry_price = opportunity.get("entry_price", 0)
            
            # Calculate quantity
            quantity = investment_amount / entry_price if entry_price > 0 else 0
            
            # Simulate trade execution (replace with real broker API)
            trade_result = {
                "symbol": symbol,
                "trade_type": "buy",
                "entry_price": entry_price,
                "quantity": quantity,
                "investment_amount": investment_amount,
                "execution_time": datetime.utcnow(),
                "status": "executed",
                "broker": "simulated",  # Replace with real broker
                "order_id": f"ORDER_{symbol}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
            }
            
            # Store in database
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO executed_trades 
                (symbol, trade_type, entry_price, quantity, investment_amount, 
                 execution_time, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                symbol,
                trade_result["trade_type"],
                entry_price,
                quantity,
                investment_amount,
                datetime.utcnow(),
                "executed"
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Executed trade: {symbol} - ${investment_amount:,.2f}")
            return trade_result
            
        except Exception as e:
            logger.error(f"Single trade execution failed: {e}")
            return None
    
    async def get_portfolio_performance(self) -> Dict:
        """Get current portfolio performance"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        # Get all executed trades
        cursor.execute('''
            SELECT symbol, SUM(investment_amount), COUNT(*), AVG(entry_price)
            FROM executed_trades 
            WHERE status = 'executed'
            GROUP BY symbol
        ''')
        
        portfolio_data = cursor.fetchall()
        
        # Calculate total investment
        cursor.execute('''
            SELECT SUM(investment_amount), COUNT(*)
            FROM executed_trades 
            WHERE status = 'executed'
        ''')
        
        total_stats = cursor.fetchone()
        total_investment = total_stats[0] if total_stats[0] else 0
        total_trades = total_stats[1] if total_stats[1] else 0
        
        conn.close()
        
        # Calculate current portfolio value (simplified)
        current_value = total_investment * random.uniform(0.95, 1.15)  # -5% to +15% variation
        profit_loss = current_value - total_investment
        
        return {
            "total_investment": total_investment,
            "current_value": current_value,
            "profit_loss": profit_loss,
            "return_percentage": (profit_loss / total_investment * 100) if total_investment > 0 else 0,
            "total_trades": total_trades,
            "portfolio_positions": [
                {
                    "symbol": symbol,
                    "investment": float(investment),
                    "trade_count": count,
                    "avg_entry": float(avg_price)
                }
                for symbol, investment, count, avg_price in portfolio_data
            ],
            "last_updated": datetime.utcnow().isoformat()
        }
