# manager/ui/improved_add_addon_dialog.py
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QFormLayout, QTextEdit,
                             QMessageBox, QDialogButtonBox, QScrollArea,
                             QWidget, QGroupBox, QTableWidget, QTableWidgetItem,
                             QHeaderView, QCheckBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))


class AddAddonDialog(QDialog):
    def __init__(self, selected_addons, token, parent=None):
        super().__init__(parent)
        self.selected_addons = selected_addons
        self.token = token
        self.filtered_addons = selected_addons.copy()
        self.update_code = None  # 统一的更新码
        self.init_ui()

    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("添加插件信息")
        self.setModal(True)
        self.resize(900, 700)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # 标题
        title_label = QLabel("填写插件更新信息")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Microsoft YaHei", 16, QFont.Bold))
        title_label.setStyleSheet("color: #1976D2; margin: 15px; padding: 10px;")
        layout.addWidget(title_label)

        # 搜索功能
        search_group = QGroupBox("搜索功能")
        search_layout = QHBoxLayout(search_group)

        search_label = QLabel("搜索插件:")
        search_label.setMinimumWidth(80)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入插件名进行模糊搜索...")
        self.search_input.textChanged.connect(self.filter_addons)
        self.search_input.setMinimumHeight(35)

        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        layout.addWidget(search_group)

        # 全选/反选按钮组
        button_group = QGroupBox("批量操作")
        button_layout = QHBoxLayout(button_group)

        self.select_all_btn = QPushButton("✓ 全选")
        self.select_all_btn.setMinimumHeight(35)
        self.select_all_btn.clicked.connect(self.select_all)

        self.select_none_btn = QPushButton("✗ 反选")
        self.select_none_btn.setMinimumHeight(35)
        self.select_none_btn.clicked.connect(self.select_none)

        button_layout.addWidget(self.select_all_btn)
        button_layout.addWidget(self.select_none_btn)
        button_layout.addStretch()
        layout.addWidget(button_group)

        # 插件表格
        table_group = QGroupBox("插件列表")
        table_layout = QVBoxLayout(table_group)

        self.addon_table = QTableWidget()
        self.addon_table.setColumnCount(4)
        self.addon_table.setHorizontalHeaderLabels(["选择", "插件名", "版本号", "下载地址"])

        # 设置表格属性
        header = self.addon_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)  # 选择列固定宽度
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # 插件名列适应内容
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # 版本号列适应内容
        header.setSectionResizeMode(3, QHeaderView.Stretch)  # 下载地址列自适应
        self.addon_table.setColumnWidth(0, 80)

        self.addon_table.setAlternatingRowColors(True)
        self.addon_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.addon_table.setMinimumHeight(300)
        # 设置行高
        self.addon_table.verticalHeader().setDefaultSectionSize(45)

        table_layout.addWidget(self.addon_table)
        layout.addWidget(table_group)

        # 统一更新码显示
        code_group = QGroupBox("统一更新码")
        code_layout = QFormLayout(code_group)

        from manager.core.code_generator import CodeGenerator
        generator = CodeGenerator()
        self.update_code = generator.generate_update_code()

        self.code_input = QLineEdit(self.update_code)
        self.code_input.setReadOnly(True)
        self.code_input.setStyleSheet("""
            background-color: #e8f4fd; 
            font-weight: bold; 
            font-size: 16px; 
            color: #1976D2;
            border: 2px solid #1976D2;
            border-radius: 6px;
            padding: 8px;
        """)
        self.code_input.setMinimumHeight(35)

        code_layout.addRow("更新码:", self.code_input)
        layout.addWidget(code_group)

        # 按钮
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal
        )
        button_box.button(QDialogButtonBox.Ok).setText("确认添加")
        button_box.button(QDialogButtonBox.Cancel).setText("取消")
        button_box.button(QDialogButtonBox.Ok).setMinimumHeight(35)
        button_box.button(QDialogButtonBox.Cancel).setMinimumHeight(35)
        button_box.accepted.connect(self.add_addons)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        # 设置样式
        self.setStyleSheet(self.get_stylesheet())

        # 初始化表格数据
        self.update_addon_table()

    def filter_addons(self):
        """过滤插件"""
        search_text = self.search_input.text().lower()

        if not search_text:
            self.filtered_addons = self.selected_addons.copy()
        else:
            self.filtered_addons = [
                addon for addon in self.selected_addons
                if search_text in addon['name'].lower()
            ]

        self.update_addon_table()

    def update_addon_table(self):
        """更新插件表格"""
        self.addon_table.setRowCount(len(self.filtered_addons))

        for row, addon in enumerate(self.filtered_addons):
            # 选择框 - 使用自定义样式的复选框
            checkbox_widget = QWidget()
            checkbox_layout = QHBoxLayout(checkbox_widget)
            checkbox_layout.setContentsMargins(0, 0, 0, 0)
            checkbox_layout.setAlignment(Qt.AlignCenter)

            checkbox = QCheckBox()
            checkbox.setChecked(True)  # 默认选中
            checkbox.setStyleSheet(self.get_checkbox_style())

            checkbox_layout.addWidget(checkbox)
            self.addon_table.setCellWidget(row, 0, checkbox_widget)

            # 插件名
            name_item = QTableWidgetItem(addon['name'])
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
            name_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.addon_table.setItem(row, 1, name_item)

            # 版本号
            version_item = QTableWidgetItem(addon['version'])
            version_item.setFlags(version_item.flags() & ~Qt.ItemIsEditable)
            version_item.setTextAlignment(Qt.AlignCenter)
            self.addon_table.setItem(row, 2, version_item)

            # 下载地址输入框 - 增加高度
            url_widget = QWidget()
            url_layout = QVBoxLayout(url_widget)
            url_layout.setContentsMargins(5, 5, 5, 5)

            url_input = QLineEdit()
            url_input.setPlaceholderText("请输入网盘直链地址...")
            url_input.setMinimumHeight(30)  # 增加输入框高度
            url_input.setStyleSheet("""
                QLineEdit {
                    border: 1px solid #ddd;
                    border-radius: 1px;
                    padding: 6px;
                    font-size: 13px;
                    background-color: white;
                }
                QLineEdit:focus {
                    border: 2px solid #2196F3;
                    background-color: #f8f9ff;
                }
            """)

            # 直接设置到表格中，不使用额外容器
            self.addon_table.setCellWidget(row, 3, url_input)

            # 为当前行设置足够的高度
            self.addon_table.setRowHeight(row, 45)

    def select_all(self):
        """全选"""
        for row in range(self.addon_table.rowCount()):
            checkbox_widget = self.addon_table.cellWidget(row, 0)
            if checkbox_widget:
                checkbox = checkbox_widget.findChild(QCheckBox)
                if checkbox:
                    checkbox.setChecked(True)

    def select_none(self):
        """反选"""
        for row in range(self.addon_table.rowCount()):
            checkbox_widget = self.addon_table.cellWidget(row, 0)
            if checkbox_widget:
                checkbox = checkbox_widget.findChild(QCheckBox)
                if checkbox:
                    checkbox.setChecked(not checkbox.isChecked())

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
            QDialog {
                background-color: #f8f9fa;
                font-family: "Microsoft YaHei", Arial, sans-serif;
            }
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 15px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px 0 10px;
                color: #1976D2;
                background-color: white;
            }
            QLineEdit {
                border: 1px solid #ddd;
                border-radius: 6px;
                padding: 10px;
                font-size: 14px;
                background-color: white;
                min-height: 20px;
            }
            QLineEdit:focus {
                border: 2px solid #2196F3;
                background-color: #f8f9ff;
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
                min-height: 15px;
            }
            QPushButton:hover {
                background-color: #1976D2;
                transform: translateY(-1px);
            }
            QPushButton:pressed {
                background-color: #1565C0;
                transform: translateY(0px);
            }
            QTableWidget {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                background-color: white;
                gridline-color: #f0f0f0;
                font-size: 13px;
                selection-background-color: #e3f2fd;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #f5f5f5;
            }
            QTableWidget::item:selected {
                background-color: #e3f2fd;
                color: #1976D2;
            }
            QHeaderView::section {
                background-color: #f5f5f5;
                border: 1px solid #e0e0e0;
                padding: 12px 8px;
                font-weight: bold;
                font-size: 14px;
                color: #333;
            }
            QHeaderView::section:hover {
                background-color: #eeeeee;
            }
            QDialogButtonBox QPushButton {
                min-width: 100px;
                padding: 10px 25px;
                font-size: 14px;
            }
            QLabel {
                color: #333;
                font-size: 14px;
            }
        """

    def add_addons(self):
        """添加插件 - 修复URL获取问题"""
        # 验证输入
        addon_data = []

        for row in range(self.addon_table.rowCount()):
            checkbox_widget = self.addon_table.cellWidget(row, 0)
            if checkbox_widget:
                checkbox = checkbox_widget.findChild(QCheckBox)
                if checkbox and checkbox.isChecked():
                    addon_name = self.addon_table.item(row, 1).text()
                    version = self.addon_table.item(row, 2).text()

                    # 修复：兼容不同的URL输入框布局方式
                    url = ""
                    url_cell_widget = self.addon_table.cellWidget(row, 3)

                    if url_cell_widget:
                        # 方法1: 直接是QLineEdit
                        if isinstance(url_cell_widget, QLineEdit):
                            url = url_cell_widget.text().strip()
                        # 方法2: 在容器中查找QLineEdit
                        else:
                            url_input = url_cell_widget.findChild(QLineEdit)
                            if url_input:
                                url = url_input.text().strip()
                            else:
                                # 方法3: 尝试在子控件中查找
                                for child in url_cell_widget.findChildren(QLineEdit):
                                    if child.text().strip():
                                        url = child.text().strip()
                                        break

                    # 调试信息 - 可以在测试时启用
                    print(f"Row {row}: addon='{addon_name}', url='{url}', widget_type={type(url_cell_widget)}")

                    if not url:
                        QMessageBox.warning(
                            self, "输入错误",
                            f"请填写插件 '{addon_name}' 的下载地址"
                        )
                        return

                    addon_data.append({
                        'name': addon_name,
                        'version': version,
                        'download_url': url,
                        'update_code': self.update_code  # 使用统一的更新码
                    })

        if not addon_data:
            QMessageBox.information(self, "提示", "请至少选择一个插件")
            return

        # 启动添加线程
        self.add_thread = AddAddonThread(addon_data, self.token)
        self.add_thread.finished.connect(self.on_add_finished)
        self.add_thread.start()

        # 禁用按钮
        self.setEnabled(False)

    def on_add_finished(self, success, message):
        """添加完成回调"""
        self.setEnabled(True)

        if success:
            QMessageBox.information(self, "添加成功", f"所有插件已成功添加！\n统一更新码: {self.update_code}")
            self.accept()
        else:
            QMessageBox.warning(self, "添加失败", message)


class AddAddonThread(QThread):
    finished = pyqtSignal(bool, str)

    def __init__(self, addon_data, token):
        super().__init__()
        self.addon_data = addon_data
        self.token = token

    def run(self):
        try:
            from manager.core.api_client import APIClient

            api_client = APIClient()

            for addon in self.addon_data:
                response = api_client.add_addon(
                    addon['name'],
                    addon['version'],
                    addon['download_url'],
                    addon['update_code'],
                    self.token
                )

                if not response.get('success', False):
                    message = response.get('message', f"添加插件 {addon['name']} 失败")
                    self.finished.emit(False, message)
                    return

            self.finished.emit(True, "所有插件添加成功")
        except Exception as e:
            self.finished.emit(False, f"添加插件失败: {str(e)}")