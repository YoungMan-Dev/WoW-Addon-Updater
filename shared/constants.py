# shared/constants.py
"""
共享常量配置文件
"""

# API配置
API_BASE_URL = "http://localhost:5000/api"  # 修改为您的服务器地址
REQUEST_TIMEOUT = 30  # 请求超时时间（秒）

# 更新码配置
UPDATE_CODE_LENGTH = 8  # 更新码长度

# 魔兽世界相关配置
DEFAULT_WOW_PATHS = [
    r"C:\Program Files\World of Warcraft",
    r"C:\Program Files (x86)\World of Warcraft",
    r"D:\World of Warcraft",
    r"E:\World of Warcraft",
    r"C:\Games\World of Warcraft",
    r"D:\Games\World of Warcraft",
    r"C:\魔兽世界",
    r"D:\魔兽世界"
]

ADDON_FOLDER = "Interface/AddOns"  # 插件文件夹路径

# 应用程序配置
APP_NAME = "魔兽世界插件管理器"
APP_VERSION = "1.0.0"

# 默认管理员密码
DEFAULT_ADMIN_PASSWORD = "admin123"

# 文件配置
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
ALLOWED_ARCHIVE_EXTENSIONS = ['.zip', '.rar', '.7z']

# 网络配置
DOWNLOAD_CHUNK_SIZE = 8192  # 下载块大小
MAX_DOWNLOAD_RETRIES = 3  # 最大重试次数

# UI配置
DEFAULT_WINDOW_WIDTH = 1400
DEFAULT_WINDOW_HEIGHT = 900
DEFAULT_FONT_SIZE = 14

# 日志配置
LOG_FORMAT = "[{timestamp}] {message}"
LOG_DATE_FORMAT = "%H:%M:%S"

# 加密配置（需要实现 crypto_util.py）
ENCRYPTION_KEY_LENGTH = 32
ENCRYPTION_ALGORITHM = "AES"