#!/usr/bin/env python3
"""
Real-time monitoring script to watch node tracking in action.

This script monitors the graph state API and shows live updates
as workflow nodes execute during conversations.
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"

class GraphStateMonitor:
    def __init__(self):
        self.known_chats = set()
        self.last_states = {}
    
    async def check_active_chats(self, session):
        """Check for active chats and monitor new ones."""
        try:
            async with session.get(f"{BASE_URL}/v1/graph-state") as response:
                if response.status == 200:
                    data = await response.json()
                    current_chats = set(data.get('active_chats', []))
                    
                    # Check for new chats
                    new_chats = current_chats - self.known_chats
                    if new_chats:
                        print(f"\n🆕 New conversations detected: {list(new_chats)}")
                        self.known_chats.update(new_chats)
                    
                    # Monitor all active chats
                    for chat_id in current_chats:
                        await self.monitor_chat(session, chat_id)
                        
        except Exception as e:
            print(f"❌ Error checking active chats: {e}")
    
    async def monitor_chat(self, session, chat_id):
        """Monitor a specific chat for state changes."""
        try:
            async with session.get(f"{BASE_URL}/v1/graph-state/{chat_id}") as response:
                if response.status == 200:
                    current_state = await response.json()
                    
                    # Check if state changed
                    last_state = self.last_states.get(chat_id)
                    if not last_state or self.state_changed(last_state, current_state):
                        self.display_state_update(chat_id, current_state, last_state)
                        self.last_states[chat_id] = current_state
                        
        except Exception as e:
            print(f"❌ Error monitoring chat {chat_id}: {e}")
    
    def state_changed(self, old_state, new_state):
        """Check if significant state changes occurred."""
        if not old_state:
            return True
            
        # Check for node changes
        if old_state.get('current_node') != new_state.get('current_node'):
            return True
            
        # Check for history changes
        old_history = old_state.get('traversal_history', [])
        new_history = new_state.get('traversal_history', [])
        if len(old_history) != len(new_history):
            return True
            
        # Check for state data changes
        old_data = old_state.get('state_data', {})
        new_data = new_state.get('state_data', {})
        if old_data != new_data:
            return True
            
        return False
    
    def display_state_update(self, chat_id, current_state, last_state):
        """Display a formatted state update."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"\n📊 [{timestamp}] UPDATE: {chat_id}")
        
        current_node = current_state.get('current_node')
        history = current_state.get('traversal_history', [])
        state_data = current_state.get('state_data', {})
        
        if last_state:
            last_node = last_state.get('current_node')
            if current_node != last_node:
                print(f"   🔄 Node: {last_node} → {current_node}")
            
            last_history = last_state.get('traversal_history', [])
            if len(history) > len(last_history):
                new_nodes = history[len(last_history):]
                print(f"   📈 New nodes: {' → '.join(new_nodes)}")
        else:
            print(f"   🎯 Current node: {current_node}")
            print(f"   📜 Full history: {' → '.join(history)}")
        
        # Show interesting state changes
        interesting_fields = ['issue_category', 'issue_priority', 'assigned_team', 
                            'needs_clarification', 'ticket_id', 'gathering_round']
        
        relevant_data = {k: v for k, v in state_data.items() if k in interesting_fields}
        if relevant_data:
            print(f"   💾 State: {json.dumps(relevant_data, indent=6)}")

async def main():
    """Main monitoring loop."""
    print("🔍 Graph State Monitor - Watching for workflow activity...")
    print("=" * 60)
    print("💡 Start a conversation in OpenWebUI or send API requests to see tracking!")
    print("🔗 Test endpoint: POST http://localhost:8000/v1/chat/completions")
    print("📊 Monitor endpoint: GET http://localhost:8000/v1/graph-state")
    print("\n⏱️  Monitoring every 2 seconds... (Press Ctrl+C to stop)")
    
    monitor = GraphStateMonitor()
    
    async with aiohttp.ClientSession() as session:
        try:
            while True:
                await monitor.check_active_chats(session)
                await asyncio.sleep(2)  # Check every 2 seconds
                
        except KeyboardInterrupt:
            print("\n\n👋 Monitoring stopped by user")
        except Exception as e:
            print(f"\n💥 Unexpected error: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")