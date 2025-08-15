# server/api/manager_api.py - 增强版本，添加缺失的路由
from flask import Blueprint, request, jsonify, current_app
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.crypto_util import CryptoUtil
from server.core.auth import require_auth, verify_admin_password, generate_token

manager_bp = Blueprint('manager', __name__)
crypto = CryptoUtil()

def safe_decrypt(request_data):
    """安全解密函数，支持明文和加密数据"""
    try:
        print(f"📥 收到请求数据: {request_data}")

        # 检查是否为加密数据
        if isinstance(request_data, dict) and 'encrypted_data' in request_data:
            print("🔒 检测到加密数据，尝试解密...")
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
                # 解密失败，fallback到明文
                return request_data, False
        else:
            print("📝 检测到明文数据")
            return request_data, False

    except Exception as e:
        print(f"💥 数据处理异常: {e}")
        return request_data, False

def safe_encrypt_response(data):
    """安全加密响应函数"""
    try:
        print(f"📤 准备响应数据: {data}")
        # 暂时不加密响应，直接返回明文
        return data

        # 如果需要加密响应，取消注释下面的代码
        # encrypted = crypto.encrypt_request(data)
        # if 'error' not in encrypted:
        #     print("✅ 响应已加密")
        #     return encrypted
        # else:
        #     print("⚠️ 响应加密失败，返回明文")
        #     return data

    except Exception as e:
        print(f"⚠️ 响应加密失败: {e}")
        return data

@manager_bp.route('/login', methods=['POST'])
def login():
    """管理员登录"""
    try:
        request_data = request.json
        data, was_encrypted = safe_decrypt(request_data)

        # 提取密码
        password = None
        if isinstance(data, dict):
            password = data.get('password')

        print(f"🔑 提取的密码: '{password}'")

        if not password:
            print("❌ 密码为空或提取失败")
            return jsonify({
                'success': False,
                'message': '密码不能为空或数据解析失败'
            }), 400

        if verify_admin_password(password):
            print("✅ 密码验证成功")
            token = generate_token()

            response_data = {
                'success': True,
                'message': '登录成功',
                'token': token
            }

            final_response = safe_encrypt_response(response_data)
            print(f"📤 返回响应: {final_response}")
            return jsonify(final_response)
        else:
            print("❌ 密码错误")
            return jsonify({
                'success': False,
                'message': '密码错误'
            }), 401

    except Exception as e:
        print(f"💥 登录处理异常: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'请求处理失败: {str(e)}'
        }), 500

@manager_bp.route('/addons', methods=['GET'])
@require_auth
def get_all_addons():
    """获取所有插件信息"""
    try:
        print("📥 收到获取插件列表请求")
        data_manager = current_app.config['DATA_MANAGER']
        addons = data_manager.get_all_addons()

        response_data = {
            'success': True,
            'addons': addons
        }
        print(f"📦 返回 {len(addons)} 个插件")

        final_response = safe_encrypt_response(response_data)
        return jsonify(final_response)

    except Exception as e:
        print(f"💥 获取插件列表异常: {e}")
        return jsonify({
            'success': False,
            'message': f'请求处理失败: {str(e)}'
        }), 500

@manager_bp.route('/addons', methods=['POST'])
@require_auth
def add_addon():
    """添加插件"""
    try:
        request_data = request.json
        data, was_encrypted = safe_decrypt(request_data)

        print(f"📋 解析的数据: {data}")

        # 提取字段
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
            return jsonify({
                'success': False,
                'message': error_msg
            }), 400

        # 构建插件信息
        from datetime import datetime
        current_time = datetime.now().isoformat()

        addon_info = {
            'version': version,
            'download_url': download_url,
            'update_code': update_code,
            'created_at': current_time,
            'updated_at': current_time
        }

        # 保存插件
        data_manager = current_app.config['DATA_MANAGER']
        data_manager.add_or_update_addon(addon_name, addon_info)
        print(f"✅ 插件 {addon_name} 添加成功")

        response_data = {
            'success': True,
            'message': '插件添加成功',
            'update_code': update_code
        }

        final_response = safe_encrypt_response(response_data)
        return jsonify(final_response)

    except Exception as e:
        print(f"💥 添加插件异常: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'请求处理失败: {str(e)}'
        }), 500

