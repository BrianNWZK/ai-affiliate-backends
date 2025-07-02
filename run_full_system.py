"""
Complete Ariel System Startup Script
Initializes database, starts API server, and runs Ariel orchestrator
"""
import asyncio
import logging
import sys
import os
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor

# Add paths for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ArielSystem")

async def initialize_database():
    """Initialize the QuantumInfinityDB"""
    logger.info("Initializing QuantumInfinityDB...")
    try:
        from database import get_db
        db = await get_db()
        logger.info("Database initialized successfully!")
        return True
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False

def run_api_server():
    """Run the FastAPI server"""
    logger.info("Starting FastAPI server...")
    try:
        import uvicorn
        from main import app
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
    except Exception as e:
        logger.error(f"API server failed: {e}")

async def run_ariel_standalone():
    """Run Ariel orchestrator in standalone mode"""
    logger.info("Starting Ariel orchestrator...")
    try:
        from ariel.orchestrator import ArielOrchestrator
        ariel = ArielOrchestrator()
        await ariel.run_forever()
    except Exception as e:
        logger.error(f"Ariel orchestrator failed: {e}")

async def main():
    """Main startup sequence"""
    logger.info("🚀 Starting Complete Ariel System...")
    
    # Initialize database first
    db_success = await initialize_database()
    if not db_success:
        logger.error("Failed to initialize database. Exiting.")
        return
    
    print("\n" + "="*60)
    print("🎯 ARIEL AUTONOMOUS REVENUE ORCHESTRATOR")
    print("="*60)
    print("Choose startup mode:")
    print("1. Full System (API Server + Ariel Background)")
    print("2. API Server Only")
    print("3. Ariel Orchestrator Only")
    print("4. Database Test Only")
    print("="*60)
    
    choice = input("Enter your choice (1-4): ").strip()
    
    if choice == "1":
        logger.info("Starting Full System Mode...")
        # Run API server (which includes Ariel in background)
        run_api_server()
        
    elif choice == "2":
        logger.info("Starting API Server Only...")
        run_api_server()
        
    elif choice == "3":
        logger.info("Starting Ariel Orchestrator Only...")
        await run_ariel_standalone()
        
    elif choice == "4":
        logger.info("Running Database Test...")
        await test_database()
        
    else:
        logger.error("Invalid choice. Exiting.")

async def test_database():
    """Test database functionality"""
    logger.info("Testing database operations...")
    
    try:
        from database import get_db
        db = await get_db()
        
        # Test insert
        test_data = {
            "test": True,
            "timestamp": "2025-01-02T11:46:23Z",
            "message": "Database test successful"
        }
        
        await db.insert_one("ariel_logs", test_data)
        logger.info("✅ Insert test passed")
        
        # Test find
        result = await db.find_one("ariel_logs")
        if result:
            logger.info("✅ Find test passed")
        else:
            logger.warning("⚠️ Find test returned no results")
        
        # Test list
        logs = await db.to_list("ariel_logs", 5)
        logger.info(f"✅ List test passed - found {len(logs)} records")
        
        # Test self-repair
        await db.self_repair()
        logger.info("✅ Self-repair test passed")
        
        logger.info("🎉 All database tests passed!")
        
    except Exception as e:
        logger.error(f"❌ Database test failed: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("System shutdown requested by user")
    except Exception as e:
        logger.error(f"System startup failed: {e}")
