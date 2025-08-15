# manager/ui/improved_login_window.py
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QMessageBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QIcon
from manager.ui.main_window import MainWindow
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))


class ImprovedLoginWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.main_window = None
        self.init_ui()

    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("管理器登录")
        self.setFixedSize(600, 500)  # 进一步增大窗口
        self.setModal(True)

        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(25)
        main_layout.setContentsMargins(50, 40, 50, 40)

        # 标题区域
        title_container = QVBoxLayout()
        title_label = QLabel("魔兽世界")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Microsoft YaHei", 18, QFont.Bold))
        title_label.setStyleSheet("color: #1976D2; padding: 1px;")
        title_container.addWidget(title_label)

        subtitle_label = QLabel("插件管理器")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setFont(QFont("Microsoft YaHei", 16, QFont.Bold))
        subtitle_label.setStyleSheet("color: #1976D2; padding: 1px;")
        title_container.addWidget(subtitle_label)

        main_layout.addLayout(title_container)
        main_layout.addSpacing(30)  # 添加空间

        # 密码输入区域
        password_container = QVBoxLayout()
        password_container.setSpacing(15)

        # 密码标签
        password_label = QLabel("管理员密码:")
        password_label.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        password_label.setStyleSheet("color: #333; padding: 1px;")
        password_container.addWidget(password_label)

        # 密码输入框
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("请输入管理员密码")
        self.password_input.returnPressed.connect(self.login)
        self.password_input.setFont(QFont("Microsoft YaHei", 14))
        self.password_input.setFixedHeight(50)  # 固定高度
        password_container.addWidget(self.password_input)

        main_layout.addLayout(password_container)
        main_layout.addSpacing(30)  # 添加空间

        # 按钮区域
        button_container = QHBoxLayout()
        button_container.setSpacing(20)

        # 添加左侧弹性空间
        button_container.addStretch()

        self.login_btn = QPushButton("登录")
        self.login_btn.setFixedSize(100, 45)  # 固定尺寸
        self.login_btn.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        self.login_btn.clicked.connect(self.login)
        button_container.addWidget(self.login_btn)

        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.setFixedSize(100, 45)  # 固定尺寸
        self.cancel_btn.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        self.cancel_btn.clicked.connect(self.close)
        button_container.addWidget(self.cancel_btn)

        # 添加右侧弹性空间
        button_container.addStretch()

        main_layout.addLayout(button_container)
        main_layout.addSpacing(20)  # 添加空间

        # 提示信息区域
        hint_container = QVBoxLayout()
        hint_label = QLabel("默认密码: admin123")
        hint_label.setAlignment(Qt.AlignCenter)
        hint_label.setFont(QFont("Microsoft YaHei", 12))
        hint_label.setStyleSheet("color: #666; padding: 10px; background-color: #f0f0f0; border-radius: 5px;")
        hint_container.addWidget(hint_label)

        main_layout.addLayout(hint_container)

        # 添加底部弹性空间
        main_layout.addStretch()

        # 设置样式
        self.setStyleSheet(self.get_stylesheet())

        # 设置焦点
        self.password_input.setFocus()

    def get_stylesheet(self):
        """获取样式表"""
        return """
            QDialog {
                background-color: #ffffff;
                border: 2px solid #e0e0e0;
                border-radius: 10px;
            }
            QLabel {
                color: #333333;
            }
            QLineEdit {
                border: 2px solid #ddd;
                border-radius: 8px;
                padding: 12px 15px;
                font-size: 14px;
                background-color: #fafafa;
            }
            QLineEdit:focus {
                border-color: #2196F3;
                background-color: #ffffff;
                outline: none;
            }
            QLineEdit::placeholder {
                color: #999;
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """

    def login(self):
        """登录"""
        password = self.password_input.text().strip()

        if not password:
            QMessageBox.warning(self, "提示", "请输入密码")
            return

        # 启动登录线程
        self.login_btn.setEnabled(False)
        self.login_btn.setText("登录中...")

        self.login_thread = LoginThread(password)
        self.login_thread.finished.connect(self.on_login_finished)
        self.login_thread.start()

    def on_login_finished(self, success, message, token):
        """登录完成回调"""
        self.login_btn.setEnabled(True)
        self.login_btn.setText("登录")

        if success:
            # 保存token并打开主窗口
            self.token = token
            self.main_window = MainWindow(token)
            self.main_window.show()
            self.close()
        else:
            QMessageBox.warning(self, "登录失败", message)
            self.password_input.clear()
            self.password_input.setFocus()


class LoginThread(QThread):
    finished = pyqtSignal(bool, str, str)

    def __init__(self, password):
        super().__init__()
        self.password = password

    def run(self):
        try:
            from manager.core.api_client import APIClient

            api_client = APIClient()
            response = api_client.login(self.password)

            if response.get('success', False):
                token = response.get('token', '')
                self.finished.emit(True, "登录成功", token)
            else:
                message = response.get('message', '登录失败')
                self.finished.emit(False, message, '')
        except Exception as e:
            self.finished.emit(False, f"登录失败: {str(e)}", '')