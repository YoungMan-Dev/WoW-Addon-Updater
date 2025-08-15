# server / local_server.py - 支持加密传输和JSON文件存储(改进版)
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
import uuid
import sys
import os
import json
from pathlib import Path
import threading
import re
import requests
from urllib.parse import urlparse

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 导入加密工具
from shared.crypto_util import CryptoUtil

app = Flask(__name__)
CORS(app)

# 初始化加密工具
crypto = CryptoUtil()

# JSON数据文件路径
DATA_FILE = Path(__file__).parent / 'data' / 'addons.json'
TOKEN_FILE = Path(__file__).parent / 'data' / 'tokens.json'
# 线程锁，确保文件操作的线程安全
file_lock = threading.Lock()


class URLValidator:
    """URL验证和转换工具"""

    @staticmethod
    def is_valid_url(url):
        """验证URL格式"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False

    @staticmethod
    def is_direct_download_url(url):
        """检查是否为直链下载"""
        if not url:
            return False

        # 检查常见直链特征
        direct_indicators = [
            '.zip',
            '.rar',
            '.7z',
            'download.php',
            'dl=1',  # Dropbox
            'raw=1',  # GitHub
            '/d/',  # Google Drive (需转换)
            'lanzou',  # 蓝奏云
            'ctfile',  # 城通网盘
        ]

        return any(indicator in url.lower() for indicator in direct_indicators)

    @staticmethod
    def convert_to_direct_url(url):
        """转换为直链"""
        if not url:
            return url, "URL为空"

        original_url = url

        try:
            # 蓝奏云特殊处理
            if 'lanzou' in url or 'lanzoui' in url or 'lanzoup' in url or 'lanzoux' in url:
                return url, "蓝奏云链接需要特殊处理，建议使用其他网盘服务"

            # Dropbox转换
            if 'dropbox.com' in url:
                if 'dl=0' in url:
                    url = url.replace('dl=0', 'dl=1')
                    return url, "已转换Dropbox直链"
                elif '?dl=1' not in url and 'dl=1' not in url:
                    url = url + ('&' if '?' in url else '?') + 'dl=1'
                    return url, "已添加Dropbox直链参数"

            # Google Drive转换
            if 'drive.google.com' in url:
                # 提取文件ID
                file_id_match = re.search(r'/d/([a-zA-Z0-9-_]+)', url)
                if file_id_match:
                    file_id = file_id_match.group(1)
                    direct_url = f"https://drive.google.com/uc?export=download&id={file_id}"
                    return direct_url, "已转换Google Drive直链"
                else:
                    return url, "无法解析Google Drive文件ID"

            # OneDrive转换
            if 'onedrive' in url or '1drv.ms' in url:
                if 'download=1' not in url:
                    url = url + ('&' if '?' in url else '?') + 'download=1'
                    return url, "已添加OneDrive直链参数"

            # 如果包含常见文件扩展名，认为是直链
            if any(ext in url.lower() for ext in ['.zip', '.rar', '.7z']):
                return url, "检测到文件扩展名，认为是直链"

            # 其他情况返回原URL
            return url, "保持原始URL"

        except Exception as e:
            return original_url, f"转换失败: {str(e)}"

    @staticmethod
    def test_download_url(url, timeout=10):
        """测试下载链接有效性"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }

            # 蓝奏云链接特殊处理
            if any(domain in url.lower() for domain in ['lanzou', 'lanzoui', 'lanzoup', 'lanzoux']):
                return False, "蓝奏云链接需要浏览器访问，无法直接下载"

            # 发送HEAD请求测试
            response = requests.head(url, headers=headers, timeout=timeout, allow_redirects=True)

            # 如果HEAD失败，尝试GET前几个字节
            if response.status_code != 200:
                response = requests.get(url, headers=headers, timeout=timeout, stream=True)
                # 只读取前1024字节用于测试
                content = next(response.iter_content(1024), b'')
                response.close()

            content_type = response.headers.get('content-type', '').lower()
            content_length = response.headers.get('content-length', '0')

            # 检查是否为HTML页面（通常表示不是直链）
            if 'text/html' in content_type:
                return False, "链接返回HTML页面，不是直接下载链接"

            # 检查是否为文件下载
            if any(indicator in content_type for indicator in
                   ['application/zip', 'application/octet-stream', 'application/x-zip']):
                return True, f"有效的下载链接 (类型: {content_type}, 大小: {content_length} bytes)"

            # 检查Content-Disposition头
            content_disposition = response.headers.get('content-disposition', '')
            if 'attachment' in content_disposition.lower():
                return True, f"有效的下载链接 (附件下载, 大小: {content_length} bytes)"

            # 其他情况，可能是有效的
            return True, f"可能有效的链接 (类型: {content_type})"

        except requests.exceptions.Timeout:
            return False, "连接超时"
        except requests.exceptions.ConnectionError:
            return False, "连接失败"
        except requests.exceptions.RequestException as e:
            return False, f"请求失败: {str(e)}"
        except Exception as e:
            return False, f"测试失败: {str(e)}"


