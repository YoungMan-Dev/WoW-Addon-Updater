# updater/core/addon_manager.py
import os
import re
from pathlib import Path
import configparser


class AddonManager:
    """插件管理器"""

    def __init__(self):
        self.version_patterns = [
            r"##\s*Version\s*:\s*([^\s\n\r]+)",
            r"##\s*Title\s*:.*?([0-9]+\.[0-9]+(?:\.[0-9]+)?)",
            r"version\s*=\s*[\"']([^\"']+)[\"']",
            r"VERSION\s*=\s*[\"']([^\"']+)[\"']"
        ]

    def get_local_addons(self, wow_path):
        """获取本地安装的插件列表"""
        from .wow_detector import WoWDetector

        detector = WoWDetector()
        addon_path = detector.get_addon_path(wow_path)

        if not addon_path or not os.path.exists(addon_path):
            return {}

        addons = {}
        addon_dir = Path(addon_path)

        for item in addon_dir.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                version = self._get_addon_version(item)
                if version:
                    addons[item.name] = version

        return addons

    def _get_addon_version(self, addon_dir):
        """获取插件版本号"""
        # 查找.toc文件
        toc_files = list(addon_dir.glob("*.toc"))

        for toc_file in toc_files:
            try:
                with open(toc_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                # 尝试匹配版本号
                for pattern in self.version_patterns:
                    match = re.search(pattern, content, re.IGNORECASE)
                    if match:
                        version = match.group(1).strip()
                        if self._is_valid_version(version):
                            return version
            except Exception:
                continue

        # 如果找不到版本信息，返回默认版本
        return "1.0.0"

    def _is_valid_version(self, version):
        """验证版本号格式"""
        version_pattern = r'^\d+\.\d+(?:\.\d+)?(?:[-+].*)?$'
        return re.match(version_pattern, version) is not None

    def backup_addon(self, addon_path):
        """备份插件"""
        try:
            backup_path = f"{addon_path}.backup"
            if os.path.exists(backup_path):
                import shutil
                shutil.rmtree(backup_path)

            import shutil
            shutil.copytree(addon_path, backup_path)
            return True
        except Exception as e:
            print(f"备份插件失败: {e}")
            return False

    def restore_addon(self, addon_path):
        """恢复插件备份"""
        try:
            backup_path = f"{addon_path}.backup"
            if not os.path.exists(backup_path):
                return False

            if os.path.exists(addon_path):
                import shutil
                shutil.rmtree(addon_path)

            import shutil
            shutil.copytree(backup_path, addon_path)
            shutil.rmtree(backup_path)
            return True
        except Exception as e:
            print(f"恢复插件失败: {e}")
            return False
