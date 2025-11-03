"""
Unit tests for Mock Server management
"""
import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from aceflow_mcp_server.mock.server import MockServer


class TestMockServer:
    """Test MockServer class"""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def contract_file(self, temp_dir):
        """Create a sample contract file"""
        contract = {
            "openapi": "3.0.0",
            "info": {"title": "Test API", "version": "1.0.0"},
            "paths": {
                "/api/test": {
                    "get": {
                        "summary": "Test endpoint",
                        "responses": {"200": {"description": "OK"}}
                    }
                }
            }
        }

        contract_path = temp_dir / "test-api.json"
        with open(contract_path, 'w') as f:
            json.dump(contract, f)

        return contract_path

    def test_mock_server_init(self, contract_file):
        """Test MockServer initialization"""
        server = MockServer(contract_file, port=4010)

        assert server.contract_file == contract_file
        assert server.port == 4010
        assert server.process is None

    def test_check_prism_installed_success(self, contract_file):
        """Test Prism installation check (installed)"""
        server = MockServer(contract_file)

        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0)
            result = server.check_prism_installed()

            assert result is True
            mock_run.assert_called_once()
            assert mock_run.call_args[0][0] == ["prism", "--version"]

    def test_check_prism_installed_not_found(self, contract_file):
        """Test Prism installation check (not installed)"""
        server = MockServer(contract_file)

        with patch('subprocess.run', side_effect=FileNotFoundError):
            result = server.check_prism_installed()
            assert result is False

    def test_is_port_in_use_true(self, contract_file):
        """Test port in use detection (port occupied)"""
        server = MockServer(contract_file, port=4010)

        with patch('socket.socket') as mock_socket:
            mock_sock = MagicMock()
            mock_sock.connect_ex.return_value = 0  # Port in use
            mock_socket.return_value.__enter__.return_value = mock_sock

            result = server._is_port_in_use(4010)
            assert result is True

    def test_is_port_in_use_false(self, contract_file):
        """Test port in use detection (port available)"""
        server = MockServer(contract_file, port=4010)

        with patch('socket.socket') as mock_socket:
            mock_sock = MagicMock()
            mock_sock.connect_ex.return_value = 1  # Port available
            mock_socket.return_value.__enter__.return_value = mock_sock

            result = server._is_port_in_use(4010)
            assert result is False

    def test_start_prism_not_installed(self, contract_file):
        """Test starting server when Prism not installed"""
        server = MockServer(contract_file)

        with patch.object(server, 'check_prism_installed', return_value=False):
            result = server.start()
            assert result is False

    def test_start_contract_not_exists(self, temp_dir):
        """Test starting server with non-existent contract"""
        nonexistent = temp_dir / "nonexistent.json"
        server = MockServer(nonexistent)

        with patch.object(server, 'check_prism_installed', return_value=True):
            result = server.start()
            assert result is False

    def test_start_port_in_use(self, contract_file):
        """Test starting server on occupied port"""
        server = MockServer(contract_file, port=4010)

        with patch.object(server, 'check_prism_installed', return_value=True):
            with patch.object(server, '_is_port_in_use', return_value=True):
                result = server.start()
                assert result is False

    @patch('subprocess.Popen')
    def test_start_success(self, mock_popen, contract_file, temp_dir):
        """Test successful server start"""
        # Change working directory to temp_dir for PID file
        import os
        original_cwd = os.getcwd()
        os.chdir(temp_dir)

        try:
            server = MockServer(contract_file, port=4010)

            mock_process = Mock()
            mock_process.pid = 12345
            mock_popen.return_value = mock_process

            with patch.object(server, 'check_prism_installed', return_value=True):
                with patch.object(server, '_is_port_in_use', return_value=False):
                    result = server.start()

                    assert result is True
                    assert server.process == mock_process

                    # Check PID file created
                    assert server.pid_file.exists()
                    with open(server.pid_file) as f:
                        pid_data = json.load(f)
                        assert pid_data['pid'] == 12345
                        assert pid_data['port'] == 4010
        finally:
            os.chdir(original_cwd)

    def test_stop_pid_file_not_exists(self, contract_file):
        """Test stopping server when PID file doesn't exist"""
        server = MockServer(contract_file, port=4010)

        result = server.stop()
        assert result is False

    @patch('psutil.Process')
    def test_stop_success(self, mock_process_class, contract_file, temp_dir):
        """Test successful server stop"""
        import os
        original_cwd = os.getcwd()
        os.chdir(temp_dir)

        try:
            server = MockServer(contract_file, port=4010)

            # Create PID file
            server.pid_file.parent.mkdir(parents=True, exist_ok=True)
            with open(server.pid_file, 'w') as f:
                json.dump({'pid': 12345, 'port': 4010}, f)

            mock_process = Mock()
            mock_process_class.return_value = mock_process

            result = server.stop()

            assert result is True
            mock_process.terminate.assert_called_once()
            mock_process.wait.assert_called_once()
            assert not server.pid_file.exists()
        finally:
            os.chdir(original_cwd)

    def test_list_running_empty(self, temp_dir):
        """Test listing running servers (none running)"""
        import os
        original_cwd = os.getcwd()
        os.chdir(temp_dir)

        try:
            servers = MockServer.list_running()
            assert servers == []
        finally:
            os.chdir(original_cwd)

    def test_list_running_with_servers(self, temp_dir):
        """Test listing running servers"""
        import os
        original_cwd = os.getcwd()
        os.chdir(temp_dir)

        try:
            # Create mock directory and PID files
            mock_dir = temp_dir / ".aceflow" / "mock"
            mock_dir.mkdir(parents=True, exist_ok=True)

            pid_file = mock_dir / "prism_4010.pid"
            with open(pid_file, 'w') as f:
                json.dump({
                    'pid': 12345,
                    'port': 4010,
                    'contract': 'test-api.json',
                    'dynamic': True,
                    'validate': True
                }, f)

            with patch('psutil.pid_exists', return_value=True):
                servers = MockServer.list_running()

                assert len(servers) == 1
                assert servers[0]['pid'] == 12345
                assert servers[0]['port'] == 4010
        finally:
            os.chdir(original_cwd)

    def test_command_generation(self, contract_file):
        """Test Prism command generation"""
        server = MockServer(contract_file, port=4010)

        # We can't directly test private methods, but we can verify through start
        with patch('subprocess.Popen') as mock_popen:
            with patch.object(server, 'check_prism_installed', return_value=True):
                with patch.object(server, '_is_port_in_use', return_value=False):
                    server.start(dynamic=True, validate=True)

                    # Verify command arguments
                    call_args = mock_popen.call_args[0][0]
                    assert "prism" in call_args
                    assert "mock" in call_args
                    assert str(contract_file) in call_args
                    assert "--port" in call_args
                    assert "4010" in call_args
                    assert "--dynamic" in call_args
