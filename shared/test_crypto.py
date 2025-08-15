#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
加密解密测试脚本
用于验证客户端和服务器的加密解密是否一致
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from shared.crypto_util import CryptoUtil


def test_encryption_decryption():
    """测试加密解密功能"""
    print("🔧 开始测试加密解密功能...")

    # 创建加密工具实例
    crypto = CryptoUtil()

    # 测试数据
    test_data = {
        'password': 'admin123',
        'test_field': '测试中文字符',
        'number': 12345
    }

    print(f"📝 原始数据: {test_data}")

    # 测试加密
    print("\n🔒 测试加密...")
    encrypted = crypto.encrypt_request(test_data)
    print(f"✅ 加密结果: {encrypted}")

    if 'error' in encrypted:
        print("❌ 加密失败！")
        return False

    # 测试解密
    print("\n🔓 测试解密...")
    decrypted = crypto.decrypt_request(encrypted)
    print(f"✅ 解密结果: {decrypted}")

    if 'error' in decrypted:
        print("❌ 解密失败！")
        return False

    # 验证数据是否一致
    if decrypted == test_data:
        print("✅ 加密解密测试通过！数据完全一致")
        return True
    else:
        print("❌ 加密解密测试失败！数据不一致")
        print(f"期望: {test_data}")
        print(f"实际: {decrypted}")
        return False


def test_real_login_data():
    """测试真实的登录数据"""
    print("\n🔐 测试真实登录数据...")

    crypto = CryptoUtil()

    # 模拟客户端发送的数据
    login_data = {'password': 'admin123'}

    # 客户端加密
    print("📱 客户端加密数据...")
    encrypted_payload = crypto.encrypt_request(login_data)
    print(f"📦 客户端发送: {encrypted_payload}")

    # 服务器解密
    print("🖥️  服务器解密数据...")
    decrypted_data = crypto.decrypt_request(encrypted_payload)
    print(f"🔍 服务器解析: {decrypted_data}")

    # 检查密码
    password = decrypted_data.get('password')
    print(f"🔑 提取的密码: '{password}'")

    if password == 'admin123':
        print("✅ 登录数据测试通过！")
        return True
    else:
        print("❌ 登录数据测试失败！")
        return False


def test_token_generation():
    """测试令牌生成"""
    print("\n🎫 测试令牌生成...")

    crypto = CryptoUtil()

    # 生成令牌
    token = crypto.generate_token({'admin': True})
    print(f"🎫 生成的令牌: {token[:50]}...")

    if token:
        # 验证令牌
        is_valid, user_data = crypto.verify_token(token)
        print(f"✅ 令牌验证结果: {is_valid}, 用户数据: {user_data}")
        return is_valid
    else:
        print("❌ 令牌生成失败！")
        return False


def main():
    """主测试函数"""
    print("🚀 开始加密解密功能测试")
    print("=" * 50)

    success_count = 0
    total_tests = 3

    # 测试1：基本加密解密
    if test_encryption_decryption():
        success_count += 1

    # 测试2：真实登录数据
    if test_real_login_data():
        success_count += 1

    # 测试3：令牌生成验证
    if test_token_generation():
        success_count += 1

    print("\n" + "=" * 50)
    print(f"📊 测试结果: {success_count}/{total_tests} 通过")

    if success_count == total_tests:
        print("🎉 所有测试通过！加密解密功能正常")
        print("💡 建议：重启服务器以使用更新的加密工具")
    else:
        print("⚠️  部分测试失败，请检查加密工具配置")

    return success_count == total_tests


if __name__ == "__main__":
    main()