# updater/core/downloader.py - 改进版
import os
import zipfile
import requests
from pathlib import Path
import tempfile
import shutil
from urllib.parse import urlparse
import time

from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QMessageBox


class Downloader:
    """文件下载器 - 改进版"""

    def __init__(self, progress_callback=None):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'WoW-Addon-Updater/1.0'
        })
        self.progress_callback = progress_callback

    def set_progress_callback(self, callback):
        """设置进度回调函数"""
        self.progress_callback = callback

    def download_and_install(self, addon_name, download_url, wow_path):
        """下载并安装插件"""
        try:
            print(f"🔽 开始下载插件: {addon_name}")
            print(f"📍 下载地址: {download_url}")
            print(f"📁 WoW路径: {wow_path}")

            # 验证下载地址
            if not self._validate_url(download_url):
                print(f"❌ 无效的下载地址: {download_url}")
                return False

            # 报告开始下载
            self._report_progress(addon_name, "开始下载", 0)

            # 创建临时目录
            with tempfile.TemporaryDirectory() as temp_dir:
                print(f"📂 临时目录: {temp_dir}")

                # 下载文件
                self._report_progress(addon_name, "正在下载", 10)
                zip_path = self._download_file(download_url, temp_dir, addon_name)
                if not zip_path:
                    self._report_progress(addon_name, "下载失败", 0)
                    return False

                print(f"✅ 下载完成: {zip_path}")
                self._report_progress(addon_name, "下载完成", 60)

                # 解压并安装
                self._report_progress(addon_name, "正在安装", 70)
                result = self._extract_and_install(zip_path, addon_name, wow_path)

                if result:
                    print(f"🎉 插件 {addon_name} 安装成功")
                    self._report_progress(addon_name, "安装完成", 100)
                else:
                    print(f"❌ 插件 {addon_name} 安装失败")
                    self._report_progress(addon_name, "安装失败", 0)

                return result

        except Exception as e:
            print(f"❌ 下载安装插件 {addon_name} 失败: {e}")
            import traceback
            traceback.print_exc()
            self._report_progress(addon_name, f"错误: {str(e)}", 0)
            return False

    def _validate_url(self, url):
        """验证下载地址"""
        if not url or not isinstance(url, str):
            return False

        url = url.strip()
        if not url.startswith(('http://', 'https://')):
            return False

        # 排除明显的占位符URL
        invalid_patterns = ['example.com', 'localhost', '127.0.0.1', 'test.com']
        for pattern in invalid_patterns:
            if pattern in url.lower():
                return False

        return True

    def _report_progress(self, addon_name, status, percentage):
        """报告进度"""
        if self.progress_callback:
            try:
                self.progress_callback(addon_name, status, percentage)
            except Exception as e:
                print(f"⚠️ 进度回调失败: {e}")

    def _download_file(self, url, download_dir, addon_name):
        """下载文件 - 带进度报告"""
        try:
            print(f"🌐 开始下载: {url}")

            # 获取文件信息
            response = self.session.head(url, timeout=10)
            response.raise_for_status()

            file_size = int(response.headers.get('Content-Length', 0))
            print(f"📏 文件大小: {file_size / 1024 / 1024:.2f} MB" if file_size > 0 else "📏 文件大小: 未知")

            # 开始下载
            response = self.session.get(url, stream=True, timeout=30)
            response.raise_for_status()

            # 确定文件名
            filename = self._get_filename_from_url(url, response, addon_name)
            file_path = os.path.join(download_dir, filename)
            print(f"💾 保存文件: {filename}")

            # 下载文件并报告进度
            downloaded = 0
            start_time = time.time()

            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)

                        # 每下载1MB报告一次进度
                        if downloaded % (1024 * 1024) == 0 or file_size == 0:
                            if file_size > 0:
                                progress = min(50, int((downloaded / file_size) * 50) + 10)  # 10-60%
                                self._report_progress(addon_name, "正在下载", progress)

                            # 计算下载速度
                            elapsed = time.time() - start_time
                            if elapsed > 0:
                                speed = downloaded / elapsed / 1024 / 1024  # MB/s
                                print(f"⚡ 下载速度: {speed:.2f} MB/s")

            print(f"✅ 下载完成: {filename} ({downloaded / 1024 / 1024:.2f} MB)")
            return file_path

        except requests.exceptions.Timeout:
            print("❌ 下载超时")
            return None
        except requests.exceptions.RequestException as e:
            print(f"❌ 下载请求失败: {e}")
            return None
        except Exception as e:
            print(f"❌ 下载文件失败: {e}")
            return None

    def _get_filename_from_url(self, url, response, addon_name):
        """从URL或响应头获取文件名"""
        # 尝试从Content-Disposition头获取文件名
        content_disposition = response.headers.get('Content-Disposition', '')
        if 'filename=' in content_disposition:
            import re
            filename_match = re.search(r'filename[^=]*=\s*["\']?([^"\';\s]+)', content_disposition)
            if filename_match:
                filename = filename_match.group(1)
                print(f"📋 从响应头获取文件名: {filename}")
                return filename

        # 从URL获取文件名
        parsed_url = urlparse(url)
        filename = os.path.basename(parsed_url.path)

        if filename and '.' in filename:
            print(f"📋 从URL获取文件名: {filename}")
            return filename

        # 使用插件名作为文件名
        filename = f"{addon_name}.zip"
        print(f"📋 使用默认文件名: {filename}")
        return filename

    def _extract_and_install(self, zip_path, addon_name, wow_path):
        """解压并安装插件 - 改进版"""
        try:
            from .wow_detector import WoWDetector

            detector = WoWDetector()
            addon_dir = detector.get_addon_path(wow_path)

            if not addon_dir:
                print("❌ 无法确定插件安装目录")
                return False

            print(f"📁 插件安装目录: {addon_dir}")

            # 备份现有插件
            existing_addon_paths = self._find_existing_addon_paths(addon_dir, addon_name)
            backup_info = []

            for existing_path in existing_addon_paths:
                if os.path.exists(existing_path):
                    backup_path = f"{existing_path}.backup_{int(time.time())}"
                    print(f"💾 备份现有插件: {existing_path} -> {backup_path}")
                    shutil.copytree(existing_path, backup_path)
                    backup_info.append((existing_path, backup_path))
                    shutil.rmtree(existing_path)

            try:
                self._report_progress(addon_name, "正在解压", 80)

                # 解压文件
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    # 检查压缩包结构并解压
                    extract_result = self._smart_extract(zip_ref, addon_name, addon_dir)

                if not extract_result:
                    raise Exception("解压失败")

                self._report_progress(addon_name, "正在验证", 90)

                # 验证安装
                if self._validate_installation(addon_name, addon_dir):
                    # 删除备份
                    for _, backup_path in backup_info:
                        if os.path.exists(backup_path):
                            shutil.rmtree(backup_path)
                            print(f"🗑️ 删除备份: {backup_path}")
                    return True
                else:
                    raise Exception("安装验证失败")

            except Exception as e:
                print(f"❌ 安装过程失败: {e}")
                # 恢复备份
                for existing_path, backup_path in backup_info:
                    if os.path.exists(backup_path):
                        if os.path.exists(existing_path):
                            shutil.rmtree(existing_path)
                        shutil.copytree(backup_path, existing_path)
                        shutil.rmtree(backup_path)
                        print(f"🔄 恢复备份: {backup_path} -> {existing_path}")
                return False

        except Exception as e:
            print(f"❌ 解压安装失败: {e}")
            return False

    def _find_existing_addon_paths(self, addon_dir, addon_name):
        """查找现有的插件路径（可能有多个目录）"""
        paths = []

        # 直接匹配的目录
        direct_path = os.path.join(addon_dir, addon_name)
        if os.path.exists(direct_path):
            paths.append(direct_path)

        # 查找相似名称的目录
        try:
            for item in os.listdir(addon_dir):
                item_path = os.path.join(addon_dir, item)
                if os.path.isdir(item_path):
                    # 不区分大小写匹配
                    if item.lower() == addon_name.lower() and item_path not in paths:
                        paths.append(item_path)
                    # 包含匹配（小心使用）
                    elif addon_name.lower() in item.lower() and len(item) - len(addon_name) <= 5:
                        paths.append(item_path)
        except Exception as e:
            print(f"⚠️ 扫描现有插件目录失败: {e}")

        return paths

    def _smart_extract(self, zip_ref, addon_name, addon_dir):
        """智能解压 - 处理各种压缩包结构"""
        try:
            file_list = zip_ref.namelist()
            print(f"📦 压缩包包含 {len(file_list)} 个文件")

            # 分析压缩包结构
            top_level_items = set()
            for file_path in file_list:
                if '/' in file_path:
                    top_item = file_path.split('/')[0]
                    top_level_items.add(top_item)
                else:
                    top_level_items.add(file_path)

            print(f"📋 顶级项目: {list(top_level_items)}")

            # 情况1: 压缩包直接包含插件文件
            if any(f.endswith('.toc') for f in file_list if '/' not in f):
                print("📂 情况1: 压缩包直接包含插件文件")
                target_path = os.path.join(addon_dir, addon_name)
                os.makedirs(target_path, exist_ok=True)
                zip_ref.extractall(target_path)
                return True

            # 情况2: 压缩包包含单个插件目录
            elif len(top_level_items) == 1 and not any(f.endswith(('.txt', '.md', '.pdf')) for f in top_level_items):
                top_item = list(top_level_items)[0]
                print(f"📂 情况2: 压缩包包含单个目录: {top_item}")

                # 检查这个目录是否包含.toc文件
                toc_files = [f for f in file_list if f.startswith(f"{top_item}/") and f.endswith('.toc')]
                if toc_files:
                    # 解压到addon_dir，然后重命名
                    zip_ref.extractall(addon_dir)
                    extracted_path = os.path.join(addon_dir, top_item)
                    target_path = os.path.join(addon_dir, addon_name)

                    if extracted_path != target_path:
                        if os.path.exists(target_path):
                            shutil.rmtree(target_path)
                        os.rename(extracted_path, target_path)
                        print(f"📂 重命名: {top_item} -> {addon_name}")
                    return True

            # 情况3: 压缩包包含多个插件目录
            elif len(top_level_items) > 1:
                print(f"📂 情况3: 压缩包包含多个目录")

                # 查找与插件名最匹配的目录
                best_match = None
                best_score = 0

                for item in top_level_items:
                    if not any(f.startswith(f"{item}/") and f.endswith('.toc') for f in file_list):
                        continue

                    score = self._calculate_name_similarity(addon_name, item)
                    print(f"📊 目录 {item} 相似度: {score:.3f}")

                    if score > best_score:
                        best_match = item
                        best_score = score

                if best_match and best_score > 0.5:
                    print(f"📂 选择最佳匹配目录: {best_match}")
                    zip_ref.extractall(addon_dir)

                    extracted_path = os.path.join(addon_dir, best_match)
                    target_path = os.path.join(addon_dir, addon_name)

                    if extracted_path != target_path:
                        if os.path.exists(target_path):
                            shutil.rmtree(target_path)
                        os.rename(extracted_path, target_path)
                        print(f"📂 重命名: {best_match} -> {addon_name}")

                    # 清理其他解压的目录
                    for item in top_level_items:
                        if item != best_match:
                            item_path = os.path.join(addon_dir, item)
                            if os.path.exists(item_path):
                                shutil.rmtree(item_path)
                                print(f"🗑️ 清理: {item}")

                    return True

            # 情况4: 无法识别结构，直接解压到插件目录
            print("📂 情况4: 无法识别结构，使用默认解压")
            target_path = os.path.join(addon_dir, addon_name)
            os.makedirs(target_path, exist_ok=True)
            zip_ref.extractall(target_path)
            return True

        except Exception as e:
            print(f"❌ 智能解压失败: {e}")
            return False

    def _calculate_name_similarity(self, name1, name2):
        """计算名称相似度"""
        name1_lower = name1.lower()
        name2_lower = name2.lower()

        if name1_lower == name2_lower:
            return 1.0

        if name1_lower in name2_lower or name2_lower in name1_lower:
            return 0.8

        # 简单的相似度计算
        common_chars = set(name1_lower) & set(name2_lower)
        total_chars = set(name1_lower) | set(name2_lower)

        return len(common_chars) / len(total_chars) if total_chars else 0.0

    def _validate_installation(self, addon_name, addon_dir):
        """验证插件安装是否成功 - 改进版"""
        addon_path = os.path.join(addon_dir, addon_name)

        if not os.path.exists(addon_path):
            print(f"❌ 插件目录不存在: {addon_path}")
            return False

        # 检查是否存在.toc文件
        toc_files = []
        try:
            for file in os.listdir(addon_path):
                if file.endswith('.toc'):
                    toc_files.append(file)

            if toc_files:
                print(f"✅ 找到TOC文件: {toc_files}")
                return True
            else:
                print(f"❌ 未找到TOC文件在: {addon_path}")

                # 列出目录内容用于调试
                try:
                    contents = os.listdir(addon_path)
                    print(f"📋 目录内容: {contents}")
                except Exception as e:
                    print(f"⚠️ 无法列出目录内容: {e}")

                return False

        except Exception as e:
            print(f"❌ 验证安装时发生错误: {e}")
            return False


