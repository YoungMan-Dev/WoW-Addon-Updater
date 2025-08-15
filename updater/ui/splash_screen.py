# updater/ui/splash_screen.py - 使用assets图片版本
from PyQt5.QtWidgets import QSplashScreen, QLabel, QVBoxLayout, QWidget, QProgressBar
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QFont, QPainter, QLinearGradient, QColor, QBrush, QPen
import os
from pathlib import Path


class SplashScreen(QSplashScreen):
    def __init__(self):
        # 尝试加载assets中的启动图片
        pixmap = self.load_splash_image()
        super().__init__(pixmap, Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)

        # 根据图片大小设置窗口尺寸
        self.setFixedSize(pixmap.size())

        # 设置窗口属性
        if pixmap.hasAlphaChannel():
            self.setAttribute(Qt.WA_TranslucentBackground)

        # 初始化进度值
        self.progress_value = 0
        self.max_progress = 100
        self.loading_messages = [
            "正在初始化更新器...",
            "正在加载核心模块...",
            "正在检测游戏环境...",
            "正在准备用户界面...",
            "正在建立网络连接...",
            "启动完成！"
        ]
        self.current_message_index = 0

        # 显示初始消息
        self.update_message()

        # 启动进度定时器
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(80)  # 每80ms更新一次

    def load_splash_image(self):
        """加载启动图片 - 支持PyInstaller打包"""

        # 获取资源路径 - 兼容开发环境和打包后的exe
        def get_resource_path():
            """获取资源文件路径"""
            import sys

            if hasattr(sys, '_MEIPASS'):
                # PyInstaller打包后的临时目录
                base_path = Path(sys._MEIPASS)
                assets_path = base_path / 'assets'
                print(f"🔍 PyInstaller模式 - 资源路径: {assets_path}")
            else:
                # 开发环境
                current_dir = Path(__file__).parent.parent  # updater目录
                assets_path = current_dir / 'assets'
                print(f"🔍 开发模式 - 资源路径: {assets_path}")

            return assets_path

        assets_dir = get_resource_path()

        # 支持的图片格式
        image_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.gif', '.svg']

        # 可能的启动图片文件名
        possible_names = [
            'splash',
            'startup',
            'logo',
            'banner',
            'background',
            'splash_screen',
            'updater_splash',
            'wow_updater'
        ]

        print(f"🔍 在路径中查找启动图片: {assets_dir}")
        print(f"📁 assets目录存在: {assets_dir.exists()}")

        # 如果assets目录存在，列出所有文件
        if assets_dir.exists():
            try:
                files = list(assets_dir.iterdir())
                print(f"📁 assets目录中的文件: {[f.name for f in files]}")
            except Exception as e:
                print(f"❌ 无法读取assets目录: {e}")
                return self.create_default_splash_pixmap()
        else:
            print(f"❌ assets目录不存在: {assets_dir}")
            return self.create_default_splash_pixmap()

        # 尝试按优先级加载图片
        for name in possible_names:
            for ext in image_extensions:
                image_path = assets_dir / f"{name}{ext}"
                print(f"  📷 尝试加载: {image_path}")

                if image_path.exists():
                    try:
                        pixmap = QPixmap(str(image_path))
                        if not pixmap.isNull():
                            print(f"✅ 成功加载启动图片: {image_path}")
                            print(f"📐 图片尺寸: {pixmap.width()}x{pixmap.height()}")

                            # 如果图片太大，进行缩放
                            if pixmap.width() > 800 or pixmap.height() > 600:
                                pixmap = pixmap.scaled(800, 600, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                                print(f"📐 缩放后尺寸: {pixmap.width()}x{pixmap.height()}")

                            return pixmap
                    except Exception as e:
                        print(f"❌ 加载图片失败 {image_path}: {e}")
                        continue

        # 尝试加载目录中的任何图片文件
        try:
            if assets_dir.exists():
                for file in assets_dir.iterdir():
                    if file.suffix.lower() in image_extensions and file.is_file():
                        try:
                            pixmap = QPixmap(str(file))
                            if not pixmap.isNull():
                                print(f"✅ 加载到图片文件: {file}")

                                # 缩放处理
                                if pixmap.width() > 800 or pixmap.height() > 600:
                                    pixmap = pixmap.scaled(800, 600, Qt.KeepAspectRatio, Qt.SmoothTransformation)

                                return pixmap
                        except Exception as e:
                            print(f"❌ 加载 {file} 失败: {e}")
        except Exception as e:
            print(f"❌ 扫描assets目录失败: {e}")

        # 如果都失败了，创建默认图片
        print("⚠️ 未找到启动图片，使用默认图片")
        return self.create_default_splash_pixmap()

    def create_default_splash_pixmap(self):
        """创建默认启动图片"""
        pixmap = QPixmap(500, 350)
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing, True)

        # 绘制主背景渐变
        main_gradient = QLinearGradient(0, 0, 0, 350)
        main_gradient.setColorAt(0, QColor(33, 150, 243, 240))
        main_gradient.setColorAt(0.5, QColor(25, 118, 210, 250))
        main_gradient.setColorAt(1, QColor(13, 71, 161, 240))

        # 绘制圆角矩形背景
        painter.setBrush(QBrush(main_gradient))
        painter.setPen(QPen(QColor(255, 255, 255, 50), 2))
        painter.drawRoundedRect(10, 10, 480, 330, 20, 20)

        # 绘制标题文字
        painter.setPen(QColor(255, 255, 255, 255))

        # 主标题
        title_font = QFont("Arial", 28, QFont.Bold)
        painter.setFont(title_font)
        title_rect = painter.fontMetrics().boundingRect("WoW 插件更新器")
        title_x = (500 - title_rect.width()) // 2
        painter.drawText(title_x, 180, "WoW 插件更新器")

        # 副标题
        subtitle_font = QFont("Arial", 12)
        painter.setFont(subtitle_font)
        painter.setPen(QColor(255, 255, 255, 200))
        subtitle_text = "Addon Updater"
        subtitle_rect = painter.fontMetrics().boundingRect(subtitle_text)
        subtitle_x = (500 - subtitle_rect.width()) // 2
        painter.drawText(subtitle_x, 210, subtitle_text)

        painter.end()
        return pixmap

    def update_progress(self):
        """更新进度"""
        try:
            self.progress_value += 1.8

            if self.progress_value <= self.max_progress:
                self.update_message()

                # 根据进度更新消息
                message_index = min(int(self.progress_value / 20), len(self.loading_messages) - 2)
                if message_index != self.current_message_index:
                    self.current_message_index = message_index
            else:
                # 显示完成消息
                self.current_message_index = len(self.loading_messages) - 1
                self.update_message()

                # 延迟一下然后关闭
                self.timer.stop()
                QTimer.singleShot(500, self.close)

        except Exception as e:
            print(f"更新进度时出错: {e}")
            self.timer.stop()
            self.close()

    def update_message(self):
        """更新显示消息 - 无进度条版本"""
        try:
            # 获取当前消息
            current_message = self.loading_messages[self.current_message_index]

            # 只显示加载消息，不显示进度条和百分比
            message = current_message

            # 在图片底部显示消息
            self.showMessage(message,
                             Qt.AlignHCenter | Qt.AlignBottom,
                             QColor(255, 255, 255))

        except Exception as e:
            print(f"更新消息时出错: {e}")

    def mousePressEvent(self, event):
        """鼠标点击事件 - 允许点击跳过"""
        if event.button() == Qt.LeftButton:
            self.timer.stop()
            QTimer.singleShot(100, self.close)
        super().mousePressEvent(event)


