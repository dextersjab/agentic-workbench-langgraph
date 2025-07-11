# 🎯 HelpHub – IT Support Chatbot Case Study

> **Enterprise Agent Development Course**  
> A comprehensive case study for building realistic AI agents using LangGraph in IT support environments

## 🚀 Quick Start

```bash
# Clone and setup
git clone https://github.com/dextersjab/agentic-course-case-study-0
cd agentic-course-case-study-0
# Setup with uv (recommended)\nuv venv\nsource .venv/bin/activate  # On Windows: .venv\\Scripts\\activate\nuv pip install -r requirements.txt\n\n# Alternative: traditional pip\n# pip install -r requirements.txt

# Start the mock API
uvicorn api.main:app --reload
```

Open [http://localhost:8000/docs](http://localhost:8000/docs) for Swagger UI.

## 🧪 Testing

```bash
pytest -q
```

---

# 📋 Product Requirements Document (PRD)

## 1. Executive Summary

**HelpHub** is an AI-powered IT support chatbot designed to automatically **categorize**, **prioritize**, and **route** support tickets while intelligently leveraging knowledge base resources when appropriate. This system serves as a comprehensive case study for building enterprise-grade AI agents using **LangGraph** that handle real-world IT support scenarios through intelligent multi-turn conversations.

### Key Objectives
- **Automate** ticket categorization and routing through conversational AI
- **Reduce** mean time to resolution (MTTR) via intelligent question loops
- **Improve** first-contact resolution rates with intelligent KB utilization
- **Handle** interruptions, topic changes, and escalation requests seamlessly

## 2. LangGraph Workflow Architecture

```mermaid
graph TD
    A[User Query] --> B[Agent Analysis]
    B -.->|Clear Issue| C[Categorization]
    B -.->|Needs KB Context| D[KB Search Tool]
    B -.->|Need Clarification| E[Ask Questions]
    
    D --> F[Apply KB Knowledge]
    F -.->|Resolved| G[Return Answer] 
    F -.->|Still Need Ticket| C
    
    E -.->|Got Info| B
    E -.->|Still Unclear| E
    
    C --> H[Priority Assessment]
    H --> I[Queue Assignment] 
    I --> J[ServiceHub Integration]
    J --> K[Ticket Created]
    K --> L[User Notification]
    
    M[ServiceHub] --> J
    N[Knowledge Base] --> D
    
    style B stroke:#1976d2,stroke-width:3px
    style D stroke:#388e3c,stroke-width:3px
    style E stroke:#f57c00,stroke-width:3px
    style J stroke:#7b1fa2,stroke-width:3px
```

## 3. Core Workflows

### 3.1 Intelligent Conversation Flow

```mermaid
sequenceDiagram
    participant U as User
    participant H as HelpHub Agent
    participant KB as Knowledge Base
    participant SH as ServiceHub
    
    U->>H: "My computer isn't working"
    Note over H: Agent analyzes - vague issue, needs clarification
    H->>U: "What happens when you try to turn it on?"
    U->>H: "The screen stays black"
    H->>U: "Do you see any lights on the laptop?"
    U->>H: "No lights at all"
    Note over H: Clear hardware failure, skip KB - emergency ticket needed
    H->>U: "Actually, I need to check email first"
    Note over H: Handle interruption gracefully
    H->>U: "I understand. Let me quickly create a P1 hardware ticket for your laptop, then help with email"
    Note over H: Direct categorization: Hardware P1
    H->>SH: Create ticket: Hardware, P1, "laptop no power"
    SH->>H: Ticket #HW-12345
    H->>U: "P1 ticket #HW-12345 created - technician will contact you within 2 hours. Now, what's the email issue?"
```

### 3.2 LangGraph Decision Flow

```mermaid
flowchart TD
    A[User Input] --> B[Clarification Node]
    B -.->|Vague| B
    B -.->|Multi-Issue| C[Issue Decomposition]
    B -.->|Clear| D[Direct Processing]
    
    C -.->|Primary Issue| D
    C -.->|Secondary Issues| E[Queue for Later]
    
    D --> F[Categorization]
    F --> G[Priority Assessment]
    G --> H[Ticket Creation]
    
    style B stroke:#ff8f00,stroke-width:3px
    style C stroke:#1976d2,stroke-width:3px
    style F stroke:#388e3c,stroke-width:3px
```

## 4. Realistic Ticket Scenarios

### 4.1 Vague Descriptions
| User Input | Agent Response | Expected Outcome |
|------------|---------------|------------------|
| "Everything is broken" | "I'm sorry to hear that. Can you tell me what specifically isn't working?" | Question loop to clarify |
| "My computer is slow" | "When did you first notice the slowness? Is it when starting up, opening programs, or browsing?" | Categorize as Performance issue |
| "I can't work" | "What's preventing you from working? Is it a login issue, application problem, or hardware failure?" | Multiple clarifying questions |

### 4.2 Multi-Category Issues
| Scenario | Categorization Challenge | Expected Handling |
|----------|------------------------|-------------------|
| "Can't login to email on new laptop" | Access + Hardware setup | Decompose into two tickets |
| "VPN won't connect and now Teams is down" | Network + Software | Prioritize VPN (likely root cause) |
| "Printer offline and need software installed" | Hardware + Software | Handle separately, software can wait |

### 4.3 Interruption Scenarios
| Original Issue | Interruption | Expected Behavior |
|---------------|-------------|------------------|
| Password reset request | "Actually, I need to join a meeting first" | Save context, prioritize meeting access |
| Hardware repair | "Wait, is the help desk open now?" | Answer query, return to hardware issue |
| Software installation | "This is urgent, my presentation is in 10 minutes" | Escalate priority, expedite handling |

## 5. Technical Components

### 5.1 Categorization Engine

The system uses a multi-stage NLP pipeline to categorize incoming tickets:

| Category | Common Phrases | Confidence Threshold |
|----------|---------------|---------------------|
| Hardware | "laptop", "battery", "printer", "black screen", "won't turn on" | 0.75 |
| Software | "password", "login", "application", "install", "error message" | 0.80 |
| Network | "wifi", "vpn", "connection", "internet", "can't connect" | 0.70 |
| Access | "permissions", "account", "locked out", "can't access", "reset" | 0.85 |
| Billing | "invoice", "cost", "license", "payment", "subscription" | 0.65 |

### 5.2 Priority Assessment Logic

```mermaid
graph LR
    A[Incident Description] --> B[Keyword Analysis]
    B -.->|cannot, down, outage, urgent| C[P1 - Critical]
    B -.->|slow, warning, error, intermittent| D[P2 - High] 
    B -.->|request, question, when possible| E[P3 - Medium]
    
    C --> F[Final Priority]
    D --> F
    E --> F
    
    style C stroke:#d32f2f,stroke-width:3px
    style D stroke:#f57c00,stroke-width:3px
    style F stroke:#388e3c,stroke-width:3px
```

### 5.3 Built-in Constraints

```mermaid
graph TD
    A[Agent Request] --> B[Rate Limiter]
    B -.->|Exceeded| C[Queue Request]
    B -.->|Within Limits| D[Data Privacy Check]
    D --> E[PII Detection API]
    E -.->|PII Found| F[Mask/Anonymize]
    E -.->|No PII| G[Process Request]
    F --> G
    
    style B stroke:#f57c00,stroke-width:3px
    style E stroke:#388e3c,stroke-width:3px
    style F stroke:#d32f2f,stroke-width:3px
```

## 6. Intelligent KB Tool Usage

### 6.1 When the Agent Uses KB

The LLM agent intelligently decides when to leverage the knowledge base:

| Scenario | Agent Decision | Reasoning |
|----------|---------------|-----------|
| "Server room flooding!" | Skip KB, immediate P1 ticket | Emergency - no time for KB search |
| "How do I reset my password?" | Search KB first | Common question likely in KB |
| "Email is slow sometimes" | Check KB for email troubleshooting | KB might have diagnostic steps |
| "My laptop won't start, no lights" | Skip KB, direct to hardware ticket | Clear hardware failure symptoms |
| "I can't access the thing" | Ask clarification first | Too vague for effective KB search |

### 6.2 KB Search Strategies

```mermaid
graph TD
    A[User Query] --> B[Agent Analysis]
    B -.->|Common Question Pattern| C[KB Search Tool]
    B -.->|Emergency Keywords| D[Skip KB, Direct Ticket]
    B -.->|Vague Description| E[Clarify First]
    
    C -.->|Helpful Result| F[Provide KB Answer]
    C -.->|Incomplete| G[KB + Ticket Creation]
    C -.->|No Results| H[Direct to Categorization]
    
    style C stroke:#388e3c,stroke-width:3px
    style D stroke:#d32f2f,stroke-width:3px
    style E stroke:#f57c00,stroke-width:3px
```

## 7. User Journey Examples

### 7.1 Success Journey - Hardware Issue
```
User: "My laptop won't start"
Agent: "I'll help you with that. When you press the power button, what happens?"
User: "Nothing at all, no lights or sounds"
Agent: "Are you using the power adapter or just battery?"
User: "I have it plugged in"
Agent: "I've created ticket #12345 for a hardware repair. This appears to be a power supply issue. A technician will contact you within 2 hours."
```

### 7.2 Intelligent KB Usage Journey
```
User: "How do I reset my password?"
Agent: "Let me check our knowledge base for the most current password reset instructions."
[Agent searches KB: "password reset"]
Agent: "I found the steps! You can use our self-service portal at company.com/reset. If your account is locked, you'll need to call the service desk at ext. 4357. Would you like me to walk you through the self-service process?"
User: "Yes please"
Agent: "Great! First, go to company.com/reset and enter your username..."
```

### 7.3 Complex Journey - Multiple Issues  
```
User: "I can't log into my email and my new laptop setup isn't working"
Agent: "I'll help you with both issues. Let's start with your email login - what error do you see?"
User: "It says invalid credentials"
Agent: "I'll create a password reset ticket for you. While that's processing, what's not working with your laptop setup?"
User: "Actually, the email thing is more urgent, I have a client call in 5 minutes"
Agent: "Understood. I'll prioritize the email issue and create an urgent ticket. Try the password reset link I'm sending now."
```

### 7.4 Escalation Journey
```
User: "The server room is flooding!"
Agent: "This is a critical emergency. I'm creating a P1 ticket and immediately notifying the facilities team. Are you in a safe location?"
User: "Yes, I'm out of the room"
Agent: "Ticket #99999 created. Emergency response team has been alerted. Please stay clear of the area."
```

## 8. ServiceHub Integration

### 8.1 Mock Enterprise System

ServiceHub simulates a realistic ITSM platform with:

- **Ticket Management**: Creation, updates, status tracking
- **Assignment Groups**: L1-Hardware, L1-Software, L2-Network, etc.
- **SLA Tracking**: Automatic escalation based on priority
- **Reporting**: Metrics dashboard and KPI tracking

```mermaid
graph LR
    A[HelpHub Agent] -->|REST API| B[ServiceHub Instance]
    B -->|Webhook| A
    
    A --> C[API Authentication]
    B --> D[Incident Table]
    B --> E[User Table]
    B --> F[Assignment Groups]
    B --> G[SLA Rules]
    
    style B stroke:#1976d2,stroke-width:3px
    style C stroke:#f57c00,stroke-width:3px
```

### 8.2 API Integration Points

| Endpoint | Method | Purpose | Example |
|----------|---------|---------|---------|
| `/servicehub/incidents` | POST | Create new ticket | `{"category": "hardware", "priority": "P1"}` |
| `/servicehub/incidents/{id}` | GET | Retrieve ticket status | Returns ticket details |
| `/servicehub/incidents/{id}` | PUT | Update ticket | Add notes, change status |
| `/servicehub/users/{id}` | GET | Get user details | For assignment and notifications |

## 9. Evaluation Criteria

### 9.1 Automated Assessment

**Categorization Accuracy Score**: `(Correct Category + Correct Priority) / Total Predictions * 100`

| Component | Weight | Measurement |
|-----------|---------|-------------|
| Category Accuracy | 40% | Hardware/Software/Network/Access/Billing |
| Priority Accuracy | 30% | P1/P2/P3 assignment |
| Conversation Quality | 20% | Multi-turn handling, context retention |
| Edge Case Handling | 10% | Interruptions, topic changes, escalations |

### 9.2 Test Dataset Structure

```csv
ticket_id,description,user_context,expected_category,expected_priority,conversation_turns,has_interruption
1,"My laptop battery dies in 5 minutes","Remote worker, urgent project",hardware,P2,2,false
2,"Can't access shared drive, presentation in 1 hour","Manager, time pressure",access,P1,3,true
3,"Email is slow, not urgent","Regular user, no time pressure",software,P3,1,false
```

### 9.3 Multi-Turn Conversation Evaluation

Test scenarios evaluate:
- **Context Retention**: Agent remembers previous conversation details
- **Clarification Quality**: Questions are relevant and specific
- **Interruption Handling**: Graceful context switching
- **Topic Management**: Ability to juggle multiple issues

## 10. Technology Stack

### 10.1 Core Technologies

| Component | Technology | Purpose |
|-----------|------------|---------|
| Agent Framework | LangGraph | Workflow orchestration |
| LLM Provider | OpenRouter (GPT-4.1-mini) | Natural language processing |
| Alternative LLM | DeepSeek R1 | Cost-effective option |
| API Framework | FastAPI | Mock ServiceHub endpoints |
| Testing | pytest | Automated evaluation |

### 10.2 LangGraph Structure

```python
# Project structure following Gemini quickstart pattern
src/
├── graph.py          # Main workflow definition
├── nodes.py          # Individual workflow steps
├── state.py          # Conversation state management
├── tools.py          # ServiceHub integration tools
└── evaluator.py      # Assessment logic
```

### 10.3 Environment Setup

```bash
# Required environment variables
OPENROUTER_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here  # Optional fallback
SERVICEHUB_BASE_URL=http://localhost:8000
```

## 11. Success Metrics & KPIs

### 11.1 Participant Success Metrics

| Metric | Target | Measurement |
|--------|---------|-------------|
| Categorization Accuracy | ≥85% | Automated evaluation |
| Priority Accuracy | ≥80% | Automated evaluation |
| Multi-turn Conversation Score | ≥75% | Conversation quality rubric |
| Edge Case Handling | ≥70% | Interruption/topic change scenarios |

### 11.2 Assessment Flow

```mermaid
graph TD
    A[Submission] --> B[Automated Tests]
    B --> C[Categorization Accuracy]
    B --> D[Priority Accuracy]
    B --> E[Conversation Quality]
    B --> F[Edge Case Handling]
    
    C --> G[Overall Score]
    D --> G
    E --> G
    F --> G
    
    G -.->|≥80%| H[Requirements Met]
    G -.->|<80%| I[Additional Work Needed]
    
    style G stroke:#388e3c,stroke-width:3px
    style H stroke:#4caf50,stroke-width:3px
    style I stroke:#d32f2f,stroke-width:3px
```

## 12. Implementation Roadmap

### Phase 1: Core Agent (Week 1)
- [x] Basic LangGraph structure
- [x] Simple question loop
- [x] KB search integration
- [x] Mock ServiceHub endpoints

### Phase 2: Conversation Intelligence (Week 2)
- [ ] Multi-turn conversation handling
- [ ] Context retention across turns
- [ ] Interruption management
- [ ] Topic change detection

### Phase 3: Advanced Features (Week 3)
- [ ] Complex scenario handling
- [ ] Built-in constraints (rate limiting, PII detection)
- [ ] Escalation workflows
- [ ] Performance optimization

### Phase 4: Evaluation & Testing (Week 4)
- [ ] Comprehensive test dataset
- [ ] Automated scoring system
- [ ] Edge case scenarios
- [ ] Participant assessment tools

## 13. Project Structure

```
agentic-course-case-study-0/
├── src/
│   ├── graph.py              # LangGraph workflow
│   ├── nodes.py              # Workflow nodes
│   ├── state.py              # Conversation state
│   ├── tools.py              # ServiceHub tools
│   └── evaluator.py          # Assessment logic
├── api/
│   ├── main.py               # FastAPI mock services
│   └── servicehub.py         # ServiceHub simulation
├── data/
│   ├── tickets_train.csv     # Training scenarios
│   ├── tickets_test.csv      # Test scenarios
│   └── conversations.json    # Multi-turn examples
├── kb/
│   └── articles.json         # Knowledge base articles
├── tests/
│   ├── test_categorization.py
│   ├── test_conversation.py
│   └── test_integration.py
├── docs/
│   └── course_guide.md       # Participant instructions
└── requirements.txt
```

## 14. Participant Learning Path

### 14.1 Prerequisites
- **Python Proficiency**: Comfortable with Python programming
- **Basic AI/ML Understanding**: Familiarity with LLMs and prompting
- **No LangGraph Experience Required**: Will be taught as part of the course

### 14.2 Learning Progression

1. **Week 1**: Understand the problem domain and existing codebase
2. **Week 2**: Implement basic LangGraph workflow with question loop
3. **Week 3**: Add conversation intelligence and edge case handling
4. **Week 4**: Optimize performance and complete evaluation

### 14.3 Success Criteria

Participants will demonstrate mastery by:
- Building a functional multi-turn conversation agent
- Achieving ≥80% accuracy on categorization and priority assessment
- Handling interruptions and topic changes gracefully
- Integrating with mock enterprise systems

## 15. API Reference

### 15.1 Core Endpoints

| Endpoint | Method | Purpose | Example Request |
|----------|---------|---------|-----------------|
| `/chat` | POST | Start conversation | `{"message": "My laptop won't start"}` |
| `/chat/continue` | POST | Continue conversation | `{"session_id": "123", "message": "No lights"}` |
| `/categorize` | POST | Categorize ticket | `{"description": "Email password reset"}` |
| `/prioritize` | POST | Assess priority | `{"description": "Server room flooding"}` |
| `/kb/search` | GET | Search knowledge base | `?query=password+reset` |

### 15.2 Response Formats

```json
{
  "session_id": "uuid",
  "response": "I'll help you with that laptop issue...",
  "needs_clarification": true,
  "suggested_questions": ["What happens when you press power?"],
  "category": "hardware",
  "priority": "P1",
  "confidence": 0.85
}
```

## 16. Common Issues & Solutions

### 16.1 Development Issues

| Problem | Solution |
|---------|----------|
| LangGraph workflow not executing | Check node connections and state schema |
| OpenRouter API limits | Implement rate limiting and retry logic |
| Conversation context lost | Verify state persistence between turns |
| Categorization accuracy low | Review training data and prompt engineering |

### 16.2 Testing Issues

| Problem | Solution |
|---------|----------|
| Tests failing inconsistently | Use deterministic test data and mock LLM responses |
| Slow test execution | Implement test data caching and parallel execution |
| Evaluation scores varying | Ensure consistent scoring criteria and test environment |

## 17. Course Support

### 17.1 Getting Help

- **Issues**: Report problems at [GitHub Issues](https://github.com/dextersjab/agentic-course-case-study-0/issues)
- **Discussion**: Use GitHub Discussions for questions and collaboration
- **Documentation**: Comprehensive guides in `/docs` directory

### 17.2 Contributing

Participants are encouraged to:
1. Fork the repository
2. Implement required features
3. Add comprehensive tests
4. Submit pull requests with clear descriptions

---

## 🎓 About This Course

This case study is part of the **Enterprise Agent Development Course**, focusing on building practical AI agents that handle real-world business scenarios. This particular case study emphasizes **intelligent LangGraph workflows** with LLM-driven decision making, distinguishing it from other case studies that focus on ReAct loops and complex workflow orchestration.

### 🚀 Next Steps

1. **Clone the repository** and explore the codebase
2. **Set up your development environment** with OpenRouter API access
3. **Run the existing tests** to understand the evaluation criteria
4. **Start implementing** your LangGraph workflow
5. **Test thoroughly** with the provided scenarios

*For questions or feedback, please open an issue on GitHub. Happy coding!*