# 为DownloadThread提供的包装函数
def download_addon_with_progress(addon_name, download_url, wow_path, progress_callback=None):
    """下载插件的便捷函数"""
    downloader = Downloader(progress_callback)
    return downloader.download_and_install(addon_name, download_url, wow_path)


# 在 downloader.py 中添加文件验证
def validate_downloaded_file(self, file_path):
    """验证下载的文件"""
    try:
        if not os.path.exists(file_path):
            return False, "文件不存在"

        file_size = os.path.getsize(file_path)
        if file_size == 0:
            return False, "文件大小为0"

        # 检查文件头，确认是ZIP文件
        with open(file_path, 'rb') as f:
            header = f.read(4)

        # ZIP文件的魔数
        zip_signatures = [
            b'PK\x03\x04',  # 标准ZIP
            b'PK\x05\x06',  # 空ZIP
            b'PK\x07\x08'  # ZIP with data descriptor
        ]

        if not any(header.startswith(sig) for sig in zip_signatures):
            # 检查文件内容是否为HTML
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(1000)
                if '<html' in content.lower() or '<!doctype' in content.lower():
                    return False, "下载的是HTML页面，不是ZIP文件。可能是网盘分享页面。"

            return False, "文件不是有效的ZIP格式"

        return True, "文件验证通过"

    except Exception as e:
        return False, f"文件验证失败: {str(e)}"