class JSONStorage:
    """JSON文件存储管理器"""

    def __init__(self, data_file, token_file):
        self.data_file = Path(data_file)
        self.token_file = Path(token_file)
        self.addon_storage = {}
        self.valid_tokens = set()

        # 确保目录存在
        self.data_file.parent.mkdir(parents=True, exist_ok=True)

        # 加载数据
        self.load_data()
        self.load_tokens()

    def load_data(self):
        """从JSON文件加载插件数据"""
        try:
            if self.data_file.exists():
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.addon_storage = json.load(f)
                print(f"✅ 从 {self.data_file} 加载了 {len(self.addon_storage)} 个插件")
            else:
                # 创建默认数据，使用真实的示例URL
                self.addon_storage = {
                    'TestAddon': {
                        'version': '1.0.0',
                        'download_url': 'https://github.com/example/TestAddon/archive/refs/heads/main.zip',
                        'update_code': 'TEST1234',
                        'created_at': '2025-08-14T10:00:00',
                        'updated_at': '2025-08-14T10:00:00',
                        'url_status': 'unknown'
                    }
                }
                self.save_data()
                print(f"📄 创建默认数据文件: {self.data_file}")
        except Exception as e:
            print(f"❌ 加载数据文件失败: {e}")
            self.addon_storage = {}

    def save_data(self):
        """保存插件数据到JSON文件"""
        try:
            with file_lock:
                with open(self.data_file, 'w', encoding='utf-8') as f:
                    json.dump(self.addon_storage, f, ensure_ascii=False, indent=2)
                print(f"💾 数据已保存到 {self.data_file}")
        except Exception as e:
            print(f"❌ 保存数据文件失败: {e}")

    def load_tokens(self):
        """从JSON文件加载有效token"""
        try:
            if self.token_file.exists():
                with open(self.token_file, 'r', encoding='utf-8') as f:
                    token_data = json.load(f)
                    self.valid_tokens = set(token_data.get('tokens', []))
                print(f"🔑 加载了 {len(self.valid_tokens)} 个有效token")
            else:
                self.valid_tokens = set()
                self.save_tokens()
        except Exception as e:
            print(f"❌ 加载token文件失败: {e}")
            self.valid_tokens = set()

    def save_tokens(self):
        """保存有效token到JSON文件"""
        try:
            with file_lock:
                token_data = {
                    'tokens': list(self.valid_tokens),
                    'updated_at': datetime.now().isoformat()
                }
                with open(self.token_file, 'w', encoding='utf-8') as f:
                    json.dump(token_data, f, ensure_ascii=False, indent=2)
                print(f"🔑 Token已保存到 {self.token_file}")
        except Exception as e:
            print(f"❌ 保存token文件失败: {e}")

    def add_addon(self, addon_name, version, download_url, update_code):
        """添加插件"""
        current_time = datetime.now().isoformat()

        # 验证和转换URL
        converted_url, url_message = URLValidator.convert_to_direct_url(download_url)
        is_valid, test_message = URLValidator.test_download_url(converted_url)

        self.addon_storage[addon_name] = {
            'version': version,
            'download_url': converted_url,
            'original_url': download_url,
            'update_code': update_code,
            'created_at': current_time,
            'updated_at': current_time,
            'url_conversion': url_message,
            'url_status': 'valid' if is_valid else 'invalid',
            'url_test_message': test_message
        }

        self.save_data()
        print(f"📝 插件 {addon_name} 已添加")
        print(f"🔗 URL转换: {url_message}")
        print(f"✅ URL测试: {test_message}")

    def update_addon_url(self, addon_name, new_url):
        """更新插件下载地址"""
        if addon_name in self.addon_storage:
            # 验证和转换新URL
            converted_url, url_message = URLValidator.convert_to_direct_url(new_url)
            is_valid, test_message = URLValidator.test_download_url(converted_url)

            self.addon_storage[addon_name]['download_url'] = converted_url
            self.addon_storage[addon_name]['original_url'] = new_url
            self.addon_storage[addon_name]['updated_at'] = datetime.now().isoformat()
            self.addon_storage[addon_name]['url_conversion'] = url_message
            self.addon_storage[addon_name]['url_status'] = 'valid' if is_valid else 'invalid'
            self.addon_storage[addon_name]['url_test_message'] = test_message

            self.save_data()
            print(f"📝 插件 {addon_name} URL已更新")
            print(f"🔗 URL转换: {url_message}")
            print(f"✅ URL测试: {test_message}")
            return True
        return False

    def delete_addon(self, addon_name):
        """删除插件"""
        if addon_name in self.addon_storage:
            del self.addon_storage[addon_name]
            self.save_data()
            return True
        return False

    def add_token(self, token):
        """添加有效token"""
        self.valid_tokens.add(token)
        self.save_tokens()

    def verify_token(self, token):
        """验证token"""
        return token in self.valid_tokens

    def get_addon_count(self):
        """获取插件数量"""
        return len(self.addon_storage)

    def get_token_count(self):
        """获取有效token数量"""
        return len(self.valid_tokens)

    def get_all_addons(self):
        """获取所有插件"""
        return self.addon_storage.copy()

    def addon_exists(self, addon_name):
        """检查插件是否存在"""
        return addon_name in self.addon_storage

    def validate_all_urls(self):
        """验证所有插件的URL"""
        print("🔍 开始验证所有插件URL...")
        for addon_name, addon_info in self.addon_storage.items():
            url = addon_info.get('download_url')
            if url:
                is_valid, test_message = URLValidator.test_download_url(url)
                self.addon_storage[addon_name]['url_status'] = 'valid' if is_valid else 'invalid'
                self.addon_storage[addon_name]['url_test_message'] = test_message
                self.addon_storage[addon_name]['last_checked'] = datetime.now().isoformat()
                print(f"📋 {addon_name}: {'✅' if is_valid else '❌'} {test_message}")

        self.save_data()
        print("✅ URL验证完成")