class SimpleSplashScreen(QSplashScreen):
    """简化版启动画面 - 当assets图片不可用时使用"""

    def __init__(self):
        # 尝试从assets加载简单图片
        current_dir = Path(__file__).parent.parent
        assets_dir = current_dir / 'assets'

        # 尝试找到任何可用的图片
        pixmap = None
        if assets_dir.exists():
            for file in assets_dir.iterdir():
                if file.suffix.lower() in ['.png', '.jpg', '.jpeg', '.bmp']:
                    try:
                        test_pixmap = QPixmap(str(file))
                        if not test_pixmap.isNull():
                            pixmap = test_pixmap.scaled(400, 280, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                            break
                    except:
                        continue

        # 如果没有找到，创建默认图片
        if pixmap is None:
            pixmap = QPixmap(400, 280)
            pixmap.fill(QColor(33, 150, 243))

        super().__init__(pixmap, Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)

        self.setFixedSize(pixmap.size())

        # 显示静态消息
        self.showMessage("正在启动魔兽世界插件更新器...",
                         Qt.AlignHCenter | Qt.AlignBottom,
                         QColor(255, 255, 255))

        # 简单定时关闭
        QTimer.singleShot(2000, self.close)


def create_splash_screen():
    """创建启动画面工厂函数"""
    try:
        # 尝试创建完整版启动画面
        return SplashScreen()
    except Exception as e:
        print(f"创建完整启动画面失败: {e}")
        try:
            # fallback到简化版
            return SimpleSplashScreen()
        except Exception as e2:
            print(f"创建简化启动画面也失败: {e2}")
            # 最后的fallback - 无启动画面
            return None


# 调试函数 - 列出assets目录内容
def debug_assets_directory():
    """调试函数：列出assets目录中的所有文件"""
    current_dir = Path(__file__).parent.parent
    assets_dir = current_dir / 'assets'

    print(f"🔍 调试信息:")
    print(f"📁 当前文件路径: {Path(__file__)}")
    print(f"📁 updater目录: {current_dir}")
    print(f"📁 assets目录: {assets_dir}")
    print(f"📁 assets目录存在: {assets_dir.exists()}")

    if assets_dir.exists():
        files = list(assets_dir.iterdir())
        print(f"📁 assets目录中的文件:")
        for file in files:
            print(f"  - {file.name} ({'目录' if file.is_dir() else '文件'}) - {file.suffix}")
    else:
        print("❌ assets目录不存在")


if __name__ == "__main__":
    # 运行调试函数
    debug_assets_directory()

    # 测试启动画面
    from PyQt5.QtWidgets import QApplication

    app = QApplication([])
    splash = create_splash_screen()
    if splash:
        splash.show()
        app.exec_()