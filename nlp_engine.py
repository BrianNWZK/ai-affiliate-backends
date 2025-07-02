import asyncio
import logging
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json
import re

logger = logging.getLogger("ArielMatrix.NLPEngine")

class NLPEngine:
    def __init__(self):
        self.models = {}
        self.processed_texts = []
        self.sentiment_cache = {}
        self.keywords = [
            "revenue", "profit", "opportunity", "investment", "growth",
            "market", "business", "startup", "funding", "acquisition"
        ]
        
    async def initialize(self):
        """Initialize NLP engine"""
        logger.info("🧠 Initializing NLP engine...")
        
        # Initialize models (simulated)
        self.models = {
            "sentiment": {"status": "loaded", "accuracy": 0.92},
            "entity_extraction": {"status": "loaded", "accuracy": 0.88},
            "text_classification": {"status": "loaded", "accuracy": 0.90},
            "keyword_extraction": {"status": "loaded", "accuracy": 0.85}
        }
        
        logger.info("✅ NLP engine initialized")
    
    async def analyze_text(self, text: str) -> Dict:
        """Analyze text for opportunities and insights"""
        logger.info("🧠 Analyzing text for opportunities...")
        
        try:
            # Sentiment analysis
            sentiment = await self._analyze_sentiment(text)
            
            # Entity extraction
            entities = await self._extract_entities(text)
            
            # Keyword extraction
            keywords = await self._extract_keywords(text)
            
            # Opportunity detection
            opportunities = await self._detect_opportunities(text)
            
            analysis_result = {
                "sentiment": sentiment,
                "entities": entities,
                "keywords": keywords,
                "opportunities": opportunities,
                "text_length": len(text),
                "analyzed_at": datetime.utcnow().isoformat()
            }
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Text analysis failed: {e}")
            return {"error": str(e)}
    
    async def _analyze_sentiment(self, text: str) -> Dict:
        """Analyze sentiment of text"""
        try:
            # Simulate sentiment analysis
            await asyncio.sleep(0.1)
            
            # Simple keyword-based sentiment
            positive_words = ["good", "great", "excellent", "profit", "growth", "success"]
            negative_words = ["bad", "terrible", "loss", "decline", "failure", "risk"]
            
            text_lower = text.lower()
            positive_count = sum(1 for word in positive_words if word in text_lower)
            negative_count = sum(1 for word in negative_words if word in text_lower)
            
            if positive_count > negative_count:
                sentiment = "positive"
                confidence = min(0.9, 0.6 + (positive_count - negative_count) * 0.1)
            elif negative_count > positive_count:
                sentiment = "negative"
                confidence = min(0.9, 0.6 + (negative_count - positive_count) * 0.1)
            else:
                sentiment = "neutral"
                confidence = 0.5
            
            return {
                "sentiment": sentiment,
                "confidence": confidence,
                "positive_indicators": positive_count,
                "negative_indicators": negative_count
            }
            
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            return {"sentiment": "neutral", "confidence": 0.5}
    
    async def _extract_entities(self, text: str) -> List[Dict]:
        """Extract entities from text"""
        try:
            entities = []
            
            # Simple regex-based entity extraction
            # Money amounts
            money_pattern = r'\$[\d,]+(?:\.\d{2})?'
            money_matches = re.findall(money_pattern, text)
            for match in money_matches:
                entities.append({
                    "type": "MONEY",
                    "text": match,
                    "confidence": 0.9
                })
            
            # Company names (capitalized words)
            company_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'
            company_matches = re.findall(company_pattern, text)
            for match in company_matches[:5]:  # Limit to 5
                if len(match) > 2:
                    entities.append({
                        "type": "ORGANIZATION",
                        "text": match,
                        "confidence": 0.7
                    })
            
            # Percentages
            percent_pattern = r'\d+(?:\.\d+)?%'
            percent_matches = re.findall(percent_pattern, text)
            for match in percent_matches:
                entities.append({
                    "type": "PERCENT",
                    "text": match,
                    "confidence": 0.95
                })
            
            return entities
            
        except Exception as e:
            logger.error(f"Entity extraction failed: {e}")
            return []
    
    async def _extract_keywords(self, text: str) -> List[Dict]:
        """Extract keywords from text"""
        try:
            keywords = []
            text_lower = text.lower()
            
            # Check for predefined keywords
            for keyword in self.keywords:
                if keyword in text_lower:
                    # Count occurrences
                    count = text_lower.count(keyword)
                    keywords.append({
                        "keyword": keyword,
                        "count": count,
                        "relevance": min(1.0, count * 0.2)
                    })
            
            # Sort by relevance
            keywords.sort(key=lambda x: x["relevance"], reverse=True)
            
            return keywords[:10]  # Top 10 keywords
            
        except Exception as e:
            logger.error(f"Keyword extraction failed: {e}")
            return []
    
    async def _detect_opportunities(self, text: str) -> List[Dict]:
        """Detect business opportunities in text"""
        try:
            opportunities = []
            text_lower = text.lower()
            
            # Opportunity indicators
            opportunity_patterns = [
                (r'funding.*\$[\d,]+', "funding_opportunity"),
                (r'acquisition.*\$[\d,]+', "acquisition_opportunity"),
                (r'investment.*\$[\d,]+', "investment_opportunity"),
                (r'revenue.*\$[\d,]+', "revenue_opportunity"),
                (r'market.*growth', "market_growth"),
                (r'new.*product', "product_opportunity"),
                (r'partnership', "partnership_opportunity")
            ]
            
            for pattern, opp_type in opportunity_patterns:
                matches = re.findall(pattern, text_lower)
                if matches:
                    for match in matches:
                        opportunities.append({
                            "type": opp_type,
                            "text_match": match,
                            "confidence": random.uniform(0.6, 0.9),
                            "potential_value": random.uniform(10000, 500000)
                        })
            
            return opportunities
            
        except Exception as e:
            logger.error(f"Opportunity detection failed: {e}")
            return []
    
    async def process_batch(self, texts: List[str]) -> List[Dict]:
        """Process multiple texts in batch"""
        logger.info(f"🧠 Processing batch of {len(texts)} texts...")
        
        try:
            results = []
            
            for text in texts:
                result = await self.analyze_text(text)
                results.append(result)
                
                # Small delay to prevent overwhelming
                await asyncio.sleep(0.05)
            
            return results
            
        except Exception as e:
            logger.error(f"Batch processing failed: {e}")
            return []
    
    async def get_insights(self) -> Dict:
        """Get NLP insights and statistics"""
        try:
            total_processed = len(self.processed_texts)
            
            # Calculate statistics
            avg_sentiment = 0.5  # Placeholder
            top_keywords = self.keywords[:5]  # Top 5 keywords
            
            insights = {
                "total_texts_processed": total_processed,
                "average_sentiment": avg_sentiment,
                "top_keywords": top_keywords,
                "models_loaded": len(self.models),
                "cache_size": len(self.sentiment_cache),
                "last_updated": datetime.utcnow().isoformat()
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"Insights generation failed: {e}")
            return {"error": str(e)}
    
    async def get_status(self) -> Dict:
        """Get NLP engine status"""
        return {
            "models_loaded": len(self.models),
            "texts_processed": len(self.processed_texts),
            "cache_size": len(self.sentiment_cache),
            "keywords_configured": len(self.keywords),
            "status": "active"
        }
