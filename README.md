# HelpHub – IT Support Chatbot Case Study

Clone the repo, then:

```bash
pip install -r requirements.txt
uvicorn api.main:app --reload
```

Open <http://localhost:8000/docs> for Swagger‑UI.

## Run Tests

```bash
pytest -q
```

## Folder Structure
| Path | Purpose |
|------|---------|
| /api | FastAPI mock services |
| /kb  | Knowledge base articles |
| /data | Seed tickets for classification practice |
| /tests | Autograder suite |
| /docs | PRD and diagrams |

Enjoy!