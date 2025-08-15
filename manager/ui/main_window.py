# manager/ui/main_window.py
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QTabWidget, QLabel, QPushButton, QListWidget,
                             QListWidgetItem, QMessageBox, QTextEdit, QGroupBox,
                             QLineEdit, QFileDialog, QCheckBox, QScrollArea,
                             QTableWidget, QTableWidgetItem, QHeaderView,
                             QComboBox, QSplitter, QFrame, QDialog, QFormLayout,
                             QDialogButtonBox, QTreeWidget, QTreeWidgetItem,
                             QMenu, QAction)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QPalette
from .add_addon_dialog import AddAddonDialog
from .manage_addon_dialog import ManageAddonDialog
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))


class MainWindow(QMainWindow):
    def __init__(self, token):
        super().__init__()
        self.token = token
        self.all_local_addons = {}  # 存储所有本地插件
        self.all_server_addons = {}  # 存储所有服务器插件
        self.init_ui()
        self.refresh_addon_list()

    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("魔兽世界插件管理器")
        self.setGeometry(100, 100, 1400, 900)

        # 中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # 标题
        title_label = QLabel("魔兽世界插件管理器")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 20, QFont.Bold))
        title_label.setStyleSheet("color: #1976D2; margin: 15px;")
        layout.addWidget(title_label)

        # 选项卡
        self.tab_widget = QTabWidget()

        # 添加插件选项卡
        self.add_tab = self.create_add_addon_tab()
        self.tab_widget.addTab(self.add_tab, "添加插件")

        # 管理插件选项卡
        self.manage_tab = self.create_manage_addon_tab()
        self.tab_widget.addTab(self.manage_tab, "管理插件")

        layout.addWidget(self.tab_widget)

        # 设置样式
        self.setStyleSheet(self.get_stylesheet())

    def create_add_addon_tab(self):
        """创建添加插件选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # WoW路径设置
        path_group = QGroupBox("魔兽世界路径设置")
        path_layout = QHBoxLayout(path_group)

        self.wow_path_input = QLineEdit()
        self.wow_path_input.setPlaceholderText("魔兽世界安装路径...")
        self.wow_path_input.setReadOnly(True)

        self.browse_wow_btn = QPushButton("浏览")
        self.browse_wow_btn.clicked.connect(self.browse_wow_path)

        self.detect_wow_btn = QPushButton("自动检测")
        self.detect_wow_btn.clicked.connect(self.auto_detect_wow_path)

        path_layout.addWidget(QLabel("WoW路径:"))
        path_layout.addWidget(self.wow_path_input)
        path_layout.addWidget(self.browse_wow_btn)
        path_layout.addWidget(self.detect_wow_btn)
        layout.addWidget(path_group)

        # 插件选择
        addon_group = QGroupBox("插件选择")
        addon_layout = QVBoxLayout(addon_group)

        # 搜索和操作按钮
        top_layout = QHBoxLayout()

        # 搜索框
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("搜索:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入插件名进行模糊搜索...")
        self.search_input.textChanged.connect(self.filter_local_addons)
        search_layout.addWidget(self.search_input)
        top_layout.addLayout(search_layout)

        # 操作按钮
        self.scan_addons_btn = QPushButton("扫描本地插件")
        self.scan_addons_btn.clicked.connect(self.scan_local_addons)

        self.add_selected_btn = QPushButton("添加选中插件")
        self.add_selected_btn.clicked.connect(self.add_selected_addons)
        self.add_selected_btn.setEnabled(False)

        top_layout.addWidget(self.scan_addons_btn)
        top_layout.addStretch()
        top_layout.addWidget(self.add_selected_btn)
        addon_layout.addLayout(top_layout)

        # 插件表格
        self.local_addon_table = QTableWidget()
        # 设置行高
        self.local_addon_table.verticalHeader().setDefaultSectionSize(40)
        self.local_addon_table.setColumnCount(3)
        self.local_addon_table.setHorizontalHeaderLabels(["选择", "插件名", "版本号"])

        # 设置表格属性
        header = self.local_addon_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)  # 选择列固定宽度
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # 插件名列自适应
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # 版本号列适应内容
        self.local_addon_table.setColumnWidth(0, 80)

        self.local_addon_table.setAlternatingRowColors(True)
        self.local_addon_table.setSelectionBehavior(QTableWidget.SelectRows)

        addon_layout.addWidget(self.local_addon_table)
        layout.addWidget(addon_group)

        # 日志
        log_group = QGroupBox("操作日志")
        log_layout = QVBoxLayout(log_group)
        log_group.setMaximumHeight(200)  # 设置整个框架高度
        log_group.setMinimumHeight(120)  # 设置最小框架高度

        self.add_log_text = QTextEdit()
        self.add_log_text.setMaximumHeight(150)
        self.add_log_text.setReadOnly(True)
        # 增大字号
        font = self.add_log_text.font()
        font.setPointSize(14)
        self.add_log_text.setFont(font)
        log_layout.addWidget(self.add_log_text)
        layout.addWidget(log_group)

        self.auto_detect_wow_path()
        return widget

    def create_manage_addon_tab(self):
        """创建管理插件选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # 搜索和操作按钮
        top_layout = QHBoxLayout()

        # 搜索框
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("搜索:"))
        self.manage_search_input = QLineEdit()
        self.manage_search_input.setPlaceholderText("按插件名或更新码搜索...")
        self.manage_search_input.textChanged.connect(self.filter_server_addons)
        search_layout.addWidget(self.manage_search_input)
        top_layout.addLayout(search_layout)

        # 操作按钮
        self.refresh_btn = QPushButton("刷新列表")
        self.refresh_btn.clicked.connect(self.refresh_addon_list)

        self.edit_addon_btn = QPushButton("编辑插件")
        self.edit_addon_btn.clicked.connect(self.edit_addon)
        self.edit_addon_btn.setEnabled(False)

        self.delete_addon_btn = QPushButton("删除插件")
        self.delete_addon_btn.clicked.connect(self.delete_addon)
        self.delete_addon_btn.setEnabled(False)

        top_layout.addWidget(self.refresh_btn)
        top_layout.addStretch()
        top_layout.addWidget(self.edit_addon_btn)
        top_layout.addWidget(self.delete_addon_btn)
        layout.addLayout(top_layout)

        # 插件管理表格
        self.manage_addon_table = QTableWidget()
        self.manage_addon_table.setColumnCount(6)
        self.manage_addon_table.setHorizontalHeaderLabels([
            "插件名", "版本号", "更新码", "下载地址", "创建时间", "更新时间"
        ])

        # 设置表格属性
        header = self.manage_addon_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # 插件名
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # 版本号
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # 更新码
        header.setSectionResizeMode(3, QHeaderView.Stretch)  # 下载地址
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # 创建时间
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # 更新时间

        # 启用排序
        self.manage_addon_table.setSortingEnabled(True)
        self.manage_addon_table.setAlternatingRowColors(True)
        self.manage_addon_table.setSelectionBehavior(QTableWidget.SelectRows)

        # 双击事件
        self.manage_addon_table.cellDoubleClicked.connect(self.on_table_double_clicked)
        self.manage_addon_table.itemSelectionChanged.connect(self.on_manage_selection_changed)

        # 添加右键菜单功能
        self.manage_addon_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.manage_addon_table.customContextMenuRequested.connect(self.show_context_menu)

        # 添加列标题下拉筛选功能
        self.setup_column_filters()

        layout.addWidget(self.manage_addon_table)

        # 日志
        log_group = QGroupBox("操作日志")
        log_layout = QVBoxLayout(log_group)
        log_group.setMaximumHeight(200)  # 设置整个框架高度
        log_group.setMinimumHeight(120)  # 设置最小框架高度

        self.manage_log_text = QTextEdit()
        self.manage_log_text.setMaximumHeight(150)
        self.manage_log_text.setReadOnly(True)
        # 增大字号
        font = self.manage_log_text.font()
        font.setPointSize(14)
        self.manage_log_text.setFont(font)
        log_layout.addWidget(self.manage_log_text)
        layout.addWidget(log_group)

        return widget

    def setup_column_filters(self):
        """设置列标题下拉筛选"""
        header = self.manage_addon_table.horizontalHeader()
        header.sectionClicked.connect(self.show_column_filter)

    def show_column_filter(self, column):
        """显示列筛选菜单"""
        if column in [0, 1, 2]:  # 插件名、版本号、更新码列支持筛选
            menu = QMenu(self)

            # 获取该列的所有唯一值
            values = set()
            for row in range(self.manage_addon_table.rowCount()):
                item = self.manage_addon_table.item(row, column)
                if item:
                    values.add(item.text())

            # 添加"全部"选项
            all_action = QAction("全部", self)
            all_action.triggered.connect(lambda: self.filter_by_column(column, None))
            menu.addAction(all_action)

            menu.addSeparator()

            # 添加各个值的选项
            for value in sorted(values):
                action = QAction(value, self)
                action.triggered.connect(lambda checked, v=value: self.filter_by_column(column, v))
                menu.addAction(action)

            # 显示菜单
            header = self.manage_addon_table.horizontalHeader()
            header_pos = header.mapToGlobal(header.rect().topLeft())
            header_pos.setX(header_pos.x() + header.sectionPosition(column))
            header_pos.setY(header_pos.y() + header.height())
            menu.exec_(header_pos)

    def filter_by_column(self, column, value):
        """按列值筛选"""
        for row in range(self.manage_addon_table.rowCount()):
            item = self.manage_addon_table.item(row, column)
            if value is None:  # 显示全部
                self.manage_addon_table.setRowHidden(row, False)
            else:
                should_hide = item is None or item.text() != value
                self.manage_addon_table.setRowHidden(row, should_hide)

    def filter_local_addons(self):
        """过滤本地插件"""
        search_text = self.search_input.text().lower()

        for row in range(self.local_addon_table.rowCount()):
            addon_name_item = self.local_addon_table.item(row, 1)
            if addon_name_item:
                addon_name = addon_name_item.text().lower()
                should_show = search_text in addon_name
                self.local_addon_table.setRowHidden(row, not should_show)

    def filter_server_addons(self):
        """过滤服务器插件"""
        search_text = self.manage_search_input.text().lower()

        for row in range(self.manage_addon_table.rowCount()):
            should_show = False

            # 检查插件名
            addon_name_item = self.manage_addon_table.item(row, 0)
            if addon_name_item and search_text in addon_name_item.text().lower():
                should_show = True

            # 检查更新码
            update_code_item = self.manage_addon_table.item(row, 2)
            if update_code_item and search_text in update_code_item.text().lower():
                should_show = True

            self.manage_addon_table.setRowHidden(row, not should_show)

    def scan_local_addons(self):
        """扫描本地插件"""
        wow_path = self.wow_path_input.text()
        if not wow_path:
            QMessageBox.warning(self, "提示", "请先设置魔兽世界路径")
            return

        self.add_log("正在扫描本地插件...")

        # 启动扫描线程
        self.scan_thread = ScanAddonThread(wow_path)
        self.scan_thread.finished.connect(self.on_scan_finished)
        self.scan_thread.start()

    def on_scan_finished(self, success, message, addons):
        """扫描完成回调"""
        if success:
            self.all_local_addons = addons
            self.display_local_addons(addons)
            self.add_log(f"扫描完成，发现 {len(addons)} 个插件")
        else:
            self.add_log(f"扫描失败: {message}")
            QMessageBox.warning(self, "扫描失败", message)

    def display_local_addons(self, addons):
        """显示本地插件"""
        self.local_addon_table.setRowCount(len(addons))

        for row, (addon_name, version) in enumerate(addons.items()):
            # 选择框 - 使用统一的包装方式
            checkbox_widget = QWidget()
            checkbox_layout = QHBoxLayout(checkbox_widget)
            checkbox_layout.setContentsMargins(0, 0, 0, 0)
            checkbox_layout.setAlignment(Qt.AlignCenter)

            checkbox = QCheckBox()
            checkbox.setChecked(False)  # 本地插件默认选中
            checkbox.setStyleSheet(self.get_checkbox_style())  # 应用统一样式

            checkbox_layout.addWidget(checkbox)
            self.local_addon_table.setCellWidget(row, 0, checkbox_widget)

            # 插件名
            name_item = QTableWidgetItem(addon_name)
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
            self.local_addon_table.setItem(row, 1, name_item)

            # 版本号
            version_item = QTableWidgetItem(version)
            version_item.setFlags(version_item.flags() & ~Qt.ItemIsEditable)
            self.local_addon_table.setItem(row, 2, version_item)

        self.add_selected_btn.setEnabled(len(addons) > 0)

    def add_selected_addons(self):
        """添加选中的插件 - 修复版本"""
        try:
            self.add_log("开始获取选中的插件...")
            selected_addons = []

            for row in range(self.local_addon_table.rowCount()):
                # 获取复选框包装器
                checkbox_widget = self.local_addon_table.cellWidget(row, 0)

                if checkbox_widget is None:
                    continue

                # 查找实际的复选框控件
                checkbox = None
                if isinstance(checkbox_widget, QCheckBox):
                    # 如果直接是复选框
                    checkbox = checkbox_widget
                elif isinstance(checkbox_widget, QWidget):
                    # 如果是包装器，查找子控件
                    checkbox = checkbox_widget.findChild(QCheckBox)

                # 检查复选框是否选中
                if checkbox and checkbox.isChecked():
                    # 获取插件信息
                    name_item = self.local_addon_table.item(row, 1)
                    version_item = self.local_addon_table.item(row, 2)

                    if name_item and version_item:
                        addon_name = name_item.text()
                        version = version_item.text()
                        selected_addons.append({
                            'name': addon_name,
                            'version': version
                        })
                        self.add_log(f"选中插件: {addon_name} - {version}")

            if not selected_addons:
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Information)
                msg.setWindowTitle("提示")
                msg.setText("请选择要添加的插件")

                # 设置样式，包含按钮居中
                msg.setStyleSheet("""
                    QMessageBox {
                        background-color: #f8f9fa;
                        font-family: "Microsoft YaHei UI";
                        font-size: 14px;
                    }
                    QMessageBox QLabel {
                        color: #333;
                        font-size: 14px;
                        padding: 10px;
                    }
                    QMessageBox QPushButton {
                        background-color: #2196F3;
                        color: white;
                        border: none;
                        padding: 8px 20px;
                        border-radius: 4px;
                        font-weight: bold;
                        min-width: 80px;
                        font-size: 13px;
                    }
                    QMessageBox QPushButton:hover {
                        background-color: #1976D2;
                    }
                    QMessageBox .QDialogButtonBox {
                        alignment: center;              /* 按钮容器居中 */
                    }
                    QDialogButtonBox {
                        qproperty-centerButtons: true;  /* 按钮居中属性 */
                    }
                """)

                msg.exec_()
                return

                msg.exec_()
                return
            self.add_log(f"共选中 {len(selected_addons)} 个插件")

            # 使用改进的添加插件对话框
            dialog = AddAddonDialog(selected_addons, self.token, self)
            if dialog.exec_() == QDialog.Accepted:
                self.add_log("插件添加成功")
                self.refresh_addon_list()

        except Exception as e:
            self.add_log(f"添加插件时发生错误: {str(e)}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "错误", f"添加插件时发生错误: {str(e)}")

    def refresh_addon_list(self):
        """刷新插件列表"""
        self.manage_log("正在刷新插件列表...")

        # 启动刷新线程
        self.refresh_thread = RefreshAddonThread(self.token)
        self.refresh_thread.finished.connect(self.on_refresh_finished)
        self.refresh_thread.start()

    def on_refresh_finished(self, success, message, addons):
        """刷新完成回调"""
        if success:
            self.all_server_addons = addons
            self.display_server_addons(addons)
            self.manage_log(f"刷新完成，共 {len(addons)} 个插件")
        else:
            self.manage_log(f"刷新失败: {message}")
            QMessageBox.warning(self, "刷新失败", message)

    def display_server_addons(self, addons):
        """显示服务器插件"""
        self.manage_addon_table.setRowCount(len(addons))

        for row, (addon_name, addon_info) in enumerate(addons.items()):
            # 插件名
            name_item = QTableWidgetItem(addon_name)
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
            name_item.setData(Qt.UserRole, {'name': addon_name, 'info': addon_info})
            self.manage_addon_table.setItem(row, 0, name_item)

            # 版本号
            version_item = QTableWidgetItem(addon_info.get('version', ''))
            version_item.setFlags(version_item.flags() & ~Qt.ItemIsEditable)
            self.manage_addon_table.setItem(row, 1, version_item)

            # 更新码
            code_item = QTableWidgetItem(addon_info.get('update_code', ''))
            code_item.setFlags(code_item.flags() & ~Qt.ItemIsEditable)
            self.manage_addon_table.setItem(row, 2, code_item)

            # 下载地址 - 只显示前50个字符
            url = addon_info.get('download_url', '')
            display_url = url[:50] + '...' if len(url) > 50 else url
            url_item = QTableWidgetItem(display_url)
            url_item.setFlags(url_item.flags() & ~Qt.ItemIsEditable)
            url_item.setToolTip(url)  # 完整URL作为提示
            self.manage_addon_table.setItem(row, 3, url_item)

            # 创建时间
            created_time = addon_info.get('created_at', '')
            if created_time:
                created_time = created_time[:19].replace('T', ' ')
            created_item = QTableWidgetItem(created_time)
            created_item.setFlags(created_item.flags() & ~Qt.ItemIsEditable)
            self.manage_addon_table.setItem(row, 4, created_item)

            # 更新时间
            updated_time = addon_info.get('updated_at', '')
            if updated_time:
                updated_time = updated_time[:19].replace('T', ' ')
            updated_item = QTableWidgetItem(updated_time)
            updated_item.setFlags(updated_item.flags() & ~Qt.ItemIsEditable)
            self.manage_addon_table.setItem(row, 5, updated_item)

    def on_table_double_clicked(self, row, column):
        """表格双击事件"""
        self.edit_addon()

    def on_manage_selection_changed(self):
        """管理表格选择改变"""
        has_selection = len(self.manage_addon_table.selectedItems()) > 0
        self.edit_addon_btn.setEnabled(has_selection)
        self.delete_addon_btn.setEnabled(has_selection)

    def edit_addon(self):
        """编辑插件"""
        current_row = self.manage_addon_table.currentRow()
        if current_row < 0:
            return

        name_item = self.manage_addon_table.item(current_row, 0)
        addon_data = name_item.data(Qt.UserRole)

        dialog = ManageAddonDialog(addon_data, self.token, self)
        if dialog.exec_() == QDialog.Accepted:
            self.manage_log("插件信息更新成功")
            self.refresh_addon_list()

    def delete_addon(self):
        """删除插件"""
        current_row = self.manage_addon_table.currentRow()
        if current_row < 0:
            return

        name_item = self.manage_addon_table.item(current_row, 0)
        addon_data = name_item.data(Qt.UserRole)
        addon_name = addon_data['name']

        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除插件 '{addon_name}' 吗？\n此操作不可恢复！",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.manage_log(f"正在删除插件: {addon_name}")

            # 启动删除线程
            self.delete_thread = DeleteAddonThread(addon_name, self.token)
            self.delete_thread.finished.connect(self.on_delete_finished)
            self.delete_thread.start()

    def on_delete_finished(self, success, message, addon_name):
        """删除完成回调"""
        if success:
            self.manage_log(f"插件 {addon_name} 删除成功")
            self.refresh_addon_list()
        else:
            self.manage_log(f"删除插件 {addon_name} 失败: {message}")
            QMessageBox.warning(self, "删除失败", message)

    def show_context_menu(self, position):
        """显示右键菜单"""
        if self.manage_addon_table.itemAt(position) is None:
            return

        menu = QMenu(self)

        edit_action = QAction("编辑插件", self)
        edit_action.triggered.connect(self.edit_addon)
        menu.addAction(edit_action)

        delete_action = QAction("删除插件", self)
        delete_action.triggered.connect(self.delete_addon)
        menu.addAction(delete_action)

        menu.exec_(self.manage_addon_table.mapToGlobal(position))

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
                font-family: "Microsoft YaHei;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 2px solid #2196F3;
            }
            QLabel {
                font-size: 14px;
            }
        """

    def auto_detect_wow_path(self):
        """自动检测WoW路径"""
        from manager.core.wow_detector import WoWDetector

        detector = WoWDetector()
        path = detector.detect_wow_path()
        if path:
            self.wow_path_input.setText(path)
            self.add_log("检测到魔兽世界安装路径: " + path)
        else:
            self.add_log("未能自动检测到魔兽世界安装路径，请手动选择")

    def browse_wow_path(self):
        """浏览选择WoW路径"""
        path = QFileDialog.getExistingDirectory(self, "选择魔兽世界安装目录")
        if path:
            from manager.core.wow_detector import WoWDetector

            detector = WoWDetector()
            if detector.validate_wow_path(path):
                self.wow_path_input.setText(path)
                self.add_log("设置魔兽世界路径: " + path)
            else:
                QMessageBox.warning(self, "错误", "选择的目录不是有效的魔兽世界安装目录")

    def add_log(self, message):
        """添加日志到添加选项卡"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.add_log_text.append(f"[{timestamp}] {message}")

    def manage_log(self, message):
        """添加日志到管理选项卡"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.manage_log_text.append(f"[{timestamp}] {message}")


# 工作线程类保持不变
class ScanAddonThread(QThread):
    finished = pyqtSignal(bool, str, dict)

    def __init__(self, wow_path):
        super().__init__()
        self.wow_path = wow_path

    def run(self):
        try:
            from manager.core.addon_scanner import AddonScanner

            scanner = AddonScanner()
            addons = scanner.scan_addons(self.wow_path)

            self.finished.emit(True, "扫描完成", addons)
        except Exception as e:
            self.finished.emit(False, str(e), {})


class RefreshAddonThread(QThread):
    finished = pyqtSignal(bool, str, dict)

    def __init__(self, token):
        super().__init__()
        self.token = token

    def run(self):
        try:
            from manager.core.api_client import APIClient

            api_client = APIClient()
            response = api_client.get_all_addons(self.token)

            if response.get('success', False):
                addons = response.get('addons', {})
                self.finished.emit(True, "刷新完成", addons)
            else:
                message = response.get('message', '刷新失败')
                self.finished.emit(False, message, {})
        except Exception as e:
            self.finished.emit(False, str(e), {})


class DeleteAddonThread(QThread):
    finished = pyqtSignal(bool, str, str)

    def __init__(self, addon_name, token):
        super().__init__()
        self.addon_name = addon_name
        self.token = token

    def run(self):
        try:
            from manager.core.api_client import APIClient

            api_client = APIClient()
            response = api_client.delete_addon(self.addon_name, self.token)

            if response.get('success', False):
                self.finished.emit(True, "删除成功", self.addon_name)
            else:
                message = response.get('message', '删除失败')
                self.finished.emit(False, message, self.addon_name)
        except Exception as e:
            self.finished.emit(False, str(e), self.addon_name)