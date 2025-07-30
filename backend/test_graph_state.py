#!/usr/bin/env python3
"""
Test script for Graph State API endpoints.

This script tests the graph state tracking functionality by making
direct API calls to verify the endpoints work correctly.
"""

import asyncio
import aiohttp
import json
import sys
from typing import Dict, Any, Optional

# Base URL for the API
BASE_URL = "http://localhost:8000"

async def test_graph_state_api():
    """Test the graph state API endpoints."""
    
    print("🧪 Starting Graph State API Tests")
    print("=" * 50)
    
    async with aiohttp.ClientSession() as session:
        
        # Test 1: List active chats (should be empty initially)
        print("\n📋 Test 1: List active chats")
        try:
            async with session.get(f"{BASE_URL}/v1/graph-state") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Active chats: {data}")
                else:
                    print(f"❌ Failed to list active chats: {response.status}")
        except Exception as e:
            print(f"❌ Error listing active chats: {e}")
        
        # Test 2: Try to get state for non-existent chat (should return 404)
        print("\n🔍 Test 2: Get non-existent chat state")
        test_chat_id = "test-chat-123"
        try:
            async with session.get(f"{BASE_URL}/v1/graph-state/{test_chat_id}") as response:
                if response.status == 404:
                    print(f"✅ Correctly returned 404 for non-existent chat: {test_chat_id}")
                else:
                    print(f"❌ Unexpected status for non-existent chat: {response.status}")
        except Exception as e:
            print(f"❌ Error getting non-existent chat state: {e}")
        
        # Test 3: Simulate workflow execution by directly calling the state manager
        print("\n⚙️ Test 3: Simulate workflow state updates")
        try:
            # Import the state manager to simulate workflow updates
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
            
            from src.api.graph_state import update_graph_state
            
            # Simulate some workflow progression
            test_chat_id = "chat-test-simulation"
            
            # Simulate classify_issue node
            update_graph_state(test_chat_id, "classify_issue", {
                "issue_category": None,
                "needs_clarification": True,
                "clarification_attempts": 0
            })
            
            # Simulate clarify_issue node
            update_graph_state(test_chat_id, "clarify_issue", {
                "issue_category": None,
                "needs_clarification": True,
                "clarification_attempts": 1
            })
            
            # Simulate classify_issue again (after clarification)
            update_graph_state(test_chat_id, "classify_issue", {
                "issue_category": "hardware",
                "issue_priority": "medium",
                "needs_clarification": False,
                "clarification_attempts": 1
            })
            
            # Simulate triage_issue node
            update_graph_state(test_chat_id, "triage_issue", {
                "issue_category": "hardware",
                "issue_priority": "medium",
                "assigned_team": "L2",
                "needs_clarification": False
            })
            
            print(f"✅ Simulated workflow progression for {test_chat_id}")
            
        except Exception as e:
            print(f"❌ Error simulating workflow: {e}")
        
        # Test 4: Get the simulated chat state
        print("\n📊 Test 4: Get simulated chat state")
        try:
            async with session.get(f"{BASE_URL}/v1/graph-state/{test_chat_id}") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Retrieved state for {test_chat_id}:")
                    print(f"   Current node: {data.get('current_node')}")
                    print(f"   Traversal history: {data.get('traversal_history')}")
                    print(f"   State data: {json.dumps(data.get('state_data', {}), indent=2)}")
                    print(f"   Graph structure: {len(data.get('graph_structure', {}).get('nodes', []))} nodes, {len(data.get('graph_structure', {}).get('edges', []))} edges")
                else:
                    print(f"❌ Failed to get chat state: {response.status}")
                    error_text = await response.text()
                    print(f"   Error: {error_text}")
        except Exception as e:
            print(f"❌ Error getting chat state: {e}")
        
        # Test 5: List active chats again (should show our test chat)
        print("\n📋 Test 5: List active chats (after simulation)")
        try:
            async with session.get(f"{BASE_URL}/v1/graph-state") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Active chats: {data}")
                    if test_chat_id in data.get('active_chats', []):
                        print(f"✅ Test chat {test_chat_id} found in active chats")
                    else:
                        print(f"❌ Test chat {test_chat_id} not found in active chats")
                else:
                    print(f"❌ Failed to list active chats: {response.status}")
        except Exception as e:
            print(f"❌ Error listing active chats: {e}")
        
        # Test 6: Delete the test chat state
        print("\n🗑️ Test 6: Delete test chat state")
        try:
            async with session.delete(f"{BASE_URL}/v1/graph-state/{test_chat_id}") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Deleted chat state: {data}")
                else:
                    print(f"❌ Failed to delete chat state: {response.status}")
                    error_text = await response.text()
                    print(f"   Error: {error_text}")
        except Exception as e:
            print(f"❌ Error deleting chat state: {e}")
        
        # Test 7: Verify deletion worked
        print("\n🔍 Test 7: Verify chat deletion")
        try:
            async with session.get(f"{BASE_URL}/v1/graph-state/{test_chat_id}") as response:
                if response.status == 404:
                    print(f"✅ Chat state correctly deleted (404 returned)")
                else:
                    print(f"❌ Chat state not deleted (status: {response.status})")
        except Exception as e:
            print(f"❌ Error verifying deletion: {e}")

def print_usage():
    """Print usage instructions."""
    print("""
🚀 Graph State API Test Script

Usage:
    python test_graph_state.py

Prerequisites:
    1. Start the backend server:
       cd backend && python main.py
    
    2. Ensure the server is running on http://localhost:8000
    
    3. Run this test script to verify graph state functionality

Manual API Testing:
    # List active chats
    curl http://localhost:8000/v1/graph-state
    
    # Get specific chat state (replace CHAT_ID)
    curl http://localhost:8000/v1/graph-state/CHAT_ID
    
    # Delete specific chat state  
    curl -X DELETE http://localhost:8000/v1/graph-state/CHAT_ID
    
    # Cleanup old states
    curl -X POST "http://localhost:8000/v1/graph-state/cleanup?max_age_hours=1"

Integration Testing:
    1. Start a conversation in OpenWebUI
    2. Note the chat ID from browser network tab
    3. Check graph state: curl http://localhost:8000/v1/graph-state/chat-CHAT_ID
    4. Send messages and watch the state evolve
    5. Verify traversal history shows node progression

Expected Flow:
    classify_issue → clarify_issue → classify_issue → triage_issue → 
    has_sufficient_info → gather_info → has_sufficient_info → send_to_desk
""")

async def main():
    """Main test function."""
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help']:
        print_usage()
        sys.exit(0)
    
    try:
        await test_graph_state_api()
        print("\n🎉 Graph State API tests completed!")
        print("\nNext steps:")
        print("1. Start a conversation in OpenWebUI")
        print("2. Monitor the graph state API during conversation")
        print("3. Verify workflow progression is tracked accurately")
        
    except KeyboardInterrupt:
        print("\n⚠️ Tests interrupted by user")
    except Exception as e:
        print(f"\n💥 Unexpected error during tests: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())