# 初始化存储管理器
storage = JSONStorage(DATA_FILE, TOKEN_FILE)


def generate_token():
    """生成调试token"""
    token = f"debug-token-{uuid.uuid4().hex[:8]}"
    storage.add_token(token)
    return token


def safe_decrypt(request_data):
    """安全解密函数，支持明文和加密数据"""
    try:
        print(f"📥 收到请求数据类型: {type(request_data)}")
        print(f"📥 收到请求数据: {request_data}")

        # 检查是否为加密数据
        if isinstance(request_data, dict) and 'encrypted_data' in request_data:
            print("🔒 检测到加密数据，开始解密...")
            try:
                decrypted = crypto.decrypt_request(request_data)
                print(f"✅ 解密成功: {decrypted}")

                # 检查解密是否有错误
                if isinstance(decrypted, dict) and 'error' not in decrypted:
                    return decrypted, True
                else:
                    print(f"⚠️ 解密结果有错误: {decrypted}")
                    # 解密失败，fallback到明文
                    return request_data, False

            except Exception as e:
                print(f"❌ 解密异常: {e}")
                import traceback
                traceback.print_exc()
                # 解密失败，fallback到明文
                return request_data, False
        else:
            print("📝 检测到明文数据")
            return request_data, False

    except Exception as e:
        print(f"💥 数据处理异常: {e}")
        return request_data, False


def safe_encrypt_response(data, force_plaintext=False):
    """安全加密响应函数"""
    try:
        print(f"📤 准备响应数据: {data}")

        if force_plaintext:
            print("📝 强制使用明文响应")
            return data

        # 尝试加密响应
        try:
            encrypted = crypto.encrypt_request(data)
            if isinstance(encrypted, dict) and 'error' not in encrypted:
                print("✅ 响应已加密")
                return encrypted
            else:
                print("⚠️ 响应加密失败，返回明文")
                return data
        except Exception as encrypt_error:
            print(f"⚠️ 响应加密异常: {encrypt_error}")
            return data

    except Exception as e:
        print(f"💥 响应处理异常: {e}")
        return data


# 新增URL验证和测试接口
@app.route('/api/admin/validate_urls', methods=['POST'])
def validate_urls():
    """验证所有插件URL"""
    try:
        # 检查授权
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            if not storage.verify_token(token):
                return jsonify({'success': False, 'message': '无效token'}), 401

        storage.validate_all_urls()

        response_data = {
            'success': True,
            'message': 'URL验证完成',
            'addons': storage.get_all_addons()
        }

        final_response = safe_encrypt_response(response_data)
        return jsonify(final_response)

    except Exception as e:
        print(f"❌ 验证URL异常: {e}")
        return jsonify({
            'success': False,
            'message': f'服务器错误: {str(e)}'
        }), 500


@app.route('/api/admin/test_url', methods=['POST'])
def test_url(addon_name=None):
    """测试单个URL"""
    try:
        # 检查授权
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            if not storage.verify_token(token):
                return jsonify({'success': False, 'message': '无效token'}), 401

        request_data = request.get_json()

        # 解密请求数据
        data, was_encrypted = safe_decrypt(request_data)
        print(f"📋 解析的数据: {data}")

        new_url = data.get('download_url')
        if not new_url:
            print("❌ 下载地址为空")

            error_response = {
                'success': False,
                'message': '下载地址不能为空'
            }

            final_response = safe_encrypt_response(error_response, force_plaintext=not was_encrypted)
            return jsonify(final_response), 400

        if storage.update_addon_url(addon_name, new_url):
            print(f"✅ 插件 {addon_name} URL更新成功并保存到文件")

            # 获取更新后的URL信息
            addon_info = storage.addon_storage.get(addon_name, {})

            response_data = {
                'success': True,
                'message': '下载地址更新成功',
                'url_info': {
                    'original_url': addon_info.get('original_url'),
                    'converted_url': addon_info.get('download_url'),
                    'conversion_message': addon_info.get('url_conversion'),
                    'url_status': addon_info.get('url_status'),
                    'test_message': addon_info.get('url_test_message')
                }
            }

            # 根据请求是否加密来决定响应格式
            final_response = safe_encrypt_response(response_data, force_plaintext=not was_encrypted)
            return jsonify(final_response)
        else:
            print(f"❌ 插件 {addon_name} 不存在")

            error_response = {
                'success': False,
                'message': '插件不存在'
            }

            final_response = safe_encrypt_response(error_response, force_plaintext=not was_encrypted)
            return jsonify(final_response), 404

    except Exception as e:
        print(f"❌ 更新插件URL异常: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'服务器错误: {str(e)}'
        }), 500


@app.route('/api/admin/backup', methods=['GET'])
def backup_data():
    """备份数据"""
    try:
        # 检查授权
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            if not storage.verify_token(token):
                return jsonify({'success': False, 'message': '无效token'}), 401

        backup_data = {
            'addons': storage.get_all_addons(),
            'tokens': list(storage.valid_tokens),
            'backup_time': datetime.now().isoformat(),
            'version': '1.0.1'
        }

        print(f"📦 生成备份数据，包含 {storage.get_addon_count()} 个插件")

        response_data = {
            'success': True,
            'backup_data': backup_data
        }

        final_response = safe_encrypt_response(response_data)
        return jsonify(final_response)

    except Exception as e:
        print(f"❌ 备份数据异常: {e}")
        return jsonify({
            'success': False,
            'message': f'服务器错误: {str(e)}'
        }), 500


