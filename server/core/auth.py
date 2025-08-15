# server/core/auth.py
import hashlib
from functools import wraps
from flask import request, jsonify, current_app
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.crypto_util import CryptoUtil

crypto = CryptoUtil()

# 管理员密码哈希 (默认密码: admin123)
ADMIN_PASSWORD_HASH = crypto.hash_password("admin123")


def require_auth(f):
    """需要认证的装饰器"""

    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Missing authorization header'}), 401

        token = auth_header[7:]  # 移除 "Bearer " 前缀
        if not verify_token(token):
            return jsonify({'error': 'Invalid token'}), 401

        return f(*args, **kwargs)

    return decorated


def verify_token(token):
    """验证令牌"""
    try:
        # 简单的token验证，实际项目中应该使用JWT
        expected_token = hashlib.sha256(f"{ADMIN_PASSWORD_HASH}_token".encode()).hexdigest()
        return token == expected_token
    except:
        return False


def generate_token():
    """生成令牌"""
    return hashlib.sha256(f"{ADMIN_PASSWORD_HASH}_token".encode()).hexdigest()


def verify_admin_password(password):
    """验证管理员密码"""
    return crypto.hash_password(password) == ADMIN_PASSWORD_HASH


def verify_update_code(addon_name, update_code):
    """验证更新码"""
    data_manager = current_app.config['DATA_MANAGER']
    addon_info = data_manager.get_addon(addon_name)
    if not addon_info:
        return False
    return addon_info.get('update_code') == update_code
