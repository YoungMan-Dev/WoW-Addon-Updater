# updater/config/settings.py
import os
import configparser
from pathlib import Path


class Settings:
    """设置管理器"""

    def __init__(self):
        self.config_dir = Path.home() / '.wow_addon_updater'
        self.config_file = self.config_dir / 'config.ini'
        self.config = configparser.ConfigParser()

        self._ensure_config_dir()
        self._load_config()

    def _ensure_config_dir(self):
        """确保配置目录存在"""
        self.config_dir.mkdir(exist_ok=True)

    def _load_config(self):
        """加载配置"""
        if self.config_file.exists():
            self.config.read(self.config_file, encoding='utf-8')

        # 设置默认值
        if not self.config.has_section('General'):
            self.config.add_section('General')

        if not self.config.has_section('UpdateCodes'):
            self.config.add_section('UpdateCodes')

    def save_config(self):
        """保存配置"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            self.config.write(f)

    def get_wow_path(self):
        """获取WoW路径"""
        return self.config.get('General', 'wow_path', fallback='')

    def set_wow_path(self, path):
        """设置WoW路径"""
        self.config.set('General', 'wow_path', path)
        self.save_config()

    def get_update_codes(self):
        """获取更新码列表"""
        codes_str = self.config.get('UpdateCodes', 'codes', fallback='')
        if codes_str:
            return [code.strip() for code in codes_str.split(',') if code.strip()]
        return []

    def set_update_codes(self, codes):
        """设置更新码列表"""
        codes_str = ','.join(codes)
        self.config.set('UpdateCodes', 'codes', codes_str)
        self.save_config()

    def get_auto_check_updates(self):
        """获取自动检查更新设置"""
        return self.config.getboolean('General', 'auto_check_updates', fallback=True)

    def set_auto_check_updates(self, enabled):
        """设置自动检查更新"""
        self.config.set('General', 'auto_check_updates', str(enabled))
        self.save_config()