@app.route('/api/admin/restore', methods=['POST'])
def restore_data():
    """恢复数据"""
    try:
        # 检查授权
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            if not storage.verify_token(token):
                return jsonify({'success': False, 'message': '无效token'}), 401

        request_data = request.get_json()
        data, was_encrypted = safe_decrypt(request_data)

        backup_data = data.get('backup_data')
        if not backup_data:
            error_response = {
                'success': False,
                'message': '备份数据不能为空'
            }
            final_response = safe_encrypt_response(error_response, force_plaintext=not was_encrypted)
            return jsonify(final_response), 400

        # 恢复插件数据
        if 'addons' in backup_data:
            storage.addon_storage = backup_data['addons']
            storage.save_data()

        # 恢复token数据
        if 'tokens' in backup_data:
            storage.valid_tokens = set(backup_data['tokens'])
            storage.save_tokens()

        print(f"🔄 数据恢复完成，包含 {storage.get_addon_count()} 个插件")

        response_data = {
            'success': True,
            'message': '数据恢复成功',
            'addons_count': storage.get_addon_count(),
            'tokens_count': storage.get_token_count()
        }

        final_response = safe_encrypt_response(response_data, force_plaintext=not was_encrypted)
        return jsonify(final_response)

    except Exception as e:
        print(f"❌ 恢复数据异常: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'服务器错误: {str(e)}'
        }), 500


@app.route('/api/debug/decrypt', methods=['POST'])
def debug_decrypt():
    """调试解密接口"""
    try:
        request_data = request.get_json()
        print(f"🔍 调试解密请求: {request_data}")

        data, was_encrypted = safe_decrypt(request_data)

        return jsonify({
            'success': True,
            'original_data': request_data,
            'decrypted_data': data,
            'was_encrypted': was_encrypted
        })

    except Exception as e:
        print(f"❌ 调试解密异常: {e}")
        return jsonify({
            'success': False,
            'message': f'调试失败: {str(e)}'
        }), 500


@app.route('/api/debug/storage', methods=['GET'])
def debug_storage():
    """调试存储状态"""
    try:
        return jsonify({
            'success': True,
            'storage_info': {
                'data_file': str(DATA_FILE),
                'token_file': str(TOKEN_FILE),
                'data_file_exists': DATA_FILE.exists(),
                'token_file_exists': TOKEN_FILE.exists(),
                'data_file_size': DATA_FILE.stat().st_size if DATA_FILE.exists() else 0,
                'token_file_size': TOKEN_FILE.stat().st_size if TOKEN_FILE.exists() else 0,
                'addons_count': storage.get_addon_count(),
                'tokens_count': storage.get_token_count(),
                'addon_names': list(storage.addon_storage.keys())
            }
        })
    except Exception as e:
        print(f"❌ 调试存储异常: {e}")
        return jsonify({
            'success': False,
            'message': f'调试失败: {str(e)}'
        }), 500


