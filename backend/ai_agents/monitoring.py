from typing import Dict, List, Any, Optional, Set
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
import asyncio
import json
from pathlib import Path
import logging
import psutil
import time
from collections import defaultdict
from .error_handler import error_handler, ErrorMetadata

class MetricValue(BaseModel):
    """Schema for a single metric value."""
    value: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    labels: Dict[str, str] = Field(default_factory=dict)

class Metric(BaseModel):
    """Schema for a metric with its history."""
    name: str
    description: str
    unit: str
    values: List[MetricValue] = Field(default_factory=list)
    alert_threshold: Optional[float] = None

class AgentMetrics(BaseModel):
    """Schema for agent-specific metrics."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time: float = 0.0
    last_error: Optional[str] = None
    last_active: Optional[datetime] = None

class SystemMetrics(BaseModel):
    """Schema for system-wide metrics."""
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    active_conversations: int = 0
    requests_per_minute: float = 0.0
    error_rate: float = 0.0
    uptime: float = 0.0

class Alert(BaseModel):
    """Schema for system alerts."""
    severity: str
    message: str
    metric_name: str
    current_value: float
    threshold_value: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    acknowledged: bool = False

class MonitoringSystem:
    """System monitoring and alerting."""
    
    def __init__(self):
        self.start_time = datetime.utcnow()
        self.metrics_dir = Path("data/metrics")
        self.metrics_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize metrics storage
        self.metrics: Dict[str, Metric] = {}
        self.agent_metrics: Dict[str, AgentMetrics] = defaultdict(AgentMetrics)
        self.system_metrics = SystemMetrics()
        
        # Alert storage
        self.alerts: List[Alert] = []
        self.alert_handlers: Set[callable] = set()
        
        # Configure logging
        self.logger = logging.getLogger(__name__)
        self.setup_logging()
        
        # Define default metrics
        self.define_default_metrics()
        
        # Start background tasks
        asyncio.create_task(self.collect_metrics_loop())
        asyncio.create_task(self.cleanup_old_metrics_loop())

    def setup_logging(self):
        """Set up logging configuration."""
        log_file = self.metrics_dir / "monitoring.log"
        handler = logging.FileHandler(log_file)
        handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def define_default_metrics(self):
        """Define default system metrics."""
        self.add_metric(
            name="cpu_usage",
            description="System CPU usage percentage",
            unit="%",
            alert_threshold=90.0
        )
        self.add_metric(
            name="memory_usage",
            description="System memory usage percentage",
            unit="%",
            alert_threshold=90.0
        )
        self.add_metric(
            name="requests_per_minute",
            description="Number of requests processed per minute",
            unit="requests/min",
            alert_threshold=1000.0
        )
        self.add_metric(
            name="error_rate",
            description="Percentage of requests resulting in errors",
            unit="%",
            alert_threshold=5.0
        )
        self.add_metric(
            name="response_time",
            description="Average response time",
            unit="ms",
            alert_threshold=2000.0
        )

    def add_metric(self, 
                  name: str, 
                  description: str, 
                  unit: str,
                  alert_threshold: Optional[float] = None):
        """Add a new metric to track."""
        self.metrics[name] = Metric(
            name=name,
            description=description,
            unit=unit,
            alert_threshold=alert_threshold
        )

    def record_metric(self, 
                     name: str, 
                     value: float, 
                     labels: Optional[Dict[str, str]] = None):
        """Record a metric value."""
        if name not in self.metrics:
            self.logger.warning(f"Attempting to record unknown metric: {name}")
            return
            
        metric = self.metrics[name]
        metric_value = MetricValue(
            value=value,
            labels=labels or {}
        )
        metric.values.append(metric_value)
        
        # Check alert threshold
        if (metric.alert_threshold is not None and 
            value > metric.alert_threshold):
            self.create_alert(
                severity="warning",
                message=f"Metric {name} exceeded threshold",
                metric_name=name,
                current_value=value,
                threshold_value=metric.alert_threshold
            )

    def record_request(self, 
                      agent_name: str, 
                      success: bool, 
                      response_time: float):
        """Record agent request metrics."""
        metrics = self.agent_metrics[agent_name]
        metrics.total_requests += 1
        if success:
            metrics.successful_requests += 1
        else:
            metrics.failed_requests += 1
            
        # Update average response time
        metrics.average_response_time = (
            (metrics.average_response_time * (metrics.total_requests - 1) +
             response_time) / metrics.total_requests
        )
        metrics.last_active = datetime.utcnow()

    def record_error(self, agent_name: str, error: str):
        """Record agent error."""
        metrics = self.agent_metrics[agent_name]
        metrics.last_error = error
        metrics.failed_requests += 1

    def create_alert(self,
                    severity: str,
                    message: str,
                    metric_name: str,
                    current_value: float,
                    threshold_value: float):
        """Create and handle a new alert."""
        alert = Alert(
            severity=severity,
            message=message,
            metric_name=metric_name,
            current_value=current_value,
            threshold_value=threshold_value
        )
        self.alerts.append(alert)
        
        # Notify alert handlers
        for handler in self.alert_handlers:
            try:
                handler(alert)
            except Exception as e:
                self.logger.error(f"Error in alert handler: {e}")

    def add_alert_handler(self, handler: callable):
        """Add a new alert handler."""
        self.alert_handlers.add(handler)

    async def collect_metrics_loop(self):
        """Background task to collect system metrics."""
        while True:
            try:
                # Collect system metrics
                self.system_metrics.cpu_usage = psutil.cpu_percent()
                self.system_metrics.memory_usage = psutil.virtual_memory().percent
                self.system_metrics.uptime = (
                    datetime.utcnow() - self.start_time
                ).total_seconds()
                
                # Record metrics
                self.record_metric("cpu_usage", self.system_metrics.cpu_usage)
                self.record_metric("memory_usage", self.system_metrics.memory_usage)
                
                # Calculate error rate
                total_requests = sum(
                    metrics.total_requests 
                    for metrics in self.agent_metrics.values()
                )
                total_errors = sum(
                    metrics.failed_requests 
                    for metrics in self.agent_metrics.values()
                )
                if total_requests > 0:
                    error_rate = (total_errors / total_requests) * 100
                    self.record_metric("error_rate", error_rate)
                
                # Save metrics to file
                await self.save_metrics()
                
            except Exception as e:
                self.logger.error(f"Error collecting metrics: {e}")
                
            await asyncio.sleep(60)  # Collect metrics every minute

    async def cleanup_old_metrics_loop(self):
        """Background task to clean up old metrics."""
        while True:
            try:
                cutoff = datetime.utcnow() - timedelta(days=7)
                
                # Clean up old metric values
                for metric in self.metrics.values():
                    metric.values = [
                        value for value in metric.values
                        if value.timestamp > cutoff
                    ]
                
                # Clean up old alerts
                self.alerts = [
                    alert for alert in self.alerts
                    if alert.timestamp > cutoff
                ]
                
            except Exception as e:
                self.logger.error(f"Error cleaning up metrics: {e}")
                
            await asyncio.sleep(3600)  # Clean up every hour

    async def save_metrics(self):
        """Save current metrics to file."""
        try:
            metrics_file = self.metrics_dir / "current_metrics.json"
            
            data = {
                "timestamp": datetime.utcnow().isoformat(),
                "system_metrics": self.system_metrics.model_dump(),
                "agent_metrics": {
                    name: metrics.model_dump()
                    for name, metrics in self.agent_metrics.items()
                },
                "metrics": {
                    name: metric.model_dump()
                    for name, metric in self.metrics.items()
                }
            }
            
            async with aiofiles.open(metrics_file, 'w') as f:
                await f.write(json.dumps(data, indent=2))
                
        except Exception as e:
            self.logger.error(f"Error saving metrics: {e}")

    def get_system_health(self) -> Dict[str, Any]:
        """Get current system health status."""
        return {
            "status": "healthy" if self.system_metrics.error_rate < 5.0 else "degraded",
            "metrics": self.system_metrics.model_dump(),
            "agents": {
                name: metrics.model_dump()
                for name, metrics in self.agent_metrics.items()
            },
            "alerts": [
                alert.model_dump() 
                for alert in self.alerts 
                if not alert.acknowledged
            ]
        }

    def get_agent_health(self, agent_name: str) -> Dict[str, Any]:
        """Get health status for a specific agent."""
        metrics = self.agent_metrics[agent_name]
        return {
            "status": "healthy" if metrics.failed_requests == 0 else "degraded",
            "metrics": metrics.model_dump(),
            "last_active": metrics.last_active.isoformat() if metrics.last_active else None,
            "error_rate": (
                (metrics.failed_requests / metrics.total_requests * 100)
                if metrics.total_requests > 0 else 0.0
            )
        }

# Create singleton instance
monitoring_system = MonitoringSystem()