@manager_bp.route('/addons/<addon_name>', methods=['DELETE'])
@require_auth
def delete_addon(addon_name):
    """删除插件"""
    try:
        print(f"📥 收到删除插件请求: {addon_name}")

        data_manager = current_app.config['DATA_MANAGER']
        if data_manager.delete_addon(addon_name):
            print(f"✅ 插件 {addon_name} 删除成功")
            response_data = {
                'success': True,
                'message': '插件删除成功'
            }

            final_response = safe_encrypt_response(response_data)
            return jsonify(final_response)
        else:
            print(f"❌ 插件 {addon_name} 不存在")
            return jsonify({
                'success': False,
                'message': '插件不存在'
            }), 404

    except Exception as e:
        print(f"💥 删除插件异常: {e}")
        return jsonify({
            'success': False,
            'message': f'请求处理失败: {str(e)}'
        }), 500

@manager_bp.route('/addons/<addon_name>/url', methods=['PUT'])
@require_auth
def update_addon_url(addon_name):
    """更新插件下载地址"""
    try:
        request_data = request.json
        data, was_encrypted = safe_decrypt(request_data)

        print(f"📋 解析的数据: {data}")

        new_url = data.get('download_url')
        if not new_url:
            print("❌ 下载地址为空")
            return jsonify({
                'success': False,
                'message': '下载地址不能为空'
            }), 400

        data_manager = current_app.config['DATA_MANAGER']
        if data_manager.update_addon_url(addon_name, new_url):
            print(f"✅ 插件 {addon_name} URL更新成功")
            response_data = {
                'success': True,
                'message': '下载地址更新成功'
            }

            final_response = safe_encrypt_response(response_data)
            return jsonify(final_response)
        else:
            print(f"❌ 插件 {addon_name} 不存在")
            return jsonify({
                'success': False,
                'message': '插件不存在'
            }), 404

    except Exception as e:
        print(f"💥 更新插件URL异常: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'请求处理失败: {str(e)}'
        }), 500

@manager_bp.route('/addons/<addon_name>/update_code', methods=['PUT'])
@require_auth
def update_addon_update_code(addon_name):
    """更新插件更新码"""
    try:
        request_data = request.json
        data, was_encrypted = safe_decrypt(request_data)

        print(f"📋 解析的数据: {data}")

        new_update_code = data.get('update_code')
        if not new_update_code:
            print("❌ 更新码为空")
            return jsonify({
                'success': False,
                'message': '更新码不能为空'
            }), 400

        data_manager = current_app.config['DATA_MANAGER']
        if data_manager.update_addon_update_code(addon_name, new_update_code):
            print(f"✅ 插件 {addon_name} 更新码更新成功")
            response_data = {
                'success': True,
                'message': '更新码更新成功'
            }

            final_response = safe_encrypt_response(response_data)
            return jsonify(final_response)
        else:
            print(f"❌ 插件 {addon_name} 不存在")
            return jsonify({
                'success': False,
                'message': '插件不存在'
            }), 404

    except Exception as e:
        print(f"💥 更新插件更新码异常: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'请求处理失败: {str(e)}'
        }), 500

@manager_bp.route('/addons/batch/update_code', methods=['PUT'])
@require_auth
def batch_update_update_code():
    """批量更新插件更新码"""
    try:
        request_data = request.json
        data, was_encrypted = safe_decrypt(request_data)

        print(f"📋 解析的数据: {data}")

        addon_names = data.get('addon_names', [])
        new_update_code = data.get('update_code')

        if not addon_names or not new_update_code:
            error_msg = '缺少插件名列表或更新码参数'
            print(f"❌ {error_msg}")
            return jsonify({
                'success': False,
                'message': error_msg
            }), 400

        data_manager = current_app.config['DATA_MANAGER']
        if data_manager.batch_update_update_code(addon_names, new_update_code):
            print(f"✅ 批量更新 {len(addon_names)} 个插件的更新码成功")
            response_data = {
                'success': True,
                'message': f'成功为 {len(addon_names)} 个插件更新了更新码',
                'updated_count': len(addon_names),
                'new_update_code': new_update_code
            }

            final_response = safe_encrypt_response(response_data)
            return jsonify(final_response)
        else:
            print(f"❌ 批量更新插件更新码失败")
            return jsonify({
                'success': False,
                'message': '批量更新插件更新码失败'
            }), 400

    except Exception as e:
        print(f"💥 批量更新插件更新码异常: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'请求处理失败: {str(e)}'
        }), 500

@manager_bp.route('/stats', methods=['GET'])
@require_auth
def get_stats():
    """获取统计信息"""
    try:
        print("📥 收到获取统计信息请求")
        data_manager = current_app.config['DATA_MANAGER']
        stats = data_manager.get_stats()

        response_data = {
            'success': True,
            'stats': stats
        }

        final_response = safe_encrypt_response(response_data)
        return jsonify(final_response)

    except Exception as e:
        print(f"💥 获取统计信息异常: {e}")
        return jsonify({
            'success': False,
            'message': f'请求处理失败: {str(e)}'
        }), 500