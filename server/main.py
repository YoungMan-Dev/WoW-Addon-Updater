# start_server.py - 服务器启动脚本
"""
WoW插件管理系统服务器启动脚本
提供简单的服务器启动和管理功能
"""

import sys
import os
import time
import subprocess
import signal
import argparse
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 服务器文件路径
SERVER_FILE = project_root / 'main.py'
DATA_FILE = project_root / 'server' / 'data' / 'addons.json'


class ServerManager:
    """服务器管理器"""

    def __init__(self):
        self.server_process = None
        self.is_running = False

    def check_dependencies(self):
        """检查依赖"""
        print("🔍 检查系统依赖...")

        missing_deps = []

        # 检查Python版本
        if sys.version_info < (3, 6):
            print("❌ 需要Python 3.6或更高版本")
            return False
        else:
            print(f"✅ Python版本: {sys.version}")

        # 检查Flask
        try:
            import flask
            print(f"✅ Flask版本: {flask.__version__}")
        except ImportError:
            missing_deps.append('flask')
            print("❌ Flask未安装")

        # 检查Flask-CORS
        try:
            import flask_cors
            print("✅ Flask-CORS已安装")
        except ImportError:
            missing_deps.append('flask-cors')
            print("❌ Flask-CORS未安装")

        # 检查加密库（可选）
        try:
            import cryptography
            print(f"✅ Cryptography已安装")
        except ImportError:
            print("⚠️ Cryptography未安装，将使用简化加密")

        if missing_deps:
            print(f"\n❌ 缺少依赖: {', '.join(missing_deps)}")
            print("请运行以下命令安装:")
            print(f"pip install {' '.join(missing_deps)}")
            return False

        print("✅ 所有必要依赖已满足")
        return True

    def check_server_file(self):
        """检查服务器文件"""
        if not SERVER_FILE.exists():
            print(f"❌ 服务器文件不存在: {SERVER_FILE}")
            return False

        print(f"✅ 服务器文件存在: {SERVER_FILE}")
        return True

    def init_data_file(self):
        """初始化数据文件"""
        if not DATA_FILE.exists():
            print("📄 创建默认数据文件...")

            # 确保目录存在
            DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

            # 创建默认数据
            default_data = {
                "TestAddon": {
                    "version": "1.0.0",
                    "download_url": "https://example.com/test.zip",
                    "update_code": "TEST1234",
                    "created_at": "2025-08-14T10:00:00",
                    "updated_at": "2025-08-14T10:00:00"
                }
            }

            try:
                import json
                with open(DATA_FILE, 'w', encoding='utf-8') as f:
                    json.dump(default_data, f, ensure_ascii=False, indent=2)

                print(f"✅ 默认数据文件创建成功: {DATA_FILE}")
                return True

            except Exception as e:
                print(f"❌ 创建数据文件失败: {e}")
                return False
        else:
            print(f"✅ 数据文件已存在: {DATA_FILE}")
            return True

    def start_server(self, host='127.0.0.1', port=5000, debug=True):
        """启动服务器"""
        if not self.check_dependencies():
            return False

        if not self.check_server_file():
            return False

        if not self.init_data_file():
            return False

        print(f"\n🚀 启动服务器...")
        print(f"📍 地址: http://{host}:{port}")
        print(f"🔧 调试模式: {'开启' if debug else '关闭'}")
        print(f"💾 数据文件: {DATA_FILE}")
        print("\n" + "=" * 60)

        try:
            # 设置环境变量
            env = os.environ.copy()
            env['FLASK_APP'] = str(SERVER_FILE)
            env['FLASK_ENV'] = 'development' if debug else 'production'

            # 启动服务器进程
            cmd = [
                sys.executable,
                str(SERVER_FILE)
            ]

            self.server_process = subprocess.Popen(
                cmd,
                env=env,
                cwd=str(project_root),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )

            self.is_running = True

            # 监控服务器输出
            self.monitor_server()

        except KeyboardInterrupt:
            print("\n👋 接收到中断信号，正在关闭服务器...")
            self.stop_server()
        except Exception as e:
            print(f"❌ 启动服务器失败: {e}")
            return False

        return True

    def monitor_server(self):
        """监控服务器输出"""
        if not self.server_process:
            return

        try:
            while self.is_running and self.server_process.poll() is None:
                line = self.server_process.stdout.readline()
                if line:
                    print(line.rstrip())
                else:
                    time.sleep(0.1)
        except Exception as e:
            print(f"❌ 监控服务器输出时出错: {e}")
        finally:
            if self.server_process and self.server_process.poll() is None:
                self.stop_server()

    def stop_server(self):
        """停止服务器"""
        if self.server_process:
            print("🛑 正在停止服务器...")

            try:
                # 尝试优雅关闭
                self.server_process.terminate()

                # 等待进程结束
                timeout = 5
                for _ in range(timeout):
                    if self.server_process.poll() is not None:
                        break
                    time.sleep(1)
                else:
                    # 强制关闭
                    print("⚠️ 正在强制关闭服务器...")
                    self.server_process.kill()

                self.server_process.wait()
                print("✅ 服务器已停止")

            except Exception as e:
                print(f"❌ 停止服务器时出错: {e}")
            finally:
                self.server_process = None
                self.is_running = False

    def get_server_status(self):
        """获取服务器状态"""
        if self.is_running and self.server_process and self.server_process.poll() is None:
            return "运行中"
        else:
            return "已停止"

    def restart_server(self, host='127.0.0.1', port=5000, debug=True):
        """重启服务器"""
        print("🔄 重启服务器...")
        if self.is_running:
            self.stop_server()
            time.sleep(2)

        return self.start_server(host, port, debug)


