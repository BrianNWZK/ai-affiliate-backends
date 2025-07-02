import asyncio
import logging
from datetime import datetime, timedelta
import random
from typing import Dict, List
from auth import auth_manager
from blog_generator import blog_generator

logger = logging.getLogger("ArielMatrix.DatabaseSeeder")

class DatabaseSeeder:
    def __init__(self):
        self.seeded_data = {
            "users": [],
            "quantum_research": [],
            "revenue_records": [],
            "blog_posts": [],
            "affiliate_campaigns": []
        }
    
    async def seed_all(self):
        """Seed all database tables with sample data"""
        logger.info("Starting database seeding...")
        
        try:
            # Seed users
            await self.seed_users()
            
            # Seed quantum research data
            await self.seed_quantum_research()
            
            # Seed revenue records
            await self.seed_revenue_records()
            
            # Seed blog posts
            await self.seed_blog_posts()
            
            # Seed affiliate campaigns
            await self.seed_affiliate_campaigns()
            
            logger.info("Database seeding completed successfully")
            return self.seeded_data
            
        except Exception as e:
            logger.error(f"Database seeding failed: {e}")
            raise
    
    async def seed_users(self):
        """Seed user accounts"""
        logger.info("Seeding user accounts...")
        
        sample_users = [
            {
                "email": "admin@arielmatrix.com",
                "password": "admin123",
                "role": "admin",
                "quantum_access": True,
                "affiliate_access": True,
                "autonomous_mode": True
            },
            {
                "email": "quantum@arielmatrix.com", 
                "password": "quantum123",
                "role": "quantum_researcher",
                "quantum_access": True,
                "affiliate_access": False,
                "autonomous_mode": True
            },
            {
                "email": "affiliate@arielmatrix.com",
                "password": "affiliate123", 
                "role": "affiliate_manager",
                "quantum_access": False,
                "affiliate_access": True,
                "autonomous_mode": True
            },
            {
                "email": "user@arielmatrix.com",
                "password": "user123",
                "role": "user",
                "quantum_access": True,
                "affiliate_access": True,
                "autonomous_mode": False
            }
        ]
        
        for user_data in sample_users:
            password = user_data.pop("password")
            result = await auth_manager.register_user(
                user_data["email"],
                password,
                user_data
            )
            
            if result["success"]:
                self.seeded_data["users"].append({
                    "email": user_data["email"],
                    "role": user_data["role"],
                    "created": True
                })
                logger.info(f"Created user: {user_data['email']}")
            else:
                logger.warning(f"Failed to create user: {user_data['email']}")
    
    async def seed_quantum_research(self):
        """Seed quantum research data"""
        logger.info("Seeding quantum research data...")
        
        quantum_algorithms = ["grover", "shor", "vqe", "qaoa", "quantum_annealing"]
        research_areas = ["optimization", "cryptography", "machine_learning", "simulation"]
        
        for i in range(20):
            research_record = {
                "id": f"quantum_research_{i+1}",
                "algorithm": random.choice(quantum_algorithms),
                "research_area": random.choice(research_areas),
                "potential_speedup": random.uniform(2.0, 1000.0),
                "confidence": random.uniform(0.6, 0.95),
                "implementation_complexity": random.choice(["low", "medium", "high"]),
                "commercial_viability": random.uniform(0.3, 0.9),
                "potential_revenue": random.uniform(5000, 200000),
                "time_to_market": random.randint(6, 48),
                "risk_level": random.choice(["low", "medium", "high"]),
                "created_at": (datetime.utcnow() - timedelta(days=random.randint(1, 30))).isoformat(),
                "status": random.choice(["active", "completed", "on_hold"]),
                "autonomous_generated": True
            }
            
            self.seeded_data["quantum_research"].append(research_record)
        
        logger.info(f"Created {len(self.seeded_data['quantum_research'])} quantum research records")
    
    async def seed_revenue_records(self):
        """Seed revenue tracking records"""
        logger.info("Seeding revenue records...")
        
        revenue_sources = [
            "affiliate_commissions",
            "quantum_consulting", 
            "ai_services",
            "content_licensing",
            "api_subscriptions",
            "premium_features"
        ]
        
        for i in range(50):
            revenue_record = {
                "id": f"revenue_{i+1}",
                "source": random.choice(revenue_sources),
                "amount": round(random.uniform(10.0, 5000.0), 2),
                "currency": "USD",
                "transaction_date": (datetime.utcnow() - timedelta(days=random.randint(1, 90))).isoformat(),
                "status": random.choice(["completed", "pending", "failed"]),
                "commission_rate": random.uniform(0.05, 0.30),
                "campaign_id": f"campaign_{random.randint(1, 10)}",
                "user_id": f"user_{random.randint(1, 4)}",
                "autonomous_generated": True,
                "quantum_optimized": random.choice([True, False])
            }
            
            self.seeded_data["revenue_records"].append(revenue_record)
        
        logger.info(f"Created {len(self.seeded_data['revenue_records'])} revenue records")
    
    async def seed_blog_posts(self):
        """Seed blog posts using AI generator"""
        logger.info("Seeding AI-generated blog posts...")
        
        # Generate blog posts using the AI blog generator
        generated_posts = await blog_generator.generate_multiple_posts(10)
        
        for post in generated_posts:
            blog_record = {
                "id": post["id"],
                "title": post["title"],
                "slug": post["slug"],
                "content": post["content"],
                "excerpt": post["excerpt"],
                "author": post["author"],
                "topic": post["topic"],
                "status": post["status"],
                "created_at": post["created_at"],
                "word_count": post["word_count"],
                "estimated_read_time": post["estimated_read_time"],
                "tags": post["tags"],
                "seo_metadata": post["seo"],
                "autonomous_generated": True,
                "ai_optimized": True
            }
            
            self.seeded_data["blog_posts"].append(blog_record)
        
        logger.info(f"Created {len(self.seeded_data['blog_posts'])} AI-generated blog posts")
    
    async def seed_affiliate_campaigns(self):
        """Seed affiliate campaign data"""
        logger.info("Seeding affiliate campaigns...")
        
        campaign_types = ["tech_products", "health_wellness", "finance", "education", "software"]
        campaign_statuses = ["active", "paused", "completed", "draft"]
        
        for i in range(15):
            campaign_record = {
                "id": f"campaign_{i+1}",
                "name": f"{random.choice(campaign_types).replace('_', ' ').title()} Campaign {i+1}",
                "type": random.choice(campaign_types),
                "status": random.choice(campaign_statuses),
                "budget": round(random.uniform(100.0, 10000.0), 2),
                "spent": round(random.uniform(50.0, 8000.0), 2),
                "revenue": round(random.uniform(200.0, 15000.0), 2),
                "commission_rate": random.uniform(0.05, 0.25),
                "click_count": random.randint(100, 10000),
                "conversion_count": random.randint(10, 500),
                "conversion_rate": random.uniform(0.01, 0.08),
                "created_at": (datetime.utcnow() - timedelta(days=random.randint(1, 60))).isoformat(),
                "updated_at": (datetime.utcnow() - timedelta(days=random.randint(0, 30))).isoformat(),
                "autonomous_managed": True,
                "ai_optimized": True,
                "quantum_enhanced": random.choice([True, False])
            }
            
            self.seeded_data["affiliate_campaigns"].append(campaign_record)
        
        logger.info(f"Created {len(self.seeded_data['affiliate_campaigns'])} affiliate campaigns")
    
    async def get_seeding_summary(self) -> Dict:
        """Get summary of seeded data"""
        return {
            "total_users": len(self.seeded_data["users"]),
            "total_quantum_research": len(self.seeded_data["quantum_research"]),
            "total_revenue_records": len(self.seeded_data["revenue_records"]),
            "total_blog_posts": len(self.seeded_data["blog_posts"]),
            "total_affiliate_campaigns": len(self.seeded_data["affiliate_campaigns"]),
            "seeding_completed": True,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_seeded_data(self) -> Dict:
        """Get all seeded data"""
        return self.seeded_data

# Global database seeder instance
db_seeder = DatabaseSeeder()

# Main seeding function
async def main():
    """Main function to run database seeding"""
    try:
        await db_seeder.seed_all()
        summary = await db_seeder.get_seeding_summary()
        print("Database Seeding Summary:")
        print(f"- Users: {summary['total_users']}")
        print(f"- Quantum Research: {summary['total_quantum_research']}")
        print(f"- Revenue Records: {summary['total_revenue_records']}")
        print(f"- Blog Posts: {summary['total_blog_posts']}")
        print(f"- Affiliate Campaigns: {summary['total_affiliate_campaigns']}")
        print("Seeding completed successfully!")
        
    except Exception as e:
        print(f"Seeding failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
