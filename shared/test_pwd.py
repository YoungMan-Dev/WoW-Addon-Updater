#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速调试加密解密问题
"""

import sys
import os
from pathlib import Path
import traceback

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


# 测试真实的加密数据
def test_real_encrypted_data():
    """测试真实的加密数据"""
    print("🔍 测试真实的加密数据...")

    # 这是从您的日志中看到的真实加密数据
    real_encrypted_data = {
        'encrypted_data': 'Z0FBQUFBQm9uVThOTzc2V2ZxQS1VUlBLRmZ3cklsLXpWVU9NajkxRi16V3lvRjZQSDlBdVZmTk9tZVRoZWpXWk5SUWp1VGU5b3RzZmRrcURfVXYyS1FhdjR4SnZJRFFmVUUxejhsSnRqZjh4WkxKTUFpdmxpOGs9',
        'encryption_method': 'fernet'
    }

    print(f"📦 原始加密数据: {real_encrypted_data}")

    try:
        from shared.crypto_util import CryptoUtil
        crypto = CryptoUtil()

        print("🔓 尝试解密...")
        decrypted_data = crypto.decrypt_request(real_encrypted_data)
        print(f"✅ 解密结果: {decrypted_data}")

        password = decrypted_data.get('password') if isinstance(decrypted_data, dict) else None
        print(f"🔑 提取的密码: '{password}'")

        return password is not None and password == 'admin123'

    except Exception as e:
        print(f"❌ 解密失败: {e}")
        traceback.print_exc()
        return False


def test_encryption_from_scratch():
    """从头测试加密流程"""
    print("\n🔄 从头测试加密流程...")

    try:
        from shared.crypto_util import CryptoUtil
        crypto = CryptoUtil()

        # 模拟客户端数据
        original_data = {'password': 'admin123'}
        print(f"📝 原始数据: {original_data}")

        # 加密
        encrypted = crypto.encrypt_request(original_data)
        print(f"🔒 加密结果: {encrypted}")

        # 解密
        decrypted = crypto.decrypt_request(encrypted)
        print(f"🔓 解密结果: {decrypted}")

        # 验证
        password = decrypted.get('password') if isinstance(decrypted, dict) else None
        print(f"🔑 提取的密码: '{password}'")

        return password == 'admin123'

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        traceback.print_exc()
        return False


def check_crypto_util():
    """检查 crypto_util 是否正确导入"""
    print("\n📋 检查 crypto_util 模块...")

    try:
        from shared.crypto_util import CryptoUtil
        print("✅ CryptoUtil 导入成功")

        crypto = CryptoUtil()
        print("✅ CryptoUtil 实例化成功")

        # 检查关键方法是否存在
        if hasattr(crypto, 'encrypt_request'):
            print("✅ encrypt_request 方法存在")
        else:
            print("❌ encrypt_request 方法不存在")

        if hasattr(crypto, 'decrypt_request'):
            print("✅ decrypt_request 方法存在")
        else:
            print("❌ decrypt_request 方法不存在")

        return True

    except Exception as e:
        print(f"❌ CryptoUtil 检查失败: {e}")
        traceback.print_exc()
        return False


def main():
    """主函数"""
    print("🚀 开始调试加密解密问题")
    print("=" * 60)

    # 1. 检查模块导入
    if not check_crypto_util():
        print("💥 请先修复 crypto_util 模块问题")
        return

    # 2. 测试从头加密解密
    if test_encryption_from_scratch():
        print("✅ 基础加密解密测试通过")
    else:
        print("❌ 基础加密解密测试失败")
        return

    # 3. 测试真实的加密数据
    if test_real_encrypted_data():
        print("✅ 真实加密数据解密成功")
        print("🎉 加密解密功能正常，问题可能在服务器端实现")
    else:
        print("❌ 真实加密数据解密失败")
        print("🔧 需要检查客户端和服务器端是否使用相同的加密参数")


if __name__ == "__main__":
    main()