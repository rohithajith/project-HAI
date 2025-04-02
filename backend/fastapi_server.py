from fastapi import FastAPI, WebSocket, HTTPException, UploadFile, File, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json
import asyncio
from pathlib import Path

from ai_agents.agent_manager import agent_manager
from ai_agents.base_agent import AgentOutput
from ai_agents.monitoring import monitoring_system
from ai_agents.error_handler import error_handler, ErrorMetadata

class ChatMessage(BaseModel):
    """Schema for chat messages."""
    conversation_id: str = Field(..., description="Unique conversation identifier")
    message: str = Field(..., description="User's message")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ChatResponse(BaseModel):
    """Schema for chat responses."""
    conversation_id: str = Field(..., description="Unique conversation identifier")
    response: str = Field(..., description="Agent's response")
    notifications: List[Dict[str, Any]] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class MetricQuery(BaseModel):
    """Schema for metric queries."""
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    metrics: List[str] = Field(default_factory=list)
    aggregation: str = "avg"

class AlertUpdate(BaseModel):
    """Schema for alert updates."""
    acknowledged: bool = Field(..., description="Whether to acknowledge the alert")
    notes: Optional[str] = None

# Initialize FastAPI app
app = FastAPI(
    title="Hotel AI Assistant",
    description="Multi-Agent System for Hotel Services",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for active conversations
conversations: Dict[str, List[Dict[str, Any]]] = {}

# WebSocket connections
websocket_connections: Dict[str, WebSocket] = {}

async def get_conversation_history(conversation_id: str) -> List[Dict[str, Any]]:
    """Get conversation history for a given ID."""
    return conversations.get(conversation_id, [])

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(message: ChatMessage):
    """Handle chat messages via HTTP."""
    start_time = time.time()
    try:
        # Get conversation history
        history = await get_conversation_history(message.conversation_id)
        
        # Process message through agent system
        response = await agent_manager.process_message(
            message=message.message,
            conversation_id=message.conversation_id,
            history=history
        )
        
        # Update conversation history
        history.append({
            "role": "user",
            "content": message.message,
            "timestamp": message.timestamp
        })
        history.append({
            "role": "assistant",
            "content": response.response,
            "timestamp": datetime.utcnow()
        })
        conversations[message.conversation_id] = history
        
        # Record metrics
        response_time = (time.time() - start_time) * 1000  # Convert to ms
        monitoring_system.record_request(
            agent_name=response.agent_name if hasattr(response, 'agent_name') else 'unknown',
            success=True,
            response_time=response_time
        )
        
        return ChatResponse(
            conversation_id=message.conversation_id,
            response=response.response,
            notifications=response.notifications
        )
        
    except Exception as e:
        # Record error metrics
        monitoring_system.record_error(
            agent_name='unknown',
            error=str(e)
        )
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/{conversation_id}")
async def websocket_endpoint(websocket: WebSocket, conversation_id: str):
    """Handle chat messages via WebSocket."""
    try:
        await websocket.accept()
        websocket_connections[conversation_id] = websocket
        
        try:
            while True:
                start_time = time.time()
                
                # Receive message
                message_data = await websocket.receive_text()
                message = json.loads(message_data)
                
                # Get conversation history
                history = await get_conversation_history(conversation_id)
                
                # Process message through agent system
                response = await agent_manager.process_message(
                    message=message["message"],
                    conversation_id=conversation_id,
                    history=history
                )
                
                # Update conversation history
                history.append({
                    "role": "user",
                    "content": message["message"],
                    "timestamp": datetime.utcnow()
                })
                history.append({
                    "role": "assistant",
                    "content": response.response,
                    "timestamp": datetime.utcnow()
                })
                conversations[conversation_id] = history
                
                # Record metrics
                response_time = (time.time() - start_time) * 1000  # Convert to ms
                monitoring_system.record_request(
                    agent_name=response.agent_name if hasattr(response, 'agent_name') else 'unknown',
                    success=True,
                    response_time=response_time
                )
                
                # Send response
                await websocket.send_json({
                    "response": response.response,
                    "notifications": response.notifications,
                    "timestamp": datetime.utcnow().isoformat()
                })
                
        except Exception as e:
            # Record error metrics
            monitoring_system.record_error(
                agent_name='unknown',
                error=str(e)
            )
            await websocket.send_json({
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            })
            
    finally:
        if conversation_id in websocket_connections:
            del websocket_connections[conversation_id]

# Monitoring Endpoints

@app.get("/api/monitoring/health")
async def system_health():
    """Get overall system health status."""
    return monitoring_system.get_system_health()

@app.get("/api/monitoring/agents/{agent_name}")
async def agent_health(agent_name: str):
    """Get health status for a specific agent."""
    return monitoring_system.get_agent_health(agent_name)

@app.get("/api/monitoring/metrics")
async def get_metrics(query: MetricQuery):
    """Get system metrics based on query parameters."""
    try:
        metrics = monitoring_system.metrics
        if query.metrics:
            metrics = {
                name: metric for name, metric in metrics.items()
                if name in query.metrics
            }
            
        # Filter by time range if provided
        if query.start_time or query.end_time:
            for metric in metrics.values():
                metric.values = [
                    value for value in metric.values
                    if (not query.start_time or value.timestamp >= query.start_time) and
                    (not query.end_time or value.timestamp <= query.end_time)
                ]
                
        return {
            "metrics": {
                name: metric.model_dump() 
                for name, metric in metrics.items()
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/monitoring/alerts")
async def get_alerts(
    severity: Optional[str] = None,
    acknowledged: Optional[bool] = None
):
    """Get system alerts with optional filtering."""
    alerts = monitoring_system.alerts
    
    if severity:
        alerts = [alert for alert in alerts if alert.severity == severity]
    if acknowledged is not None:
        alerts = [alert for alert in alerts if alert.acknowledged == acknowledged]
        
    return {
        "alerts": [alert.model_dump() for alert in alerts]
    }

@app.put("/api/monitoring/alerts/{alert_id}")
async def update_alert(alert_id: int, update: AlertUpdate):
    """Update alert status."""
    try:
        alert = monitoring_system.alerts[alert_id]
        alert.acknowledged = update.acknowledged
        return alert.model_dump()
    except IndexError:
        raise HTTPException(status_code=404, detail="Alert not found")

@app.get("/api/monitoring/visualization")
async def get_visualization_data(
    metric_names: List[str] = Query(...),
    interval: str = "1h",
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None
):
    """Get metric data formatted for visualization."""
    try:
        # Parse interval
        interval_seconds = {
            "5m": 300,
            "15m": 900,
            "1h": 3600,
            "6h": 21600,
            "1d": 86400
        }.get(interval, 3600)
        
        # Default time range to last 24 hours if not specified
        if not end_time:
            end_time = datetime.utcnow()
        if not start_time:
            start_time = end_time - timedelta(days=1)
            
        data = {}
        for metric_name in metric_names:
            if metric_name in monitoring_system.metrics:
                metric = monitoring_system.metrics[metric_name]
                
                # Filter values by time range
                values = [
                    value for value in metric.values
                    if start_time <= value.timestamp <= end_time
                ]
                
                # Group by interval
                grouped_values = defaultdict(list)
                for value in values:
                    interval_start = value.timestamp.replace(
                        second=0,
                        microsecond=0
                    )
                    interval_start = interval_start - timedelta(
                        seconds=interval_start.timestamp() % interval_seconds
                    )
                    grouped_values[interval_start].append(value.value)
                
                # Calculate averages for each interval
                data[metric_name] = {
                    "name": metric_name,
                    "description": metric.description,
                    "unit": metric.unit,
                    "data": [
                        {
                            "timestamp": ts.isoformat(),
                            "value": sum(values) / len(values)
                        }
                        for ts, values in sorted(grouped_values.items())
                    ]
                }
                
        return data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)