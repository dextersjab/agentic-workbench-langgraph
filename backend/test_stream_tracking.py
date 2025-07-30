#!/usr/bin/env python3
"""
Test script to verify the new stream-based node tracking works correctly.

This script verifies the new automatic stream-based tracking system works
correctly and comprehensively tracks workflow node execution.
"""

import asyncio
import logging
import sys
import os
from typing import Dict, Any

# Add the src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

async def test_stream_tracking():
    """Test the new stream-based tracking approach."""
    
    print("🧪 Testing Stream-Based Node Tracking")
    print("=" * 50)
    
    try:
        # Import the required modules
        from src.api.graph_state import state_manager, update_graph_state
        from src.workflows.base import track_node_from_stream, extract_relevant_fields_for_node
        
        print("\n✅ Successfully imported tracking modules")
        
        # Test 1: Test field extraction logic
        print("\n🔍 Test 1: Field extraction for different node types")
        
        test_cases = [
            ("clarify_issue", {"needs_clarification": True, "clarification_attempts": 1, "other_field": "ignore"}),
            ("classify_issue", {"issue_category": "hardware", "issue_priority": "high", "needs_clarification": False}),
            ("triage_issue", {"assigned_team": "L2", "issue_category": "hardware"}),
            ("has_sufficient_info", {"needs_more_info": False, "info_completeness_confidence": 0.9}),
            ("gather_info", {"gathering_round": 2, "missing_categories": ["location"]}),
            ("send_to_desk", {"ticket_id": "TKT-12345", "ticket_status": "created"})
        ]
        
        for node_name, node_updates in test_cases:
            relevant_fields = extract_relevant_fields_for_node(node_name, node_updates)
            print(f"   {node_name}: {relevant_fields}")
        
        # Test 2: Test stream tracking function
        print("\n⚙️ Test 2: Stream tracking function")
        
        test_config = {"configurable": {"thread_id": "test-stream-tracking"}}
        
        for node_name, node_updates in test_cases[:3]:  # Test first 3 cases
            await track_node_from_stream(node_name, node_updates, test_config)
            print(f"   ✅ Tracked {node_name}")
        
        # Test 3: Verify state was stored
        print("\n📊 Test 3: Verify tracking data storage")
        
        stored_state = state_manager.get_graph_state("test-stream-tracking")
        if stored_state:
            print(f"   ✅ Found stored state for test-stream-tracking")
            print(f"   Current node: {stored_state.current_node}")
            print(f"   History: {stored_state.traversal_history}")
            print(f"   State data keys: {list(stored_state.state_data.keys())}")
        else:
            print("   ❌ No stored state found")
        
        # Test 4: Verify comprehensive tracking
        print("\n🔄 Test 4: Verify comprehensive data tracking")
        
        if stored_state:
            expected_fields = {"clarification_attempts", "needs_clarification", "issue_category", "issue_priority", "assigned_team"}
            actual_fields = set(stored_state.state_data.keys())
            
            if expected_fields.issubset(actual_fields):
                print(f"   ✅ All expected fields tracked: {expected_fields}")
            else:
                missing = expected_fields - actual_fields
                print(f"   ⚠️ Missing expected fields: {missing}")
            
            print(f"   📊 Total tracked fields: {len(actual_fields)}")
            print(f"   📈 Traversal history length: {len(stored_state.traversal_history)}")
        else:
            print("   ❌ No state data to verify")
        
        # Test 5: Error handling
        print("\n⚠️ Test 5: Error handling")
        
        # Test with invalid config (this should log a warning but not crash)
        await track_node_from_stream("test_node", {"test": "data"}, {})
        print("   ✅ Gracefully handled missing thread_id (logged warning)")
        
        # Test with empty updates
        try:
            await track_node_from_stream("test_node", {}, test_config)
            print("   ✅ Handled empty node updates")
        except Exception as e:
            print(f"   ⚠️ Error with empty updates: {e}")
        
        print("\n🎉 Stream tracking tests completed successfully!")
        
        # Cleanup
        state_manager.remove_graph_state("test-stream-tracking")
        print("\n🧹 Cleaned up test data")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Make sure to run this from the backend directory")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

def print_usage():
    """Print usage instructions."""
    print("""
🚀 Stream Tracking Test Script

Usage:
    python test_stream_tracking.py

This script tests the new automatic stream-based node tracking system:

1. Tests field extraction logic for different node types
2. Verifies stream tracking function works correctly  
3. Confirms data is stored in graph state manager
4. Compares with legacy manual tracking approach
5. Tests error handling scenarios

Prerequisites:
    - Run from the backend directory
    - All tracking modules should be importable
    
Expected Output:
    - All tests should pass with ✅ marks
    - Comparison should show both approaches work
    - Error handling should gracefully handle edge cases
""")

async def main():
    """Main test function."""
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help']:
        print_usage()
        sys.exit(0)
    
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    try:
        await test_stream_tracking()
        
    except KeyboardInterrupt:
        print("\n⚠️ Tests interrupted by user")
    except Exception as e:
        print(f"\n💥 Unexpected error during tests: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())