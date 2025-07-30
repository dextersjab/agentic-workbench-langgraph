# 🧪 Testing Graph State Tracking

## Quick Test (2 minutes)

### 1. Start the Backend
```bash
cd backend
python main.py
```

### 2. Check Initial State (Should be empty)
```bash
curl http://localhost:8000/v1/graph-state
# Expected: {"active_chats": [], "count": 0}
```

### 3. Send a Test Message
```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "x-chat-id: test-tracking" \
  -d '{
    "model": "support-desk",
    "messages": [{"role": "user", "content": "My laptop screen is flickering"}],
    "stream": false
  }'
```

### 4. Check Tracking Worked
```bash
curl http://localhost:8000/v1/graph-state/chat-test-tracking
```

**Expected Response:**
```json
{
  "current_node": "classify_issue",
  "graph_structure": {
    "nodes": ["classify_issue", "clarify_issue", "triage_issue", ...],
    "edges": [...]
  },
  "traversal_history": ["classify_issue"],
  "state_data": {
    "issue_category": "hardware",
    "issue_priority": "medium",
    "needs_clarification": false
  }
}
```

## Real-time Monitoring

### Start the Monitor
```bash
cd backend
python monitor_tracking.py
```

Then start a conversation in OpenWebUI or send API requests. You'll see live updates like:

```
📊 [14:32:15] UPDATE: chat-test-tracking
   🎯 Current node: classify_issue
   📜 Full history: classify_issue
   💾 State: {
      "issue_category": "hardware",
      "issue_priority": "medium"
   }

📊 [14:32:18] UPDATE: chat-test-tracking  
   🔄 Node: classify_issue → triage_issue
   📈 New nodes: triage_issue
   💾 State: {
      "assigned_team": "L2",
      "issue_category": "hardware"
   }
```

## Full Integration Test

### 1. Start Full Stack
```bash
docker-compose up
```

### 2. Open OpenWebUI
http://localhost:3000

### 3. Start Conversation
Send: "My computer won't start"

### 4. Monitor in Real-time
```bash
# In new terminal
python backend/monitor_tracking.py
```

### 5. Continue Conversation
- Watch the monitor show node transitions
- See state data update as workflow progresses
- Note traversal history growing

## What to Look For

### ✅ Success Indicators:
- **Active chats appear** in `/v1/graph-state`
- **Current node updates** as workflow progresses  
- **Traversal history grows** with each node execution
- **State data contains** relevant fields (category, priority, etc.)
- **Multiple chats** maintain separate state

### ❌ Failure Signs:
- Empty response from graph state API
- Same node repeated without state changes
- Missing state data fields
- Error messages in logs

## Troubleshooting

### No Active Chats
- Check backend is running on port 8000
- Verify you sent `x-chat-id` header
- Look for errors in backend logs

### Empty State Data  
- Check backend logs for "Stream tracking" messages
- Verify stream_mode includes "updates"
- Look for tracking error messages

### API Errors
- Confirm endpoints: `/v1/graph-state` and `/v1/graph-state/{chat_id}`
- Check CORS headers if testing from browser
- Verify JSON response format

## Log Messages to Watch For

When tracking works, you should see:
```
INFO:src.api.graph_state:Created new graph state for chat-test: classify_issue
INFO:src.workflows.base:Stream tracking: classify_issue -> {'issue_category': 'hardware'}
INFO:src.api.graph_state:Updated graph state for chat-test: triage_issue  
```

## Expected Workflow Flow

1. **classify_issue** → Sets category/priority
2. **triage_issue** → Sets assigned_team  
3. **has_sufficient_info** → Checks completeness
4. **gather_info** → Asks questions (if needed)
5. **send_to_desk** → Creates ticket

Each step should update the graph state with relevant data!