# 更新后的DownloadThread，与改进的下载器完美集成

class DownloadThread(QThread):
    progress = pyqtSignal(str, str)
    finished = pyqtSignal(bool, str)

    def __init__(self, wow_path, addons, update_codes):
        super().__init__()
        self.wow_path = wow_path
        self.addons = addons
        self.update_codes = update_codes

    def run(self):
        try:
            from updater.core.downloader import Downloader
            from updater.core.api_client import APIClient

            downloader = Downloader()
            api_client = APIClient()

            # 首先获取完整的插件信息，包括下载地址
            addon_info_map = {}
            try:
                # 从服务器获取插件列表，包含真实下载地址
                response = api_client.get_addon_list(self.update_codes)
                if response.get('success'):
                    server_addons = response.get('addons', {})

                    # 建立插件名到下载信息的映射
                    for server_name, server_info in server_addons.items():
                        addon_info_map[server_name.lower()] = {
                            'download_url': server_info.get('download_url'),
                            'update_code': server_info.get('update_code'),
                            'url_status': server_info.get('url_status', 'unknown')
                        }

                        # 也为可能的匹配名称创建映射
                        addon_info_map[server_name] = addon_info_map[server_name.lower()]

            except Exception as e:
                self.finished.emit(False, f"获取插件信息失败: {str(e)}")
                return

            success_count = 0
            fail_count = 0

            for addon in self.addons:
                addon_name = addon['name']
                self.progress.emit(addon_name, "downloading")

                # 查找对应的下载地址
                download_url = None
                url_status = 'unknown'

                # 尝试多种匹配方式
                for key in [addon_name, addon_name.lower()]:
                    if key in addon_info_map:
                        download_url = addon_info_map[key]['download_url']
                        url_status = addon_info_map[key]['url_status']
                        break

                # 如果没有精确匹配，尝试模糊匹配
                if not download_url:
                    for server_name, info in addon_info_map.items():
                        if (addon_name.lower() in server_name.lower() or
                                server_name.lower() in addon_name.lower()):
                            download_url = info['download_url']
                            url_status = info['url_status']
                            break

                if not download_url:
                    self.progress.emit(addon_name, "failed")
                    fail_count += 1
                    print(f"❌ 未找到插件 {addon_name} 的下载地址")
                    continue

                # 检查URL状态
                if url_status == 'invalid':
                    self.progress.emit(addon_name, "failed")
                    fail_count += 1
                    print(f"❌ 插件 {addon_name} 的下载地址无效")
                    continue

                print(f"🔽 开始下载插件: {addon_name}")
                print(f"📍 下载地址: {download_url}")
                print(f"📁 WoW路径: {self.wow_path}")

                try:
                    success = downloader.download_and_install(
                        addon_name, download_url, self.wow_path
                    )

                    if success:
                        self.progress.emit(addon_name, "completed")
                        success_count += 1
                        print(f"✅ 插件 {addon_name} 更新成功")
                    else:
                        self.progress.emit(addon_name, "failed")
                        fail_count += 1
                        print(f"❌ 插件 {addon_name} 更新失败")

                except Exception as e:
                    self.progress.emit(addon_name, "failed")
                    fail_count += 1
                    print(f"❌ 插件 {addon_name} 下载异常: {str(e)}")

            # 构建结果消息
            total = len(self.addons)
            if success_count == total:
                message = f"所有 {total} 个插件更新完成"
                self.finished.emit(True, message)
            elif success_count > 0:
                message = f"部分插件更新完成: 成功 {success_count}/{total}"
                self.finished.emit(True, message)
            else:
                message = f"所有插件更新失败: {fail_count}/{total}"
                self.finished.emit(False, message)

        except Exception as e:
            self.finished.emit(False, f"更新过程出现异常: {str(e)}")


