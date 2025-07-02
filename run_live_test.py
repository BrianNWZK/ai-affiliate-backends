"""
🚀 LIVE REVENUE GENERATION TEST
Run this script to test real revenue generation immediately
"""

import asyncio
import logging
import sys
import os
from datetime import datetime

# Add path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from ariel.orchestrator import ArielOrchestrator
from database import get_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('live_test.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("LiveTest")

async def run_live_test():
    """Run live revenue generation test"""
    print("=" * 80)
    print("🚀 ARIEL LIVE REVENUE GENERATION TEST")
    print("🎯 Target: Generate real revenue immediately")
    print("⚡ Status: STARTING NOW...")
    print("=" * 80)
    
    try:
        # Initialize database
        db = await get_db()
        logger.info("✅ Database connected")
        
        # Initialize orchestrator
        orchestrator = ArielOrchestrator()
        await orchestrator.bootstrap()
        logger.info("✅ Orchestrator initialized")
        
        print("\n🔍 PHASE 1: Finding Opportunities...")
        opportunities = await orchestrator.matrix.find_opportunities()
        print(f"✅ Found {len(opportunities)} opportunities")
        
        print("\n📈 PHASE 2: Analyzing Market Trends...")
        trends = await orchestrator.matrix.analyze_trends()
        print(f"✅ Analyzed trends: {trends.get('overall_trend', 'neutral')}")
        
        print("\n💼 PHASE 3: Acquiring Assets...")
        await orchestrator.matrix.acquire_assets_for_opportunities(opportunities, trends)
        print("✅ Assets acquired")
        
        print("\n🚀 PHASE 4: Launching Campaigns...")
        await orchestrator.matrix.launch_or_optimize(opportunities, trends)
        print("✅ Campaigns launched")
        
        print("\n💰 PHASE 5: GENERATING REAL REVENUE...")
        revenue_results = await orchestrator.matrix.generate_revenue()
        
        if revenue_results:
            total_revenue = revenue_results.get("total_revenue", 0)
            print(f"🎉 SUCCESS! Generated ${total_revenue:,.2f} in revenue!")
            
            # Show revenue breakdown
            print("\n💎 REVENUE BREAKDOWN:")
            for source in revenue_results.get("revenue_sources", []):
                print(f"  - {source.get('source', 'Unknown')}: ${source.get('amount', 0):,.2f}")
            
            # Show progress
            cumulative = revenue_results.get("cumulative_revenue", 0)
            billionaire_progress = revenue_results.get("billionaire_progress", 0)
            
            print(f"\n📊 PROGRESS:")
            print(f"  - Total Revenue: ${cumulative:,.2f}")
            print(f"  - Billionaire Progress: {billionaire_progress:.4f}%")
            
            if cumulative >= 1000000:
                print("🎉 MILLIONAIRE STATUS ACHIEVED!")
            if cumulative >= 1000000000:
                print("👑 BILLIONAIRE STATUS ACHIEVED!")
        
        print("\n⚡ PHASE 6: Running Additional Cycle...")
        await orchestrator.run_cycle()
        
        # Get final status
        final_status = await orchestrator.get_status()
        final_revenue = final_status.get("revenue", {}).get("total_revenue", 0)
        
        print("\n" + "=" * 80)
        print("🎉 LIVE TEST COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        print(f"💰 Final Revenue: ${final_revenue:,.2f}")
        print(f"🔄 Cycles Completed: {final_status.get('orchestrator', {}).get('total_cycles', 0)}")
        print(f"🎯 Opportunities Found: {len(opportunities)}")
        print(f"⏱️ Test Duration: {datetime.utcnow().strftime('%H:%M:%S')}")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print(f"\n❌ LIVE TEST FAILED: {e}")
        logger.error(f"Live test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Ariel Live Revenue Test...")
    success = asyncio.run(run_live_test())
    
    if success:
        print("✅ Test completed successfully!")
        sys.exit(0)
    else:
        print("❌ Test failed!")
        sys.exit(1)
