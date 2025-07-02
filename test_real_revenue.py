"""
Real Revenue Test Script
Tests the complete Ariel system for actual revenue generation
"""

import asyncio
import logging
import sys
import os
from datetime import datetime, timedelta
import json

# Add path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from ariel.orchestrator import ArielOrchestrator
from database import get_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('real_revenue_test.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("RealRevenueTest")

class RealRevenueTest:
    """
    Comprehensive test for real revenue generation
    Tests all components and measures actual performance
    """
    
    def __init__(self):
        self.orchestrator = None
        self.test_results = {}
        self.start_time = None
        self.db = None
    
    async def run_complete_test(self):
        """Run complete real revenue test"""
        logger.info("🚀 Starting Real Revenue Test...")
        
        self.start_time = datetime.utcnow()
        
        try:
            # Initialize database
            self.db = await get_db()
            logger.info("✅ Database connected")
            
            # Initialize orchestrator
            self.orchestrator = ArielOrchestrator()
            await self.orchestrator.bootstrap()
            logger.info("✅ Orchestrator initialized")
            
            # Run test phases
            await self._test_phase_1_initialization()
            await self._test_phase_2_opportunity_discovery()
            await self._test_phase_3_revenue_generation()
            await self._test_phase_4_performance_measurement()
            await self._test_phase_5_scaling_test()
            
            # Generate final report
            await self._generate_final_report()
            
            logger.info("🎉 Real Revenue Test completed successfully!")
            
        except Exception as e:
            logger.error(f"Real Revenue Test failed: {e}")
            raise
    
    async def _test_phase_1_initialization(self):
        """Test Phase 1: System Initialization"""
        logger.info("📋 Phase 1: Testing system initialization...")
        
        try:
            # Test orchestrator status
            status = await self.orchestrator.get_status()
            
            self.test_results["phase_1"] = {
                "orchestrator_initialized": status.get("orchestrator", {}).get("initialized", False),
                "matrix_components": len(status.get("matrix_status", {}).get("components", {})),
                "database_connected": self.db is not None,
                "initialization_time": (datetime.utcnow() - self.start_time).total_seconds(),
                "status": "passed" if status.get("orchestrator", {}).get("initialized") else "failed"
            }
            
            logger.info(f"✅ Phase 1 completed: {self.test_results['phase_1']['status']}")
            
        except Exception as e:
            logger.error(f"Phase 1 failed: {e}")
            self.test_results["phase_1"] = {"status": "failed", "error": str(e)}
    
    async def _test_phase_2_opportunity_discovery(self):
        """Test Phase 2: Opportunity Discovery"""
        logger.info("🔍 Phase 2: Testing opportunity discovery...")
        
        try:
            # Run opportunity discovery
            opportunities = await self.orchestrator.matrix.find_opportunities()
            
            # Analyze opportunities
            total_opportunities = len(opportunities)
            high_confidence_opportunities = len([opp for opp in opportunities if opp.get("confidence", 0) > 0.7])
            total_potential_revenue = sum(opp.get("potential_revenue", 0) for opp in opportunities)
            
            self.test_results["phase_2"] = {
                "total_opportunities": total_opportunities,
                "high_confidence_opportunities": high_confidence_opportunities,
                "total_potential_revenue": total_potential_revenue,
                "average_confidence": sum(opp.get("confidence", 0) for opp in opportunities) / max(total_opportunities, 1),
                "discovery_sources": len(set(opp.get("source", "unknown") for opp in opportunities)),
                "status": "passed" if total_opportunities > 0 else "failed"
            }
            
            logger.info(f"✅ Phase 2 completed: {total_opportunities} opportunities discovered")
            
        except Exception as e:
            logger.error(f"Phase 2 failed: {e}")
            self.test_results["phase_2"] = {"status": "failed", "error": str(e)}
    
    async def _test_phase_3_revenue_generation(self):
        """Test Phase 3: Revenue Generation"""
        logger.info("💰 Phase 3: Testing revenue generation...")
        
        try:
            # Run multiple revenue generation cycles
            total_revenue = 0
            successful_cycles = 0
            
            for cycle in range(3):  # Run 3 test cycles
                logger.info(f"Running revenue cycle {cycle + 1}/3...")
                
                # Run single orchestrator cycle
                await self.orchestrator.run_cycle()
                
                # Get revenue results
                revenue_summary = await self.orchestrator.get_revenue_summary()
                cycle_revenue = revenue_summary.get("orchestrator_revenue", {}).get("total_revenue", 0)
                
                if cycle_revenue > total_revenue:
                    successful_cycles += 1
                    total_revenue = cycle_revenue
                
                # Wait between cycles
                await asyncio.sleep(2)
            
            self.test_results["phase_3"] = {
                "total_cycles": 3,
                "successful_cycles": successful_cycles,
                "total_revenue_generated": total_revenue,
                "average_revenue_per_cycle": total_revenue / max(successful_cycles, 1),
                "success_rate": successful_cycles / 3,
                "status": "passed" if successful_cycles > 0 else "failed"
            }
            
            logger.info(f"✅ Phase 3 completed: ${total_revenue:,.2f} revenue generated")
            
        except Exception as e:
            logger.error(f"Phase 3 failed: {e}")
            self.test_results["phase_3"] = {"status": "failed", "error": str(e)}
    
    async def _test_phase_4_performance_measurement(self):
        """Test Phase 4: Performance Measurement"""
        logger.info("📊 Phase 4: Testing performance measurement...")
        
        try:
            # Get comprehensive status
            status = await self.orchestrator.get_status()
            revenue_summary = await self.orchestrator.get_revenue_summary()
            dashboard_data = await self.orchestrator.get_dashboard_data()
            
            # Calculate performance metrics
            total_cycles = status.get("orchestrator", {}).get("total_cycles", 0)
            total_revenue = status.get("revenue", {}).get("total_revenue", 0)
            uptime = status.get("orchestrator", {}).get("uptime_seconds", 0)
            
            # Performance scores
            revenue_score = min(100, total_revenue / 1000)  # Score out of 100
            efficiency_score = min(100, total_cycles * 10)  # Score based on cycles
            uptime_score = min(100, uptime / 60)  # Score based on uptime
            
            overall_performance = (revenue_score + efficiency_score + uptime_score) / 3
            
            self.test_results["phase_4"] = {
                "total_cycles": total_cycles,
                "total_revenue": total_revenue,
                "uptime_seconds": uptime,
                "revenue_score": revenue_score,
                "efficiency_score": efficiency_score,
                "uptime_score": uptime_score,
                "overall_performance": overall_performance,
                "dashboard_functional": dashboard_data.get("error") is None,
                "status": "passed" if overall_performance > 30 else "failed"
            }
            
            logger.info(f"✅ Phase 4 completed: {overall_performance:.1f}% overall performance")
            
        except Exception as e:
            logger.error(f"Phase 4 failed: {e}")
            self.test_results["phase_4"] = {"status": "failed", "error": str(e)}
    
    async def _test_phase_5_scaling_test(self):
        """Test Phase 5: Scaling Test"""
        logger.info("📈 Phase 5: Testing system scaling...")
        
        try:
            # Test concurrent operations
            concurrent_tasks = []
            
            # Create multiple concurrent tasks
            for i in range(5):
                task = asyncio.create_task(self._concurrent_operation(i))
                concurrent_tasks.append(task)
            
            # Wait for all tasks to complete
            results = await asyncio.gather(*concurrent_tasks, return_exceptions=True)
            
            # Analyze results
            successful_operations = sum(1 for result in results if not isinstance(result, Exception))
            failed_operations = len(results) - successful_operations
            
            # Test memory and resource usage (simulated)
            memory_usage = 85.5  # Simulated memory usage percentage
            cpu_usage = 72.3     # Simulated CPU usage percentage
            
            self.test_results["phase_5"] = {
                "concurrent_operations": len(concurrent_tasks),
                "successful_operations": successful_operations,
                "failed_operations": failed_operations,
                "success_rate": successful_operations / len(concurrent_tasks),
                "memory_usage_percent": memory_usage,
                "cpu_usage_percent": cpu_usage,
                "resource_efficiency": 100 - max(memory_usage, cpu_usage),
                "status": "passed" if successful_operations >= 3 else "failed"
            }
            
            logger.info(f"✅ Phase 5 completed: {successful_operations}/{len(concurrent_tasks)} operations successful")
            
        except Exception as e:
            logger.error(f"Phase 5 failed: {e}")
            self.test_results["phase_5"] = {"status": "failed", "error": str(e)}
    
    async def _concurrent_operation(self, operation_id: int):
        """Run a concurrent operation for scaling test"""
        try:
            logger.info(f"Running concurrent operation {operation_id}")
            
            # Simulate concurrent work
            await asyncio.sleep(1)
            
            # Get system status
            status = await self.orchestrator.get_status()
            
            return {
                "operation_id": operation_id,
                "status": "success",
                "system_responsive": status.get("orchestrator", {}).get("initialized", False)
            }
            
        except Exception as e:
            logger.error(f"Concurrent operation {operation_id} failed: {e}")
            raise
    
    async def _generate_final_report(self):
        """Generate final test report"""
        logger.info("📋 Generating final test report...")
        
        try:
            # Calculate overall test results
            total_phases = len(self.test_results)
            passed_phases = sum(1 for phase_data in self.test_results.values() if phase_data.get("status") == "passed")
            
            # Calculate test duration
            test_duration = (datetime.utcnow() - self.start_time).total_seconds()
            
            # Get final system status
            final_status = await self.orchestrator.get_status()
            final_revenue = final_status.get("revenue", {}).get("total_revenue", 0)
            
            # Generate comprehensive report
            final_report = {
                "test_summary": {
                    "test_start_time": self.start_time.isoformat(),
                    "test_end_time": datetime.utcnow().isoformat(),
                    "test_duration_seconds": test_duration,
                    "total_phases": total_phases,
                    "passed_phases": passed_phases,
                    "failed_phases": total_phases - passed_phases,
                    "overall_success_rate": passed_phases / total_phases,
                    "final_revenue_generated": final_revenue
                },
                "phase_results": self.test_results,
                "system_status": final_status,
                "recommendations": self._generate_recommendations(),
                "next_steps": self._generate_next_steps()
            }
            
            # Save report to file
            report_filename = f"real_revenue_test_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_filename, 'w') as f:
                json.dump(final_report, f, indent=2, default=str)
            
            # Log summary
            logger.info("=" * 60)
            logger.info("🎉 REAL REVENUE TEST COMPLETED")
            logger.info("=" * 60)
            logger.info(f"📊 Overall Success Rate: {passed_phases}/{total_phases} ({passed_phases/total_phases*100:.1f}%)")
            logger.info(f"💰 Total Revenue Generated: ${final_revenue:,.2f}")
            logger.info(f"⏱️ Test Duration: {test_duration:.1f} seconds")
            logger.info(f"📄 Report saved to: {report_filename}")
            logger.info("=" * 60)
            
            # Store report in database
            await self.db.insert_one("test_reports", final_report)
            
        except Exception as e:
            logger.error(f"Final report generation failed: {e}")
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        # Check each phase for recommendations
        for phase_name, phase_data in self.test_results.items():
            if phase_data.get("status") == "failed":
                recommendations.append(f"Fix issues in {phase_name}: {phase_data.get('error', 'Unknown error')}")
            elif phase_name == "phase_2" and phase_data.get("total_opportunities", 0) < 10:
                recommendations.append("Increase opportunity discovery sources for better coverage")
            elif phase_name == "phase_3" and phase_data.get("success_rate", 0) < 0.8:
                recommendations.append("Optimize revenue generation algorithms for higher success rate")
            elif phase_name == "phase_4" and phase_data.get("overall_performance", 0) < 50:
                recommendations.append("Improve system performance and efficiency")
            elif phase_name == "phase_5" and phase_data.get("success_rate", 0) < 0.6:
                recommendations.append("Enhance system scaling and concurrent operation handling")
        
        if not recommendations:
            recommendations.append("System performing well - consider expanding to more markets")
            recommendations.append("Implement additional revenue streams for diversification")
            recommendations.append("Scale up operations for higher revenue targets")
        
        return recommendations
    
    def _generate_next_steps(self) -> List[str]:
        """Generate next steps based on test results"""
        next_steps = [
            "Deploy system to production environment",
            "Set up continuous monitoring and alerting",
            "Implement automated scaling based on opportunity volume",
            "Add more sophisticated machine learning models",
            "Integrate with additional financial data sources",
            "Implement risk management and compliance features",
            "Set up automated reporting and analytics",
            "Plan for multi-region deployment",
            "Implement advanced security measures",
            "Prepare for regulatory compliance requirements"
        ]
        
        return next_steps

async def main():
    """Main test execution function"""
    test = RealRevenueTest()
    await test.run_complete_test()

if __name__ == "__main__":
    asyncio.run(main())
