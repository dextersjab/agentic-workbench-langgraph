# IT Support Chatbot – Product Requirements Document (PRD)

**Version:** 1.0   **Date:** 2025-07-09

## 1  Purpose
This document defines the functional and non‑functional requirements for a chatbot‑driven IT ticket routing system, codenamed **“HelpHub”**. The system will classify, prioritise, triage, and escalate end‑user incidents raised via chat, email, or portal, integrating seamlessly with the existing ServiceNow ITSM platform.

## 2  Scope
| In Scope | Out of Scope |
|----------|--------------|
| Incident & request intake | HR service catalogue |
| Knowledge‑base Q&A surfacing | Asset discovery |
| Automated classification & priority | Change‑management approval flows |
| Intelligent routing & escalation | Non‑IT departments (e.g., Facilities) |

## 3  Stakeholders
| Role | Responsibility | Contact |
|------|----------------|---------|
| Product Owner | Feature backlog, KPI tracking | Priya Patel |
| Service Desk Lead | Incident policies & SLAs | Ahmed Khan |
| DevOps | Deployment, reliability | Chen Liu |
| Compliance | GDPR & audit | Laura O’Connor |

## 4  Personas
* **Eli – Employee (Requester):** Needs quick resolution to IT issues while remote.   
* **Jade – Level‑1 Agent:** Handles high‑volume, low‑complexity tickets.   
* **Ravi – Level‑2 Specialist:** Resolves escalated incidents requiring domain expertise.   
* **Amira – Service Desk Manager:** Monitors SLA breaches and workload balance.

## 5  User Stories & Acceptance Criteria
| ID | As a | I want | So that | Acceptance Criteria |
|----|------|--------|---------|---------------------|
| US‑01 | Eli | to ask the chatbot for help | I can reset my password fast | When I type *“forgot password”*, the bot points me to the reset portal or raises a ticket if locked |
| US‑05 | Jade | to receive only relevant tickets | my queue isn’t cluttered | Tickets with category=‘hardware’, priority != P1 route to **L1‑HW** queue |
| US‑11 | Amira | to be alerted of P1 breaches | we meet SLAs | System sends webhook to Teams if ≥80 % of P1 tickets unresolved >2 h |

*(Full table continues in Appendix A with 45 user stories.)*

## 6  Functional Requirements
### 6.1  Knowledge‑Base Integration
* **FR‑KB‑01:** System shall ingest FAQs from `/kb/articles.json` nightly.  
* **FR‑KB‑02:** Matching answers shall display with confidence ≥0.25; otherwise proceed to ticket creation.

### 6.2  Classification
* **FR‑CL‑01:** Incoming text is mapped to one of five categories: hardware, software, network, access, billing.  
* **FR‑CL‑02:** Confidence <0.4 triggers “unsure” fallback and human review.

### 6.3  Prioritisation
* **FR‑PR‑01:** Priority rules:  
  * “cannot”, “outage” ⇒ P1  
  * “slow”, “warning” ⇒ P2  
  * else ⇒ P3

### 6.4  Triaging & Routing
* **FR‑TR‑01:** Routing matrix (Table 1) maps (category, priority) → queue.  
* **FR‑TR‑02:** P1 tickets must skip L1 and route directly to L2.

### 6.5  Escalation Workflows
* **FR‑ES‑01:** If ticket remains in `OPEN` >SLA\_target, auto‑escalate to next queue and notify manager.  
* **FR‑ES‑02:** Manual escalation by agent is always permitted through `/escalate` endpoint.

## 7  Non‑Functional Requirements
| NFR | Description | Target |
|-----|-------------|--------|
| Performance | 95th percentile response time | ≤2 s |
| Reliability | Monthly uptime | ≥99.5 % |
| Security | GDPR data minimisation | Pass audit checklist |

## 8  KPIs
* **First‑Contact Resolution (FCR):** ≥60 %  
* **Mean Time‑to‑Resolution (MTTR):** ≤8 h for P2  
* **Human‑Handoff Rate:** ≤40 %

## 9  System Architecture
![architecture](images/architecture.png)

### 9.1  Sequence Diagram – Happy Path
1. User sends chat message.  
2. Bot searches KB → returns answer OR continues.  
3. Bot classifies & prioritises.  
4. Bot creates ticket in ServiceNow via REST API.  
5. Confirmation sent to user.

*(Full diagram in Appendix B.)*

## 10  Integration Requirements
| System | API | Direction | Auth |
|--------|-----|-----------|------|
| ServiceNow | `/api/now/table/incident` | bi‑directional | OAuth2 |
| Teams Webhook | Incoming | outbound | HMAC |

## 11  Assumptions & Dependencies
* ServiceNow instance available in Dev & Test envs.  
* Network egress to `*.azure.com` permitted.

## 12  Risks & Mitigations
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| Low NLP accuracy | M | H | Incremental model training sprints |

## 13  Glossary
**P1:** Highest urgency. **L1:** First‑line support. **KB:** Knowledge Base.

---
## Appendix A  – Full User Story Catalogue
*(Content truncated for brevity in sample.)*

## Appendix B  – Diagrams
*(draw.io sources in `/docs/diagrams/`.)*