@app.route('/api/updater/verify_code', methods=['POST'])
def verify_update_code():
    """验证更新码 - 供更新器使用（调试增强版）"""
    try:
        print("=" * 60)
        print("📥 收到更新码验证请求")
        request_data = request.get_json()
        print(f"📨 原始请求数据: {request_data}")

        # 解密请求数据
        data, was_encrypted = safe_decrypt(request_data)
        print(f"🔓 解密后数据: {data}")
        print(f"🔒 是否加密传输: {was_encrypted}")

        if not isinstance(data, dict):
            print("❌ 数据格式错误，不是字典类型")
            error_response = {
                'success': False,
                'message': '数据格式错误'
            }
            final_response = safe_encrypt_response(error_response, force_plaintext=not was_encrypted)
            return jsonify(final_response), 400

        # 获取参数
        addon_name = data.get('addon_name', 'unknown')
        update_code = data.get('update_code')
        update_codes = data.get('update_codes', [])

        # 支持单个更新码
        if update_code and update_code not in update_codes:
            update_codes.append(update_code)

        print(f"🎮 请求插件名: {addon_name}")
        print(f"🔑 要验证的更新码: {update_codes}")

        if not update_codes:
            print("❌ 没有提供更新码")
            error_response = {
                'success': False,
                'message': '更新码不能为空'
            }
            final_response = safe_encrypt_response(error_response, force_plaintext=not was_encrypted)
            return jsonify(final_response), 400

        # 显示当前服务器数据
        print(f"📦 服务器插件数据:")
        for name, info in storage.addon_storage.items():
            print(
                f"  - {name}: 版本={info.get('version')}, 更新码={info.get('update_code')}, URL状态={info.get('url_status', 'unknown')}")

        # 验证更新码
        valid_codes = []
        invalid_codes = []
        addon_info = {}

        for code in update_codes:
            print(f"🔍 正在验证更新码: {code}")
            is_valid = False

            # 在所有插件中查找匹配的更新码
            for name, info in storage.addon_storage.items():
                server_code = info.get('update_code')
                print(f"  📋 检查插件 '{name}' 的更新码: '{server_code}' == '{code}' ?")

                if server_code == code:
                    is_valid = True
                    addon_info[code] = {
                        'addon_name': name,
                        'version': info.get('version'),
                        'download_url': info.get('download_url'),
                        'original_url': info.get('original_url'),
                        'updated_at': info.get('updated_at', ''),
                        'created_at': info.get('created_at', ''),
                        'url_status': info.get('url_status', 'unknown'),
                        'url_test_message': info.get('url_test_message', ''),
                        'url_conversion': info.get('url_conversion', '')
                    }
                    valid_codes.append(code)
                    print(f"  ✅ 找到匹配! 插件: {name}, URL状态: {info.get('url_status', 'unknown')}")
                    break

            if not is_valid:
                invalid_codes.append(code)
                print(f"  ❌ 未找到匹配的插件")

        # 构建响应
        response_data = {
            'success': True,
            'message': f'验证完成: {len(valid_codes)} 个有效, {len(invalid_codes)} 个无效',
            'valid': len(valid_codes) > 0,
            'valid_codes': valid_codes,
            'invalid_codes': invalid_codes,
            'addon_info': addon_info,
            'total_checked': len(update_codes),
            'valid_count': len(valid_codes),
            'invalid_count': len(invalid_codes),
            # 调试信息
            'debug_info': {
                'request_addon_name': addon_name,
                'server_addons': list(storage.addon_storage.keys()),
                'server_codes': [info.get('update_code') for info in storage.addon_storage.values()],
                'was_encrypted': was_encrypted
            }
        }

        print(f"📤 验证结果:")
        print(f"  ✅ 有效更新码: {valid_codes}")
        print(f"  ❌ 无效更新码: {invalid_codes}")
        print(f"  📋 插件信息: {addon_info}")
        print("=" * 60)

        # 根据请求是否加密来决定响应格式
        final_response = safe_encrypt_response(response_data, force_plaintext=not was_encrypted)
        return jsonify(final_response)

    except Exception as e:
        print(f"❌ 验证更新码异常: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'服务器错误: {str(e)}'
        }), 500


@app.route('/api/updater/check_updates', methods=['POST'])
def check_updates():
    """检查插件更新 - 供更新器使用"""
    try:
        print("📥 收到检查更新请求")
        request_data = request.get_json()

        # 解密请求数据
        data, was_encrypted = safe_decrypt(request_data)
        print(f"📋 解析的数据: {data}")

        if not isinstance(data, dict):
            error_response = {
                'success': False,
                'message': '数据格式错误'
            }
            final_response = safe_encrypt_response(error_response, force_plaintext=not was_encrypted)
            return jsonify(final_response), 400

        # 获取参数
        local_addons = data.get('local_addons', {})  # 本地插件列表 {name: version}
        update_codes = data.get('update_codes', [])  # 有效的更新码列表

        print(f"🔍 检查更新: 本地插件={len(local_addons)}, 更新码={len(update_codes)}")
        print(f"📋 本地插件列表: {list(local_addons.keys())}")
        print(f"🔑 有效更新码: {update_codes}")

        if not update_codes:
            error_response = {
                'success': False,
                'message': '未提供有效的更新码'
            }
            final_response = safe_encrypt_response(error_response, force_plaintext=not was_encrypted)
            return jsonify(final_response), 400

        # 检查哪些插件可以更新
        updates = {}
        matched_pairs = []  # 记录匹配的插件对

        for addon_name, local_version in local_addons.items():
            print(f"🔍 检查本地插件: {addon_name} (版本: {local_version})")

            # 在服务器数据中查找匹配的插件
            best_match = None
            exact_match = False

            for server_name, server_info in storage.addon_storage.items():
                server_code = server_info.get('update_code')

                # 只检查有效更新码的插件
                if server_code not in update_codes:
                    continue

                print(f"  📋 对比服务器插件: {server_name}")

                # 优先精确匹配
                if addon_name.lower() == server_name.lower():
                    best_match = (server_name, server_info)
                    exact_match = True
                    print(f"  ✅ 找到精确匹配: {addon_name} == {server_name}")
                    break

                # 如果没有精确匹配，才考虑包含关系，但要更严格
                elif not exact_match:
                    # 检查是否为合理的包含关系（避免MeetingStone匹配MeetingStoneEx的情况）
                    if (addon_name.lower() in server_name.lower() and
                            len(addon_name) >= len(server_name) * 0.8):  # 长度相似度检查
                        if not best_match:  # 只在没有更好匹配时使用
                            best_match = (server_name, server_info)
                            print(f"  ⚠️ 找到部分匹配: {addon_name} 包含于 {server_name}")

                    elif (server_name.lower() in addon_name.lower() and
                          len(server_name) >= len(addon_name) * 0.8):  # 长度相似度检查
                        if not best_match:  # 只在没有更好匹配时使用
                            best_match = (server_name, server_info)
                            print(f"  ⚠️ 找到部分匹配: {server_name} 包含于 {addon_name}")

            # 如果找到匹配，检查版本
            if best_match:
                server_name, server_info = best_match
                server_version = server_info.get('version')
                server_code = server_info.get('update_code')

                # 防止重复匹配同一个服务器插件
                if server_name in [pair[1] for pair in matched_pairs]:
                    print(f"  ⚠️ 服务器插件 {server_name} 已被匹配，跳过")
                    continue

                # 记录匹配对
                matched_pairs.append((addon_name, server_name))

                # 简单的版本比较
                if server_version != local_version:
                    updates[addon_name] = {
                        'current_version': local_version,
                        'latest_version': server_version,
                        'download_url': server_info.get('download_url'),
                        'original_url': server_info.get('original_url'),
                        'update_code': server_code,
                        'server_name': server_name,
                        'url_status': server_info.get('url_status', 'unknown'),
                        'url_test_message': server_info.get('url_test_message', ''),
                        'url_conversion': server_info.get('url_conversion', ''),
                        'match_type': 'exact' if exact_match else 'partial'
                    }
                    print(f"🆕 发现更新: {addon_name} {local_version} -> {server_version} (匹配: {server_name})")
                else:
                    print(f"✅ 版本已是最新: {addon_name} {local_version}")
            else:
                print(f"❌ 未找到匹配的服务器插件: {addon_name}")

        print(f"📊 匹配结果:")
        for local_name, server_name in matched_pairs:
            print(f"  {local_name} <-> {server_name}")

        response_data = {
            'success': True,
            'message': f'检查完成，发现 {len(updates)} 个可更新插件',
            'updates': updates,
            'total_checked': len(local_addons),
            'updates_found': len(updates),
            'matched_pairs': matched_pairs  # 调试信息
        }

        print(f"✅ 检查更新完成: 发现 {len(updates)} 个可更新插件")

        # 根据请求是否加密来决定响应格式
        final_response = safe_encrypt_response(response_data, force_plaintext=not was_encrypted)
        return jsonify(final_response)

    except Exception as e:
        print(f"❌ 检查更新异常: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'服务器错误: {str(e)}'
        }), 500


