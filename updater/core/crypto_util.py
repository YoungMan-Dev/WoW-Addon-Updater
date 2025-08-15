# shared/crypto_util.py
import json
import base64
import hashlib
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os


class CryptoUtil:
    """加密工具类"""

    def __init__(self, password=None):
        """初始化加密工具"""
        if password is None:
            password = "wow_addon_manager_default_key_2024"

        self.password = password.encode('utf-8')
        self.salt = b"wow_addon_manager_salt_2024_fixed"  # 固定盐值以确保一致性
        self.key = self._derive_key()
        self.cipher = Fernet(self.key)

    def _derive_key(self):
        """从密码派生密钥"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.password))
        return key

    def encrypt_request(self, data):
        """加密请求数据"""
        try:
            # 将数据转换为JSON字符串
            json_data = json.dumps(data, ensure_ascii=False)
            json_bytes = json_data.encode('utf-8')

            # 加密数据
            encrypted_data = self.cipher.encrypt(json_bytes)

            # Base64编码
            encoded_data = base64.b64encode(encrypted_data).decode('ascii')

            return {
                'encrypted_data': encoded_data,
                'encryption_method': 'fernet'
            }
        except Exception as e:
            print(f"加密失败: {e}")
            return {'error': 'encryption_failed'}

    def decrypt_request(self, encrypted_payload):
        """解密请求数据"""
        try:
            if 'encrypted_data' not in encrypted_payload:
                return encrypted_payload  # 如果没有加密数据，直接返回

            # Base64解码
            encrypted_data = base64.b64decode(encrypted_payload['encrypted_data'].encode('ascii'))

            # 解密数据
            decrypted_bytes = self.cipher.decrypt(encrypted_data)

            # 转换为JSON对象
            json_data = decrypted_bytes.decode('utf-8')
            return json.loads(json_data)
        except Exception as e:
            print(f"解密失败: {e}")
            return {'error': 'decryption_failed'}

    def generate_token(self, user_data):
        """生成访问令牌"""
        try:
            # 添加时间戳
            import time
            token_data = {
                'user_data': user_data,
                'timestamp': int(time.time()),
                'random': os.urandom(16).hex()
            }

            # 加密令牌数据
            encrypted_token = self.encrypt_request(token_data)
            if 'error' in encrypted_token:
                return None

            return encrypted_token['encrypted_data']
        except Exception as e:
            print(f"生成令牌失败: {e}")
            return None

    def verify_token(self, token):
        """验证访问令牌"""
        try:
            # 解密令牌
            decrypted_data = self.decrypt_request({'encrypted_data': token})
            if 'error' in decrypted_data:
                return False, None

            # 检查令牌格式
            if 'user_data' not in decrypted_data or 'timestamp' not in decrypted_data:
                return False, None

            # 检查令牌是否过期（24小时）
            import time
            current_time = int(time.time())
            token_time = decrypted_data['timestamp']
            if current_time - token_time > 24 * 3600:  # 24小时过期
                return False, None

            return True, decrypted_data['user_data']
        except Exception as e:
            print(f"验证令牌失败: {e}")
            return False, None

    def hash_password(self, password):
        """哈希密码"""
        return hashlib.sha256((password + "wow_addon_salt").encode()).hexdigest()

    def verify_password(self, password, hashed_password):
        """验证密码"""
        return self.hash_password(password) == hashed_password