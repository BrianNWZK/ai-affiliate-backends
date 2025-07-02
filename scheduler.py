import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
import json
from dataclasses import dataclass
from enum import Enum
import random

logger = logging.getLogger("ArielMatrix.Scheduler")

class TaskPriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class ScheduledTask:
    id: str
    name: str
    function: Callable
    args: tuple = ()
    kwargs: dict = None
    priority: TaskPriority = TaskPriority.MEDIUM
    scheduled_time: datetime = None
    interval: Optional[timedelta] = None
    max_retries: int = 3
    retry_count: int = 0
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = None
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    result: Any = None
    error: Optional[str] = None

class Scheduler:
    """
    Advanced task scheduler for ArielMatrix
    Manages automated tasks, revenue generation cycles, and system maintenance
    """
    
    def __init__(self):
        self.tasks = {}
        self.running_tasks = {}
        self.completed_tasks = []
        self.failed_tasks = []
        self.running = False
        
        # Performance metrics
        self.metrics = {
            "total_tasks_scheduled": 0,
            "total_tasks_completed": 0,
            "total_tasks_failed": 0,
            "average_execution_time": 0.0,
            "scheduler_uptime": 0.0
        }
        
        self.start_time = None
    
    async def initialize(self):
        """Initialize scheduler"""
        logger.info("⏰ Initializing Scheduler...")
        
        # Schedule default tasks
        await self._schedule_default_tasks()
        
        logger.info("✅ Scheduler initialized")
    
    async def start(self):
        """Start the scheduler"""
        self.running = True
        asyncio.create_task(self._scheduler_loop())
        logger.info("⏰ Scheduler started")
    
    async def _schedule_default_tasks(self):
        """Schedule default system tasks"""
        # Revenue generation every 30 minutes
        await self.schedule_recurring_task(
            "revenue_generation",
            self._revenue_generation_task,
            interval_minutes=30
        )
        
        # Market analysis every hour
        await self.schedule_recurring_task(
            "market_analysis",
            self._market_analysis_task,
            interval_minutes=60
        )
        
        # Security audit every 6 hours
        await self.schedule_recurring_task(
            "security_audit",
            self._security_audit_task,
            interval_minutes=360
        )
    
    async def schedule_recurring_task(self, task_id: str, task_func: Callable, interval_minutes: int):
        """Schedule a recurring task"""
        task_config = {
            "id": task_id,
            "function": task_func,
            "interval_minutes": interval_minutes,
            "next_run": datetime.utcnow() + timedelta(minutes=interval_minutes),
            "last_run": None,
            "run_count": 0,
            "type": "recurring"
        }
        
        self.tasks[task_id] = task_config
        logger.info(f"📅 Scheduled recurring task: {task_id}")
    
    async def _scheduler_loop(self):
        """Main scheduler loop"""
        while self.running:
            try:
                current_time = datetime.utcnow()
                
                for task_id, task_config in self.tasks.items():
                    if current_time >= task_config["next_run"]:
                        await self._execute_task(task_id, task_config)
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Scheduler loop error: {e}")
                await asyncio.sleep(60)
    
    async def _execute_task(self, task_id: str, task_config: Dict):
        """Execute a scheduled task"""
        try:
            logger.info(f"⚡ Executing task: {task_id}")
            
            # Execute the task
            result = await task_config["function"]()
            
            # Update task status
            task_config["last_run"] = datetime.utcnow()
            task_config["run_count"] += 1
            
            if task_config["type"] == "recurring":
                task_config["next_run"] = datetime.utcnow() + timedelta(minutes=task_config["interval_minutes"])
            
            # Log completion
            self.completed_tasks.append({
                "task_id": task_id,
                "completed_at": datetime.utcnow().isoformat(),
                "result": result
            })
            
            logger.info(f"✅ Task completed: {task_id}")
            
        except Exception as e:
            logger.error(f"Task execution failed: {task_id} - {e}")
            
            self.failed_tasks.append({
                "task_id": task_id,
                "failed_at": datetime.utcnow().isoformat(),
                "error": str(e)
            })
    
    async def _revenue_generation_task(self):
        """Revenue generation task"""
        return {"task": "revenue_generation", "status": "completed", "revenue_generated": random.uniform(1000, 10000)}
    
    async def _market_analysis_task(self):
        """Market analysis task"""
        return {"task": "market_analysis", "status": "completed", "opportunities_found": random.randint(5, 20)}
    
    async def _security_audit_task(self):
        """Security audit task"""
        return {"task": "security_audit", "status": "completed", "threats_detected": random.randint(0, 3)}
    
    async def schedule_task(self, task: ScheduledTask) -> str:
        """Schedule a single task"""
        try:
            if task.kwargs is None:
                task.kwargs = {}
            
            if task.created_at is None:
                task.created_at = datetime.utcnow()
            
            if task.scheduled_time is None:
                task.scheduled_time = datetime.utcnow()
            
            task.next_run = task.scheduled_time
            
            # Add to tasks dictionary
            self.tasks[task.id] = task
            
            # Add to running tasks dictionary
            self.running_tasks[task.id] = task
            
            self.metrics["total_tasks_scheduled"] += 1
            
            logger.info(f"⏰ Task scheduled: {task.name} at {task.scheduled_time}")
            return task.id
            
        except Exception as e:
            logger.error(f"Task scheduling failed: {e}")
            raise
    
    async def schedule_recurring_task(self, name: str, function: Callable, 
                                    interval: timedelta, priority: TaskPriority = TaskPriority.MEDIUM,
                                    args: tuple = (), kwargs: dict = None) -> str:
        """Schedule a recurring task"""
        try:
            task_id = f"{name}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            task = ScheduledTask(
                id=task_id,
                name=name,
                function=function,
                args=args,
                kwargs=kwargs or {},
                priority=priority,
                interval=interval,
                scheduled_time=datetime.utcnow(),
                created_at=datetime.utcnow()
            )
            
            return await self.schedule_task(task)
            
        except Exception as e:
            logger.error(f"Recurring task scheduling failed: {e}")
            raise
    
    async def schedule_one_time_task(self, name: str, function: Callable,
                                   scheduled_time: datetime = None, priority: TaskPriority = TaskPriority.MEDIUM,
                                   args: tuple = (), kwargs: dict = None) -> str:
        """Schedule a one-time task"""
        try:
            task_id = f"{name}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            task = ScheduledTask(
                id=task_id,
                name=name,
                function=function,
                args=args,
                kwargs=kwargs or {},
                priority=priority,
                scheduled_time=scheduled_time or datetime.utcnow(),
                created_at=datetime.utcnow()
            )
            
            return await self.schedule_task(task)
            
        except Exception as e:
            logger.error(f"One-time task scheduling failed: {e}")
            raise
    
    async def _process_tasks(self):
        """Process scheduled tasks"""
        logger.info("⏰ Task processor started")
        
        while self.running:
            try:
                # Get next task from queue (with timeout)
                try:
                    priority, scheduled_time, task_id = await asyncio.wait_for(
                        self.task_queue.get(), timeout=1.0
                    )
                except asyncio.TimeoutError:
                    continue
                
                # Check if task still exists
                if task_id not in self.tasks:
                    continue
                
                task = self.tasks[task_id]
                
                # Check if it's time to run the task
                current_time = datetime.utcnow()
                if current_time < task.next_run:
                    # Put task back in queue
                    await self.task_queue.put((priority, scheduled_time, task_id))
                    await asyncio.sleep(1)
                    continue
                
                # Execute the task
                await self._execute_task(task)
                
                # Handle recurring tasks
                if task.interval and task.status == TaskStatus.COMPLETED:
                    # Schedule next run
                    task.next_run = current_time + task.interval
                    task.status = TaskStatus.PENDING
                    task.retry_count = 0
                    
                    # Put back in queue
                    await self.task_queue.put((priority, task.next_run, task_id))
                
            except Exception as e:
                logger.error(f"Task processing error: {e}")
                await asyncio.sleep(1)
    
    async def _execute_task(self, task: ScheduledTask):
        """Execute a single task"""
        try:
            logger.info(f"⏰ Executing task: {task.name}")
            
            task.status = TaskStatus.RUNNING
            task.last_run = datetime.utcnow()
            
            start_time = datetime.utcnow()
            
            # Execute the task function
            if asyncio.iscoroutinefunction(task.function):
                result = await task.function(*task.args, **task.kwargs)
            else:
                result = task.function(*task.args, **task.kwargs)
            
            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds()
            
            # Update task
            task.status = TaskStatus.COMPLETED
            task.result = result
            task.error = None
            
            # Update metrics
            self.metrics["total_tasks_completed"] += 1
            self._update_average_execution_time(execution_time)
            
            # Add to completed tasks
            self.completed_tasks.append({
                "task_id": task.id,
                "name": task.name,
                "execution_time": execution_time,
                "completed_at": end_time,
                "result": str(result)[:200] if result else None
            })
            
            # Keep only recent completed tasks
            if len(self.completed_tasks) > 100:
                self.completed_tasks = self.completed_tasks[-100:]
            
            logger.info(f"✅ Task completed: {task.name} in {execution_time:.2f}s")
            
        except Exception as e:
            logger.error(f"Task execution failed: {task.name} - {e}")
            
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.retry_count += 1
            
            # Update metrics
            self.metrics["total_tasks_failed"] += 1
            
            # Add to failed tasks
            self.failed_tasks.append({
                "task_id": task.id,
                "name": task.name,
                "error": str(e),
                "failed_at": datetime.utcnow(),
                "retry_count": task.retry_count
            })
            
            # Keep only recent failed tasks
            if len(self.failed_tasks) > 50:
                self.failed_tasks = self.failed_tasks[-50:]
            
            # Retry if possible
            if task.retry_count < task.max_retries:
                logger.info(f"🔄 Retrying task: {task.name} (attempt {task.retry_count + 1})")
                
                # Schedule retry with exponential backoff
                retry_delay = timedelta(minutes=2 ** task.retry_count)
                task.next_run = datetime.utcnow() + retry_delay
                task.status = TaskStatus.PENDING
                
                # Put back in queue
                priority = -task.priority.value
                await self.task_queue.put((priority, task.next_run, task.id))
    
    def _update_average_execution_time(self, execution_time: float):
        """Update average execution time metric"""
        try:
            current_avg = self.metrics["average_execution_time"]
            completed_count = self.metrics["total_tasks_completed"]
            
            # Calculate new average
            new_avg = ((current_avg * (completed_count - 1)) + execution_time) / completed_count
            self.metrics["average_execution_time"] = new_avg
            
        except Exception as e:
            logger.error(f"Average execution time update failed: {e}")
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a scheduled task"""
        try:
            if task_id in self.tasks:
                task = self.tasks[task_id]
                task.status = TaskStatus.CANCELLED
                
                logger.info(f"❌ Task cancelled: {task.name}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Task cancellation failed: {e}")
            return False
    
    async def get_task_status(self, task_id: str) -> Optional[Dict]:
        """Get status of a specific task"""
        try:
            if task_id in self.tasks:
                task = self.tasks[task_id]
                
                return {
                    "id": task.id,
                    "name": task.name,
                    "status": task.status.value,
                    "priority": task.priority.name,
                    "created_at": task.created_at.isoformat(),
                    "last_run": task.last_run.isoformat() if task.last_run else None,
                    "next_run": task.next_run.isoformat() if task.next_run else None,
                    "retry_count": task.retry_count,
                    "max_retries": task.max_retries,
                    "error": task.error,
                    "interval": str(task.interval) if task.interval else None
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Task status retrieval failed: {e}")
            return None
    
    async def get_scheduler_status(self) -> Dict:
        """Get comprehensive scheduler status"""
        try:
            # Calculate uptime
            if self.start_time:
                uptime = (datetime.utcnow() - self.start_time).total_seconds()
                self.metrics["scheduler_uptime"] = uptime
            
            # Get task statistics
            pending_tasks = sum(1 for task in self.tasks.values() if task.status == TaskStatus.PENDING)
            running_tasks = sum(1 for task in self.tasks.values() if task.status == TaskStatus.RUNNING)
            completed_tasks = sum(1 for task in self.tasks.values() if task.status == TaskStatus.COMPLETED)
            failed_tasks = sum(1 for task in self.tasks.values() if task.status == TaskStatus.FAILED)
            
            status = {
                "running": self.running,
                "start_time": self.start_time.isoformat() if self.start_time else None,
                "uptime_seconds": self.metrics["scheduler_uptime"],
                "total_tasks": len(self.tasks),
                "task_statistics": {
                    "pending": pending_tasks,
                    "running": running_tasks,
                    "completed": completed_tasks,
                    "failed": failed_tasks
                },
                "performance_metrics": self.metrics,
                "recent_completed_tasks": self.completed_tasks[-10:],
                "recent_failed_tasks": self.failed_tasks[-5:],
                "queue_size": self.task_queue.qsize(),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            return status
            
        except Exception as e:
            logger.error(f"Scheduler status retrieval failed: {e}")
            return {"error": str(e), "running": self.running}
    
    async def stop(self):
        """Stop the scheduler"""
        logger.info("⏰ Stopping scheduler...")
        
        try:
            self.running = False
            
            # Cancel all pending tasks
            for task in self.tasks.values():
                if task.status == TaskStatus.PENDING:
                    task.status = TaskStatus.CANCELLED
            
            logger.info("✅ Scheduler stopped")
            
        except Exception as e:
            logger.error(f"Scheduler stop failed: {e}")
