"""
Integration tests for contract management workflow
"""
import pytest
import tempfile
import json
import yaml
from pathlib import Path
from unittest.mock import patch, Mock
from click.testing import CliRunner

from aceflow_mcp_server.cli.main import cli
from aceflow_mcp_server.contract.generator import ContractGenerator
from aceflow_mcp_server.contract.filter import ContractFilter
from aceflow_mcp_server.contract.completion import SmartCompletion
from tests.fixtures import SAMPLE_OPENAPI, SAMPLE_CONFIG


class TestContractWorkflow:
    """Integration tests for contract generation and management workflow"""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def setup_config(self, temp_dir):
        """Setup test configuration"""
        config_dir = temp_dir / ".aceflow"
        config_dir.mkdir(parents=True, exist_ok=True)

        config_file = config_dir / "config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(SAMPLE_CONFIG, f)

        return temp_dir

    def test_contract_generation_workflow(self, setup_config):
        """Test complete contract generation workflow"""
        import os
        original_cwd = os.getcwd()
        os.chdir(setup_config)

        try:
            # Step 1: Fetch OpenAPI spec
            with patch('requests.get') as mock_get:
                mock_response = Mock()
                mock_response.json.return_value = SAMPLE_OPENAPI
                mock_response.raise_for_status = Mock()
                mock_get.return_value = mock_response

                generator = ContractGenerator("http://localhost:8080/v3/api-docs")
                openapi_spec = generator.fetch_openapi()

                assert "openapi" in openapi_spec
                assert len(openapi_spec["paths"]) == 5

            # Step 2: Filter paths
            filter_obj = ContractFilter('prefix', '/api/user/')
            filtered_spec = filter_obj.filter_paths(openapi_spec.copy())

            assert len(filtered_spec["paths"]) == 2
            assert "/api/user/login" in filtered_spec["paths"]
            assert "/api/user/{userId}" in filtered_spec["paths"]

            # Step 3: Apply smart completion
            rules = SAMPLE_CONFIG["aceflow"]["smart_completion"]["rules"]
            completion = SmartCompletion(rules)
            count = completion.apply_to_openapi(filtered_spec)

            assert count > 0

            # Step 4: Save contract
            contracts_dir = Path.cwd() / ".aceflow" / "contracts"
            contracts_dir.mkdir(parents=True, exist_ok=True)

            contract_file = contracts_dir / "user-management.json"
            with open(contract_file, 'w') as f:
                json.dump(filtered_spec, f, indent=2)

            assert contract_file.exists()

            # Verify saved contract
            with open(contract_file) as f:
                saved_spec = json.load(f)
                assert len(saved_spec["paths"]) == 2

        finally:
            os.chdir(original_cwd)

    def test_cli_feature_add_workflow(self, setup_config):
        """Test CLI feature add command workflow"""
        import os
        original_cwd = os.getcwd()
        os.chdir(setup_config)

        try:
            runner = CliRunner()

            # Add a new feature non-interactively
            result = runner.invoke(cli, [
                'feature', 'add',
                '--name', 'test-feature',
                '--api-filter', '/api/test/',
                '--filter-type', 'prefix',
                '--description', 'Test feature',
                '--dev-team', 'test@example.com',
                '--non-interactive'
            ])

            assert result.exit_code == 0
            assert '成功' in result.output or 'success' in result.output.lower()

            # List features
            result = runner.invoke(cli, ['feature', 'list'])
            assert result.exit_code == 0
            assert 'test-feature' in result.output

        finally:
            os.chdir(original_cwd)

    def test_contract_filter_completion_integration(self):
        """Test integration between filtering and completion"""
        # Filter paths
        filter_obj = ContractFilter('prefix', '/api/user/')
        filtered_spec = filter_obj.filter_paths(SAMPLE_OPENAPI.copy())

        # Apply completion
        rules = SAMPLE_CONFIG["aceflow"]["smart_completion"]["rules"]
        completion = SmartCompletion(rules)
        count = completion.apply_to_openapi(filtered_spec)

        # Verify results
        assert len(filtered_spec["paths"]) == 2

        # Check if examples were added
        user_schema = filtered_spec["paths"]["/api/user/{userId}"]["get"]["responses"]["200"]["content"]["application/json"]["schema"]
        properties = user_schema["properties"]

        # Should have examples for userId, email, phone, createDate, uuid
        assert "example" in properties["userId"]
        assert "example" in properties["email"]
        assert properties["userId"]["example"] == 12345
        assert properties["email"]["example"] == "user@example.com"

    def test_multiple_filters_workflow(self):
        """Test workflow with multiple filters"""
        # Test exact match
        exact_filter = ContractFilter('exact', '/api/user/login')
        exact_result = exact_filter.filter_paths(SAMPLE_OPENAPI.copy())
        assert len(exact_result["paths"]) == 1

        # Test prefix match
        prefix_filter = ContractFilter('prefix', '/api/reports/')
        prefix_result = prefix_filter.filter_paths(SAMPLE_OPENAPI.copy())
        assert len(prefix_result["paths"]) == 2

        # Test regex match
        regex_filter = ContractFilter('regex', r'^/api/user/.*')
        regex_result = regex_filter.filter_paths(SAMPLE_OPENAPI.copy())
        assert len(regex_result["paths"]) == 2

    @patch('subprocess.run')
    def test_prism_detection_workflow(self, mock_run):
        """Test Prism detection in workflow"""
        from aceflow_mcp_server.mock.server import MockServer

        # Simulate Prism installed
        mock_run.return_value = Mock(returncode=0)

        contract_file = Path("/tmp/test.json")
        server = MockServer(contract_file)

        assert server.check_prism_installed() is True
        mock_run.assert_called_once()

    def test_end_to_end_config_to_contract(self, setup_config):
        """Test end-to-end from config to contract generation"""
        import os
        original_cwd = os.getcwd()
        os.chdir(setup_config)

        try:
            from aceflow_mcp_server.contract.config import ContractConfig

            # Load config
            config = ContractConfig(setup_config)

            # Get feature config
            feature = config.get_feature("user-management")
            assert feature is not None

            # Use feature config to filter
            filter_type = feature["api_filter"]["type"]
            pattern = feature["api_filter"]["pattern"]

            filter_obj = ContractFilter(filter_type, pattern)
            filtered_spec = filter_obj.filter_paths(SAMPLE_OPENAPI.copy())

            # Verify filtering worked as configured
            assert len(filtered_spec["paths"]) == 2
            assert "/api/user/login" in filtered_spec["paths"]

        finally:
            os.chdir(original_cwd)