@app.route('/api/updater/get_addon_list', methods=['POST'])
def get_addon_list():
    """获取插件列表 - 供更新器使用"""
    try:
        print("📥 收到获取插件列表请求")
        request_data = request.get_json()

        # 解密请求数据
        data, was_encrypted = safe_decrypt(request_data)

        # 获取更新码列表
        update_codes = data.get('update_codes', []) if isinstance(data, dict) else []

        print(f"🔍 使用更新码获取插件列表: {len(update_codes)} 个更新码")

        if not update_codes:
            error_response = {
                'success': False,
                'message': '未提供有效的更新码'
            }
            final_response = safe_encrypt_response(error_response, force_plaintext=not was_encrypted)
            return jsonify(final_response), 400

        # 筛选有效的插件
        valid_addons = {}
        for name, info in storage.addon_storage.items():
            if info.get('update_code') in update_codes:
                valid_addons[name] = {
                    'version': info.get('version'),
                    'download_url': info.get('download_url'),
                    'original_url': info.get('original_url'),
                    'update_code': info.get('update_code'),
                    'updated_at': info.get('updated_at'),
                    'url_status': info.get('url_status', 'unknown'),
                    'url_test_message': info.get('url_test_message', ''),
                    'url_conversion': info.get('url_conversion', '')
                }

        response_data = {
            'success': True,
            'message': f'获取到 {len(valid_addons)} 个有效插件',
            'addons': valid_addons,
            'total_addons': len(valid_addons)
        }

        print(f"✅ 返回 {len(valid_addons)} 个有效插件")

        # 根据请求是否加密来决定响应格式
        final_response = safe_encrypt_response(response_data, force_plaintext=not was_encrypted)
        return jsonify(final_response)

    except Exception as e:
        print(f"❌ 获取插件列表异常: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'服务器错误: {str(e)}'
        }), 500


# 在现有代码中添加以下缺失的路由

@app.route('/api/health')
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'wow-addon-server-local',
        'version': '1.0.1-improved',
        'timestamp': datetime.now().isoformat(),
        'addons_count': storage.get_addon_count(),
        'active_tokens': storage.get_token_count(),
        'encryption': 'enabled',
        'storage': {
            'type': 'json_file',
            'data_file': str(DATA_FILE),
            'token_file': str(TOKEN_FILE),
            'data_file_exists': DATA_FILE.exists(),
            'data_file_size': DATA_FILE.stat().st_size if DATA_FILE.exists() else 0
        }
    })


@app.route('/api/test')
def test():
    return jsonify({
        'success': True,
        'message': '本地服务器运行正常',
        'addons_count': storage.get_addon_count(),
        'encryption': 'supported',
        'storage': 'json_file',
        'url_validation': 'enabled'
    })


@app.route('/api/manager/login', methods=['POST'])
def login():
    try:
        print("📥 收到登录请求")
        request_data = request.get_json()

        # 解密请求数据
        data, was_encrypted = safe_decrypt(request_data)

        if isinstance(data, dict):
            password = data.get('password')
            print(f"🔑 提取的密码: '{password}'")

            if password == 'admin123':
                token = generate_token()
                print(f"✅ 登录成功，生成token: {token}")

                response_data = {
                    'success': True,
                    'message': '登录成功',
                    'token': token
                }

                # 根据请求是否加密来决定响应格式
                final_response = safe_encrypt_response(response_data, force_plaintext=not was_encrypted)
                return jsonify(final_response)
            else:
                print("❌ 密码错误")
                error_response = {
                    'success': False,
                    'message': '密码错误'
                }
                final_response = safe_encrypt_response(error_response, force_plaintext=not was_encrypted)
                return jsonify(final_response), 401
        else:
            print("❌ 数据格式错误")
            return jsonify({
                'success': False,
                'message': '数据格式错误'
            }), 400

    except Exception as e:
        print(f"❌ 登录异常: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'服务器错误: {str(e)}'
        }), 500


