# updater/core/api_client.py
import requests
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.crypto_util import CryptoUtil
from shared.constants import API_BASE_URL, REQUEST_TIMEOUT


class APIClient:
    """API客户端"""

    def __init__(self):
        self.base_url = API_BASE_URL
        self.crypto = CryptoUtil()
        self.session = requests.Session()
        self.session.timeout = REQUEST_TIMEOUT

    def verify_update_code(self, addon_name, update_code):
        """验证单个更新码（修复版）"""
        try:
            print(f"🔍 验证更新码: {addon_name} - {update_code}")

            data = {
                'addon_name': addon_name,
                'update_code': update_code
            }

            # 加密请求数据
            encrypted_payload = self.crypto.encrypt_request(data)
            print(f"🔒 已加密请求数据")

            # 发送请求
            response = self.session.post(
                f"{self.base_url}/updater/verify_code",
                json=encrypted_payload,
                timeout=REQUEST_TIMEOUT
            )

            print(f"📡 服务器响应状态码: {response.status_code}")

            if response.status_code == 200:
                # 获取加密响应
                encrypted_response = response.json()
                print(f"📥 收到加密响应: {encrypted_response}")

                # 解密响应数据
                try:
                    decrypted_data = self.crypto.decrypt_request(encrypted_response)
                    print(f"🔓 解密后数据: {decrypted_data}")

                    # 检查解密是否成功
                    if isinstance(decrypted_data, dict) and 'error' not in decrypted_data:
                        # 解密成功，检查验证结果
                        success = decrypted_data.get('success', False)
                        valid = decrypted_data.get('valid', False)
                        valid_codes = decrypted_data.get('valid_codes', [])

                        print(f"✅ 验证结果: success={success}, valid={valid}, valid_codes={valid_codes}")

                        # 返回验证是否成功
                        return success and valid and len(valid_codes) > 0

                    else:
                        print(f"❌ 解密失败或数据有错误: {decrypted_data}")
                        return False

                except Exception as decrypt_error:
                    print(f"❌ 解密响应失败: {decrypt_error}")

                    # 尝试直接解析明文响应（fallback）
                    try:
                        result = encrypted_response  # 可能服务器返回的是明文
                        success = result.get('success', False)
                        valid = result.get('valid', False)
                        print(f"📝 尝试明文解析: success={success}, valid={valid}")
                        return success and valid
                    except Exception as plain_error:
                        print(f"❌ 明文解析也失败: {plain_error}")
                        return False
            else:
                print(f"❌ 服务器响应错误: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            print(f"❌ 验证更新码失败: {e}")
            import traceback
            traceback.print_exc()
            return False

    def verify_update_codes(self, update_codes):
        """批量验证更新码"""
        try:
            print(f"🔍 批量验证更新码: {update_codes}")

            data = {
                'update_codes': update_codes
            }

            # 加密请求数据
            encrypted_payload = self.crypto.encrypt_request(data)
            print(f"🔒 已加密请求数据")

            # 发送请求
            response = self.session.post(
                f"{self.base_url}/updater/verify_code",
                json=encrypted_payload,
                timeout=REQUEST_TIMEOUT
            )

            print(f"📡 服务器响应状态码: {response.status_code}")

            if response.status_code == 200:
                # 获取响应
                response_data = response.json()
                print(f"📥 收到响应: {response_data}")

                # 尝试解密响应数据
                try:
                    decrypted_data = self.crypto.decrypt_request(response_data)
                    print(f"🔓 解密后数据: {decrypted_data}")

                    if isinstance(decrypted_data, dict) and 'error' not in decrypted_data:
                        return decrypted_data
                    else:
                        print(f"❌ 解密失败，使用原始响应")
                        return response_data

                except Exception as decrypt_error:
                    print(f"❌ 解密响应失败: {decrypt_error}，使用原始响应")
                    return response_data
            else:
                print(f"❌ 服务器响应错误: {response.status_code}")
                return {
                    'success': False,
                    'message': f'服务器错误: {response.status_code}'
                }

        except Exception as e:
            print(f"❌ 批量验证更新码失败: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'message': f'验证失败: {str(e)}'
            }

    def get_addon_list(self, update_codes):
        """获取插件列表"""
        try:
            print(f"📋 获取插件列表，更新码: {update_codes}")

            data = {
                'update_codes': update_codes
            }

            # 加密请求数据
            encrypted_payload = self.crypto.encrypt_request(data)
            print(f"🔒 已加密请求数据")

            # 发送请求
            response = self.session.post(
                f"{self.base_url}/updater/get_addon_list",
                json=encrypted_payload,
                timeout=REQUEST_TIMEOUT
            )

            print(f"📡 服务器响应状态码: {response.status_code}")

            if response.status_code == 200:
                response_data = response.json()
                print(f"📥 收到响应: {response_data}")

                # 尝试解密响应数据
                try:
                    decrypted_data = self.crypto.decrypt_request(response_data)
                    print(f"🔓 解密后数据: {decrypted_data}")

                    if isinstance(decrypted_data, dict) and 'error' not in decrypted_data:
                        return decrypted_data
                    else:
                        print(f"❌ 解密失败，使用原始响应")
                        return response_data

                except Exception as decrypt_error:
                    print(f"❌ 解密响应失败: {decrypt_error}，使用原始响应")
                    return response_data
            else:
                print(f"❌ 服务器响应错误: {response.status_code}")
                return {
                    'success': False,
                    'message': f'服务器错误: {response.status_code}'
                }

        except Exception as e:
            print(f"❌ 获取插件列表失败: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'message': f'获取失败: {str(e)}'
            }

    def get_addons(self, update_codes):
        """获取插件列表（别名方法，为了兼容性）"""
        return self.get_addon_list(update_codes)

    def check_updates(self, local_addons, update_codes):
        """检查更新"""
        try:
            print(f"🔍 检查更新，本地插件: {len(local_addons)}, 更新码: {len(update_codes)}")

            data = {
                'local_addons': local_addons,
                'update_codes': update_codes
            }

            encrypted_payload = self.crypto.encrypt_request(data)

            response = self.session.post(
                f"{self.base_url}/updater/check_updates",
                json=encrypted_payload,
                timeout=REQUEST_TIMEOUT
            )

            print(f"📡 服务器响应状态码: {response.status_code}")

            if response.status_code == 200:
                response_data = response.json()
                print(f"📥 收到响应: {response_data}")

                # 尝试解密响应数据
                try:
                    decrypted_data = self.crypto.decrypt_request(response_data)
                    print(f"🔓 解密后数据: {decrypted_data}")

                    if isinstance(decrypted_data, dict) and 'error' not in decrypted_data:
                        return decrypted_data
                    else:
                        print(f"❌ 解密失败，使用原始响应")
                        return response_data

                except Exception as decrypt_error:
                    print(f"❌ 解密响应失败: {decrypt_error}，使用原始响应")
                    return response_data
            else:
                print(f"❌ 服务器响应错误: {response.status_code}")
                return {
                    'success': False,
                    'message': f'服务器错误: {response.status_code}'
                }

        except Exception as e:
            print(f"❌ 检查更新失败: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'message': f'检查失败: {str(e)}'
            }