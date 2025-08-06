#!/usr/bin/env python3
"""Simple test for stage validation mechanism."""

import sys
import os
from pathlib import Path

# Add the aceflow-mcp-server to the path
sys.path.insert(0, str(Path(__file__).parent / "aceflow-mcp-server"))

from aceflow_mcp_server.tools import AceFlowTools

def test_stage_execute():
    """Test stage execution with input/output validation."""
    print("🧪 Testing Stage Execution with I/O Validation...")
    print("=" * 60)
    
    tools = AceFlowTools()
    
    # Test in project directory
    os.chdir("debug-test-output")
    
    # Test 1: Execute current stage
    print("\n🚀 Test 1: Execute current stage")
    result = tools.aceflow_stage(action="execute")
    print(f"Execute result: {result}")
    
    # Test 2: Check if output was created
    print("\n📁 Test 2: Check output files")
    result_dir = Path("aceflow_result")
    if result_dir.exists():
        files = list(result_dir.glob("*.md"))
        print(f"Generated files: {[f.name for f in files]}")
        
        # Read the first file to see content
        if files:
            content = files[0].read_text(encoding='utf-8')
            print(f"\nContent preview of {files[0].name}:")
            print(content[:300] + "..." if len(content) > 300 else content)
    else:
        print("No aceflow_result directory found")
    
    # Test 3: Try to execute a specific stage
    print("\n🎯 Test 3: Execute specific stage")
    result = tools.aceflow_stage(action="execute", stage="implementation")
    print(f"Specific stage result: {result}")

if __name__ == "__main__":
    test_stage_execute()