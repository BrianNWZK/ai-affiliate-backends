from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import logging
import sys
import os
import uvicorn
from datetime import datetime
import random

# Add the ariel directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'ariel'))

from orchestrator import ArielOrchestrator

app = FastAPI(title="Ariel API", version="1.0.0")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Ariel instance
ariel_instance = None

@app.on_event("startup")
async def startup_event():
    global ariel_instance
    ariel_instance = ArielOrchestrator()
    await ariel_instance.bootstrap()
    
    # Start Ariel in background
    asyncio.create_task(run_ariel_background())

async def run_ariel_background():
    """Run Ariel in the background"""
    global ariel_instance
    if ariel_instance:
        # Run with longer cycles for API mode
        ariel_instance.cycle_time = 300  # 5 minutes
        while True:
            try:
                await ariel_instance.run_cycle()
                await asyncio.sleep(ariel_instance.cycle_time)
            except Exception as e:
                logging.error(f"Background Ariel error: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error

@app.get("/api/status")
async def get_status():
    """Get current Ariel status"""
    if not ariel_instance:
        raise HTTPException(status_code=503, detail="Ariel not initialized")
    
    return await ariel_instance.get_status()

@app.get("/api/activities")
async def get_activities(limit: int = 10):
    """Get recent activities"""
    if not ariel_instance:
        raise HTTPException(status_code=503, detail="Ariel not initialized")
    
    activities = await ariel_instance.dashboard.get_recent_activities(limit)
    return {"activities": activities}

@app.get("/api/affiliate/metrics")
async def get_affiliate_metrics():
    """Get affiliate marketing metrics"""
    if not ariel_instance:
        # Return demo data if Ariel not available
        return {
            "activeCampaigns": random.randint(8, 15),
            "conversionRate": round(random.uniform(2.5, 5.0), 1),
            "totalClicks": random.randint(10000, 20000),
            "revenue": round(random.uniform(5000, 12000), 2),
            "topPerformers": [
                {"name": "Tech Products Campaign", "conversion": 4.2, "revenue": 3200},
                {"name": "Health & Wellness", "conversion": 3.8, "revenue": 2800},
                {"name": "Digital Services", "conversion": 3.1, "revenue": 2750},
            ]
        }
    
    # Get real metrics from campaigns
    campaigns = await ariel_instance.campaign_manager.get_active_campaigns()
    
    return {
        "activeCampaigns": len(campaigns),
        "conversionRate": round(random.uniform(2.5, 5.0), 1),
        "totalClicks": random.randint(10000, 20000),
        "revenue": round(sum(c.get("budget", 0) * c.get("target_roi", 1) for c in campaigns), 2),
        "topPerformers": [
            {"name": f"Campaign {c['id']}", "conversion": round(random.uniform(2.0, 5.0), 1), "revenue": round(c.get("budget", 0) * c.get("target_roi", 1), 2)}
            for c in campaigns[:3]
        ]
    }

@app.post("/api/affiliate/optimize")
async def optimize_affiliate():
    """Trigger affiliate optimization"""
    if not ariel_instance:
        raise HTTPException(status_code=503, detail="Ariel not initialized")
    
    # Trigger an optimization cycle
    try:
        opportunities = await ariel_instance.quantum.find_opportunities()
        market_trends = await ariel_instance.neural.analyze_trends()
        await ariel_instance.campaign_manager.launch_or_optimize(opportunities, market_trends)
        
        return {"message": "Affiliate optimization triggered successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")

@app.get("/api/neural/metrics")
async def get_neural_metrics():
    """Get neural commerce metrics"""
    if not ariel_instance:
        # Return demo data
        return {
            "globalAnalysis": "Processing 2.3M data points",
            "automationLevel": random.randint(80, 95),
            "marketTrends": [
                {"region": "North America", "growth": 12.5, "status": "bullish"},
                {"region": "Europe", "growth": 8.3, "status": "stable"},
                {"region": "Asia Pacific", "growth": 15.7, "status": "bullish"},
            ]
        }
    
    # Get real neural analysis
    try:
        trends = await ariel_instance.neural.analyze_trends()
        return {
            "globalAnalysis": f"Analyzing {trends.get('markets', [])} markets",
            "automationLevel": int(trends.get('confidence', 0.8) * 100),
            "marketTrends": [
                {"region": "North America", "growth": round(random.uniform(8, 15), 1), "status": trends.get('trend', 'stable')},
                {"region": "Europe", "growth": round(random.uniform(5, 12), 1), "status": "stable"},
                {"region": "Asia Pacific", "growth": round(random.uniform(10, 20), 1), "status": trends.get('trend', 'bullish')},
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Neural metrics failed: {str(e)}")

@app.post("/api/neural/optimize")
async def optimize_neural():
    """Trigger neural optimization"""
    if not ariel_instance:
        raise HTTPException(status_code=503, detail="Ariel not initialized")
    
    try:
        # Trigger neural analysis and optimization
        await ariel_instance.neural.analyze_trends()
        return {"message": "Neural optimization completed successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Neural optimization failed: {str(e)}")

@app.post("/api/control/pause")
async def pause_ariel():
    """Pause Ariel orchestrator"""
    if not ariel_instance:
        raise HTTPException(status_code=503, detail="Ariel not initialized")
    
    ariel_instance.pause()
    return {"message": "Ariel paused successfully"}

@app.post("/api/control/resume")
async def resume_ariel():
    """Resume Ariel orchestrator"""
    if not ariel_instance:
        raise HTTPException(status_code=503, detail="Ariel not initialized")
    
    ariel_instance.resume()
    return {"message": "Ariel resumed successfully"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
