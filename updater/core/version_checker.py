# updater/core/version_checker.py
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from .api_client import APIClient


class VersionChecker:
    """版本检查器"""

    def __init__(self):
        self.api_client = APIClient()

    def check_updates(self, local_addons, update_codes):
        """检查插件更新"""
        try:
            # 从服务器获取更新信息
            server_response = self.api_client.check_updates(local_addons, update_codes)

            if not server_response.get('success', False):
                raise Exception(server_response.get('message', '检查更新失败'))

            updates = server_response.get('updates', {})
            return updates

        except Exception as e:
            raise Exception(f"检查更新失败: {str(e)}")

    def compare_versions(self, version1, version2):
        """比较版本号
        返回值: 1 表示 version1 > version2
               0 表示 version1 = version2
              -1 表示 version1 < version2
        """

        def normalize_version(v):
            # 移除版本号中的非数字字符（保留点号）
            import re
            v = re.sub(r'[^\d\.]', '', v)
            parts = v.split('.')
            # 确保至少有3个部分
            while len(parts) < 3:
                parts.append('0')
            return [int(x) for x in parts[:3]]

        try:
            v1_parts = normalize_version(version1)
            v2_parts = normalize_version(version2)

            for i in range(3):
                if v1_parts[i] > v2_parts[i]:
                    return 1
                elif v1_parts[i] < v2_parts[i]:
                    return -1

            return 0
        except Exception:
            # 如果版本号格式无法解析，则进行字符串比较
            if version1 > version2:
                return 1
            elif version1 < version2:
                return -1
            else:
                return 0