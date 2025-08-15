# shared/crypto_util.py - 简单的加密工具
import base64
import json
import hashlib
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os


class CryptoUtil:
    """简单的加密解密工具"""

    def __init__(self, password=None):
        """初始化加密工具

        Args:
            password: 加密密码，如果不提供则使用默认密码
        """
        if password is None:
            password = "wow-addon-updater-2025"  # 默认密码

        self.password = password.encode()
        self.salt = b'wow_addon_salt_2025'  # 固定盐值，实际应用中应该随机生成
        self.key = self._derive_key()
        self.fernet = Fernet(self.key)

    def _derive_key(self):
        """从密码派生加密密钥"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.password))
        return key

    def encrypt_request(self, data):
        """加密请求数据

        Args:
            data: 要加密的数据（字典或其他可JSON序列化的数据）

        Returns:
            dict: 包含加密数据的字典
        """
        try:
            # 将数据序列化为JSON字符串
            json_str = json.dumps(data, ensure_ascii=False)

            # 加密数据
            encrypted_bytes = self.fernet.encrypt(json_str.encode('utf-8'))

            # 转换为base64字符串
            encrypted_str = base64.b64encode(encrypted_bytes).decode('ascii')

            # 生成校验和
            checksum = hashlib.sha256(encrypted_str.encode()).hexdigest()[:16]

            return {
                'encrypted_data': encrypted_str,
                'checksum': checksum,
                'version': '1.0'
            }

        except Exception as e:
            return {
                'error': f'加密失败: {str(e)}'
            }

    def decrypt_request(self, encrypted_data):
        """解密请求数据

        Args:
            encrypted_data: 包含加密数据的字典

        Returns:
            dict: 解密后的原始数据
        """
        try:
            if not isinstance(encrypted_data, dict):
                return {'error': '数据格式错误'}

            if 'encrypted_data' not in encrypted_data:
                return {'error': '缺少加密数据'}

            encrypted_str = encrypted_data['encrypted_data']
            received_checksum = encrypted_data.get('checksum', '')

            # 验证校验和
            expected_checksum = hashlib.sha256(encrypted_str.encode()).hexdigest()[:16]
            if received_checksum != expected_checksum:
                return {'error': '数据校验失败'}

            # 解码base64
            encrypted_bytes = base64.b64decode(encrypted_str.encode('ascii'))

            # 解密数据
            decrypted_bytes = self.fernet.decrypt(encrypted_bytes)

            # 解析JSON
            json_str = decrypted_bytes.decode('utf-8')
            data = json.loads(json_str)

            return data

        except Exception as e:
            return {
                'error': f'解密失败: {str(e)}'
            }

    def encrypt_text(self, text):
        """加密纯文本

        Args:
            text: 要加密的文本字符串

        Returns:
            str: 加密后的base64字符串
        """
        try:
            encrypted_bytes = self.fernet.encrypt(text.encode('utf-8'))
            return base64.b64encode(encrypted_bytes).decode('ascii')
        except Exception as e:
            raise Exception(f'文本加密失败: {str(e)}')

    def decrypt_text(self, encrypted_text):
        """解密纯文本

        Args:
            encrypted_text: 加密的base64字符串

        Returns:
            str: 解密后的原始文本
        """
        try:
            encrypted_bytes = base64.b64decode(encrypted_text.encode('ascii'))
            decrypted_bytes = self.fernet.decrypt(encrypted_bytes)
            return decrypted_bytes.decode('utf-8')
        except Exception as e:
            raise Exception(f'文本解密失败: {str(e)}')

    def generate_update_code(self, length=8):
        """生成更新码

        Args:
            length: 更新码长度，默认8位

        Returns:
            str: 生成的更新码
        """
        import random
        import string

        # 使用大写字母和数字
        chars = string.ascii_uppercase + string.digits
        # 排除容易混淆的字符
        chars = chars.replace('0', '').replace('O', '').replace('1', '').replace('I', '')

        return ''.join(random.choice(chars) for _ in range(length))

    def hash_password(self, password):
        """哈希密码

        Args:
            password: 原始密码

        Returns:
            str: 哈希后的密码
        """
        salt = os.urandom(32)  # 32字节的随机盐
        pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        return salt + pwdhash

    def verify_password(self, password, stored_hash):
        """验证密码

        Args:
            password: 输入的密码
            stored_hash: 存储的哈希值

        Returns:
            bool: 密码是否正确
        """
        try:
            salt = stored_hash[:32]  # 前32字节是盐
            stored_pwdhash = stored_hash[32:]  # 后面是哈希值
            pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
            return pwdhash == stored_pwdhash
        except Exception:
            return False


class SimpleCryptoUtil:
    """简化版加密工具（当cryptography库不可用时的备选方案）"""

    def __init__(self, password=None):
        if password is None:
            password = "wow-addon-updater-2025"
        self.password = password

    def _simple_encrypt(self, data):
        """简单的XOR加密"""
        key = self.password.encode()
        data_bytes = data.encode('utf-8')

        encrypted = bytearray()
        for i, byte in enumerate(data_bytes):
            encrypted.append(byte ^ key[i % len(key)])

        return base64.b64encode(encrypted).decode('ascii')

    def _simple_decrypt(self, encrypted_data):
        """简单的XOR解密"""
        key = self.password.encode()
        encrypted_bytes = base64.b64decode(encrypted_data.encode('ascii'))

        decrypted = bytearray()
        for i, byte in enumerate(encrypted_bytes):
            decrypted.append(byte ^ key[i % len(key)])

        return decrypted.decode('utf-8')

    def encrypt_request(self, data):
        """加密请求数据"""
        try:
            json_str = json.dumps(data, ensure_ascii=False)
            encrypted_str = self._simple_encrypt(json_str)

            return {
                'encrypted_data': encrypted_str,
                'version': '1.0-simple'
            }
        except Exception as e:
            return {'error': f'加密失败: {str(e)}'}

    def decrypt_request(self, encrypted_data):
        """解密请求数据"""
        try:
            if not isinstance(encrypted_data, dict) or 'encrypted_data' not in encrypted_data:
                return {'error': '数据格式错误'}

            encrypted_str = encrypted_data['encrypted_data']
            json_str = self._simple_decrypt(encrypted_str)
            data = json.loads(json_str)

            return data
        except Exception as e:
            return {'error': f'解密失败: {str(e)}'}

    def generate_update_code(self, length=8):
        """生成更新码"""
        import random
        import string
        chars = string.ascii_uppercase + string.digits
        chars = chars.replace('0', '').replace('O', '').replace('1', '').replace('I', '')
        return ''.join(random.choice(chars) for _ in range(length))


# 自动选择可用的加密工具
def create_crypto_util(password=None):
    """创建加密工具实例，自动选择可用的实现"""
    try:
        # 尝试使用完整版
        from cryptography.fernet import Fernet
        return CryptoUtil(password)
    except ImportError:
        print("⚠️ cryptography库不可用，使用简化版加密工具")
        return SimpleCryptoUtil(password)


# 导出主要类和函数
__all__ = ['CryptoUtil', 'SimpleCryptoUtil', 'create_crypto_util']

# 测试代码
if __name__ == '__main__':
    print("🔧 测试加密工具...")

    # 测试完整版
    try:
        crypto = CryptoUtil()
        test_data = {'username': 'admin', 'password': 'test123', '中文': '测试'}

        print(f"原始数据: {test_data}")

        # 测试加密
        encrypted = crypto.encrypt_request(test_data)
        print(f"加密结果: {encrypted}")

        # 测试解密
        decrypted = crypto.decrypt_request(encrypted)
        print(f"解密结果: {decrypted}")

        # 验证结果
        if decrypted == test_data:
            print("✅ 完整版加密工具测试通过")
        else:
            print("❌ 完整版加密工具测试失败")

        # 测试更新码生成
        update_code = crypto.generate_update_code()
        print(f"生成的更新码: {update_code}")

    except Exception as e:
        print(f"❌ 完整版测试失败: {e}")

    # 测试简化版
    try:
        simple_crypto = SimpleCryptoUtil()

        encrypted_simple = simple_crypto.encrypt_request(test_data)
        print(f"简化版加密结果: {encrypted_simple}")

        decrypted_simple = simple_crypto.decrypt_request(encrypted_simple)
        print(f"简化版解密结果: {decrypted_simple}")

        if decrypted_simple == test_data:
            print("✅ 简化版加密工具测试通过")
        else:
            print("❌ 简化版加密工具测试失败")

    except Exception as e:
        print(f"❌ 简化版测试失败: {e}")

    print("🔧 加密工具测试完成")