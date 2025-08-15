# updater/core/wow_detector.py
import os
import winreg
from pathlib import Path
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.constants import DEFAULT_WOW_PATHS, ADDON_FOLDER


class WoWDetector:
    """魔兽世界路径检测器"""

    def __init__(self):
        self.wow_executable_names = [
            "Wow.exe", "WowClassic.exe", "WoW-64.exe",
            "World of Warcraft.exe", "魔兽世界.exe"
        ]

    def detect_wow_path(self):
        """自动检测魔兽世界安装路径"""
        # 1. 从注册表检测Battle.net安装的路径
        registry_path = self._detect_from_registry()
        if registry_path and self.validate_wow_path(registry_path):
            return registry_path

        # 2. 检查默认安装路径
        for default_path in DEFAULT_WOW_PATHS:
            if self.validate_wow_path(default_path):
                return default_path

        # 3. 搜索常见磁盘驱动器
        for drive in ['C:', 'D:', 'E:', 'F:']:
            search_paths = [
                f"{drive}\\Games\\World of Warcraft",
                f"{drive}\\Program Files\\World of Warcraft",
                f"{drive}\\Program Files (x86)\\World of Warcraft",
                f"{drive}\\魔兽世界",
                f"{drive}\\World of Warcraft"
            ]

            for path in search_paths:
                if self.validate_wow_path(path):
                    return path

        return None

    def _detect_from_registry(self):
        """从注册表检测Battle.net游戏路径"""
        try:
            # Battle.net注册表路径
            registry_paths = [
                r"SOFTWARE\WOW6432Node\Blizzard Entertainment\World of Warcraft",
                r"SOFTWARE\Blizzard Entertainment\World of Warcraft",
                r"SOFTWARE\WOW6432Node\暴雪娱乐\魔兽世界",
                r"SOFTWARE\暴雪娱乐\魔兽世界"
            ]

            for reg_path in registry_paths:
                try:
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path) as key:
                        install_path, _ = winreg.QueryValueEx(key, "InstallPath")
                        if self.validate_wow_path(install_path):
                            return install_path
                except (FileNotFoundError, OSError):
                    continue

            # 尝试从Battle.net客户端配置检测
            battle_net_config = self._get_battle_net_config()
            if battle_net_config:
                return battle_net_config

        except Exception as e:
            print(f"注册表检测失败: {e}")

        return None

    def _get_battle_net_config(self):
        """从Battle.net配置文件获取游戏路径"""
        try:
            programdata_path = os.environ.get('PROGRAMDATA', 'C:\\ProgramData')
            battle_net_path = os.path.join(programdata_path, 'Battle.net')

            # 查找Battle.net配置文件
            config_files = [
                os.path.join(battle_net_path, 'Agent', 'product.db'),
                os.path.join(battle_net_path, 'setup.ini')
            ]

            for config_file in config_files:
                if os.path.exists(config_file):
                    # 这里可以添加解析配置文件的逻辑
                    # 由于Battle.net配置比较复杂，这里简化处理
                    pass
        except Exception:
            pass

        return None

    def validate_wow_path(self, path):
        """验证路径是否为有效的魔兽世界安装目录"""
        if not path or not os.path.exists(path):
            return False

        path = Path(path)

        # 检查是否存在魔兽世界可执行文件
        for exe_name in self.wow_executable_names:
            exe_path = path / exe_name
            if exe_path.exists():
                # 进一步检查是否存在AddOns目录
                addons_path = path / ADDON_FOLDER
                if addons_path.exists() or addons_path.parent.exists():
                    return True

        return False

    def get_addon_path(self, wow_path):
        """获取插件安装路径"""
        if not wow_path:
            return None

        addon_path = Path(wow_path) / ADDON_FOLDER
        addon_path.mkdir(parents=True, exist_ok=True)
        return str(addon_path)