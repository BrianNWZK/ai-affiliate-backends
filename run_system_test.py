#!/usr/bin/env python3
"""
Quick system test runner
Tests all components before starting real revenue generation
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.test_system import run_quick_test, SystemTester

async def main():
    print("🚀 ARIEL SYSTEM - QUICK TEST")
    print("=" * 40)
    
    # Run quick test first
    success = await run_quick_test()
    
    if success:
        print("\n✅ SYSTEM READY!")
        print("\nNext steps:")
        print("1. Run full system: python scripts/run_full_system.py")
        print("2. Start API server: python main.py")
        print("3. View dashboard: http://localhost:8000/docs")
        print("\n💰 Ready to generate REAL REVENUE!")
    else:
        print("\n❌ SYSTEM NOT READY")
        print("Run comprehensive tests: python scripts/test_system.py")

if __name__ == "__main__":
    asyncio.run(main())
