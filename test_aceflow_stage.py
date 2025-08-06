#!/usr/bin/env python3
"""Test script for aceflow_stage functionality."""

import sys
import os
from pathlib import Path

# Add the aceflow-mcp-server to the path
sys.path.insert(0, str(Path(__file__).parent / "aceflow-mcp-server"))

from aceflow_mcp_server.tools import AceFlowTools

def test_aceflow_stage():
    """Test the aceflow_stage functionality."""
    tools = AceFlowTools()
    
    print("🧪 Testing aceflow_stage tool...")
    print("=" * 50)
    
    # Test 1: Check status
    print("\n📊 Test 1: Check project status")
    result = tools.aceflow_stage(action="status")
    print(f"Result: {result}")
    
    # Test 2: List all stages
    print("\n📋 Test 2: List all stages")
    result = tools.aceflow_stage(action="list")
    print(f"Result: {result}")
    
    # Test 3: Try to advance to next stage
    print("\n⏭️ Test 3: Advance to next stage")
    result = tools.aceflow_stage(action="next")
    print(f"Result: {result}")
    
    # Test 4: Reset project (if needed)
    print("\n🔄 Test 4: Reset project")
    result = tools.aceflow_stage(action="reset")
    print(f"Result: {result}")
    
    # Test 5: Invalid action
    print("\n❌ Test 5: Invalid action")
    result = tools.aceflow_stage(action="invalid")
    print(f"Result: {result}")

if __name__ == "__main__":
    test_aceflow_stage()