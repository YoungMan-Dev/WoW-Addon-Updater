# manager/core/api_client.py
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

    def login(self, password):
        """管理员登录"""
        try:
            data = {'password': password}
            print(f"登录请求数据: {data}")  # 调试日志

            # 先尝试加密传输
            try:
                encrypted_payload = self.crypto.encrypt_request(data)
                headers = {'Content-Type': 'application/json'}

                response = self.session.post(
                    f"{self.base_url}/manager/login",
                    json=encrypted_payload,
                    headers=headers,
                    timeout=REQUEST_TIMEOUT
                )
            except Exception as encrypt_error:
                print(f"加密登录失败，尝试明文: {encrypt_error}")
                # 如果加密失败，尝试明文传输
                headers = {'Content-Type': 'application/json'}
                response = self.session.post(
                    f"{self.base_url}/manager/login",
                    json=data,
                    headers=headers,
                    timeout=REQUEST_TIMEOUT
                )

            print(f"登录响应状态码: {response.status_code}")
            print(f"登录响应内容: {response.text}")

            if response.status_code == 200:
                try:
                    response_data = response.json()
                    # 尝试解密响应
                    if 'encrypted_data' in response_data:
                        decrypted_data = self.crypto.decrypt_request(response_data)
                        return decrypted_data
                    else:
                        return response_data
                except Exception as decrypt_error:
                    print(f"解密登录响应失败: {decrypt_error}")
                    return response.json()
            else:
                error_msg = f'登录失败，HTTP状态码: {response.status_code}'
                if response.text:
                    error_msg += f', 错误信息: {response.text}'
                return {
                    'success': False,
                    'message': error_msg
                }

        except Exception as e:
            print(f"登录异常: {e}")
            return {
                'success': False,
                'message': f'登录失败: {str(e)}'
            }

    def get_all_addons(self, token):
        """获取所有插件信息"""
        try:
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }

            print(f"获取插件列表请求")  # 调试日志

            response = self.session.get(
                f"{self.base_url}/manager/addons",
                headers=headers,
                timeout=REQUEST_TIMEOUT
            )

            print(f"获取插件列表响应状态码: {response.status_code}")
            print(f"获取插件列表响应内容: {response.text[:200]}...")  # 只显示前200字符

            if response.status_code == 200:
                try:
                    response_data = response.json()
                    # 尝试解密响应
                    if 'encrypted_data' in response_data:
                        decrypted_data = self.crypto.decrypt_request(response_data)
                        return {
                            'success': True,
                            'addons': decrypted_data.get('addons', {})
                        }
                    else:
                        return {
                            'success': True,
                            'addons': response_data.get('addons', {})
                        }
                except Exception as decrypt_error:
                    print(f"解密插件列表响应失败: {decrypt_error}")
                    response_data = response.json()
                    return {
                        'success': True,
                        'addons': response_data.get('addons', {})
                    }
            else:
                error_msg = f'获取插件列表失败，HTTP状态码: {response.status_code}'
                if response.text:
                    error_msg += f', 错误信息: {response.text}'
                return {
                    'success': False,
                    'message': error_msg,
                    'addons': {}
                }

        except Exception as e:
            print(f"获取插件列表异常: {e}")
            return {
                'success': False,
                'message': f'获取插件列表失败: {str(e)}',
                'addons': {}
            }

    def add_addon(self, addon_name, version, download_url, update_code, token):
        """添加插件"""
        try:
            data = {
                'addon_name': addon_name,
                'version': version,
                'download_url': download_url,
                'update_code': update_code
            }

            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }

            print(f"发送请求数据: {data}")  # 调试日志

            # 先尝试加密传输
            try:
                encrypted_payload = self.crypto.encrypt_request(data)
                print(f"使用加密传输")  # 调试日志

                response = self.session.post(
                    f"{self.base_url}/manager/addons",
                    json=encrypted_payload,
                    headers=headers,
                    timeout=REQUEST_TIMEOUT
                )
            except Exception as encrypt_error:
                print(f"加密失败，尝试明文传输: {encrypt_error}")
                # 如果加密失败，尝试明文传输
                response = self.session.post(
                    f"{self.base_url}/manager/addons",
                    json=data,
                    headers=headers,
                    timeout=REQUEST_TIMEOUT
                )

            print(f"响应状态码: {response.status_code}")  # 调试日志
            print(f"响应内容: {response.text}")  # 调试日志

            if response.status_code == 200:
                try:
                    response_data = response.json()
                    # 尝试解密响应
                    if 'encrypted_data' in response_data:
                        decrypted_data = self.crypto.decrypt_request(response_data)
                        return decrypted_data
                    else:
                        return response_data
                except Exception as decrypt_error:
                    print(f"解密响应失败: {decrypt_error}")
                    return response.json()
            else:
                error_msg = f'添加插件失败，HTTP状态码: {response.status_code}'
                if response.text:
                    error_msg += f', 错误信息: {response.text}'
                return {
                    'success': False,
                    'message': error_msg
                }

        except Exception as e:
            print(f"请求异常: {e}")  # 调试日志
            return {
                'success': False,
                'message': f'添加插件失败: {str(e)}'
            }

    def delete_addon(self, addon_name, token):
        """删除插件"""
        try:
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }

            print(f"删除插件请求: {addon_name}")  # 调试日志

            response = self.session.delete(
                f"{self.base_url}/manager/addons/{addon_name}",
                headers=headers,
                timeout=REQUEST_TIMEOUT
            )

            print(f"删除插件响应状态码: {response.status_code}")
            print(f"删除插件响应内容: {response.text}")

            if response.status_code == 200:
                try:
                    response_data = response.json()
                    # 尝试解密响应
                    if 'encrypted_data' in response_data:
                        decrypted_data = self.crypto.decrypt_request(response_data)
                        return decrypted_data
                    else:
                        return response_data
                except Exception as decrypt_error:
                    print(f"解密删除响应失败: {decrypt_error}")
                    return response.json()
            else:
                error_msg = f'删除插件失败，HTTP状态码: {response.status_code}'
                if response.text:
                    error_msg += f', 错误信息: {response.text}'
                return {
                    'success': False,
                    'message': error_msg
                }

        except Exception as e:
            print(f"删除插件异常: {e}")
            return {
                'success': False,
                'message': f'删除插件失败: {str(e)}'
            }

    def update_addon_url(self, addon_name, new_url, token):
        """更新插件下载地址"""
        try:
            data = {'download_url': new_url}
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }

            print(f"更新插件URL请求: {addon_name}, {new_url}")  # 调试日志

            # 先尝试加密传输
            try:
                encrypted_payload = self.crypto.encrypt_request(data)
                response = self.session.put(
                    f"{self.base_url}/manager/addons/{addon_name}/url",
                    json=encrypted_payload,
                    headers=headers,
                    timeout=REQUEST_TIMEOUT
                )
            except Exception as encrypt_error:
                print(f"加密更新URL失败，尝试明文: {encrypt_error}")
                # 如果加密失败，尝试明文传输
                response = self.session.put(
                    f"{self.base_url}/manager/addons/{addon_name}/url",
                    json=data,
                    headers=headers,
                    timeout=REQUEST_TIMEOUT
                )

            print(f"更新URL响应状态码: {response.status_code}")
            print(f"更新URL响应内容: {response.text}")

            if response.status_code == 200:
                try:
                    response_data = response.json()
                    # 尝试解密响应
                    if 'encrypted_data' in response_data:
                        decrypted_data = self.crypto.decrypt_request(response_data)
                        return decrypted_data
                    else:
                        return response_data
                except Exception as decrypt_error:
                    print(f"解密更新URL响应失败: {decrypt_error}")
                    return response.json()
            else:
                error_msg = f'更新下载地址失败，HTTP状态码: {response.status_code}'
                if response.text:
                    error_msg += f', 错误信息: {response.text}'
                return {
                    'success': False,
                    'message': error_msg
                }

        except Exception as e:
            print(f"更新下载地址异常: {e}")
            return {
                'success': False,
                'message': f'更新下载地址失败: {str(e)}'
            }

    def update_addon_update_code(self, addon_name, new_update_code, token):
        """更新插件更新码"""
        try:
            data = {'update_code': new_update_code}
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }

            print(f"更新插件更新码请求: {addon_name}, {new_update_code}")  # 调试日志

            # 先尝试加密传输
            try:
                encrypted_payload = self.crypto.encrypt_request(data)
                response = self.session.put(
                    f"{self.base_url}/manager/addons/{addon_name}/update_code",
                    json=encrypted_payload,
                    headers=headers,
                    timeout=REQUEST_TIMEOUT
                )
            except Exception as encrypt_error:
                print(f"加密更新更新码失败，尝试明文: {encrypt_error}")
                # 如果加密失败，尝试明文传输
                response = self.session.put(
                    f"{self.base_url}/manager/addons/{addon_name}/update_code",
                    json=data,
                    headers=headers,
                    timeout=REQUEST_TIMEOUT
                )

            print(f"更新更新码响应状态码: {response.status_code}")
            print(f"更新更新码响应内容: {response.text}")

            if response.status_code == 200:
                try:
                    response_data = response.json()
                    # 尝试解密响应
                    if 'encrypted_data' in response_data:
                        decrypted_data = self.crypto.decrypt_request(response_data)
                        return decrypted_data
                    else:
                        return response_data
                except Exception as decrypt_error:
                    print(f"解密更新更新码响应失败: {decrypt_error}")
                    return response.json()
            else:
                error_msg = f'更新更新码失败，HTTP状态码: {response.status_code}'
                if response.text:
                    error_msg += f', 错误信息: {response.text}'
                return {
                    'success': False,
                    'message': error_msg
                }

        except Exception as e:
            print(f"更新更新码异常: {e}")
            return {
                'success': False,
                'message': f'更新更新码失败: {str(e)}'
            }

    def batch_update_update_code(self, addon_names, new_update_code, token):
        """批量更新插件更新码"""
        try:
            data = {
                'addon_names': addon_names,
                'update_code': new_update_code
            }
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }

            print(f"批量更新更新码请求: {addon_names}, {new_update_code}")  # 调试日志

            # 先尝试加密传输
            try:
                encrypted_payload = self.crypto.encrypt_request(data)
                response = self.session.put(
                    f"{self.base_url}/manager/addons/batch/update_code",
                    json=encrypted_payload,
                    headers=headers,
                    timeout=REQUEST_TIMEOUT
                )
            except Exception as encrypt_error:
                print(f"加密批量更新更新码失败，尝试明文: {encrypt_error}")
                # 如果加密失败，尝试明文传输
                response = self.session.put(
                    f"{self.base_url}/manager/addons/batch/update_code",
                    json=data,
                    headers=headers,
                    timeout=REQUEST_TIMEOUT
                )

            print(f"批量更新更新码响应状态码: {response.status_code}")
            print(f"批量更新更新码响应内容: {response.text}")

            if response.status_code == 200:
                try:
                    response_data = response.json()
                    # 尝试解密响应
                    if 'encrypted_data' in response_data:
                        decrypted_data = self.crypto.decrypt_request(response_data)
                        return decrypted_data
                    else:
                        return response_data
                except Exception as decrypt_error:
                    print(f"解密批量更新更新码响应失败: {decrypt_error}")
                    return response.json()
            else:
                error_msg = f'批量更新更新码失败，HTTP状态码: {response.status_code}'
                if response.text:
                    error_msg += f', 错误信息: {response.text}'
                return {
                    'success': False,
                    'message': error_msg
                }

        except Exception as e:
            print(f"批量更新更新码异常: {e}")
            return {
                'success': False,
                'message': f'批量更新更新码失败: {str(e)}'
            }