"""
Unit tests for contract filter module
"""
import pytest
from aceflow_mcp_server.contract.filter import ContractFilter


class TestContractFilter:
    """Test ContractFilter class"""

    def test_exact_match_single(self):
        """Test exact path matching"""
        filter_obj = ContractFilter({'type': 'exact', 'pattern': '/api/user/login'})

        assert filter_obj.matches('/api/user/login') is True
        assert filter_obj.matches('/api/user/logout') is False
        assert filter_obj.matches('/api/user') is False

    def test_prefix_match(self):
        """Test prefix path matching"""
        filter_obj = ContractFilter({'type': 'prefix', 'pattern': '/api/user/'})

        assert filter_obj.matches('/api/user/login') is True
        assert filter_obj.matches('/api/user/logout') is True
        assert filter_obj.matches('/api/user/profile') is True
        assert filter_obj.matches('/api/admin/settings') is False
        assert filter_obj.matches('/api/reports/list') is False

    def test_regex_match(self):
        """Test regex path matching"""
        # Match all /api/user/* endpoints
        filter_obj = ContractFilter({'type': 'regex', 'pattern': r'^/api/user/.*'})

        assert filter_obj.matches('/api/user/login') is True
        assert filter_obj.matches('/api/user/123') is True
        assert filter_obj.matches('/api/admin/login') is False

    def test_regex_complex_pattern(self):
        """Test complex regex patterns"""
        # Match paths with numeric IDs
        filter_obj = ContractFilter({'type': 'regex', 'pattern': r'^/api/\w+/\d+$'})

        assert filter_obj.matches('/api/user/123') is True
        assert filter_obj.matches('/api/product/456') is True
        assert filter_obj.matches('/api/user/login') is False

    def test_filter_paths(self):
        """Test filtering OpenAPI paths"""
        openapi_spec = {
            "paths": {
                "/api/user/login": {"post": {}},
                "/api/user/logout": {"post": {}},
                "/api/user/123": {"get": {}},
                "/api/admin/settings": {"get": {}},
                "/api/reports/export": {"post": {}}
            }
        }

        # Test prefix filter
        filter_obj = ContractFilter({'type': 'prefix', 'pattern': '/api/user/'})
        filtered = filter_obj.filter_paths(openapi_spec)

        assert len(filtered['paths']) == 3
        assert '/api/user/login' in filtered['paths']
        assert '/api/user/logout' in filtered['paths']
        assert '/api/user/123' in filtered['paths']
        assert '/api/admin/settings' not in filtered['paths']

    def test_filter_paths_no_match(self):
        """Test filtering with no matches"""
        openapi_spec = {
            "paths": {
                "/api/admin/settings": {"get": {}},
                "/api/reports/export": {"post": {}}
            }
        }

        filter_obj = ContractFilter({'type': 'prefix', 'pattern': '/api/user/'})
        filtered = filter_obj.filter_paths(openapi_spec)

        assert len(filtered['paths']) == 0

    def test_invalid_regex(self):
        """Test invalid regex pattern handling"""
        with pytest.raises(ValueError):
            ContractFilter({'type': 'regex', 'pattern': '[invalid(regex'})

    def test_filter_type_validation(self):
        """Test filter type validation"""
        # Should not raise error for valid types
        ContractFilter({'type': 'exact', 'pattern': '/api/test'})
        ContractFilter({'type': 'prefix', 'pattern': '/api/test'})
        ContractFilter({'type': 'regex', 'pattern': '^/api/test'})

        # Invalid type should raise ValueError
        filter_obj = ContractFilter({'type': 'unknown', 'pattern': '/api/test'})
        with pytest.raises(ValueError, match="Unknown filter type"):
            filter_obj.matches('/api/test')

    def test_empty_pattern(self):
        """Test empty pattern handling"""
        filter_obj = ContractFilter({'type': 'prefix', 'pattern': ''})

        # Empty prefix matches everything
        assert filter_obj.matches('/api/user/login') is True
        assert filter_obj.matches('/anything') is True

    def test_case_sensitivity(self):
        """Test case sensitivity in matching"""
        filter_obj = ContractFilter({'type': 'exact', 'pattern': '/api/User/Login'})

        # Exact match is case-sensitive
        assert filter_obj.matches('/api/User/Login') is True
        assert filter_obj.matches('/api/user/login') is False

    def test_regex_case_insensitive(self):
        """Test case-insensitive regex matching"""
        filter_obj = ContractFilter({'type': 'regex', 'pattern': r'(?i)^/api/user/.*'})

        assert filter_obj.matches('/api/user/login') is True
        assert filter_obj.matches('/api/USER/login') is True
        assert filter_obj.matches('/api/User/Login') is True
