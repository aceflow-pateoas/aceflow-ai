"""
Unit tests for configuration management
"""
import pytest
import tempfile
import yaml
from pathlib import Path
from aceflow_mcp_server.contract.config import ContractConfig


class TestContractConfig:
    """Test ContractConfig class"""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for tests"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def sample_config(self, temp_dir):
        """Create a sample config file"""
        config_data = {
            "aceflow": {
                "project": {
                    "name": "Test Project",
                    "openapi_url": "http://localhost:8080/v3/api-docs"
                },
                "features": {
                    "user-management": {
                        "description": "User management",
                        "api_filter": {
                            "type": "prefix",
                            "pattern": "/api/user/"
                        },
                        "dev_team": ["alice@example.com"],
                        "enabled": True
                    }
                },
                "contract_repo": {
                    "url": "git@github.com:test/contracts.git",
                    "branch": "main",
                    "base_path": "contracts/active"
                },
                "notification": {
                    "smtp": {
                        "host": "smtp.example.com",
                        "port": 587,
                        "user": "test@example.com",
                        "password": "${SMTP_PASSWORD}",
                        "from_email": "aceflow@example.com"
                    }
                }
            }
        }

        config_file = temp_dir / ".aceflow" / "config.yaml"
        config_file.parent.mkdir(parents=True, exist_ok=True)

        with open(config_file, 'w') as f:
            yaml.dump(config_data, f)

        return temp_dir

    def test_load_config(self, sample_config):
        """Test loading configuration from file"""
        config = ContractConfig(sample_config)

        assert config.project_name == "Test Project"
        assert config.openapi_url == "http://localhost:8080/v3/api-docs"

    def test_get_feature(self, sample_config):
        """Test getting feature configuration"""
        config = ContractConfig(sample_config)

        feature = config.get_feature("user-management")

        assert feature is not None
        assert feature["description"] == "User management"
        assert feature["api_filter"]["type"] == "prefix"
        assert feature["api_filter"]["pattern"] == "/api/user/"

    def test_get_nonexistent_feature(self, sample_config):
        """Test getting non-existent feature"""
        config = ContractConfig(sample_config)

        feature = config.get_feature("nonexistent")
        assert feature is None

    def test_add_feature(self, sample_config):
        """Test adding a new feature"""
        config = ContractConfig(sample_config)

        new_feature = {
            "description": "Reports",
            "api_filter": {
                "type": "prefix",
                "pattern": "/api/reports/"
            },
            "dev_team": ["bob@example.com"],
            "enabled": True
        }

        config.add_feature("reports", new_feature)

        feature = config.get_feature("reports")
        assert feature is not None
        assert feature["description"] == "Reports"

    def test_remove_feature(self, sample_config):
        """Test removing a feature"""
        config = ContractConfig(sample_config)

        config.remove_feature("user-management")

        feature = config.get_feature("user-management")
        assert feature is None

    def test_get_features(self, sample_config):
        """Test getting all features"""
        config = ContractConfig(sample_config)

        features = config.get_features()

        assert isinstance(features, dict)
        assert "user-management" in features
        assert len(features) == 1

    def test_contract_repo_config(self, sample_config):
        """Test contract repository configuration"""
        config = ContractConfig(sample_config)

        repo_config = config.contract_repo_config

        assert repo_config["url"] == "git@github.com:test/contracts.git"
        assert repo_config["branch"] == "main"
        assert repo_config["base_path"] == "contracts/active"

    def test_smtp_config(self, sample_config):
        """Test SMTP configuration"""
        config = ContractConfig(sample_config)

        smtp = config.smtp_config

        assert smtp["host"] == "smtp.example.com"
        assert smtp["port"] == 587
        assert smtp["user"] == "test@example.com"
        assert smtp["password"] == "${SMTP_PASSWORD}"

    def test_save_config(self, temp_dir):
        """Test saving configuration"""
        config_file = temp_dir / ".aceflow" / "config.yaml"
        config_file.parent.mkdir(parents=True, exist_ok=True)

        # Create empty config
        initial_data = {"aceflow": {"project": {}, "features": {}}}
        with open(config_file, 'w') as f:
            yaml.dump(initial_data, f)

        config = ContractConfig(temp_dir)

        # Add feature
        new_feature = {
            "description": "Test",
            "api_filter": {"type": "exact", "pattern": "/api/test"},
            "dev_team": [],
            "enabled": True
        }
        config.add_feature("test", new_feature)

        # Reload and verify
        config2 = ContractConfig(temp_dir)
        feature = config2.get_feature("test")
        assert feature is not None
        assert feature["description"] == "Test"

    def test_missing_config_file(self, temp_dir):
        """Test handling missing config file"""
        with pytest.raises(FileNotFoundError):
            ContractConfig(temp_dir)

    def test_get_completion_rules(self, sample_config):
        """Test getting smart completion rules"""
        config = ContractConfig(sample_config)

        # Config doesn't have completion rules, should return default or empty
        rules = config.get_completion_rules()

        # Should return something even if not defined
        assert isinstance(rules, (list, type(None)))

    def test_feature_enabled_flag(self, sample_config):
        """Test feature enabled/disabled flag"""
        config = ContractConfig(sample_config)

        feature = config.get_feature("user-management")
        assert feature["enabled"] is True

        # Disable feature
        feature["enabled"] = False
        config.add_feature("user-management", feature)

        updated_feature = config.get_feature("user-management")
        assert updated_feature["enabled"] is False
