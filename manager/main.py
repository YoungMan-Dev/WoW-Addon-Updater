# manager/main.py
import sys
import os
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from manager.ui.login_window import ImprovedLoginWindow


def setup_application():
    """设置应用程序"""
    app = QApplication(sys.argv)
    app.setApplicationName("魔兽世界插件管理器")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("WoW Addon Manager")

    # 设置全局字体
    font = QFont("Microsoft YaHei", 10)
    app.setFont(font)

    # 设置高DPI支持
    app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    return app


def main():
    """主函数"""
    try:
        app = setup_application()

        # 显示登录窗口
        login_window = ImprovedLoginWindow()
        login_window.show()

        # 运行应用程序
        sys.exit(app.exec_())

    except Exception as e:
        print(f"应用程序启动失败: {e}")
        if 'app' in locals():
            QMessageBox.critical(None, "错误", f"应用程序启动失败:\n{str(e)}")
        return 1


if __name__ == "__main__":
    main()