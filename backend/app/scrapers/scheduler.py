"""Background scheduler for periodic data updates."""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, Callable, List, Dict, Any

logger = logging.getLogger(__name__)


class ScraperScheduler:
    """Scheduler for running scraper tasks at intervals."""
    
    def __init__(self, enable_logging: bool = True):
        """
        Initialize scheduler.
        
        Args:
            enable_logging: Whether to log scheduled tasks
        """
        self.tasks: Dict[str, Dict[str, Any]] = {}
        self.is_running = False
        self.enable_logging = enable_logging
    
    def schedule_task(
        self,
        task_name: str,
        task_func: Callable,
        interval_minutes: int,
        run_immediately: bool = False
    ) -> None:
        """
        Schedule a task to run at regular intervals.
        
        Args:
            task_name: Name of the task
            task_func: Async function to execute
            interval_minutes: Interval between executions in minutes
            run_immediately: Whether to run immediately
        """
        self.tasks[task_name] = {
            "func": task_func,
            "interval": timedelta(minutes=interval_minutes),
            "last_run": datetime.now() if run_immediately else datetime.now() - timedelta(minutes=interval_minutes),
            "run_count": 0,
            "error_count": 0,
            "next_run": datetime.now() if run_immediately else datetime.now() + timedelta(minutes=interval_minutes)
        }
        
        if self.enable_logging:
            logger.info(f"Scheduled task '{task_name}' to run every {interval_minutes} minutes")
    
    async def start(self) -> None:
        """Start the scheduler loop."""
        if self.is_running:
            logger.warning("Scheduler already running")
            return
        
        self.is_running = True
        logger.info("🚀 Scraper scheduler started")
        
        try:
            while self.is_running:
                await self._check_and_run_tasks()
                await asyncio.sleep(60)  # Check every minute
        except Exception as e:
            logger.error(f"Scheduler error: {e}")
            self.is_running = False
    
    async def _check_and_run_tasks(self) -> None:
        """Check and run tasks that are due."""
        now = datetime.now()
        
        for task_name, task_info in self.tasks.items():
            if now >= task_info["next_run"]:
                await self._run_task(task_name, task_info)
    
    async def _run_task(self, task_name: str, task_info: Dict[str, Any]) -> None:
        """
        Run a single task.
        
        Args:
            task_name: Name of the task
            task_info: Task information
        """
        try:
            if self.enable_logging:
                logger.info(f"⏱️ Running task: {task_name}")
            
            # Run the task
            await task_info["func"]()
            
            # Update task info
            task_info["run_count"] += 1
            task_info["last_run"] = datetime.now()
            task_info["next_run"] = datetime.now() + task_info["interval"]
            
            if self.enable_logging:
                logger.info(f"✅ Task '{task_name}' completed (Run #{task_info['run_count']})")
        
        except Exception as e:
            task_info["error_count"] += 1
            logger.error(f"❌ Task '{task_name}' failed: {e}")
            # Reschedule for retry
            task_info["next_run"] = datetime.now() + timedelta(minutes=5)
    
    async def stop(self) -> None:
        """Stop the scheduler."""
        self.is_running = False
        logger.info("⏹️ Scraper scheduler stopped")
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get scheduler status.
        
        Returns:
            Status dictionary
        """
        tasks_status = {}
        for task_name, task_info in self.tasks.items():
            tasks_status[task_name] = {
                "run_count": task_info["run_count"],
                "error_count": task_info["error_count"],
                "last_run": task_info["last_run"].isoformat(),
                "next_run": task_info["next_run"].isoformat(),
                "interval_minutes": int(task_info["interval"].total_seconds() / 60)
            }
        
        return {
            "is_running": self.is_running,
            "tasks_count": len(self.tasks),
            "tasks": tasks_status
        }
    
    def get_task_info(self, task_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific task.
        
        Args:
            task_name: Name of the task
            
        Returns:
            Task information or None if not found
        """
        if task_name not in self.tasks:
            return None
        
        task_info = self.tasks[task_name]
        return {
            "name": task_name,
            "run_count": task_info["run_count"],
            "error_count": task_info["error_count"],
            "last_run": task_info["last_run"].isoformat(),
            "next_run": task_info["next_run"].isoformat(),
            "interval_minutes": int(task_info["interval"].total_seconds() / 60)
        }


# Global scheduler instance
_scheduler_instance: Optional[ScraperScheduler] = None


def get_scheduler() -> ScraperScheduler:
    """
    Get or create the global scheduler instance.
    
    Returns:
        ScraperScheduler instance
    """
    global _scheduler_instance
    if _scheduler_instance is None:
        _scheduler_instance = ScraperScheduler()
    return _scheduler_instance
