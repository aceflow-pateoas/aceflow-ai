"""
Unit tests for smart completion module
"""
import pytest
from aceflow_mcp_server.contract.completion import SmartCompletion


class TestSmartCompletion:
    """Test SmartCompletion class"""

    @pytest.fixture
    def completion(self):
        """Create SmartCompletion instance"""
        rules = [
            {"pattern": r".*[Ii]d$", "example": 12345},
            {"pattern": r".*[Dd]ate$", "example": "2025-01-01"},
            {"pattern": r".*[Uu]uid$", "example": "550e8400-e29b-41d4-a716-446655440000"},
            {"pattern": r".*[Ee]mail$", "example": "user@example.com"},
            {"pattern": r".*[Pp]hone$", "example": "13800138000"}
        ]
        return SmartCompletion(rules)

    def test_match_id_field(self, completion):
        """Test matching ID fields"""
        assert completion.get_example_for_property("userId", {}) == 12345
        assert completion.get_example_for_property("orderId", {}) == 12345
        assert completion.get_example_for_property("id", {}) == 12345
        assert completion.get_example_for_property("ID", {}) == 12345

    def test_match_date_field(self, completion):
        """Test matching date fields"""
        assert completion.get_example_for_property("createDate", {}) == "2025-01-01"
        assert completion.get_example_for_property("updateDate", {}) == "2025-01-01"
        assert completion.get_example_for_property("date", {}) == "2025-01-01"

    def test_match_uuid_field(self, completion):
        """Test matching UUID fields"""
        assert completion.get_example_for_property("uuid", {}) == "550e8400-e29b-41d4-a716-446655440000"
        assert completion.get_example_for_property("requestUuid", {}) == "550e8400-e29b-41d4-a716-446655440000"

    def test_match_email_field(self, completion):
        """Test matching email fields"""
        assert completion.get_example_for_property("email", {}) == "user@example.com"
        assert completion.get_example_for_property("userEmail", {}) == "user@example.com"

    def test_match_phone_field(self, completion):
        """Test matching phone fields"""
        assert completion.get_example_for_property("phone", {}) == "13800138000"
        assert completion.get_example_for_property("mobilePhone", {}) == "13800138000"

    def test_no_match(self, completion):
        """Test fields that don't match any pattern"""
        assert completion.get_example_for_property("username", {}) is None
        assert completion.get_example_for_property("address", {}) is None

    def test_existing_example_preserved(self, completion):
        """Test that existing examples are not overwritten"""
        schema = {"example": "existing_value"}
        result = completion.get_example_for_property("userId", schema)
        assert result == "existing_value"

    def test_apply_to_simple_schema(self, completion):
        """Test applying completion to a simple schema"""
        schema = {
            "type": "object",
            "properties": {
                "userId": {"type": "integer"},
                "username": {"type": "string"},
                "email": {"type": "string"}
            }
        }

        count = completion.apply_to_schema(schema)

        assert count == 2  # userId and email should be completed
        assert schema["properties"]["userId"]["example"] == 12345
        assert schema["properties"]["email"]["example"] == "user@example.com"
        assert "example" not in schema["properties"]["username"]

    def test_apply_to_nested_schema(self, completion):
        """Test applying completion to nested schemas"""
        schema = {
            "type": "object",
            "properties": {
                "user": {
                    "type": "object",
                    "properties": {
                        "userId": {"type": "integer"},
                        "email": {"type": "string"}
                    }
                },
                "createDate": {"type": "string"}
            }
        }

        count = completion.apply_to_schema(schema)

        assert count == 3  # userId, email, and createDate
        assert schema["properties"]["user"]["properties"]["userId"]["example"] == 12345
        assert schema["properties"]["user"]["properties"]["email"]["example"] == "user@example.com"
        assert schema["properties"]["createDate"]["example"] == "2025-01-01"

    def test_apply_to_openapi_spec(self, completion):
        """Test applying completion to full OpenAPI spec"""
        openapi_spec = {
            "paths": {
                "/api/user/{userId}": {
                    "get": {
                        "responses": {
                            "200": {
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "properties": {
                                                "userId": {"type": "integer"},
                                                "email": {"type": "string"},
                                                "phone": {"type": "string"}
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

        count = completion.apply_to_openapi(openapi_spec)

        assert count == 3
        schema = openapi_spec["paths"]["/api/user/{userId}"]["get"]["responses"]["200"]["content"]["application/json"]["schema"]
        assert schema["properties"]["userId"]["example"] == 12345
        assert schema["properties"]["email"]["example"] == "user@example.com"
        assert schema["properties"]["phone"]["example"] == "13800138000"

    def test_apply_with_existing_examples(self, completion):
        """Test that existing examples are preserved"""
        schema = {
            "type": "object",
            "properties": {
                "userId": {"type": "integer", "example": 999},
                "email": {"type": "string"}
            }
        }

        count = completion.apply_to_schema(schema)

        assert count == 1  # Only email should be added
        assert schema["properties"]["userId"]["example"] == 999  # Preserved
        assert schema["properties"]["email"]["example"] == "user@example.com"  # Added

    def test_empty_rules(self):
        """Test completion with no rules"""
        completion = SmartCompletion([])

        schema = {
            "type": "object",
            "properties": {
                "userId": {"type": "integer"}
            }
        }

        count = completion.apply_to_schema(schema)
        assert count == 0
        assert "example" not in schema["properties"]["userId"]

    def test_case_sensitive_matching(self, completion):
        """Test that pattern matching is case-sensitive"""
        # Should match
        assert completion.get_example_for_property("userId", {}) == 12345
        assert completion.get_example_for_property("ID", {}) == 12345

        # Pattern is .*[Ii]d$ so it should match both cases at the end
        assert completion.get_example_for_property("userID", {}) == 12345

    def test_multiple_patterns_same_field(self):
        """Test field matching multiple patterns (first match wins)"""
        rules = [
            {"pattern": r".*[Ii]d$", "example": 12345},
            {"pattern": r"^user.*", "example": "user_value"}
        ]
        completion = SmartCompletion(rules)

        # userId matches both patterns, first should win
        assert completion.get_example_for_property("userId", {}) == 12345
