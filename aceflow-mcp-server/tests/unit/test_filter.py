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
        filter_obj = ContractFilter('prefix', '/api/user/')

        assert filter_obj.matches('/api/user/login') is True
        assert filter_obj.matches('/api/user/logout') is True
        assert filter_obj.matches('/api/user/profile') is True
        assert filter_obj.matches('/api/admin/settings') is False
        assert filter_obj.matches('/api/reports/list') is False

    def test_regex_match(self):
        """Test regex path matching"""
        # Match all /api/user/* endpoints
        filter_obj = ContractFilter('regex', r'^/api/user/.*')

        assert filter_obj.matches('/api/user/login') is True
        assert filter_obj.matches('/api/user/123') is True
        assert filter_obj.matches('/api/admin/login') is False

    def test_regex_complex_pattern(self):
        """Test complex regex patterns"""
        # Match paths with numeric IDs
        filter_obj = ContractFilter('regex', r'^/api/\w+/\d+$')

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
        filter_obj = ContractFilter('prefix', '/api/user/')
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

        filter_obj = ContractFilter('prefix', '/api/user/')
        filtered = filter_obj.filter_paths(openapi_spec)

        assert len(filtered['paths']) == 0

    def test_invalid_regex(self):
        """Test invalid regex pattern handling"""
        with pytest.raises(ValueError):
            ContractFilter('regex', '[invalid(regex')

    def test_filter_type_validation(self):
        """Test filter type validation"""
        # Should not raise error for valid types
        ContractFilter('exact', '/api/test')
        ContractFilter('prefix', '/api/test')
        ContractFilter('regex', '^/api/test')

        # Invalid type should work but with warning (or we could add validation)
        filter_obj = ContractFilter('unknown', '/api/test')
        assert filter_obj.matches('/api/test') is False

    def test_empty_pattern(self):
        """Test empty pattern handling"""
        filter_obj = ContractFilter('prefix', '')

        # Empty prefix matches everything
        assert filter_obj.matches('/api/user/login') is True
        assert filter_obj.matches('/anything') is True

    def test_case_sensitivity(self):
        """Test case sensitivity in matching"""
        filter_obj = ContractFilter('exact', '/api/User/Login')

        # Exact match is case-sensitive
        assert filter_obj.matches('/api/User/Login') is True
        assert filter_obj.matches('/api/user/login') is False

    def test_regex_case_insensitive(self):
        """Test case-insensitive regex matching"""
        filter_obj = ContractFilter('regex', r'(?i)^/api/user/.*')

        assert filter_obj.matches('/api/user/login') is True
        assert filter_obj.matches('/api/USER/login') is True
        assert filter_obj.matches('/api/User/Login') is True
