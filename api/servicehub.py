from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import uuid
from datetime import datetime, timedelta
import json

# ServiceHub Mock API - Simulates enterprise ITSM platform

class IncidentCreate(BaseModel):
    subject: str
    description: str
    category: str
    priority: str
    user_id: Optional[str] = "anonymous"
    assignment_group: Optional[str] = None

class IncidentUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None
    assignment_group: Optional[str] = None

class IncidentResponse(BaseModel):
    incident_id: str
    subject: str
    description: str
    category: str
    priority: str
    status: str
    created_date: datetime
    updated_date: datetime
    assignment_group: str
    sla_breach_time: Optional[datetime]
    user_id: str

class User(BaseModel):
    user_id: str
    name: str
    email: str
    department: str
    manager: Optional[str] = None

# In-memory storage for demo purposes
incidents_db = {}
users_db = {
    "user_001": {"user_id": "user_001", "name": "John Doe", "email": "john@company.com", "department": "Engineering"},
    "user_002": {"user_id": "user_002", "name": "Jane Smith", "email": "jane@company.com", "department": "Marketing"},
    "user_003": {"user_id": "user_003", "name": "Bob Wilson", "email": "bob@company.com", "department": "Sales"},
}

# Assignment group mappings
ASSIGNMENT_GROUPS = {
    "hardware_P1": "L2-Hardware",
    "hardware_P2": "L1-Hardware", 
    "hardware_P3": "L1-Hardware",
    "software_P1": "L2-Software",
    "software_P2": "L1-Software",
    "software_P3": "L1-Software", 
    "network_P1": "L2-Network",
    "network_P2": "L1-Network",
    "network_P3": "L1-Network",
    "access_P1": "L2-Access",
    "access_P2": "L1-Access",
    "access_P3": "L1-Access",
    "billing_P1": "L2-Billing",
    "billing_P2": "L1-Billing",
    "billing_P3": "L1-Billing"
}

# SLA times in hours
SLA_TIMES = {
    "P1": 2,
    "P2": 8, 
    "P3": 24
}

def calculate_sla_breach_time(priority: str, created_date: datetime) -> datetime:
    """Calculate when SLA will be breached"""
    sla_hours = SLA_TIMES.get(priority, 24)
    return created_date + timedelta(hours=sla_hours)

def get_assignment_group(category: str, priority: str) -> str:
    """Determine assignment group based on category and priority"""
    key = f"{category}_{priority}"
    return ASSIGNMENT_GROUPS.get(key, "L1-General")

servicehub_app = FastAPI(title="ServiceHub Mock API", description="Enterprise ITSM Platform Simulation")

@servicehub_app.post("/servicehub/incidents", response_model=IncidentResponse)
async def create_incident(incident: IncidentCreate):
    """Create a new incident ticket"""
    incident_id = f"INC-{str(uuid.uuid4())[:8].upper()}"
    
    assignment_group = incident.assignment_group or get_assignment_group(incident.category, incident.priority)
    created_date = datetime.now()
    sla_breach_time = calculate_sla_breach_time(incident.priority, created_date)
    
    incident_data = {
        "incident_id": incident_id,
        "subject": incident.subject,
        "description": incident.description,
        "category": incident.category,
        "priority": incident.priority,
        "status": "Open",
        "created_date": created_date,
        "updated_date": created_date,
        "assignment_group": assignment_group,
        "sla_breach_time": sla_breach_time,
        "user_id": incident.user_id
    }
    
    incidents_db[incident_id] = incident_data
    
    return IncidentResponse(**incident_data)

@servicehub_app.get("/servicehub/incidents/{incident_id}", response_model=IncidentResponse)
async def get_incident(incident_id: str):
    """Retrieve incident details"""
    if incident_id not in incidents_db:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    return IncidentResponse(**incidents_db[incident_id])

@servicehub_app.put("/servicehub/incidents/{incident_id}", response_model=IncidentResponse)
async def update_incident(incident_id: str, update: IncidentUpdate):
    """Update incident details"""
    if incident_id not in incidents_db:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    incident_data = incidents_db[incident_id]
    
    if update.status:
        incident_data["status"] = update.status
    if update.assignment_group:
        incident_data["assignment_group"] = update.assignment_group
    if update.notes:
        # In a real system, notes would be appended to a notes field
        incident_data["description"] += f"\n\nUpdate: {update.notes}"
    
    incident_data["updated_date"] = datetime.now()
    
    return IncidentResponse(**incident_data)

@servicehub_app.get("/servicehub/incidents", response_model=List[IncidentResponse])
async def list_incidents(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    category: Optional[str] = None,
    assignment_group: Optional[str] = None
):
    """List incidents with optional filtering"""
    filtered_incidents = []
    
    for incident_data in incidents_db.values():
        # Apply filters
        if status and incident_data["status"] != status:
            continue
        if priority and incident_data["priority"] != priority:
            continue  
        if category and incident_data["category"] != category:
            continue
        if assignment_group and incident_data["assignment_group"] != assignment_group:
            continue
            
        filtered_incidents.append(IncidentResponse(**incident_data))
    
    return filtered_incidents

@servicehub_app.get("/servicehub/users/{user_id}", response_model=User)
async def get_user(user_id: str):
    """Get user details"""
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    return User(**users_db[user_id])

@servicehub_app.get("/servicehub/assignment-groups")
async def get_assignment_groups():
    """Get available assignment groups"""
    unique_groups = list(set(ASSIGNMENT_GROUPS.values()))
    return {"assignment_groups": unique_groups}

@servicehub_app.get("/servicehub/sla-status")
async def get_sla_status():
    """Get SLA status for all active incidents"""
    sla_status = []
    current_time = datetime.now()
    
    for incident_id, incident_data in incidents_db.items():
        if incident_data["status"] in ["Open", "In Progress"]:
            time_remaining = incident_data["sla_breach_time"] - current_time
            is_breached = time_remaining.total_seconds() < 0
            
            sla_status.append({
                "incident_id": incident_id,
                "priority": incident_data["priority"],
                "sla_breach_time": incident_data["sla_breach_time"],
                "time_remaining_hours": time_remaining.total_seconds() / 3600,
                "is_breached": is_breached,
                "status": incident_data["status"]
            })
    
    return {"sla_incidents": sla_status}

@servicehub_app.post("/servicehub/incidents/{incident_id}/escalate")
async def escalate_incident(incident_id: str):
    """Escalate incident to next level"""
    if incident_id not in incidents_db:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    incident_data = incidents_db[incident_id]
    current_group = incident_data["assignment_group"]
    
    # Escalation logic
    if current_group.startswith("L1-"):
        new_group = current_group.replace("L1-", "L2-")
    else:
        new_group = "L3-Management"
    
    incident_data["assignment_group"] = new_group
    incident_data["updated_date"] = datetime.now()
    incident_data["description"] += f"\n\nEscalated from {current_group} to {new_group}"
    
    return {
        "message": f"Incident {incident_id} escalated to {new_group}",
        "incident": IncidentResponse(**incident_data)
    }