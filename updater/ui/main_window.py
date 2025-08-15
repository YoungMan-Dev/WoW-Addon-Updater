# updater/ui/main_window.py - 统一UI风格版本
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QListWidget, QListWidgetItem,
                             QProgressBar, QTextEdit, QGroupBox, QLineEdit,
                             QMessageBox, QFileDialog, QCheckBox, QScrollArea,
                             QTableWidget, QTableWidgetItem, QHeaderView,
                             QFrame, QSplitter, QTabWidget)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QPalette
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from updater.core.wow_detector import WoWDetector
from updater.core.addon_manager import AddonManager
from updater.core.version_checker import VersionChecker
from updater.core.downloader import Downloader


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.addon_manager = AddonManager()
        self.version_checker = VersionChecker()
        self.downloader = Downloader()
        self.addon_items = []

        self.init_ui()
        self.init_wow_path()

    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("魔兽世界插件更新器")
        self.setGeometry(100, 100, 1200, 800)

        # 中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # 标题
        title_label = QLabel("魔兽世界插件更新器")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 20, QFont.Bold))
        title_label.setStyleSheet("color: #1976D2; margin: 15px;")
        layout.addWidget(title_label)

        # 创建选项卡
        self.tab_widget = QTabWidget()

        # 更新器主界面选项卡
        self.update_tab = self.create_update_tab()
        self.tab_widget.addTab(self.update_tab, "插件更新")

        # 设置选项卡
        self.settings_tab = self.create_settings_tab()
        self.tab_widget.addTab(self.settings_tab, "设置")

        layout.addWidget(self.tab_widget)

        # 设置样式
        self.setStyleSheet(self.get_stylesheet())

    def create_update_tab(self):
        """创建更新选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # WoW路径设置
        path_group = QGroupBox("游戏路径设置")
        path_layout = QHBoxLayout(path_group)

        self.path_label = QLineEdit()
        self.path_label.setPlaceholderText("魔兽世界安装路径...")
        self.path_label.setReadOnly(True)

        self.browse_btn = QPushButton("浏览")
        self.browse_btn.clicked.connect(self.browse_wow_path)

        self.detect_btn = QPushButton("自动检测")
        self.detect_btn.clicked.connect(self.auto_detect_wow_path)

        path_layout.addWidget(QLabel("WoW路径:"))
        path_layout.addWidget(self.path_label)
        path_layout.addWidget(self.browse_btn)
        path_layout.addWidget(self.detect_btn)
        layout.addWidget(path_group)

        # 更新码设置
        code_group = QGroupBox("更新码设置")
        code_layout = QHBoxLayout(code_group)

        self.update_codes_input = QLineEdit()
        self.update_codes_input.setPlaceholderText("请输入更新码，多个更新码用逗号分隔...")

        self.verify_btn = QPushButton("验证更新码")
        self.verify_btn.clicked.connect(self.verify_update_codes)

        code_layout.addWidget(QLabel("更新码:"))
        code_layout.addWidget(self.update_codes_input)
        code_layout.addWidget(self.verify_btn)
        layout.addWidget(code_group)

        # 插件列表区域
        addon_group = QGroupBox("可更新插件列表")
        addon_layout = QVBoxLayout(addon_group)

        # 操作按钮栏
        btn_layout = QHBoxLayout()

        # 搜索框
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("搜索:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("按插件名搜索...")
        self.search_input.textChanged.connect(self.filter_addons)
        search_layout.addWidget(self.search_input)
        btn_layout.addLayout(search_layout)

        # 操作按钮
        self.refresh_btn = QPushButton("刷新列表")
        self.refresh_btn.clicked.connect(self.refresh_addon_list)

        self.update_selected_btn = QPushButton("更新选中")
        self.update_selected_btn.clicked.connect(self.update_selected_addons)
        self.update_selected_btn.setEnabled(False)

        self.update_all_btn = QPushButton("全部更新")
        self.update_all_btn.clicked.connect(self.update_all_addons)
        self.update_all_btn.setEnabled(False)

        btn_layout.addWidget(self.refresh_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self.update_selected_btn)
        btn_layout.addWidget(self.update_all_btn)
        addon_layout.addLayout(btn_layout)

        # 插件表格
        self.addon_table = QTableWidget()
        self.addon_table.setColumnCount(4)
        self.addon_table.setHorizontalHeaderLabels(["选择", "插件名", "当前版本", "最新版本"])

        # 设置表格属性
        header = self.addon_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)  # 选择列固定宽度
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # 插件名列自适应
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # 版本号列适应内容
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # 版本号列适应内容
        self.addon_table.setColumnWidth(0, 80)

        self.addon_table.setAlternatingRowColors(True)
        self.addon_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.addon_table.verticalHeader().setDefaultSectionSize(40)

        addon_layout.addWidget(self.addon_table)
        layout.addWidget(addon_group)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # 日志输出
        log_group = QGroupBox("操作日志")
        log_layout = QVBoxLayout(log_group)
        log_group.setMaximumHeight(200)
        log_group.setMinimumHeight(120)

        # 日志控制栏
        log_control_layout = QHBoxLayout()
        self.clear_log_btn = QPushButton("清空日志")
        self.clear_log_btn.setMaximumWidth(80)
        self.clear_log_btn.clicked.connect(lambda: self.log_text.clear())
        log_control_layout.addWidget(self.clear_log_btn)
        log_control_layout.addStretch()
        log_layout.addLayout(log_control_layout)

        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(150)
        self.log_text.setReadOnly(True)
        # 增大字号
        font = self.log_text.font()
        font.setPointSize(14)
        self.log_text.setFont(font)
        log_layout.addWidget(self.log_text)
        layout.addWidget(log_group)

        return widget

    def create_settings_tab(self):
        """创建设置选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # 服务器设置
        server_group = QGroupBox("服务器设置")
        server_layout = QVBoxLayout(server_group)

        # 服务器地址
        server_addr_layout = QHBoxLayout()
        server_addr_layout.addWidget(QLabel("服务器地址:"))
        self.server_addr_input = QLineEdit()
        self.server_addr_input.setText("http://127.0.0.1:5000/api")
        self.server_addr_input.setPlaceholderText("请输入服务器API地址...")
        server_addr_layout.addWidget(self.server_addr_input)
        server_layout.addLayout(server_addr_layout)

        # 连接测试
        test_layout = QHBoxLayout()
        self.test_connection_btn = QPushButton("测试连接")
        self.test_connection_btn.clicked.connect(self.test_server_connection)
        self.connection_status_label = QLabel("状态: 未连接")
        test_layout.addWidget(self.test_connection_btn)
        test_layout.addWidget(self.connection_status_label)
        test_layout.addStretch()
        server_layout.addLayout(test_layout)

        layout.addWidget(server_group)

        # 更新设置
        update_group = QGroupBox("更新设置")
        update_layout = QVBoxLayout(update_group)

        # 自动检查
        self.auto_check_checkbox = QCheckBox("启动时自动检查更新")
        self.auto_check_checkbox.setChecked(True)
        update_layout.addWidget(self.auto_check_checkbox)

        # 下载路径
        download_layout = QHBoxLayout()
        download_layout.addWidget(QLabel("临时下载路径:"))
        self.download_path_input = QLineEdit()
        self.download_path_input.setText("./temp")
        self.download_path_input.setReadOnly(True)
        self.browse_download_btn = QPushButton("浏览")
        self.browse_download_btn.clicked.connect(self.browse_download_path)
        download_layout.addWidget(self.download_path_input)
        download_layout.addWidget(self.browse_download_btn)
        update_layout.addLayout(download_layout)

        layout.addWidget(update_group)

        # 关于信息
        about_group = QGroupBox("关于")
        about_layout = QVBoxLayout(about_group)

        about_text = QTextEdit()
        about_text.setReadOnly(True)
        about_text.setMaximumHeight(150)
        about_text.setHtml("""
        <h3>魔兽世界插件更新器 v1.0</h3>
        <p><b>功能:</b> 自动检测和更新魔兽世界插件</p>
        <p><b>支持:</b> 加密通信、批量更新、版本检查</p>
        <p><b>开发:</b> WoW插件管理团队</p>
        <p><b>许可:</b> MIT License</p>
        """)
        about_layout.addWidget(about_text)

        layout.addWidget(about_group)
        layout.addStretch()

        return widget

    def filter_addons(self):
        """过滤插件列表"""
        search_text = self.search_input.text().lower()

        for row in range(self.addon_table.rowCount()):
            addon_name_item = self.addon_table.item(row, 1)
            if addon_name_item:
                addon_name = addon_name_item.text().lower()
                should_show = search_text in addon_name
                self.addon_table.setRowHidden(row, not should_show)

    def test_server_connection(self):
        """测试服务器连接"""
        self.connection_status_label.setText("状态: 连接中...")
        self.test_connection_btn.setEnabled(False)

        # 启动连接测试线程
        self.test_thread = TestConnectionThread(self.server_addr_input.text())
        self.test_thread.finished.connect(self.on_test_finished)
        self.test_thread.start()

    def on_test_finished(self, success, message):
        """连接测试完成"""
        if success:
            self.connection_status_label.setText("状态: 连接成功")
            self.connection_status_label.setStyleSheet("color: green;")
        else:
            self.connection_status_label.setText(f"状态: 连接失败 - {message}")
            self.connection_status_label.setStyleSheet("color: red;")

        self.test_connection_btn.setEnabled(True)

    def browse_download_path(self):
        """浏览下载路径"""
        path = QFileDialog.getExistingDirectory(self, "选择临时下载目录")
        if path:
            self.download_path_input.setText(path)

    def get_checkbox_style(self):
        """获取复选框样式"""
        return """
            QCheckBox {
                spacing: 5px;
                font-size: 14px;
                color: #333;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 3px;
                border: 2px solid #ddd;
                background-color: white;
            }
            QCheckBox::indicator:hover {
                border-color: #2196F3;
                background-color: #f0f8ff;
            }
            QCheckBox::indicator:checked {
                background-color: #2196F3;
                border-color: #2196F3;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iOSIgdmlld0JveD0iMCAwIDEyIDkiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik0xIDQuNUw0LjUgOEwxMSAxIiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPgo8L3N2Zz4K);
            }
            QCheckBox::indicator:checked:hover {
                background-color: #1976D2;
                border-color: #1976D2;
            }
            QCheckBox::indicator:disabled {
                background-color: #f5f5f5;
                border-color: #ddd;
            }
        """

    def get_stylesheet(self):
        """获取样式表"""
        return """
            QMainWindow {
                background-color: #f5f5f5;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
                font-size: 14px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
                min-height: 20px;
                font-size: 14px;
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
            QLineEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px;
                font-size: 14px;
            }
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                font-family: Consolas, monospace;
                font-size: 14px;
            }
            QTableWidget {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
                gridline-color: #e0e0e0;
                font-size: 13px;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #f0f0f0;
            }
            QTableWidget::item:selected {
                background-color: #e3f2fd;
                color: #1976D2;
            }
            QHeaderView::section {
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                padding: 8px;
                font-weight: bold;
                font-size: 13px;
            }
            QHeaderView::section:hover {
                background-color: #e3f2fd;
                cursor: pointer;
            }
            QTabWidget::pane {
                border: 1px solid #ddd;
                border-radius: 4px;
            }
            QTabBar::tab {
                background-color: #e0e0e0;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                font-size: 13px;
                font-family: "Microsoft YaHei";
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 2px solid #2196F3;
            }
            QLabel {
                font-size: 14px;
            }
            QProgressBar {
                border: 1px solid #ddd;
                border-radius: 4px;
                text-align: center;
                font-weight: bold;
                font-size: 12px;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 3px;
            }
        """

    def init_wow_path(self):
        """初始化WoW路径"""
        self.auto_detect_wow_path()

    def auto_detect_wow_path(self):
        """自动检测WoW路径"""
        detector = WoWDetector()
        path = detector.detect_wow_path()
        if path:
            self.path_label.setText(path)
            self.log("检测到魔兽世界安装路径: " + path)
        else:
            self.log("未能自动检测到魔兽世界安装路径，请手动选择")

    def browse_wow_path(self):
        """浏览选择WoW路径"""
        path = QFileDialog.getExistingDirectory(self, "选择魔兽世界安装目录")
        if path:
            detector = WoWDetector()
            if detector.validate_wow_path(path):
                self.path_label.setText(path)
                self.log("设置魔兽世界路径: " + path)
            else:
                QMessageBox.warning(self, "错误", "选择的目录不是有效的魔兽世界安装目录")

    def verify_update_codes(self):
        """验证更新码"""
        codes_text = self.update_codes_input.text().strip()
        if not codes_text:
            QMessageBox.warning(self, "提示", "请输入更新码")
            return

        codes = [code.strip() for code in codes_text.split(',') if code.strip()]
        if not codes:
            QMessageBox.warning(self, "提示", "请输入有效的更新码")
            return

        self.log(f"正在验证 {len(codes)} 个更新码...")

        # 启动验证线程
        self.verify_thread = VerifyThread(codes)
        self.verify_thread.finished.connect(self.on_verify_finished)
        self.verify_thread.start()

    def on_verify_finished(self, success, message, valid_codes):
        """验证完成回调"""
        if success:
            self.log(f"更新码验证成功，有效码数量: {len(valid_codes)}")
            self.valid_update_codes = valid_codes
            self.refresh_addon_list()
        else:
            self.log(f"更新码验证失败: {message}")
            QMessageBox.warning(self, "验证失败", message)

    def refresh_addon_list(self):
        """刷新插件列表"""
        if not hasattr(self, 'valid_update_codes') or not self.valid_update_codes:
            QMessageBox.warning(self, "提示", "请先验证更新码")
            return

        wow_path = self.path_label.text()
        if not wow_path:
            QMessageBox.warning(self, "提示", "请先设置魔兽世界路径")
            return

        self.log("正在检查插件更新...")

        # 启动检查更新线程
        self.check_thread = CheckUpdateThread(wow_path, self.valid_update_codes)
        self.check_thread.finished.connect(self.on_check_finished)
        self.check_thread.start()

    def on_check_finished(self, success, message, updates):
        """检查更新完成回调"""
        if success:
            self.display_updates(updates)
            self.log(f"检查完成，发现 {len(updates)} 个可更新插件")
        else:
            self.log(f"检查更新失败: {message}")
            QMessageBox.warning(self, "检查失败", message)

    def display_updates(self, updates):
        """显示可更新插件"""
        self.addon_table.setRowCount(len(updates))

        if not updates:
            self.update_selected_btn.setEnabled(False)
            self.update_all_btn.setEnabled(False)
            return

        for row, (addon_name, info) in enumerate(updates.items()):
            # 选择框 - 使用统一的包装方式
            checkbox_widget = QWidget()
            checkbox_layout = QHBoxLayout(checkbox_widget)
            checkbox_layout.setContentsMargins(0, 0, 0, 0)
            checkbox_layout.setAlignment(Qt.AlignCenter)

            checkbox = QCheckBox()
            checkbox.setChecked(True)
            checkbox.setStyleSheet(self.get_checkbox_style())

            checkbox_layout.addWidget(checkbox)
            self.addon_table.setCellWidget(row, 0, checkbox_widget)

            # 插件名
            name_item = QTableWidgetItem(addon_name)
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
            self.addon_table.setItem(row, 1, name_item)

            # 当前版本
            current_version_item = QTableWidgetItem(info['current_version'])
            current_version_item.setFlags(current_version_item.flags() & ~Qt.ItemIsEditable)
            self.addon_table.setItem(row, 2, current_version_item)

            # 最新版本
            latest_version_item = QTableWidgetItem(info['latest_version'])
            latest_version_item.setFlags(latest_version_item.flags() & ~Qt.ItemIsEditable)
            self.addon_table.setItem(row, 3, latest_version_item)

        self.update_selected_btn.setEnabled(True)
        self.update_all_btn.setEnabled(True)

    def update_selected_addons(self):
        """更新选中的插件"""
        selected_addons = []
        for row in range(self.addon_table.rowCount()):
            checkbox_widget = self.addon_table.cellWidget(row, 0)
            if checkbox_widget:
                checkbox = checkbox_widget.findChild(QCheckBox)
                if checkbox and checkbox.isChecked():
                    name_item = self.addon_table.item(row, 1)
                    current_item = self.addon_table.item(row, 2)
                    latest_item = self.addon_table.item(row, 3)

                    if name_item and current_item and latest_item:
                        selected_addons.append({
                            'name': name_item.text(),
                            'current_version': current_item.text(),
                            'latest_version': latest_item.text()
                        })

        if not selected_addons:
            QMessageBox.information(self, "提示", "请选择要更新的插件")
            return

        self.start_update(selected_addons)

    def update_all_addons(self):
        """更新全部插件"""
        all_addons = []
        for row in range(self.addon_table.rowCount()):
            name_item = self.addon_table.item(row, 1)
            current_item = self.addon_table.item(row, 2)
            latest_item = self.addon_table.item(row, 3)

            if name_item and current_item and latest_item:
                all_addons.append({
                    'name': name_item.text(),
                    'current_version': current_item.text(),
                    'latest_version': latest_item.text()
                })

        if not all_addons:
            return

        self.start_update(all_addons)

    def start_update(self, addons):
        """开始更新插件"""
        wow_path = self.path_label.text()
        if not wow_path:
            QMessageBox.warning(self, "提示", "请先设置魔兽世界路径")
            return

        # 检查是否有有效的更新码
        if not hasattr(self, 'valid_update_codes') or not self.valid_update_codes:
            QMessageBox.warning(self, "提示", "请先验证更新码")
            return

        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, len(addons))
        self.progress_bar.setValue(0)

        self.log(f"开始更新 {len(addons)} 个插件...")

        # 禁用按钮
        self.update_selected_btn.setEnabled(False)
        self.update_all_btn.setEnabled(False)

        # 启动下载线程，传入更新码参数
        self.download_thread = DownloadThread(wow_path, addons, self.valid_update_codes)
        self.download_thread.progress.connect(self.on_download_progress)
        self.download_thread.finished.connect(self.on_download_finished)
        self.download_thread.start()


    def on_download_progress(self, addon_name, status):
        """下载进度回调"""
        current_value = self.progress_bar.value()
        if status == "completed":
            self.progress_bar.setValue(current_value + 1)
            self.log(f"插件 {addon_name} 更新完成")
        elif status == "failed":
            self.progress_bar.setValue(current_value + 1)
            self.log(f"插件 {addon_name} 更新失败")
        else:
            self.log(f"正在更新插件 {addon_name}...")

    def on_download_finished(self, success, message):
        """下载完成回调"""
        self.progress_bar.setVisible(False)
        self.update_selected_btn.setEnabled(True)
        self.update_all_btn.setEnabled(True)

        if success:
            self.log("所有插件更新完成！")
            QMessageBox.information(self, "更新完成", "所有插件更新完成！")
            self.refresh_addon_list()
        else:
            self.log(f"更新过程中出现错误: {message}")
            QMessageBox.warning(self, "更新失败", message)

    def log(self, message):
        """添加日志"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")


# 工作线程类
class TestConnectionThread(QThread):
    finished = pyqtSignal(bool, str)

    def __init__(self, server_url):
        super().__init__()
        self.server_url = server_url

    def run(self):
        try:
            import requests
            response = requests.get(f"{self.server_url}/health", timeout=5)
            if response.status_code == 200:
                self.finished.emit(True, "连接成功")
            else:
                self.finished.emit(False, f"服务器响应错误: {response.status_code}")
        except Exception as e:
            self.finished.emit(False, str(e))


class VerifyThread(QThread):
    finished = pyqtSignal(bool, str, list)

    def __init__(self, update_codes):
        super().__init__()
        self.update_codes = update_codes

    def run(self):
        try:
            from updater.core.api_client import APIClient
            api_client = APIClient()

            valid_codes = []
            for code in self.update_codes:
                if api_client.verify_update_code("test_addon", code):
                    valid_codes.append(code)

            if valid_codes:
                self.finished.emit(True, "验证成功", valid_codes)
            else:
                self.finished.emit(False, "没有有效的更新码", [])
        except Exception as e:
            self.finished.emit(False, str(e), [])


class CheckUpdateThread(QThread):
    finished = pyqtSignal(bool, str, dict)

    def __init__(self, wow_path, update_codes):
        super().__init__()
        self.wow_path = wow_path
        self.update_codes = update_codes

    def run(self):
        try:
            from updater.core.addon_manager import AddonManager
            from updater.core.version_checker import VersionChecker

            addon_manager = AddonManager()
            version_checker = VersionChecker()

            # 获取本地插件列表
            local_addons = addon_manager.get_local_addons(self.wow_path)

            # 检查更新
            updates = version_checker.check_updates(local_addons, self.update_codes)

            self.finished.emit(True, "检查完成", updates)
        except Exception as e:
            self.finished.emit(False, str(e), {})


class DownloadThread(QThread):
    progress = pyqtSignal(str, str)
    finished = pyqtSignal(bool, str)

    def __init__(self, wow_path, addons, update_codes):
        super().__init__()
        self.wow_path = wow_path
        self.addons = addons
        self.update_codes = update_codes

    def run(self):
        try:
            from updater.core.downloader import Downloader
            from updater.core.api_client import APIClient

            downloader = Downloader()
            api_client = APIClient()

            # 首先获取完整的插件信息，包括下载地址
            addon_info_map = {}
            try:
                # 从服务器获取插件列表，包含真实下载地址
                response = api_client.get_addon_list(self.update_codes)
                if response.get('success'):
                    server_addons = response.get('addons', {})

                    # 建立插件名到下载信息的映射
                    for server_name, server_info in server_addons.items():
                        # 创建多种可能的匹配键
                        keys = [
                            server_name,
                            server_name.lower(),
                            server_name.replace(' ', ''),
                            server_name.replace(' ', '').lower()
                        ]

                        addon_data = {
                            'download_url': server_info.get('download_url'),
                            'update_code': server_info.get('update_code'),
                            'url_status': server_info.get('url_status', 'unknown'),
                            'server_name': server_name
                        }

                        for key in keys:
                            addon_info_map[key] = addon_data

            except Exception as e:
                self.finished.emit(False, f"获取插件信息失败: {str(e)}")
                return

            success_count = 0
            fail_count = 0

            for addon in self.addons:
                addon_name = addon['name']
                self.progress.emit(addon_name, "downloading")

                # 查找对应的下载地址
                download_url = None
                url_status = 'unknown'
                server_name = addon_name

                # 尝试多种匹配方式
                search_keys = [
                    addon_name,
                    addon_name.lower(),
                    addon_name.replace(' ', ''),
                    addon_name.replace(' ', '').lower()
                ]

                # 精确匹配
                for key in search_keys:
                    if key in addon_info_map:
                        addon_data = addon_info_map[key]
                        download_url = addon_data['download_url']
                        url_status = addon_data['url_status']
                        server_name = addon_data['server_name']
                        print(f"✅ 精确匹配: {addon_name} -> {server_name}")
                        break

                # 如果没有精确匹配，尝试模糊匹配
                if not download_url:
                    for key, addon_data in addon_info_map.items():
                        key_lower = key.lower()
                        addon_lower = addon_name.lower()

                        # 避免短名称匹配长名称的问题
                        if (addon_lower in key_lower and len(addon_lower) >= len(key_lower) * 0.7) or \
                                (key_lower in addon_lower and len(key_lower) >= len(addon_lower) * 0.7):
                            download_url = addon_data['download_url']
                            url_status = addon_data['url_status']
                            server_name = addon_data['server_name']
                            print(f"⚠️ 模糊匹配: {addon_name} -> {server_name}")
                            break

                if not download_url:
                    self.progress.emit(addon_name, "failed")
                    fail_count += 1
                    print(f"❌ 未找到插件 {addon_name} 的下载地址")
                    continue

                # 检查URL状态
                if url_status == 'invalid':
                    self.progress.emit(addon_name, "failed")
                    fail_count += 1
                    print(f"❌ 插件 {addon_name} 的下载地址无效")
                    continue

                print(f"🔽 开始下载插件: {addon_name}")
                print(f"📍 下载地址: {download_url}")
                print(f"📁 WoW路径: {self.wow_path}")

                try:
                    success = downloader.download_and_install(
                        addon_name, download_url, self.wow_path
                    )

                    if success:
                        self.progress.emit(addon_name, "completed")
                        success_count += 1
                        print(f"✅ 插件 {addon_name} 更新成功")
                    else:
                        self.progress.emit(addon_name, "failed")
                        fail_count += 1
                        print(f"❌ 插件 {addon_name} 更新失败")

                except Exception as e:
                    self.progress.emit(addon_name, "failed")
                    fail_count += 1
                    print(f"❌ 插件 {addon_name} 下载异常: {str(e)}")

            # 构建结果消息
            total = len(self.addons)
            if success_count == total:
                message = f"所有 {total} 个插件更新完成"
                self.finished.emit(True, message)
            elif success_count > 0:
                message = f"部分插件更新完成: 成功 {success_count}/{total}"
                self.finished.emit(True, message)
            else:
                message = f"所有插件更新失败: {fail_count}/{total}"
                self.finished.emit(False, message)

        except Exception as e:
            self.finished.emit(False, f"更新过程出现异常: {str(e)}")