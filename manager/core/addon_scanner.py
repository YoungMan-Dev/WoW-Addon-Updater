# manager/core/addon_scanner.py
import os
import re
from pathlib import Path


class AddonScanner:
    """插件扫描器"""

    def __init__(self):
        self.version_patterns = [
            r"##\s*Version\s*:\s*([^\s\n\r]+)",
            r"##\s*Title\s*:.*?([0-9]+\.[0-9]+(?:\.[0-9]+)?)",
            r"version\s*=\s*[\"']([^\"']+)[\"']",
            r"VERSION\s*=\s*[\"']([^\"']+)[\"']"
        ]

    def scan_addons(self, wow_path):
        """扫描指定路径下的插件"""
        from .wow_detector import WoWDetector

        detector = WoWDetector()
        addon_path = detector.get_addon_path(wow_path)

        if not addon_path or not os.path.exists(addon_path):
            return {}

        addons = {}
        addon_dir = Path(addon_path)

        for item in addon_dir.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                # 跳过一些系统目录
                if item.name.lower() in ['blizzard_', 'system']:
                    continue

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
        return bool(re.match(version_pattern, version))