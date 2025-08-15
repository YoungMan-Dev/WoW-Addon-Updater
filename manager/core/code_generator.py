# manager/core/code_generator.py
import secrets
import string
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.constants import UPDATE_CODE_LENGTH


class CodeGenerator:
    """更新码生成器"""

    def __init__(self):
        # 排除容易混淆的字符
        self.chars = string.ascii_uppercase + string.digits
        self.exclude_chars = ['0', 'O', '1', 'I', 'L']
        self.available_chars = ''.join(
            c for c in self.chars if c not in self.exclude_chars
        )

    def generate_update_code(self):
        """生成8位更新码"""
        return ''.join(
            secrets.choice(self.available_chars)
            for _ in range(UPDATE_CODE_LENGTH)
        )

    def generate_multiple_codes(self, count):
        """生成多个更新码"""
        codes = set()
        while len(codes) < count:
            code = self.generate_update_code()
            codes.add(code)
        return list(codes)

    def validate_update_code(self, code):
        """验证更新码格式"""
        if not code or len(code) != UPDATE_CODE_LENGTH:
            return False

        return all(c in self.available_chars for c in code.upper())