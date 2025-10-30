#!/usr/bin/env python3
"""
HTTP 测试运行器 - 启动服务器并运行测试
"""

import subprocess
import sys
import time
import requests
import os
import signal

def main():
    print("🚀 AceFlow MCP HTTP 完整测试流程")
    print("=" * 80)

    # 切换到正确的目录
    os.chdir('/home/chenjing/AI/aceflow-ai/aceflow-mcp-server')

    # 获取端口配置
    port = int(os.getenv('ACEFLOW_PORT', '8000'))
    print(f"\n📌 使用端口: {port}")

    # 启动服务器
    print("\n🌐 启动 MCP HTTP 服务器...")
    server_process = subprocess.Popen(
        [sys.executable, '-m', 'aceflow_mcp_server.mcp_http_server'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,  # Merge stderr into stdout
        text=True,
        bufsize=1,  # Line buffered
        env={**os.environ, 'ACEFLOW_PORT': str(port)}
    )

    print(f"服务器进程 PID: {server_process.pid}")

    # 等待服务器启动
    print("\n⏳ 等待服务器启动...")
    max_attempts = 15
    server_ready = False

    for i in range(max_attempts):
        try:
            response = requests.get(f'http://localhost:{port}/health', timeout=2)
            if response.status_code == 200:
                print("✅ 服务器已就绪")
                server_ready = True
                break
        except:
            pass

        print(f"等待服务器启动... ({i+1}/{max_attempts})")
        time.sleep(2)

    if not server_ready:
        print("❌ 服务器启动超时")
        print("\n服务器输出:")
        if server_process.poll() is None:
            server_process.terminate()
            try:
                output, _ = server_process.communicate(timeout=2)
                print(output)
            except:
                pass
        else:
            # Process already exited, read remaining output
            output = server_process.stdout.read()
            print(output)
        return 1

    # 运行测试
    print("\n🧪 运行完整测试套件...")
    print("=" * 80)

    test_process = subprocess.run(
        [sys.executable, 'tests/test_mcp_http_complete.py', '--url', f'http://localhost:{port}', '--report'],
        capture_output=False,
        env={**os.environ, 'ACEFLOW_PORT': str(port)}
    )

    test_exit_code = test_process.returncode

    # 停止服务器
    print("\n🛑 停止服务器...")
    server_process.terminate()
    try:
        server_process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        server_process.kill()

    # 输出结果
    print("\n" + "=" * 80)
    if test_exit_code == 0:
        print("🎉 所有测试通过!")
    else:
        print("💥 部分测试失败")
    print("=" * 80)

    return test_exit_code

if __name__ == '__main__':
    sys.exit(main())
