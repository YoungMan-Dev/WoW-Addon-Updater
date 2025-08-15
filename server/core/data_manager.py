# server/core/data_manager.py
import json
import os
import threading
from datetime import datetime
from pathlib import Path


class DataManager:
    def __init__(self):
        self.data_file = Path(__file__).parent.parent / 'data' / 'addons.json'
        self.lock = threading.RLock()
        self._ensure_data_file()

    def _ensure_data_file(self):
        """确保数据文件存在"""
        self.data_file.parent.mkdir(exist_ok=True)
        if not self.data_file.exists():
            self._save_data({'addons': {}})

    def _load_data(self):
        """加载数据"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {'addons': {}}

    def _save_data(self, data):
        """保存数据"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def get_all_addons(self):
        """获取所有插件信息"""
        with self.lock:
            return self._load_data()['addons']

    def get_addon(self, addon_name):
        """获取单个插件信息"""
        with self.lock:
            addons = self._load_data()['addons']
            return addons.get(addon_name)

    def add_or_update_addon(self, addon_name, addon_info):
        """添加或更新插件"""
        with self.lock:
            data = self._load_data()
            current_time = datetime.now().isoformat()

            if addon_name in data['addons']:
                addon_info['created_at'] = data['addons'][addon_name].get('created_at', current_time)
                addon_info['updated_at'] = current_time
            else:
                addon_info['created_at'] = current_time
                addon_info['updated_at'] = current_time

            data['addons'][addon_name] = addon_info
            self._save_data(data)

    def delete_addon(self, addon_name):
        """删除插件"""
        with self.lock:
            data = self._load_data()
            if addon_name in data['addons']:
                del data['addons'][addon_name]
                self._save_data(data)
                return True
            return False

    def update_addon_url(self, addon_name, new_url):
        """更新插件下载地址"""
        with self.lock:
            data = self._load_data()
            if addon_name in data['addons']:
                data['addons'][addon_name]['download_url'] = new_url
                data['addons'][addon_name]['updated_at'] = datetime.now().isoformat()
                self._save_data(data)
                return True
            return False