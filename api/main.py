from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
import csv, json, uuid

app = FastAPI(title="IT Support Bot Mock API")

class Ticket(BaseModel):
    subject: str
    description: str

@app.post("/classify")
async def classify(ticket: Ticket):
    # dummy logic
    cat = "software" if "password" in ticket.description.lower() else "hardware"
    return {"category": cat, "confidence": 0.6}

@app.post("/prioritise")
async def prioritise(ticket: Ticket):
    # dummy logic
    prio = "P1" if "cannot" in ticket.description.lower() else "P3"
    return {"priority": prio, "score": 0.75}

@app.post("/route")
async def route(ticket: Ticket):
    # dummy chaining
    cat_resp = await classify(ticket)
    prio_resp = await prioritise(ticket)
    queue = "L2" if prio_resp["priority"] == "P1" else "L1"
    ticket_id = str(uuid.uuid4())
    return {"ticket_id": ticket_id, "category": cat_resp["category"], "priority": prio_resp["priority"], "queue": queue}

@app.post("/kb/search")
async def kb_search(query: str):
    with open("kb/articles.json") as f:
        kb = json.load(f)
    hits = [a for a in kb if query.lower() in a["question"].lower()]
    return {"results": hits[:5]}