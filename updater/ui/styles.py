# updater/ui/styles.py - 统一样式配置
"""
WoW插件更新器统一样式配置
提供整个应用程序的样式定义，确保UI一致性
"""


class AppStyles:
    """应用程序样式配置类"""

    # 颜色定义
    COLORS = {
        # 主色调
        'primary': '#007bff',
        'primary_hover': '#0056b3',
        'primary_pressed': '#004085',
        'primary_light': '#e7f3ff',

        # 成功/错误状态
        'success': '#28a745',
        'success_light': '#d4edda',
        'warning': '#ffc107',
        'warning_light': '#fff3cd',
        'danger': '#dc3545',
        'danger_light': '#f8d7da',
        'info': '#17a2b8',
        'info_light': '#d1ecf1',

        # 中性色
        'white': '#ffffff',
        'light': '#f8f9fa',
        'gray_100': '#f8f9fa',
        'gray_200': '#e9ecef',
        'gray_300': '#dee2e6',
        'gray_400': '#ced4da',
        'gray_500': '#adb5bd',
        'gray_600': '#6c757d',
        'gray_700': '#495057',
        'gray_800': '#343a40',
        'gray_900': '#212529',
        'dark': '#343a40',

        # 边框颜色
        'border': '#e9ecef',
        'border_focus': '#007bff',
        'border_hover': '#007bff',

        # 背景色
        'bg_primary': '#ffffff',
        'bg_secondary': '#f8f9fa',
        'bg_tertiary': '#e9ecef',

        # 文本颜色
        'text_primary': '#212529',
        'text_secondary': '#6c757d',
        'text_muted': '#6c757d',
        'text_white': '#ffffff',

        # 特殊效果
        'shadow': 'rgba(0, 0, 0, 0.1)',
        'shadow_hover': 'rgba(0, 123, 255, 0.15)',
    }

    # 字体定义
    FONTS = {
        'primary': '"Microsoft YaHei UI", "Segoe UI", Arial, sans-serif',
        'secondary': '"Segoe UI", "Microsoft YaHei UI", Arial, sans-serif',
        'monospace': '"Consolas", "Courier New", monospace',
        'icon': '"Segoe UI Symbol", "Segoe UI Emoji"',
    }

    # 尺寸定义
    SIZES = {
        'border_radius': '6px',
        'border_radius_lg': '8px',
        'border_radius_sm': '4px',
        'border_width': '2px',
        'shadow_sm': '0 1px 2px rgba(0, 0, 0, 0.05)',
        'shadow': '0 2px 4px rgba(0, 0, 0, 0.1)',
        'shadow_lg': '0 4px 8px rgba(0, 0, 0, 0.15)',
    }

    @classmethod
    def get_main_window_style(cls):
        """获取主窗口样式"""
        return f"""
            QMainWindow {{
                background-color: {cls.COLORS['bg_primary']};
                font-family: {cls.FONTS['primary']};
                font-size: 12px;
            }}

            /* 群组框样式 */
            QGroupBox {{
                font-weight: bold;
                border: {cls.SIZES['border_width']} solid {cls.COLORS['border']};
                border-radius: {cls.SIZES['border_radius_lg']};
                margin-top: 1ex;
                padding-top: 15px;
                background-color: {cls.COLORS['white']};
                font-size: 11px;
            }}

            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px 0 8px;
                color: {cls.COLORS['text_primary']};
                background-color: {cls.COLORS['white']};
                font-size: 10px;
            }}

            /* 按钮样式 */
            QPushButton {{
                background-color: {cls.COLORS['primary']};
                color: {cls.COLORS['text_white']};
                border: none;
                padding: 10px 18px;
                border-radius: {cls.SIZES['border_radius']};
                font-weight: 600;
                font-size: 10px;
                min-height: 16px;
                font-family: {cls.FONTS['primary']};
            }}

            QPushButton:hover {{
                background-color: {cls.COLORS['primary_hover']};
                transform: translateY(-1px);
            }}

            QPushButton:pressed {{
                background-color: {cls.COLORS['primary_pressed']};
                transform: translateY(0px);
            }}

            QPushButton:disabled {{
                background-color: {cls.COLORS['gray_500']};
                color: {cls.COLORS['text_white']};
            }}

            /* 输入框样式 */
            QLineEdit {{
                border: {cls.SIZES['border_width']} solid {cls.COLORS['border']};
                border-radius: {cls.SIZES['border_radius']};
                padding: 10px 12px;
                font-size: 10px;
                background-color: {cls.COLORS['white']};
                selection-background-color: {cls.COLORS['primary']};
                font-family: {cls.FONTS['primary']};
            }}

            QLineEdit:focus {{
                border-color: {cls.COLORS['border_focus']};
                outline: none;
            }}

            QLineEdit:read-only {{
                background-color: {cls.COLORS['bg_secondary']};
                color: {cls.COLORS['text_secondary']};
            }}

            /* 文本编辑器样式 */
            QTextEdit {{
                border: {cls.SIZES['border_width']} solid {cls.COLORS['border']};
                border-radius: {cls.SIZES['border_radius']};
                font-family: {cls.FONTS['monospace']};
                font-size: 10px;
                background-color: {cls.COLORS['white']};
                selection-background-color: {cls.COLORS['primary']};
                color: {cls.COLORS['text_primary']};
            }}

            /* 进度条样式 */
            QProgressBar {{
                border: {cls.SIZES['border_width']} solid {cls.COLORS['border']};
                border-radius: 10px;
                text-align: center;
                font-weight: bold;
                font-size: 10px;
                background-color: {cls.COLORS['bg_secondary']};
                color: {cls.COLORS['text_primary']};
            }}

            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {cls.COLORS['success']}, stop:1 #20c997);
                border-radius: 8px;
                margin: 2px;
            }}

            /* 复选框样式 */
            QCheckBox {{
                font-size: 10px;
                font-family: {cls.FONTS['primary']};
                spacing: 8px;
                color: {cls.COLORS['text_primary']};
            }}

            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border: {cls.SIZES['border_width']} solid {cls.COLORS['border']};
                border-radius: {cls.SIZES['border_radius_sm']};
                background-color: {cls.COLORS['white']};
            }}

            QCheckBox::indicator:checked {{
                background-color: {cls.COLORS['primary']};
                border-color: {cls.COLORS['primary']};
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iOSIgdmlld0JveD0iMCAwIDEyIDkiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PHBhdGggZD0iTTEwLjI4IDEuMjhMMy44NSA3LjcxTDEuNzIgNS41OCIgc3Ryb2tlPSJ3aGl0ZSIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiLz48L3N2Zz4=);
            }}

            QCheckBox::indicator:hover {{
                border-color: {cls.COLORS['border_hover']};
            }}

            /* 标签样式 */
            QLabel {{
                color: {cls.COLORS['text_primary']};
                font-family: {cls.FONTS['primary']};
                font-size: 10px;
            }}

            /* 分割器样式 */
            QSplitter::handle {{
                background-color: {cls.COLORS['border']};
                border: 1px solid {cls.COLORS['gray_400']};
            }}

            QSplitter::handle:horizontal {{
                width: 3px;
            }}

            QSplitter::handle:vertical {{
                height: 3px;
            }}

            QSplitter::handle:hover {{
                background-color: {cls.COLORS['primary']};
            }}

            /* 滚动条样式 */
            QScrollArea {{
                border: 1px solid {cls.COLORS['border']};
                border-radius: {cls.SIZES['border_radius']};
                background-color: {cls.COLORS['white']};
            }}

            QScrollBar:vertical {{
                border: none;
                background: {cls.COLORS['bg_secondary']};
                width: 12px;
                border-radius: 6px;
            }}

            QScrollBar::handle:vertical {{
                background: {cls.COLORS['gray_400']};
                border-radius: 6px;
                min-height: 20px;
            }}

            QScrollBar::handle:vertical:hover {{
                background: {cls.COLORS['gray_500']};
            }}

            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                border: none;
                background: none;
            }}
        """

    @classmethod
    def get_log_text_style(cls):
        """获取日志文本样式"""
        return f"""
            QTextEdit {{
                border: 1px solid {cls.COLORS['border']};
                border-radius: {cls.SIZES['border_radius']};
                background-color: #1e1e1e;
                color: #f0f0f0;
                font-family: {cls.FONTS['monospace']};
                font-size: 9px;
                line-height: 1.4;
                padding: 8px;
            }}
        """

    @classmethod
    def get_addon_item_style(cls):
        """获取插件项样式"""
        return f"""
            QWidget {{
                background-color: {cls.COLORS['white']};
                border: 1px solid {cls.COLORS['border']};
                border-radius: {cls.SIZES['border_radius_lg']};
                margin: 3px;
            }}

            QWidget:hover {{
                background-color: {cls.COLORS['bg_secondary']};
                border-color: {cls.COLORS['primary']};
                box-shadow: {cls.SIZES['shadow']};
            }}
        """

    @classmethod
    def get_header_style(cls):
        """获取头部样式"""
        return f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {cls.COLORS['primary']}, stop:1 #42A5F5);
                border-radius: {cls.SIZES['border_radius_lg']};
                margin-bottom: 5px;
            }}

            QLabel {{
                color: {cls.COLORS['text_white']};
                margin: 0;
            }}
        """

    @classmethod
    def get_messagebox_style(cls):
        """获取消息框样式"""
        return f"""
            QMessageBox {{
                background-color: {cls.COLORS['white']};
                font-family: {cls.FONTS['primary']};
                font-size: 12px;
                border: {cls.SIZES['border_width']} solid {cls.COLORS['border']};
                border-radius: {cls.SIZES['border_radius_lg']};
            }}

            QMessageBox QLabel {{
                color: {cls.COLORS['text_primary']};
                font-size: 12px;
                padding: 10px;
            }}

            QMessageBox QPushButton {{
                background-color: {cls.COLORS['primary']};
                color: {cls.COLORS['text_white']};
                border: none;
                padding: 8px 20px;
                border-radius: {cls.SIZES['border_radius']};
                font-weight: bold;
                min-width: 80px;
                font-size: 11px;
            }}

            QMessageBox QPushButton:hover {{
                background-color: {cls.COLORS['primary_hover']};
            }}
        """

    @classmethod
    def get_button_variants(cls):
        """获取按钮变体样式"""
        return {
            'success': f"""
                QPushButton {{
                    background-color: {cls.COLORS['success']};
                    color: {cls.COLORS['text_white']};
                }}
                QPushButton:hover {{
                    background-color: #218838;
                }}
            """,

            'warning': f"""
                QPushButton {{
                    background-color: {cls.COLORS['warning']};
                    color: #212529;
                }}
                QPushButton:hover {{
                    background-color: #e0a800;
                }}
            """,

            'danger': f"""
                QPushButton {{
                    background-color: {cls.COLORS['danger']};
                    color: {cls.COLORS['text_white']};
                }}
                QPushButton:hover {{
                    background-color: #c82333;
                }}
            """,

            'secondary': f"""
                QPushButton {{
                    background-color: {cls.COLORS['gray_600']};
                    color: {cls.COLORS['text_white']};
                }}
                QPushButton:hover {{
                    background-color: {cls.COLORS['gray_700']};
                }}
            """,

            'outline': f"""
                QPushButton {{
                    background-color: transparent;
                    color: {cls.COLORS['primary']};
                    border: {cls.SIZES['border_width']} solid {cls.COLORS['primary']};
                }}
                QPushButton:hover {{
                    background-color: {cls.COLORS['primary']};
                    color: {cls.COLORS['text_white']};
                }}
            """
        }

    @classmethod
    def get_status_styles(cls):
        """获取状态样式"""
        return {
            'success': f"color: {cls.COLORS['success']};",
            'warning': f"color: {cls.COLORS['warning']};",
            'danger': f"color: {cls.COLORS['danger']};",
            'info': f"color: {cls.COLORS['info']};",
            'muted': f"color: {cls.COLORS['text_secondary']};",
        }


class ComponentStyles:
    """组件专用样式类"""

    @staticmethod
    def get_loading_spinner_style():
        """获取加载动画样式"""
        return """
            QLabel {
                border: 3px solid #f3f3f3;
                border-top: 3px solid #007bff;
                border-radius: 50%;
                width: 40px;
                height: 40px;
            }
        """

    @staticmethod
    def get_card_style():
        """获取卡片样式"""
        return f"""
            QFrame {{
                background-color: {AppStyles.COLORS['white']};
                border: 1px solid {AppStyles.COLORS['border']};
                border-radius: {AppStyles.SIZES['border_radius_lg']};
                padding: 15px;
                margin: 5px;
            }}

            QFrame:hover {{
                box-shadow: {AppStyles.SIZES['shadow_lg']};
                border-color: {AppStyles.COLORS['border_hover']};
            }}
        """

    @staticmethod
    def get_toolbar_style():
        """获取工具栏样式"""
        return f"""
            QFrame {{
                background-color: {AppStyles.COLORS['bg_secondary']};
                border: 1px solid {AppStyles.COLORS['border']};
                border-radius: {AppStyles.SIZES['border_radius']};
                padding: 8px;
                margin: 2px;
            }}
        """


class ThemeManager:
    """主题管理器"""

    def __init__(self):
        self.current_theme = 'light'
        self.themes = {
            'light': self._get_light_theme(),
            'dark': self._get_dark_theme()
        }

    def _get_light_theme(self):
        """获取浅色主题"""
        return AppStyles.COLORS

    def _get_dark_theme(self):
        """获取深色主题"""
        dark_colors = AppStyles.COLORS.copy()
        dark_colors.update({
            'bg_primary': '#2b2b2b',
            'bg_secondary': '#3c3c3c',
            'bg_tertiary': '#4d4d4d',
            'text_primary': '#ffffff',
            'text_secondary': '#cccccc',
            'border': '#555555',
            'white': '#2b2b2b',
        })
        return dark_colors

    def apply_theme(self, theme_name='light'):
        """应用主题"""
        if theme_name in self.themes:
            self.current_theme = theme_name
            AppStyles.COLORS = self.themes[theme_name]

    def get_current_theme_style(self):
        """获取当前主题样式"""
        return AppStyles.get_main_window_style()


# 辅助函数
def apply_button_style(button, variant='primary'):
    """应用按钮样式"""
    base_style = AppStyles.get_main_window_style()
    variants = AppStyles.get_button_variants()

    if variant in variants:
        button.setStyleSheet(variants[variant])
    else:
        button.setStyleSheet(base_style)


def apply_status_style(widget, status='info'):
    """应用状态样式"""
    status_styles = AppStyles.get_status_styles()
    if status in status_styles:
        current_style = widget.styleSheet()
        widget.setStyleSheet(current_style + status_styles[status])


def get_icon_text(icon_name):
    """获取图标文本（使用Unicode图标）"""
    icons = {
        'refresh': '🔄',
        'download': '⬇️',
        'check': '✅',
        'error': '❌',
        'warning': '⚠️',
        'info': 'ℹ️',
        'settings': '⚙️',
        'folder': '📁',
        'search': '🔍',
        'update': '🔄',
        'success': '✅',
        'loading': '⌛',
        'play': '▶️',
        'pause': '⏸️',
        'stop': '⏹️',
        'close': '❌',
        'minimize': '➖',
        'maximize': '⬜',
        'home': '🏠',
        'help': '❓',
        'save': '💾',
        'delete': '🗑️',
        'edit': '✏️',
        'add': '➕',
        'remove': '➖',
        'up': '⬆️',
        'down': '⬇️',
        'left': '⬅️',
        'right': '➡️',
    }
    return icons.get(icon_name, '●')


# 导出主要样式类
__all__ = [
    'AppStyles',
    'ComponentStyles',
    'ThemeManager',
    'apply_button_style',
    'apply_status_style',
    'get_icon_text'
]