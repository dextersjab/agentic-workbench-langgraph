from fastapi import FastAPI, UploadFile, File, Query
from pydantic import BaseModel
import csv, json, uuid, time, random
from typing import Optional

app = FastAPI(title="HelpHub - IT Support Agent API", description="Mock API for IT support chatbot training")

class Ticket(BaseModel):
    subject: str
    description: str

class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None

class PIICheckRequest(BaseModel):
    text: str

# Rate limiting simulation
request_counts = {}
RATE_LIMIT = 60  # requests per minute

@app.middleware("http")
async def rate_limit_middleware(request, call_next):
    """Simulate rate limiting for API calls"""
    client_ip = request.client.host
    current_minute = int(time.time() // 60)
    
    if client_ip not in request_counts:
        request_counts[client_ip] = {}
    
    if current_minute not in request_counts[client_ip]:
        request_counts[client_ip][current_minute] = 0
    
    if request_counts[client_ip][current_minute] >= RATE_LIMIT:
        # Simulate rate limit error
        if random.random() < 0.1:  # 10% chance to trigger rate limit
            time.sleep(1)  # Simulate delay
    
    request_counts[client_ip][current_minute] += 1
    response = await call_next(request)
    return response

@app.get("/")
async def root():
    """API information and available endpoints"""
    return {
        "name": "HelpHub IT Support Agent API",
        "version": "1.0.0",
        "description": "Mock API for training AI agents in IT support scenarios",
        "endpoints": {
            "chat": "/chat - Start new conversation",
            "categorize": "/categorize - Categorize support tickets", 
            "prioritize": "/prioritize - Determine ticket priority",
            "route": "/route - Complete ticket routing workflow",
            "kb_search": "/kb/search - Search knowledge base",
            "pii_check": "/pii-check - Check for PII in text"
        },
        "course": "Enterprise Agent Development by Dexter Awoyemi"
    }

@app.post("/categorize")
async def categorize(ticket: Ticket):
    """Categorize ticket into one of: hardware, software, network, access, billing"""
    desc_lower = ticket.description.lower()
    
    # Simple keyword-based categorization (students will improve this)
    if any(word in desc_lower for word in ["password", "login", "access", "account", "locked", "permissions"]):
        return {"category": "access", "confidence": 0.85}
    elif any(word in desc_lower for word in ["wifi", "vpn", "internet", "connection", "network", "slow"]):
        return {"category": "network", "confidence": 0.80}
    elif any(word in desc_lower for word in ["laptop", "printer", "monitor", "hardware", "battery", "keyboard"]):
        return {"category": "hardware", "confidence": 0.75}
    elif any(word in desc_lower for word in ["license", "billing", "payment", "subscription", "invoice"]):
        return {"category": "billing", "confidence": 0.70}
    elif any(word in desc_lower for word in ["software", "application", "install", "crash", "error", "teams", "outlook"]):
        return {"category": "software", "confidence": 0.80}
    else:
        return {"category": "unknown", "confidence": 0.30}

@app.post("/prioritize")
async def prioritize(ticket: Ticket):
    """Determine priority based on urgency keywords"""
    desc_lower = ticket.description.lower()
    
    # P1 (Critical) - system down, cannot work, urgent
    if any(word in desc_lower for word in ["cannot", "down", "outage", "urgent", "emergency", "flooding", "critical"]):
        return {"priority": "P1", "score": 0.90}
    # P2 (High) - impacting work but not blocking
    elif any(word in desc_lower for word in ["slow", "error", "problem", "issue", "affecting", "intermittent"]):
        return {"priority": "P2", "score": 0.75}
    # P3 (Medium) - requests, questions, minor issues
    else:
        return {"priority": "P3", "score": 0.60}

@app.post("/route")
async def route(ticket: Ticket):
    """Complete workflow: categorize -> prioritize -> assign queue"""
    cat_resp = await categorize(ticket)
    prio_resp = await prioritize(ticket)
    
    # Advanced routing logic
    category = cat_resp["category"]
    priority = prio_resp["priority"]
    
    # P1 tickets go to L2, others to L1 (except billing which always starts at L1)
    if priority == "P1" and category != "billing":
        queue = f"L2-{category.title()}"
    else:
        queue = f"L1-{category.title()}"
    
    ticket_id = f"TKT-{str(uuid.uuid4())[:8].upper()}"
    
    return {
        "ticket_id": ticket_id, 
        "category": category, 
        "priority": priority, 
        "queue": queue,
        "estimated_resolution": "2 hours" if priority == "P1" else "8 hours" if priority == "P2" else "24 hours"
    }

@app.get("/kb/search")
async def kb_search(query: str = Query(..., description="Search query for knowledge base")):
    """Search knowledge base articles"""
    try:
        with open("kb/articles.json") as f:
            kb = json.load(f)
    except FileNotFoundError:
        return {"results": [], "message": "Knowledge base not available"}
    
    # Simple text matching (students can improve with semantic search)
    query_lower = query.lower()
    hits = []
    
    for article in kb:
        question_lower = article["question"].lower()
        answer_lower = article["answer"].lower()
        
        # Calculate simple relevance score
        question_matches = sum(1 for word in query_lower.split() if word in question_lower)
        answer_matches = sum(1 for word in query_lower.split() if word in answer_lower)
        total_score = question_matches * 2 + answer_matches  # Weight questions higher
        
        if total_score > 0:
            article_copy = article.copy()
            article_copy["relevance_score"] = total_score
            hits.append(article_copy)
    
    # Sort by relevance and return top 5
    hits.sort(key=lambda x: x["relevance_score"], reverse=True)
    return {"results": hits[:5], "total_found": len(hits)}

@app.post("/pii-check")
async def check_pii(request: PIICheckRequest):
    """Basic PII detection API (simulated)"""
    text = request.text.lower()
    
    # Simple PII patterns
    pii_patterns = {
        "email": "@" in text and "." in text,
        "phone": any(char.isdigit() for char in text) and len([c for c in text if c.isdigit()]) >= 10,
        "ssn": "ssn" in text or "social security" in text,
        "credit_card": len([c for c in text if c.isdigit()]) >= 13
    }
    
    detected_pii = [pii_type for pii_type, found in pii_patterns.items() if found]
    
    # Simulate masking
    masked_text = text
    if "@" in text:
        # Simple email masking
        import re
        masked_text = re.sub(r'\S+@\S+', '[EMAIL_MASKED]', masked_text)
    
    return {
        "has_pii": len(detected_pii) > 0,
        "pii_types": detected_pii,
        "original_text": request.text,
        "masked_text": masked_text if detected_pii else request.text
    }

@app.post("/chat")
async def start_chat(message: ChatMessage):
    """Start a new chat conversation"""
    session_id = str(uuid.uuid4())
    
    # Simple chat response (students will implement LangGraph here)
    return {
        "session_id": session_id,
        "response": "Hello! I'm here to help with your IT support needs. Can you describe the issue you're experiencing?",
        "needs_clarification": False,
        "suggested_questions": []
    }

@app.post("/chat/continue")
async def continue_chat(message: ChatMessage):
    """Continue an existing chat conversation"""
    if not message.session_id:
        return {"error": "Session ID required for continuing conversation"}
    
    # Placeholder for conversation handling (students implement with LangGraph)
    return {
        "session_id": message.session_id,
        "response": "I understand you're having an issue. Let me help you with that.",
        "needs_clarification": True,
        "suggested_questions": ["Can you provide more details about when this started?"]
    }