@app.route('/api/manager/addons', methods=['GET'])
def get_addons():
    """获取所有插件"""
    try:
        # 检查授权（简化版）
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            if not storage.verify_token(token):
                return jsonify({'success': False, 'message': '无效token'}), 401

        print(f"📤 返回插件列表，共 {storage.get_addon_count()} 个插件")

        response_data = {
            'success': True,
            'addons': storage.get_all_addons()
        }

        # 尝试加密响应
        final_response = safe_encrypt_response(response_data)
        return jsonify(final_response)

    except Exception as e:
        print(f"❌ 获取插件列表异常: {e}")
        return jsonify({
            'success': False,
            'message': f'服务器错误: {str(e)}'
        }), 500


@app.route('/api/manager/addons', methods=['POST'])
def add_addon():
    """添加插件"""
    try:
        # 检查授权
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            if not storage.verify_token(token):
                return jsonify({'success': False, 'message': '无效token'}), 401

        request_data = request.get_json()

        # 解密请求数据
        data, was_encrypted = safe_decrypt(request_data)
        print(f"📋 解析的数据: {data}")

        addon_name = data.get('addon_name')
        version = data.get('version')
        download_url = data.get('download_url')
        update_code = data.get('update_code')

        print(f"🎮 插件信息: 名称={addon_name}, 版本={version}, 更新码={update_code}")

        if not all([addon_name, version, download_url, update_code]):
            missing = []
            if not addon_name: missing.append('addon_name')
            if not version: missing.append('version')
            if not download_url: missing.append('download_url')
            if not update_code: missing.append('update_code')

            error_msg = f'缺少必要参数: {", ".join(missing)}'
            print(f"❌ {error_msg}")

            error_response = {
                'success': False,
                'message': error_msg
            }
            final_response = safe_encrypt_response(error_response, force_plaintext=not was_encrypted)
            return jsonify(final_response), 400

        # 使用存储管理器添加插件（包含URL验证）
        storage.add_addon(addon_name, version, download_url, update_code)

        print(f"✅ 插件 {addon_name} 添加成功并保存到文件")

        # 获取URL验证结果
        addon_info = storage.addon_storage.get(addon_name, {})

        response_data = {
            'success': True,
            'message': '插件添加成功',
            'update_code': update_code,
            'url_info': {
                'original_url': addon_info.get('original_url'),
                'converted_url': addon_info.get('download_url'),
                'conversion_message': addon_info.get('url_conversion'),
                'url_status': addon_info.get('url_status'),
                'test_message': addon_info.get('url_test_message')
            }
        }

        # 根据请求是否加密来决定响应格式
        final_response = safe_encrypt_response(response_data, force_plaintext=not was_encrypted)
        return jsonify(final_response)

    except Exception as e:
        print(f"❌ 添加插件异常: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'服务器错误: {str(e)}'
        }), 500


@app.route('/api/manager/addons/<addon_name>', methods=['DELETE'])
def delete_addon(addon_name):
    """删除插件"""
    try:
        # 检查授权
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            if not storage.verify_token(token):
                return jsonify({'success': False, 'message': '无效token'}), 401

        print(f"📥 收到删除插件请求: {addon_name}")

        if storage.delete_addon(addon_name):
            print(f"✅ 插件 {addon_name} 删除成功并保存到文件")

            response_data = {
                'success': True,
                'message': '插件删除成功'
            }

            # 尝试加密响应
            final_response = safe_encrypt_response(response_data)
            return jsonify(final_response)
        else:
            print(f"❌ 插件 {addon_name} 不存在")

            error_response = {
                'success': False,
                'message': '插件不存在'
            }

            final_response = safe_encrypt_response(error_response)
            return jsonify(final_response), 404

    except Exception as e:
        print(f"❌ 删除插件异常: {e}")
        return jsonify({
            'success': False,
            'message': f'服务器错误: {str(e)}'
        }), 500


