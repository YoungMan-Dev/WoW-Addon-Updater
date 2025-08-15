# tools/data_manager.py - 数据管理工具
"""
数据管理工具
用于管理服务器的JSON数据文件，提供命令行界面进行数据操作
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime
import argparse

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from shared.crypto_util import create_crypto_util
except ImportError:
    print("⚠️ 无法导入加密工具，某些功能可能不可用")
    create_crypto_util = None


class DataManager:
    """数据管理器"""

    def __init__(self, data_file=None):
        if data_file is None:
            data_file = project_root / 'server' / 'data' / 'addons.json'

        self.data_file = Path(data_file)
        self.token_file = self.data_file.parent / 'tokens.json'
        self.backup_dir = self.data_file.parent / 'backups'

        # 确保目录存在
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        self.data = {}
        self.tokens = set()

        # 加载数据
        self.load_data()
        self.load_tokens()

    def load_data(self):
        """加载数据"""
        try:
            if self.data_file.exists():
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
                print(f"✅ 加载了 {len(self.data)} 个插件数据")
            else:
                self.data = {}
                print("📄 数据文件不存在，将创建新文件")
        except Exception as e:
            print(f"❌ 加载数据失败: {e}")
            self.data = {}

    def save_data(self):
        """保存数据"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            print(f"💾 数据已保存到 {self.data_file}")
        except Exception as e:
            print(f"❌ 保存数据失败: {e}")

    def load_tokens(self):
        """加载token"""
        try:
            if self.token_file.exists():
                with open(self.token_file, 'r', encoding='utf-8') as f:
                    token_data = json.load(f)
                    self.tokens = set(token_data.get('tokens', []))
                print(f"🔑 加载了 {len(self.tokens)} 个token")
            else:
                self.tokens = set()
                print("🔑 Token文件不存在")
        except Exception as e:
            print(f"❌ 加载token失败: {e}")
            self.tokens = set()

    def save_tokens(self):
        """保存token"""
        try:
            token_data = {
                'tokens': list(self.tokens),
                'updated_at': datetime.now().isoformat()
            }
            with open(self.token_file, 'w', encoding='utf-8') as f:
                json.dump(token_data, f, ensure_ascii=False, indent=2)
            print(f"🔑 Token已保存到 {self.token_file}")
        except Exception as e:
            print(f"❌ 保存token失败: {e}")

    def list_addons(self):
        """列出所有插件"""
        if not self.data:
            print("📭 暂无插件数据")
            return

        print(f"\n📋 插件列表 (共 {len(self.data)} 个):")
        print("-" * 80)
        print(f"{'插件名称':<20} {'版本':<10} {'更新码':<10} {'创建时间':<20}")
        print("-" * 80)

        for name, info in self.data.items():
            created_at = info.get('created_at', 'N/A')[:19]  # 只显示日期时间部分
            print(f"{name:<20} {info.get('version', 'N/A'):<10} {info.get('update_code', 'N/A'):<10} {created_at:<20}")

    def add_addon(self, name, version, download_url, update_code=None):
        """添加插件"""
        if update_code is None:
            if create_crypto_util:
                crypto = create_crypto_util()
                update_code = crypto.generate_update_code()
            else:
                import random
                import string
                chars = string.ascii_uppercase + string.digits
                update_code = ''.join(random.choice(chars) for _ in range(8))

        current_time = datetime.now().isoformat()

        self.data[name] = {
            'version': version,
            'download_url': download_url,
            'update_code': update_code,
            'created_at': current_time,
            'updated_at': current_time
        }

        self.save_data()
        print(f"✅ 插件 '{name}' 添加成功，更新码: {update_code}")
        return update_code

    def update_addon(self, name, **kwargs):
        """更新插件信息"""
        if name not in self.data:
            print(f"❌ 插件 '{name}' 不存在")
            return False

        # 更新字段
        for key, value in kwargs.items():
            if key in ['version', 'download_url']:
                self.data[name][key] = value
                print(f"📝 更新 {key}: {value}")

        self.data[name]['updated_at'] = datetime.now().isoformat()
        self.save_data()
        print(f"✅ 插件 '{name}' 更新成功")
        return True

    def remove_addon(self, name):
        """删除插件"""
        if name not in self.data:
            print(f"❌ 插件 '{name}' 不存在")
            return False

        del self.data[name]
        self.save_data()
        print(f"🗑️ 插件 '{name}' 删除成功")
        return True

    def search_addon(self, keyword):
        """搜索插件"""
        results = []
        keyword_lower = keyword.lower()

        for name, info in self.data.items():
            if (keyword_lower in name.lower() or
                    keyword_lower in info.get('update_code', '').lower()):
                results.append((name, info))

        if results:
            print(f"\n🔍 搜索结果 (关键词: '{keyword}'):")
            print("-" * 60)
            for name, info in results:
                print(f"名称: {name}")
                print(f"版本: {info.get('version', 'N/A')}")
                print(f"更新码: {info.get('update_code', 'N/A')}")
                print(f"下载地址: {info.get('download_url', 'N/A')}")
                print("-" * 60)
        else:
            print(f"❌ 未找到包含 '{keyword}' 的插件")

    def backup_data(self):
        """备份数据"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.backup_dir / f"backup_{timestamp}.json"

        backup_data = {
            'addons': self.data,
            'tokens': list(self.tokens),
            'backup_time': datetime.now().isoformat(),
            'version': '1.0.0'
        }

        try:
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, ensure_ascii=False, indent=2)
            print(f"📦 备份已保存到: {backup_file}")
            return backup_file
        except Exception as e:
            print(f"❌ 备份失败: {e}")
            return None

    def restore_data(self, backup_file):
        """恢复数据"""
        backup_file = Path(backup_file)

        if not backup_file.exists():
            print(f"❌ 备份文件不存在: {backup_file}")
            return False

        try:
            with open(backup_file, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)

            # 恢复插件数据
            if 'addons' in backup_data:
                self.data = backup_data['addons']
                self.save_data()

            # 恢复token数据
            if 'tokens' in backup_data:
                self.tokens = set(backup_data['tokens'])
                self.save_tokens()

            print(f"🔄 数据恢复成功，恢复了 {len(self.data)} 个插件")
            return True

        except Exception as e:
            print(f"❌ 恢复失败: {e}")
            return False

    def list_backups(self):
        """列出所有备份"""
        backup_files = list(self.backup_dir.glob("backup_*.json"))

        if not backup_files:
            print("📭 暂无备份文件")
            return

        print(f"\n📦 备份文件列表 (共 {len(backup_files)} 个):")
        print("-" * 60)

        for backup_file in sorted(backup_files, reverse=True):
            try:
                stat = backup_file.stat()
                size = stat.st_size
                mtime = datetime.fromtimestamp(stat.st_mtime)

                print(f"文件: {backup_file.name}")
                print(f"时间: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"大小: {size} 字节")
                print("-" * 60)

            except Exception as e:
                print(f"❌ 读取备份文件信息失败: {e}")

    def export_csv(self, output_file=None):
        """导出CSV格式"""
        if output_file is None:
            output_file = self.data_file.parent / 'addons_export.csv'

        try:
            import csv

            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)

                # 写入表头
                writer.writerow(['插件名称', '版本', '下载地址', '更新码', '创建时间', '更新时间'])

                # 写入数据
                for name, info in self.data.items():
                    writer.writerow([
                        name,
                        info.get('version', ''),
                        info.get('download_url', ''),
                        info.get('update_code', ''),
                        info.get('created_at', ''),
                        info.get('updated_at', '')
                    ])

            print(f"📊 CSV文件已导出到: {output_file}")
            return True

        except Exception as e:
            print(f"❌ 导出CSV失败: {e}")
            return False

    def get_stats(self):
        """获取统计信息"""
        total_addons = len(self.data)
        total_tokens = len(self.tokens)

        # 统计最近创建的插件
        recent_addons = 0
        today = datetime.now().date()

        for info in self.data.values():
            try:
                created_date = datetime.fromisoformat(info.get('created_at', '')).date()
                if created_date == today:
                    recent_addons += 1
            except:
                pass

        print(f"\n📊 统计信息:")
        print("-" * 40)
        print(f"总插件数量: {total_addons}")
        print(f"有效Token数量: {total_tokens}")
        print(f"今日新增插件: {recent_addons}")
        print(f"数据文件大小: {self.data_file.stat().st_size if self.data_file.exists() else 0} 字节")
        print(f"数据文件路径: {self.data_file}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='WoW插件数据管理工具')
    parser.add_argument('--data-file', help='数据文件路径')

    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # 列表命令
    list_parser = subparsers.add_parser('list', help='列出所有插件')

    # 添加命令
    add_parser = subparsers.add_parser('add', help='添加插件')
    add_parser.add_argument('name', help='插件名称')
    add_parser.add_argument('version', help='插件版本')
    add_parser.add_argument('url', help='下载地址')
    add_parser.add_argument('--code', help='自定义更新码')

    # 更新命令
    update_parser = subparsers.add_parser('update', help='更新插件')
    update_parser.add_argument('name', help='插件名称')
    update_parser.add_argument('--version', help='新版本')
    update_parser.add_argument('--url', help='新下载地址')

    # 删除命令
    remove_parser = subparsers.add_parser('remove', help='删除插件')
    remove_parser.add_argument('name', help='插件名称')

    # 搜索命令
    search_parser = subparsers.add_parser('search', help='搜索插件')
    search_parser.add_argument('keyword', help='搜索关键词')

    # 备份命令
    backup_parser = subparsers.add_parser('backup', help='备份数据')

    # 恢复命令
    restore_parser = subparsers.add_parser('restore', help='恢复数据')
    restore_parser.add_argument('backup_file', help='备份文件路径')

    # 备份列表命令
    backups_parser = subparsers.add_parser('backups', help='列出备份文件')

    # 导出命令
    export_parser = subparsers.add_parser('export', help='导出CSV')
    export_parser.add_argument('--output', help='输出文件路径')

    # 统计命令
    stats_parser = subparsers.add_parser('stats', help='显示统计信息')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # 创建数据管理器
    dm = DataManager(args.data_file)

    # 执行命令
    try:
        if args.command == 'list':
            dm.list_addons()

        elif args.command == 'add':
            dm.add_addon(args.name, args.version, args.url, args.code)

        elif args.command == 'update':
            kwargs = {}
            if args.version:
                kwargs['version'] = args.version
            if args.url:
                kwargs['download_url'] = args.url

            if kwargs:
                dm.update_addon(args.name, **kwargs)
            else:
                print("❌ 请提供要更新的字段")

        elif args.command == 'remove':
            dm.remove_addon(args.name)

        elif args.command == 'search':
            dm.search_addon(args.keyword)

        elif args.command == 'backup':
            dm.backup_data()

        elif args.command == 'restore':
            dm.restore_data(args.backup_file)

        elif args.command == 'backups':
            dm.list_backups()

        elif args.command == 'export':
            dm.export_csv(args.output)

        elif args.command == 'stats':
            dm.get_stats()

    except KeyboardInterrupt:
        print("\n👋 操作已取消")
    except Exception as e:
        print(f"❌ 执行命令时出错: {e}")


if __name__ == '__main__':
    main()