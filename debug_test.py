#!/usr/bin/env python3
"""Debug test for aceflow-init functionality."""

import sys
import os
from pathlib import Path

# Add the aceflow-mcp-server to the path
sys.path.insert(0, str(Path(__file__).parent / "aceflow-mcp-server"))

from aceflow_mcp_server.tools import AceFlowTools

def test_init():
    """Test the aceflow_init functionality."""
    tools = AceFlowTools()
    
    # Test initialization
    result = tools.aceflow_init(
        mode="standard",
        project_name="debug-test-project",
        directory="./debug-test-output"
    )
    
    print("Result:", result)
    
    # Check if directory was created
    test_dir = Path("debug-test-output")
    if test_dir.exists():
        print(f"Project directory created: {test_dir}")
        
        clinerules_path = test_dir / ".clinerules"
        if clinerules_path.exists():
            if clinerules_path.is_dir():
                print(f"✅ .clinerules is a directory")
                files = list(clinerules_path.glob("*.md"))
                print(f"Files in .clinerules: {[f.name for f in files]}")
            else:
                print(f"❌ .clinerules is a file, not a directory")
                with open(clinerules_path, 'r', encoding='utf-8') as f:
                    content = f.read()[:200]
                    print(f"Content preview: {content}...")
        else:
            print("❌ .clinerules not found")
    else:
        print("❌ Project directory not created")

if __name__ == "__main__":
    test_init()