@app.route('/api/manager/addons/<addon_name>/url', methods=['PUT'])
def update_addon_url(addon_name):
    """更新插件下载地址"""
    try:
        print(f"📥 收到更新URL请求: {addon_name}")
        print(f"📋 当前服务器插件列表: {list(storage.addon_storage.keys())}")

        # 检查授权
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            if not storage.verify_token(token):
                return jsonify({'success': False, 'message': '无效token'}), 401

        # 尝试查找匹配的插件名（支持模糊匹配）
        actual_addon_name = None

        # 首先尝试精确匹配
        if addon_name in storage.addon_storage:
            actual_addon_name = addon_name
            print(f"✅ 找到精确匹配: {addon_name}")
        else:
            # 尝试不区分大小写的匹配
            for stored_name in storage.addon_storage.keys():
                if stored_name.lower() == addon_name.lower():
                    actual_addon_name = stored_name
                    print(f"✅ 找到大小写匹配: {addon_name} -> {stored_name}")
                    break

            # 如果还没找到，尝试包含关系匹配
            if not actual_addon_name:
                for stored_name in storage.addon_storage.keys():
                    if (addon_name.lower() in stored_name.lower() or
                            stored_name.lower() in addon_name.lower()):
                        actual_addon_name = stored_name
                        print(f"⚠️ 找到模糊匹配: {addon_name} -> {stored_name}")
                        break

        if not actual_addon_name:
            print(f"❌ 未找到插件: {addon_name}")
            print(f"📋 可用插件: {list(storage.addon_storage.keys())}")

            error_response = {
                'success': False,
                'message': f'插件不存在: {addon_name}',
                'available_addons': list(storage.addon_storage.keys())
            }
            return jsonify(error_response), 404

        # 继续处理更新URL的逻辑...
        request_data = request.get_json()
        data, was_encrypted = safe_decrypt(request_data)

        new_url = data.get('download_url')
        if not new_url:
            error_response = {
                'success': False,
                'message': '下载地址不能为空'
            }
            final_response = safe_encrypt_response(error_response, force_plaintext=not was_encrypted)
            return jsonify(final_response), 400

        # 使用找到的实际插件名进行更新
        if storage.update_addon_url(actual_addon_name, new_url):
            print(f"✅ 插件 {actual_addon_name} URL更新成功")

            addon_info = storage.addon_storage.get(actual_addon_name, {})
            response_data = {
                'success': True,
                'message': '下载地址更新成功',
                'actual_addon_name': actual_addon_name,  # 返回实际的插件名
                'url_info': {
                    'original_url': addon_info.get('original_url'),
                    'converted_url': addon_info.get('download_url'),
                    'conversion_message': addon_info.get('url_conversion'),
                    'url_status': addon_info.get('url_status'),
                    'test_message': addon_info.get('url_test_message')
                }
            }

            final_response = safe_encrypt_response(response_data, force_plaintext=not was_encrypted)
            return jsonify(final_response)
        else:
            error_response = {
                'success': False,
                'message': '更新失败'
            }
            final_response = safe_encrypt_response(error_response, force_plaintext=not was_encrypted)
            return jsonify(final_response), 500

    except Exception as e:
        print(f"❌ 更新插件URL异常: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'服务器错误: {str(e)}'
        }), 500

# 在主页路由中更新端点列表
@app.route('/')
def home():
    return jsonify({
        'message': '魔兽世界插件管理系统本地调试服务器',
        'status': 'running',
        'version': '1.0.1-improved',
        'encryption': 'supported',
        'storage': 'json_file',
        'features': ['url_validation', 'direct_link_conversion', 'url_testing'],
        'data_file': str(DATA_FILE),
        'data_directory': str(DATA_FILE.parent),
        'endpoints': {
            'health': '/api/health',
            'login': '/api/manager/login',
            'addons': '/api/manager/addons',
            'backup': '/api/admin/backup',
            'restore': '/api/admin/restore',
            'validate_urls': '/api/admin/validate_urls',  # 新增
            'test_url': '/api/admin/test_url',  # 新增
            # 更新器专用接口
            'verify_code': '/api/updater/verify_code',
            'check_updates': '/api/updater/check_updates',
            'get_addon_list': '/api/updater/get_addon_list'
        }
    })


# 同时在启动信息中添加新的端点说明
if __name__ == '__main__':
    print("🚀 启动支持加密的本地调试服务器...")
    print("📍 健康检查: http://localhost:5000/api/health")
    print("🔑 默认密码: admin123")
    print("🔒 支持加密传输")
    print("💾 数据存储: JSON文件")
    print(f"📄 数据文件: {DATA_FILE}")
    print(f"🔑 Token文件: {TOKEN_FILE}")
    print("🔍 调试接口:")
    print("  - POST /api/debug/decrypt (解密测试)")
    print("  - GET /api/debug/storage (存储状态)")
    print("🔄 管理接口:")
    print("  - GET /api/admin/backup (备份数据)")
    print("  - POST /api/admin/restore (恢复数据)")
    print("🎮 更新器接口:")
    print("  - POST /api/updater/verify_code (验证更新码)")
    print("  - POST /api/updater/check_updates (检查更新)")
    print("  - POST /api/updater/get_addon_list (获取插件列表)")

    # 测试加密工具是否正常
    try:
        test_data = {'test': 'hello'}
        encrypted = crypto.encrypt_request(test_data)
        decrypted = crypto.decrypt_request(encrypted)

        if decrypted == test_data:
            print("✅ 加密工具测试通过")
        else:
            print("❌ 加密工具测试失败")
            print(f"原始: {test_data}")
            print(f"解密后: {decrypted}")
    except Exception as e:
        print(f"⚠️ 加密工具测试异常: {e}")

    # 检查数据文件状态
    print(f"\n📊 存储状态:")
    print(f"  插件数量: {storage.get_addon_count()}")
    print(f"  Token数量: {storage.get_token_count()}")
    print(f"  数据文件: {DATA_FILE} ({'存在' if DATA_FILE.exists() else '不存在'})")
    print(f"  Token文件: {TOKEN_FILE} ({'存在' if TOKEN_FILE.exists() else '不存在'})")

    # 测试路由是否注册
    print("\n📋 注册的路由:")
    for rule in app.url_map.iter_rules():
        methods = ', '.join(rule.methods - {'HEAD', 'OPTIONS'})
        print(f"  {methods:10} {rule.rule} -> {rule.endpoint}")

    print("\n" + "=" * 60)
    app.run(debug=True, host='127.0.0.1', port=5000)