# manager/ui/123.py - 统一的插件选择对话框
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


class AddonSelectionDialog(QDialog):
    """统一的插件选择对话框 - 确保默认不全选"""

    def __init__(self, wow_addons, parent=None):
        super().__init__(parent)
        self.wow_addons = wow_addons
        self.filtered_addons = wow_addons.copy()
        self.selected_addons = []
        self.init_ui()

    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("选择要管理的插件")
        self.setModal(True)
        self.resize(800, 650)

        layout = QVBoxLayout(self)

        # 标题
        title_label = QLabel("选择要添加到管理系统的插件")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setStyleSheet("color: #1976D2; margin: 15px;")
        layout.addWidget(title_label)

        # 说明文字
        info_label = QLabel("默认没有选择任何插件，请手动勾选需要管理的插件")
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("color: #666666; font-size: 12px; margin: 5px;")
        layout.addWidget(info_label)

        # 搜索功能
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("搜索插件:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入插件名进行模糊搜索...")
        self.search_input.textChanged.connect(self.filter_addons)
        self.search_input.setStyleSheet("font-size: 14px; padding: 8px;")
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)

        # 插件表格
        self.addon_table = QTableWidget()
        self.addon_table.setColumnCount(3)
        self.addon_table.setHorizontalHeaderLabels(["选择", "插件名", "版本号"])

        # 设置表格属性
        header = self.addon_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)  # 选择列固定宽度
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # 插件名列自适应
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # 版本号列适应内容
        self.addon_table.setColumnWidth(0, 100)  # 增加选择列宽度

        self.addon_table.setAlternatingRowColors(True)
        self.addon_table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.addon_table)

        # 全选/全不选按钮和状态显示
        select_layout = QHBoxLayout()
        self.select_all_btn = QPushButton("全选")
        self.select_all_btn.clicked.connect(self.select_all)
        self.select_none_btn = QPushButton("全不选")
        self.select_none_btn.clicked.connect(self.select_none)

        # 添加选择状态标签
        self.selection_status_label = QLabel("当前选择: 0 个插件")
        self.selection_status_label.setStyleSheet("color: #666666; font-size: 12px;")

        select_layout.addWidget(self.select_all_btn)
        select_layout.addWidget(self.select_none_btn)
        select_layout.addStretch()
        select_layout.addWidget(self.selection_status_label)
        layout.addLayout(select_layout)

        # 按钮
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal
        )
        button_box.accepted.connect(self.accept_selection)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        # 设置样式
        self.setStyleSheet(self.get_stylesheet())

        # 初始化表格数据 - 确保默认不选择
        self.update_addon_table()
        self.update_selection_status()

    def create_checkbox_widget(self):
        """创建统一样式的复选框widget"""
        checkbox_widget = QWidget()
        checkbox_layout = QHBoxLayout(checkbox_widget)
        checkbox_layout.setContentsMargins(0, 0, 0, 0)
        checkbox_layout.setAlignment(Qt.AlignCenter)

        checkbox = QCheckBox()
        checkbox.setChecked(False)  # 确保默认不选择
        # 连接复选框状态变化信号
        checkbox.stateChanged.connect(self.update_selection_status)

        # 统一的复选框样式
        checkbox.setStyleSheet("""
            QCheckBox {
                font-size: 14px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
            }
            QCheckBox::indicator:unchecked {
                border: 2px solid #cccccc;
                background-color: white;
                border-radius: 3px;
            }
            QCheckBox::indicator:checked {
                border: 2px solid #2196F3;
                background-color: #2196F3;
                border-radius: 3px;
            }
        """)

        checkbox_layout.addWidget(checkbox)
        return checkbox_widget

    def filter_addons(self):
        """过滤插件"""
        try:
            search_text = self.search_input.text().lower()

            if not search_text:
                self.filtered_addons = self.wow_addons.copy()
            else:
                self.filtered_addons = [
                    addon for addon in self.wow_addons
                    if search_text in addon['name'].lower()
                ]

            # 重新构建表格，确保所有复选框都是未选中状态
            self.update_addon_table()
            self.update_selection_status()
        except Exception as e:
            print(f"❌ 过滤插件异常: {e}")

    def update_addon_table(self):
        """更新插件表格"""
        try:
            self.addon_table.setRowCount(len(self.filtered_addons))

            for row, addon in enumerate(self.filtered_addons):
                # 设置行高
                self.addon_table.setRowHeight(row, 50)

                # 选择框 - 使用统一的复选框widget
                checkbox_widget = self.create_checkbox_widget()
                self.addon_table.setCellWidget(row, 0, checkbox_widget)

                # 插件名
                name_item = QTableWidgetItem(addon['name'])
                name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
                name_item.setTextAlignment(Qt.AlignVCenter)
                self.addon_table.setItem(row, 1, name_item)

                # 版本号
                version_item = QTableWidgetItem(addon['version'])
                version_item.setFlags(version_item.flags() & ~Qt.ItemIsEditable)
                version_item.setTextAlignment(Qt.AlignVCenter)
                self.addon_table.setItem(row, 2, version_item)
        except Exception as e:
            print(f"❌ 更新插件表格异常: {e}")

    def get_selected_checkbox(self, row):
        """获取指定行的复选框"""
        try:
            checkbox_widget = self.addon_table.cellWidget(row, 0)
            if checkbox_widget:
                for child in checkbox_widget.findChildren(QCheckBox):
                    return child
            return None
        except Exception as e:
            print(f"❌ 获取复选框异常: {e}")
            return None

    def update_selection_status(self):
        """更新选择状态显示"""
        try:
            selected_count = 0
            total_count = self.addon_table.rowCount()

            for row in range(total_count):
                checkbox = self.get_selected_checkbox(row)
                if checkbox and checkbox.isChecked():
                    selected_count += 1

            if hasattr(self, 'selection_status_label'):
                self.selection_status_label.setText(f"当前选择: {selected_count} / {total_count} 个插件")
        except Exception as e:
            print(f"❌ 更新选择状态异常: {e}")

    def select_all(self):
        """全选"""
        try:
            for row in range(self.addon_table.rowCount()):
                checkbox = self.get_selected_checkbox(row)
                if checkbox:
                    checkbox.setChecked(True)
            self.update_selection_status()
        except Exception as e:
            print(f"❌ 全选操作异常: {e}")
            QMessageBox.warning(self, "操作失败", f"全选操作失败: {str(e)}")

    def select_none(self):
        """全不选"""
        try:
            for row in range(self.addon_table.rowCount()):
                checkbox = self.get_selected_checkbox(row)
                if checkbox:
                    checkbox.setChecked(False)
            self.update_selection_status()
        except Exception as e:
            print(f"❌ 全不选操作异常: {e}")
            QMessageBox.warning(self, "操作失败", f"全不选操作失败: {str(e)}")

    def accept_selection(self):
        """确认选择"""
        try:
            selected_addons = []

            for row in range(self.addon_table.rowCount()):
                checkbox = self.get_selected_checkbox(row)
                if checkbox and checkbox.isChecked():
                    addon_name = self.addon_table.item(row, 1).text()
                    version = self.addon_table.item(row, 2).text()

                    # 找到对应的原始插件数据
                    for addon in self.filtered_addons:
                        if addon['name'] == addon_name and addon['version'] == version:
                            selected_addons.append(addon)
                            break

            if not selected_addons:
                reply = QMessageBox.question(
                    self, "未选择插件",
                    "您没有选择任何插件，确定要继续吗？\n\n"
                    "点击'是'将关闭此对话框而不添加任何插件\n"
                    "点击'否继续选择插件",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
                )

                if reply == QMessageBox.No:
                    return  # 用户选择继续选择插件
                else:
                    # 用户确认不选择任何插件，关闭对话框
                    self.selected_addons = []
                    self.reject()  # 使用reject表示取消操作
                    return

            # 确认选择了插件
            self.selected_addons = selected_addons

            # 显示选择确认
            addon_names = [addon['name'] for addon in selected_addons]
            addon_list = "\n".join(f"• {name}" for name in addon_names[:10])
            extra_text = f"\n... 还有 {len(addon_names) - 10} 个插件" if len(addon_names) > 10 else ""

            message = (f"您选择了 {len(selected_addons)} 个插件：\n\n"
                       f"{addon_list}"
                       f"{extra_text}\n\n"
                       "确定要继续添加这些插件到管理系统吗？")

            reply = QMessageBox.question(
                self, "确认选择",
                message,
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )

            if reply == QMessageBox.Yes:
                self.accept()
            # 如果选择No，继续停留在选择页面

        except Exception as e:
            print(f"❌ 确认选择异常: {e}")
            QMessageBox.critical(self, "严重错误", f"确认选择时发生严重错误: {str(e)}")

    def get_selected_addons(self):
        """获取选中的插件 - 修复版本"""
        selected_addons = []

        try:
            for row in range(self.local_addon_table.rowCount()):
                # 获取复选框小部件
                checkbox_widget = self.local_addon_table.cellWidget(row, 0)

                if checkbox_widget is None:
                    print(f"第 {row} 行没有复选框小部件")
                    continue

                # 方法1: 如果是包装器方式，查找子控件
                checkbox = None
                if isinstance(checkbox_widget, QWidget):
                    # 查找QCheckBox子控件
                    checkbox = checkbox_widget.findChild(QCheckBox)
                elif isinstance(checkbox_widget, QCheckBox):
                    # 如果直接是QCheckBox
                    checkbox = checkbox_widget

                if checkbox is None:
                    print(f"第 {row} 行找不到复选框控件")
                    continue

                # 检查是否选中
                if checkbox.isChecked():
                    # 获取插件名和版本
                    name_item = self.local_addon_table.item(row, 1)
                    version_item = self.local_addon_table.item(row, 2)

                    if name_item and version_item:
                        addon_name = name_item.text()
                        version = version_item.text()

                        selected_addons.append({
                            'name': addon_name,
                            'version': version
                        })
                        print(f"选中插件: {addon_name} - {version}")

        except Exception as e:
            print(f"获取选中插件时发生错误: {e}")
            import traceback
            traceback.print_exc()
            return []

        return selected_addons

    def get_stylesheet(self):
        """获取样式表"""
        return """
            QDialog {
                background-color: #f5f5f5;
            }
            QLineEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px;
                font-size: 14px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #2196F3;
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
            QTableWidget {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
                gridline-color: #e0e0e0;
                font-size: 14px;
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
                font-size: 14px;
            }
            QLabel {
                font-size: 14px;
            }
        """