def install_dependencies():
    """安装依赖"""
    print("📦 正在安装依赖...")

    dependencies = [
        'flask>=2.0.0',
        'flask-cors>=3.0.0',
        'cryptography>=3.0.0'
    ]

    try:
        for dep in dependencies:
            print(f"安装 {dep}...")
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install', dep
            ])

        print("✅ 依赖安装完成")
        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ 安装依赖失败: {e}")
        return False


def show_help():
    """显示帮助信息"""
    print("""
🎮 WoW插件管理系统服务器

📋 使用方法:
  python start_server.py [命令] [选项]

🔧 可用命令:
  start      启动服务器 (默认)
  install    安装依赖
  check      检查系统环境
  help       显示此帮助信息

⚙️ 启动选项:
  --host HOST     服务器主机地址 (默认: 127.0.0.1)
  --port PORT     服务器端口 (默认: 5000)
  --no-debug      关闭调试模式
  --production    生产模式运行

📝 示例:
  python start_server.py                    # 启动服务器
  python start_server.py --port 8080        # 在8080端口启动
  python start_server.py install           # 安装依赖
  python start_server.py check             # 检查环境

🌐 访问地址:
  主页:           http://localhost:5000/
  健康检查:       http://localhost:5000/api/health
  API文档:        http://localhost:5000/api/test

🔑 默认管理密码: admin123

📞 快捷键:
  Ctrl+C         停止服务器

📁 文件位置:
  服务器代码:     {SERVER_FILE}
  数据文件:       {DATA_FILE}
""")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='WoW插件管理系统服务器启动器')

    parser.add_argument('command', nargs='?', default='start',
                        choices=['start', 'install', 'check', 'help'],
                        help='要执行的命令')

    parser.add_argument('--host', default='127.0.0.1',
                        help='服务器主机地址')

    parser.add_argument('--port', type=int, default=5000,
                        help='服务器端口')

    parser.add_argument('--no-debug', action='store_true',
                        help='关闭调试模式')

    parser.add_argument('--production', action='store_true',
                        help='生产模式运行')

    args = parser.parse_args()

    # 创建服务器管理器
    server_manager = ServerManager()

    try:
        if args.command == 'help':
            show_help()

        elif args.command == 'install':
            install_dependencies()

        elif args.command == 'check':
            print("🔍 系统环境检查:")
            print("-" * 40)

            deps_ok = server_manager.check_dependencies()
            server_ok = server_manager.check_server_file()
            data_ok = server_manager.init_data_file()

            print("-" * 40)
            if deps_ok and server_ok and data_ok:
                print("✅ 系统环境检查通过，可以启动服务器")
            else:
                print("❌ 系统环境检查失败，请解决上述问题")

        elif args.command == 'start':
            debug_mode = not (args.no_debug or args.production)

            # 注册信号处理器
            def signal_handler(signum, frame):
                print(f"\n接收到信号 {signum}，正在关闭服务器...")
                server_manager.stop_server()
                sys.exit(0)

            signal.signal(signal.SIGINT, signal_handler)
            if hasattr(signal, 'SIGTERM'):
                signal.signal(signal.SIGTERM, signal_handler)

            # 启动服务器
            success = server_manager.start_server(
                host=args.host,
                port=args.port,
                debug=debug_mode
            )

            if not success:
                sys.exit(1)

    except KeyboardInterrupt:
        print("\n👋 用户取消操作")

    except Exception as e:
        print(f"❌ 执行命令时出错: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()