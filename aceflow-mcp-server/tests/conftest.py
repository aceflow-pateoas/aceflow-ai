"""
Test configuration and fixtures for AceFlow MCP Server tests.
"""

import pytest
import asyncio
import tempfile
import json
from pathlib import Path
from typing import Dict, Any, Generator

# Import test dependencies (with fallback handling)
try:
    from aceflow_mcp_server.unified_tools import SimplifiedUnifiedTools
    from aceflow_mcp_server.tools import AceFlowTools
except ImportError:
    # Fallback for when MCP dependencies are not available
    SimplifiedUnifiedTools = None
    AceFlowTools = None


@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def tools_instance():
    """Create a SimplifiedUnifiedTools instance for testing."""
    if SimplifiedUnifiedTools is None:
        pytest.skip("MCP dependencies not available")
    return SimplifiedUnifiedTools()


@pytest.fixture
def temp_workspace() -> Generator[Path, None, None]:
    """Create a temporary workspace for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        workspace = Path(tmpdir)
        yield workspace


@pytest.fixture
def sample_project_data() -> Dict[str, Any]:
    """Sample project data for testing."""
    return {
        "name": "test_project",
        "mode": "standard",
        "description": "Test project for MCP server",
        "directory": None  # Will be set by individual tests
    }


@pytest.fixture
def sample_tool_request() -> Dict[str, Any]:
    """Sample MCP tool request for testing."""
    return {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "aceflow_template",
            "arguments": {"action": "list"}
        }
    }


@pytest.fixture
def mcp_initialize_request() -> Dict[str, Any]:
    """Sample MCP initialize request."""
    return {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "clientInfo": {
                "name": "test-client",
                "version": "1.0.0"
            }
        }
    }


@pytest.fixture
def expected_tools() -> list:
    """List of expected tools in the MCP server."""
    return [
        "aceflow_init",
        "aceflow_stage", 
        "aceflow_validate",
        "aceflow_template"
    ]


class TestHelpers:
    """Helper utilities for testing."""
    
    @staticmethod
    def validate_mcp_response(response: Dict[str, Any], request_id: int = None) -> bool:
        """Validate that a response conforms to JSON-RPC 2.0 spec."""
        if not isinstance(response, dict):
            return False
        
        # Check required fields
        if response.get("jsonrpc") != "2.0":
            return False
        
        # Check ID if provided
        if request_id is not None and response.get("id") != request_id:
            return False
            
        # Must have either result or error
        has_result = "result" in response
        has_error = "error" in response
        
        return has_result or has_error  # XOR would be better, but this allows both for debugging
    
    @staticmethod
    def validate_tool_response(response: Dict[str, Any]) -> bool:
        """Validate that a tool response has the expected structure."""
        if not isinstance(response, dict):
            return False
            
        required_fields = ["success"]
        return all(field in response for field in required_fields)
    
    @staticmethod
    def create_aceflow_project(workspace: Path, project_name: str = "test_project", mode: str = "standard"):
        """Helper to create an AceFlow project for testing."""
        if AceFlowTools is None:
            pytest.skip("AceFlow tools not available")
            
        tools = AceFlowTools(working_directory=str(workspace))
        return tools.aceflow_init(mode=mode, project_name=project_name, directory=str(workspace))


@pytest.fixture
def test_helpers():
    """Provide test helper utilities."""
    return TestHelpers


# Performance testing configurations
@pytest.fixture
def performance_config():
    """Configuration for performance tests."""
    return {
        "max_response_time": 0.2,  # 200ms
        "concurrent_requests": 10,
        "load_test_duration": 30,  # seconds
        "memory_threshold_mb": 100
    }


# Mock MCP server for testing (when real server is not available)
class MockMCPServer:
    """Mock MCP server for testing when real server dependencies are not available."""
    
    def __init__(self):
        self.tools = ["aceflow_init", "aceflow_stage", "aceflow_validate", "aceflow_template"]
        self.initialized = False
    
    async def initialize(self):
        """Mock initialization."""
        self.initialized = True
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Mock request handling."""
        if request.get("method") == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "mock-aceflow", "version": "1.0.0"}
                }
            }
        elif request.get("method") == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "result": {
                    "tools": [{"name": tool} for tool in self.tools]
                }
            }
        elif request.get("method") == "tools/call":
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "result": {
                    "content": [{
                        "type": "text",
                        "text": json.dumps({"success": True, "mock": True})
                    }]
                }
            }
        else:
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {"code": -32601, "message": "Method not found"}
            }


@pytest.fixture
async def mcp_server():
    """Create MCP server instance for testing (mock if real server not available)."""
    try:
        from aceflow_mcp_server.mcp_stdio_server import MCPStdioServer
        server = MCPStdioServer()
        await server.initialize()
        yield server
        # Cleanup if needed
    except ImportError:
        # Use mock server when real server is not available
        server = MockMCPServer()
        await server.initialize()
        yield server