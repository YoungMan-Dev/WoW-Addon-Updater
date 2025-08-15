# main.py - 应用程序主入口
"""
WoW插件更新器主程序
统一的应用程序入口，集成了启动画面、主窗口和样式管理
"""

import sys
import os
import traceback
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QIcon

# 添加项目路径到系统路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from updater.ui.main_window import MainWindow
    from updater.ui.splash_screen import create_splash_screen
    from updater.ui.styles import AppStyles, ThemeManager
except ImportError as e:
    print(f"导入模块失败: {e}")
    print("请确保所有依赖模块都已正确安装")
    sys.exit(1)


class ApplicationManager:
    """应用程序管理器"""

    def __init__(self):
        self.app = None
        self.main_window = None
        self.splash_screen = None
        self.theme_manager = ThemeManager()

    def setup_application(self):
        """设置应用程序"""
        # 创建QApplication实例
        self.app = QApplication(sys.argv)

        # 设置应用程序基本信息
        self.app.setApplicationName("WoW插件更新器")
        self.app.setApplicationVersion("1.0.0")
        self.app.setOrganizationName("WoW Addon Updater Team")
        self.app.setOrganizationDomain("wow-addon-updater.local")

        # 设置应用程序图标（如果存在）
        try:
            if os.path.exists("resources/icon.png"):
                self.app.setWindowIcon(QIcon("resources/icon.png"))
        except Exception:
            pass

        # 设置全局字体
        font = QFont("Microsoft YaHei UI", 9)
        font.setHintingPreference(QFont.PreferDefaultHinting)
        self.app.setFont(font)

        # 设置高DPI支持
        self.app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        self.app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

        # 应用全局样式
        self.apply_global_style()

    def apply_global_style(self):
        """应用全局样式"""
        try:
            style = self.theme_manager.get_current_theme_style()
            self.app.setStyleSheet(style)
        except Exception as e:
            print(f"应用样式失败: {e}")

    def show_splash_screen(self):
        """显示启动画面"""
        try:
            self.splash_screen = create_splash_screen()
            if self.splash_screen:
                self.splash_screen.show()
                self.app.processEvents()
                return True
        except Exception as e:
            print(f"显示启动画面失败: {e}")

        return False

    def initialize_main_window(self):
        """初始化主窗口"""
        try:
            self.main_window = MainWindow()

            # 如果有启动画面，等待其结束后显示主窗口
            if self.splash_screen:
                # 设置定时器，在启动画面结束后显示主窗口
                QTimer.singleShot(3000, self.show_main_window)
            else:
                # 直接显示主窗口
                self.show_main_window()

        except Exception as e:
            self.handle_error("初始化主窗口失败", e)

    def show_main_window(self):
        """显示主窗口"""
        try:
            if self.splash_screen:
                self.splash_screen.close()
                self.splash_screen = None

            if self.main_window:
                self.main_window.show()
                self.main_window.raise_()
                self.main_window.activateWindow()

        except Exception as e:
            self.handle_error("显示主窗口失败", e)

    def handle_error(self, title, error):
        """处理错误"""
        error_msg = f"{title}: {str(error)}\n\n详细信息:\n{traceback.format_exc()}"
        print(error_msg)

        try:
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Critical)
            msg_box.setWindowTitle("应用程序错误")
            msg_box.setText(title)
            msg_box.setDetailedText(error_msg)
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.exec_()
        except Exception:
            pass

    def run(self):
        """运行应用程序"""
        try:
            # 设置应用程序
            self.setup_application()

            # 显示启动画面
            splash_shown = self.show_splash_screen()

            # 初始化主窗口
            self.initialize_main_window()

            # 启动事件循环
            return self.app.exec_()

        except Exception as e:
            self.handle_error("启动应用程序失败", e)
            return 1


class PreflightCheck(QThread):
    """预检查线程 - 在后台进行系统检查"""
    finished = pyqtSignal(bool, str)
    progress = pyqtSignal(str)

    def run(self):
        """运行预检查"""
        try:
            # 检查Python版本
            self.progress.emit("检查Python环境...")
            if sys.version_info < (3, 6):
                self.finished.emit(False, "需要Python 3.6或更高版本")
                return

            # 检查PyQt5
            self.progress.emit("检查PyQt5...")
            try:
                from PyQt5 import QtCore
                if QtCore.QT_VERSION < 0x050900:  # 5.9.0
                    self.finished.emit(False, "需要PyQt5 5.9.0或更高版本")
                    return
            except ImportError:
                self.finished.emit(False, "PyQt5未正确安装")
                return

            # 检查网络连接
            self.progress.emit("检查网络连接...")
            try:
                import urllib.request
                urllib.request.urlopen('https://www.baidu.com', timeout=5)
            except Exception:
                self.progress.emit("网络连接检查失败，但程序可以继续运行...")

            # 检查必要目录
            self.progress.emit("检查必要目录...")
            directories = ['temp', 'logs', 'config']
            for dir_name in directories:
                if not os.path.exists(dir_name):
                    try:
                        os.makedirs(dir_name)
                    except Exception as e:
                        print(f"创建目录 {dir_name} 失败: {e}")

            self.progress.emit("预检查完成")
            self.finished.emit(True, "所有检查通过")

        except Exception as e:
            self.finished.emit(False, f"预检查失败: {str(e)}")


def setup_exception_handler():
    """设置全局异常处理器"""

    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        print(f"未捕获的异常: {error_msg}")

        # 尝试显示错误对话框
        try:
            app = QApplication.instance()
            if app:
                msg_box = QMessageBox()
                msg_box.setIcon(QMessageBox.Critical)
                msg_box.setWindowTitle("程序错误")
                msg_box.setText("程序遇到未处理的错误")
                msg_box.setDetailedText(error_msg)
                msg_box.exec_()
        except Exception:
            pass

    sys.excepthook = handle_exception


def check_single_instance():
    """检查是否已有实例在运行"""
    import tempfile
    import fcntl

    try:
        # 创建锁文件
        lock_file = os.path.join(tempfile.gettempdir(), 'wow_addon_updater.lock')

        if os.path.exists(lock_file):
            with open(lock_file, 'r') as f:
                try:
                    fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                    return True  # 可以获取锁，说明没有其他实例
                except IOError:
                    return False  # 无法获取锁，说明已有实例在运行
        else:
            # 创建锁文件
            with open(lock_file, 'w') as f:
                f.write(str(os.getpid()))
            return True

    except Exception:
        # 如果检查失败，允许启动
        return True


def main():
    """主函数"""
    try:
        # 设置异常处理器
        setup_exception_handler()

        # 检查单实例（仅在支持的系统上）
        if hasattr(os, 'name') and os.name == 'posix':
            if not check_single_instance():
                print("应用程序已在运行")
                return 1

        # 创建应用程序管理器并运行
        app_manager = ApplicationManager()
        return app_manager.run()

    except KeyboardInterrupt:
        print("\n程序被用户中断")
        return 0

    except Exception as e:
        print(f"程序启动失败: {e}")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)