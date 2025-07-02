import asyncio
import logging
import sys
import os

# Add the ariel directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'ariel'))

from orchestrator import ArielOrchestrator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ArielTest")

async def test_ariel_components():
    """Test individual Ariel components"""
    logger.info("Testing Ariel components...")
    
    ariel = ArielOrchestrator()
    
    try:
        # Test bootstrap
        logger.info("Testing bootstrap...")
        await ariel.bootstrap()
        
        # Test single cycle
        logger.info("Testing single cycle...")
        await ariel.run_cycle()
        
        # Test status
        status = await ariel.get_status()
        logger.info(f"System status: {status}")
        
        # Test dashboard data
        activities = await ariel.dashboard.get_recent_activities(5)
        logger.info(f"Recent activities: {len(activities)} found")
        
        logger.info("All tests passed!")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        raise

async def run_limited_cycles():
    """Run Ariel for a limited number of cycles for testing"""
    logger.info("Running Ariel for 3 test cycles...")
    
    ariel = ArielOrchestrator()
    ariel.cycle_time = 10  # 10 seconds for testing
    
    try:
        await ariel.bootstrap()
        
        # Run 3 cycles
        for i in range(3):
            logger.info(f"Starting test cycle {i+1}/3")
            await ariel.run_cycle()
            await asyncio.sleep(5)  # Short sleep between cycles
            
        logger.info("Limited cycle test completed successfully!")
        
    except Exception as e:
        logger.error(f"Limited cycle test failed: {e}")
        raise

if __name__ == "__main__":
    print("Ariel Test Suite")
    print("1. Test components")
    print("2. Run limited cycles")
    
    choice = input("Choose test (1 or 2): ").strip()
    
    if choice == "1":
        asyncio.run(test_ariel_components())
    elif choice == "2":
        asyncio.run(run_limited_cycles())
    else:
        print("Invalid choice")
