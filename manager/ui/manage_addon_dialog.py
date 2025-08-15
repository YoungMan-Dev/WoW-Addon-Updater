# manager/ui/improved_manage_addon_dialog.py
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QFormLayout, QTextEdit,
                             QMessageBox, QDialogButtonBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))


class ManageAddonDialog(QDialog):
    def __init__(self, addon_data, token, parent=None):
        super().__init__(parent)
        self.addon_data = addon_data
        self.token = token
        self.original_update_code = addon_data['info']['update_code']
        self.current_update_code = self.original_update_code
        self.init_ui()

    def init_ui(self):
        """初始化用户界面"""
        addon_name = self.addon_data['name']
        self.setWindowTitle(f"管理插件 - {addon_name}")
        self.setModal(True)
        self.resize(600, 400)

        layout = QVBoxLayout(self)

        # 标题
        title_label = QLabel(f"编辑插件: {addon_name}")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setStyleSheet("color: #1976D2; margin: 15px;")
        layout.addWidget(title_label)

        # 表单
        form_layout = QFormLayout()

        # 插件名（只读）
        self.name_input = QLineEdit(addon_name)
        self.name_input.setReadOnly(True)
        self.name_input.setStyleSheet("background-color: #f0f0f0; font-size: 14px;")
        form_layout.addRow("插件名:", self.name_input)

        # 版本号
        addon_info = self.addon_data['info']
        self.version_input = QLineEdit(addon_info['version'])
        self.version_input.setStyleSheet("font-size: 14px;")
        form_layout.addRow("版本号:", self.version_input)

        # 下载地址
        self.url_input = QLineEdit(addon_info['download_url'])
        self.url_input.setStyleSheet("font-size: 14px;")
        form_layout.addRow("下载地址:", self.url_input)

        # 更新码及操作按钮
        update_code_layout = QHBoxLayout()
        self.code_input = QLineEdit(self.current_update_code)
        self.code_input.setReadOnly(True)
        self.code_input.setStyleSheet("background-color: #f0f0f0; font-size: 14px; font-weight: bold;")

        self.change_code_btn = QPushButton("更换更新码")
        self.change_code_btn.clicked.connect(self.change_update_code)
        self.change_code_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
        """)

        update_code_layout.addWidget(self.code_input)
        update_code_layout.addWidget(self.change_code_btn)
        form_layout.addRow("更新码:", update_code_layout)

        # 创建时间（只读）
        if 'created_at' in addon_info:
            created_time = addon_info['created_at'][:19].replace('T', ' ')
            self.created_input = QLineEdit(created_time)
            self.created_input.setReadOnly(True)
            self.created_input.setStyleSheet("background-color: #f0f0f0; font-size: 14px;")
            form_layout.addRow("创建时间:", self.created_input)

        # 更新时间（只读）
        if 'updated_at' in addon_info:
            updated_time = addon_info['updated_at'][:19].replace('T', ' ')
            self.updated_input = QLineEdit(updated_time)
            self.updated_input.setReadOnly(True)
            self.updated_input.setStyleSheet("background-color: #f0f0f0; font-size: 14px;")
            form_layout.addRow("更新时间:", self.updated_input)

        layout.addLayout(form_layout)

        # 操作说明
        info_label = QLabel("说明：除非手动更换更新码，否则修改版本号和链接不会改变更新码")
        info_label.setStyleSheet("color: #666; font-size: 12px; margin: 10px; padding: 5px;")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        # 按钮
        button_layout = QHBoxLayout()

        self.update_url_btn = QPushButton("仅更新下载地址")
        self.update_url_btn.clicked.connect(self.update_download_url)

        self.update_version_btn = QPushButton("更新版本信息")
        self.update_version_btn.clicked.connect(self.update_version_info)

        self.close_btn = QPushButton("关闭")
        self.close_btn.clicked.connect(self.accept)

        button_layout.addWidget(self.update_url_btn)
        button_layout.addWidget(self.update_version_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.close_btn)

        layout.addLayout(button_layout)

        # 设置样式
        self.setStyleSheet(self.get_stylesheet())

    def change_update_code(self):
        """更换更新码"""
        reply = QMessageBox.question(
            self, "确认更换",
            "确定要更换新的更新码吗？\n注意：更换后需要通知用户使用新的更新码！",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            from manager.core.code_generator import CodeGenerator
            generator = CodeGenerator()
            self.current_update_code = generator.generate_update_code()
            self.code_input.setText(self.current_update_code)

            QMessageBox.information(
                self, "更新码已更换",
                f"新的更新码：{self.current_update_code}\n请记住这个更新码！"
            )

    def get_stylesheet(self):
        """获取样式表"""
        return """
            QDialog {
                background-color: #f5f5f5;
            }
            QLineEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 10px;
                font-size: 14px;
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 14px;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
            QLabel {
                font-size: 14px;
            }
        """

    def update_download_url(self):
        """更新下载地址"""
        new_url = self.url_input.text().strip()
        if not new_url:
            QMessageBox.warning(self, "输入错误", "下载地址不能为空")
            return

        addon_name = self.addon_data['name']

        # 启动更新线程
        self.update_url_thread = UpdateUrlThread(addon_name, new_url, self.token)
        self.update_url_thread.finished.connect(self.on_update_url_finished)
        self.update_url_thread.start()

        self.update_url_btn.setEnabled(False)
        self.update_url_btn.setText("更新中...")

    def update_version_info(self):
        """更新版本信息"""
        new_version = self.version_input.text().strip()
        new_url = self.url_input.text().strip()

        if not new_version or not new_url:
            QMessageBox.warning(self, "输入错误", "版本号和下载地址不能为空")
            return

        addon_name = self.addon_data['name']

        # 启动更新线程，使用当前的更新码（可能是原来的或新生成的）
        self.update_info_thread = UpdateInfoThread(
            addon_name, new_version, new_url, self.current_update_code, self.token
        )
        self.update_info_thread.finished.connect(self.on_update_info_finished)
        self.update_info_thread.start()

        self.update_version_btn.setEnabled(False)
        self.update_version_btn.setText("更新中...")

    def on_update_url_finished(self, success, message):
        """更新下载地址完成回调"""
        self.update_url_btn.setEnabled(True)
        self.update_url_btn.setText("仅更新下载地址")

        if success:
            QMessageBox.information(self, "更新成功", "下载地址更新成功！")
        else:
            QMessageBox.warning(self, "更新失败", message)

    def on_update_info_finished(self, success, message):
        """更新版本信息完成回调"""
        self.update_version_btn.setEnabled(True)
        self.update_version_btn.setText("更新版本信息")

        if success:
            success_msg = "插件信息更新成功！"
            if self.current_update_code != self.original_update_code:
                success_msg += f"\n新的更新码：{self.current_update_code}"
            QMessageBox.information(self, "更新成功", success_msg)
            self.accept()
        else:
            QMessageBox.warning(self, "更新失败", message)


class UpdateUrlThread(QThread):
    finished = pyqtSignal(bool, str)

    def __init__(self, addon_name, new_url, token):
        super().__init__()
        self.addon_name = addon_name
        self.new_url = new_url
        self.token = token

    def run(self):
        try:
            from manager.core.api_client import APIClient

            api_client = APIClient()
            response = api_client.update_addon_url(
                self.addon_name, self.new_url, self.token
            )

            if response.get('success', False):
                self.finished.emit(True, "更新成功")
            else:
                message = response.get('message', '更新失败')
                self.finished.emit(False, message)
        except Exception as e:
            self.finished.emit(False, f"更新失败: {str(e)}")


class UpdateInfoThread(QThread):
    finished = pyqtSignal(bool, str)

    def __init__(self, addon_name, version, url, update_code, token):
        super().__init__()
        self.addon_name = addon_name
        self.version = version
        self.url = url
        self.update_code = update_code
        self.token = token

    def run(self):
        try:
            from manager.core.api_client import APIClient

            api_client = APIClient()
            response = api_client.add_addon(
                self.addon_name, self.version, self.url, self.update_code, self.token
            )

            if response.get('success', False):
                self.finished.emit(True, "更新成功")
            else:
                message = response.get('message', '更新失败')
                self.finished.emit(False, message)
        except Exception as e:
            self.finished.emit(False, f"更新失败: {str(e)}")