# 同时更新主窗口中的进度处理方法
def on_download_progress(self, addon_name, status):
    """下载进度回调 - 改进版"""
    current_value = self.progress_bar.value()

    if status == "completed":
        self.progress_bar.setValue(current_value + 1)
        self.log(f"✅ 插件 {addon_name} 更新完成")
    elif status == "failed":
        self.progress_bar.setValue(current_value + 1)
        self.log(f"❌ 插件 {addon_name} 更新失败")
    elif status == "downloading":
        self.log(f"⬇️ 正在下载插件 {addon_name}...")
    elif status == "准备下载":
        self.log(f"📋 准备下载插件 {addon_name}")
    else:
        self.log(f"📝 插件 {addon_name}: {status}")


def on_detailed_download_progress(self, addon_name, status, percentage):
    """详细下载进度回调 - 新增"""
    # 更新当前插件的详细状态
    if percentage > 0:
        self.log(f"📊 {addon_name}: {status} ({percentage}%)")
    else:
        self.log(f"📝 {addon_name}: {status}")

    # 可以在这里更新更详细的进度显示，比如单个插件的进度条


# 修改主窗口的start_update方法以支持详细进度
def start_update(self, addons):
    """开始更新插件"""
    wow_path = self.path_label.text()
    if not wow_path:
        QMessageBox.warning(self, "提示", "请先设置魔兽世界路径")
        return

    # 检查是否有有效的更新码
    if not hasattr(self, 'valid_update_codes') or not self.valid_update_codes:
        QMessageBox.warning(self, "提示", "请先验证更新码")
        return

    self.progress_bar.setVisible(True)
    self.progress_bar.setRange(0, len(addons))
    self.progress_bar.setValue(0)

    self.log(f"开始更新 {len(addons)} 个插件...")

    # 禁用按钮
    self.update_selected_btn.setEnabled(False)
    self.update_all_btn.setEnabled(False)

    # 启动下载线程 - 添加 self.valid_update_codes 参数
    self.download_thread = DownloadThread(wow_path, addons, self.valid_update_codes)
    self.download_thread.progress.connect(self.on_download_progress)
    self.download_thread.finished.connect(self.on_download_finished)
    self.download_thread.start()