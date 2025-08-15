# server/api/updater_api.py
from flask import Blueprint, request, jsonify, current_app
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.crypto_util import CryptoUtil
from server.core.auth import verify_update_code

updater_bp = Blueprint('updater', __name__)
crypto = CryptoUtil()


@updater_bp.route('/verify_code', methods=['POST'])
def verify_code():
    """验证更新码"""
    try:
        encrypted_payload = request.json
        data = crypto.decrypt_request(encrypted_payload)

        addon_name = data.get('addon_name')
        update_code = data.get('update_code')

        if not addon_name or not update_code:
            return jsonify({'success': False, 'message': '缺少必要参数'}), 400

        if verify_update_code(addon_name, update_code):
            return jsonify({'success': True, 'message': '验证成功'})
        else:
            return jsonify({'success': False, 'message': '更新码无效'}), 401

    except Exception as e:
        return jsonify({'success': False, 'message': f'请求处理失败: {str(e)}'}), 400


@updater_bp.route('/addons', methods=['POST'])
def get_addons():
    """获取插件列表"""
    try:
        encrypted_payload = request.json
        data = crypto.decrypt_request(encrypted_payload)

        update_codes = data.get('update_codes', [])

        data_manager = current_app.config['DATA_MANAGER']
        all_addons = data_manager.get_all_addons()

        # 只返回有效更新码对应的插件
        valid_addons = {}
        for addon_name, addon_info in all_addons.items():
            if addon_info.get('update_code') in update_codes:
                valid_addons[addon_name] = {
                    'version': addon_info['version'],
                    'download_url': addon_info['download_url']
                }

        response_data = crypto.encrypt_request({'addons': valid_addons})
        return jsonify(response_data)

    except Exception as e:
        return jsonify({'success': False, 'message': f'请求处理失败: {str(e)}'}), 400


@updater_bp.route('/check_updates', methods=['POST'])
def check_updates():
    """检查更新"""
    try:
        encrypted_payload = request.json
        data = crypto.decrypt_request(encrypted_payload)

        local_addons = data.get('local_addons', {})  # {addon_name: version}
        update_codes = data.get('update_codes', [])

        data_manager = current_app.config['DATA_MANAGER']
        all_addons = data_manager.get_all_addons()

        updates = {}
        for addon_name, local_version in local_addons.items():
            addon_info = all_addons.get(addon_name)
            if (addon_info and
                    addon_info.get('update_code') in update_codes and
                    version_compare(addon_info['version'], local_version) > 0):
                updates[addon_name] = {
                    'current_version': local_version,
                    'latest_version': addon_info['version'],
                    'download_url': addon_info['download_url']
                }

        response_data = crypto.encrypt_request({'updates': updates})
        return jsonify(response_data)

    except Exception as e:
        return jsonify({'success': False, 'message': f'请求处理失败: {str(e)}'}), 400


def version_compare(version1, version2):
    """版本号比较，返回1表示version1>version2，0表示相等，-1表示version1<version2"""

    def version_to_tuple(v):
        return tuple(map(int, v.split('.')))

    v1_tuple = version_to_tuple(version1)
    v2_tuple = version_to_tuple(version2)

    if v1_tuple > v2_tuple:
        return 1
    elif v1_tuple < v2_tuple:
        return -1
    else:
        return 0