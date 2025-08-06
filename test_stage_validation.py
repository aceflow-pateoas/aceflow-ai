#!/usr/bin/env python3
"""Test stage input/output validation mechanism."""

import sys
import os
from pathlib import Path

# Add the aceflow-mcp-server to the path
sys.path.insert(0, str(Path(__file__).parent / "aceflow-mcp-server"))

from aceflow_mcp_server.core.stage_engine import StageEngine, StageDefinition

def test_stage_validation():
    """Test stage input/output validation."""
    print("🧪 Testing Stage Input/Output Validation...")
    print("=" * 60)
    
    # Create a test project directory
    test_project = Path("debug-test-output")
    if not test_project.exists():
        print("❌ Test project directory not found")
        return
    
    # Initialize StageEngine
    stage_engine = StageEngine(test_project)
    
    # Test 1: Check stage requirements
    print("\n📋 Test 1: Get stage requirements")
    requirements = stage_engine.get_stage_requirements("user_stories")
    print(f"Requirements: {requirements}")
    
    # Test 2: Validate stage readiness
    print("\n✅ Test 2: Validate stage readiness")
    readiness = stage_engine.validate_stage_readiness("user_stories")
    print(f"Readiness: {readiness}")
    
    # Test 3: Try to execute current stage
    print("\n🚀 Test 3: Execute current stage")
    try:
        result = stage_engine.execute_current_stage()
        print(f"Execution result: {result}")
    except Exception as e:
        print(f"Execution failed: {e}")
    
    # Test 4: Check next stage
    print("\n⏭️ Test 4: Get next stage")
    next_stage = stage_engine.get_next_stage()
    print(f"Next stage: {next_stage}")

if __name__ == "__main__":
    test_stage_validation()