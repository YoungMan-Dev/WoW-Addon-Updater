# build/pack_updater.py - 修复版
import subprocess
import os
import shutil
from pathlib import Path


def pack_updater():
    """打包更新器为单个exe文件"""
    print("🚀 开始打包更新器...")

    root_dir = Path(__file__).parent.parent
    updater_dir = root_dir / "updater"
    dist_dir = root_dir / "dist"
    assets_dir = updater_dir / "assets"
    shared_dir = root_dir / "shared"
    build_dir = root_dir / "build"

    # 确保目录存在
    dist_dir.mkdir(exist_ok=True)
    assets_dir.mkdir(exist_ok=True)
    build_dir.mkdir(exist_ok=True)

    print(f"📁 项目目录: {root_dir}")
    print(f"📁 更新器目录: {updater_dir}")
    print(f"📁 资源目录: {assets_dir}")
    print(f"📁 输出目录: {dist_dir}")

    # 检查assets目录中的文件
    print(f"\n📋 检查资源文件:")
    if assets_dir.exists():
        asset_files = list(assets_dir.iterdir())
        if asset_files:
            for file in asset_files:
                print(f"  📄 {file.name} ({'目录' if file.is_dir() else '文件'})")
        else:
            print("  ⚠️ assets目录为空")
    else:
        print("  ❌ assets目录不存在")

    # 检查图标文件
    icon_file = assets_dir / "icon.ico"
    icon_param = f"--icon={icon_file}" if icon_file.exists() else ""
    if icon_param:
        print(f"🎨 找到图标文件: {icon_file}")
    else:
        print("⚠️ 未找到icon.ico文件")

    # 检查主程序文件
    main_file = updater_dir / "main.py"
    if not main_file.exists():
        print(f"❌ 主程序文件不存在: {main_file}")
        return False

    # 构建PyInstaller命令
    cmd = [
        "pyinstaller",
        "--onefile",  # 单文件打包
        "--windowed",  # 无控制台窗口
        "--name", "WoW-Addon-Updater",  # 程序名称
        "--clean",  # 清理临时文件
        "--noconfirm",  # 不询问覆盖
    ]

    # 添加图标参数
    if icon_param:
        cmd.append(icon_param)

    # 添加资源文件 - 关键修复
    # 方式1: 添加整个assets目录
    if assets_dir.exists() and list(assets_dir.iterdir()):
        # 使用正确的格式添加assets目录
        cmd.extend([
            "--add-data", f"{assets_dir}{os.pathsep}assets"
        ])
        print(f"📦 添加资源目录: {assets_dir} -> assets")

    # 方式2: 单独添加每个资源文件（更可靠）
    if assets_dir.exists():
        for asset_file in assets_dir.iterdir():
            if asset_file.is_file():
                cmd.extend([
                    "--add-data", f"{asset_file}{os.pathsep}assets"
                ])
                print(f"📦 添加资源文件: {asset_file.name}")

    # 添加shared目录
    if shared_dir.exists():
        cmd.extend([
            "--add-data", f"{shared_dir}{os.pathsep}shared"
        ])
        print(f"📦 添加共享模块: {shared_dir}")

    # 设置输出和工作目录
    cmd.extend([
        "--distpath", str(dist_dir),
        "--workpath", str(build_dir / "temp"),
        "--specpath", str(build_dir),
    ])

    # 添加主程序文件
    cmd.append(str(main_file))

    print(f"\n🔨 执行PyInstaller命令:")
    print(f"   {' '.join(cmd)}")

    try:
        # 切换到根目录（重要！）
        original_cwd = os.getcwd()
        os.chdir(root_dir)

        # 执行打包命令
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)

        print("\n✅ 更新器打包成功!")

        # 检查输出文件
        exe_file = dist_dir / "WoW-Addon-Updater.exe"
        if exe_file.exists():
            size_mb = exe_file.stat().st_size / (1024 * 1024)
            print(f"📁 输出文件: {exe_file}")
            print(f"📏 文件大小: {size_mb:.1f} MB")

            # 测试exe文件是否能找到资源
            print(f"\n🧪 验证资源文件打包:")
            test_resources(exe_file)
        else:
            print(f"❌ 未找到输出文件: {exe_file}")
            return False

        return True

    except subprocess.CalledProcessError as e:
        print(f"\n❌ 打包失败!")
        print(f"错误代码: {e.returncode}")
        if e.stdout:
            print(f"标准输出:\n{e.stdout}")
        if e.stderr:
            print(f"错误输出:\n{e.stderr}")
        return False

    except Exception as e:
        print(f"\n❌ 打包过程中发生异常: {e}")
        return False

    finally:
        # 恢复原始工作目录
        os.chdir(original_cwd)


def test_resources(exe_file):
    """测试打包的exe是否包含资源文件"""
    try:
        # 使用PyInstaller的archive_viewer来检查打包内容
        import subprocess

        # 尝试运行pyi-archive_viewer
        try:
            result = subprocess.run(
                ["pyi-archive_viewer", str(exe_file)],
                input="X\n",  # 退出命令
                capture_output=True,
                text=True,
                timeout=10
            )

            if "assets" in result.stdout:
                print("✅ 资源文件已包含在exe中")
            else:
                print("⚠️ 未在exe中检测到assets目录")

        except (subprocess.TimeoutExpired, FileNotFoundError):
            print("ℹ️ 无法验证资源文件（pyi-archive_viewer不可用）")

    except Exception as e:
        print(f"⚠️ 资源验证失败: {e}")


def create_spec_file():
    """创建.spec文件用于更精确的打包控制"""
    root_dir = Path(__file__).parent.parent
    updater_dir = root_dir / "updater"
    assets_dir = updater_dir / "assets"
    shared_dir = root_dir / "shared"
    build_dir = root_dir / "build"

    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# 收集资源文件
datas = []

# 添加assets目录中的所有文件
import os
assets_dir = r"{assets_dir}"
if os.path.exists(assets_dir):
    for root, dirs, files in os.walk(assets_dir):
        for file in files:
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, assets_dir)
            datas.append((file_path, os.path.join('assets', rel_path)))

# 添加shared目录
shared_dir = r"{shared_dir}"
if os.path.exists(shared_dir):
    for root, dirs, files in os.walk(shared_dir):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, shared_dir)
                datas.append((file_path, os.path.join('shared', rel_path)))

a = Analysis(
    [r"{updater_dir / 'main.py'}"],
    pathex=[r"{root_dir}"],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='WoW-Addon-Updater',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=r"{assets_dir / 'icon.ico'}" if (assets_dir / 'icon.ico').exists() else None,
)
'''

    spec_file = build_dir / "WoW-Addon-Updater.spec"
    with open(spec_file, 'w', encoding='utf-8') as f:
        f.write(spec_content)

    print(f"📝 创建spec文件: {spec_file}")
    return spec_file


def pack_with_spec():
    """使用spec文件打包（更可靠的方法）"""
    print("🚀 使用spec文件打包更新器...")

    root_dir = Path(__file__).parent.parent
    dist_dir = root_dir / "dist"

    # 创建spec文件
    spec_file = create_spec_file()

    try:
        original_cwd = os.getcwd()
        os.chdir(root_dir)

        cmd = [
            "pyinstaller",
            "--clean",
            "--noconfirm",
            "--distpath", str(dist_dir),
            str(spec_file)
        ]

        print(f"🔨 执行命令: {' '.join(cmd)}")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)

        print("✅ spec文件打包成功!")

        exe_file = dist_dir / "WoW-Addon-Updater.exe"
        if exe_file.exists():
            size_mb = exe_file.stat().st_size / (1024 * 1024)
            print(f"📁 输出文件: {exe_file}")
            print(f"📏 文件大小: {size_mb:.1f} MB")

        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ spec文件打包失败: {e}")
        if e.stdout:
            print(f"输出: {e.stdout}")
        if e.stderr:
            print(f"错误: {e.stderr}")
        return False
    finally:
        os.chdir(original_cwd)


if __name__ == "__main__":
    print("选择打包方式:")
    print("1. 标准打包")
    print("2. 使用spec文件打包（推荐）")

    choice = input("请选择 (1/2): ").strip()

    if choice == "2":
        success = pack_with_spec()
    else:
        success = pack_updater()

    if success:
        print("\n🎉 打包完成！")
    else:
        print("\n💥 打包失败！")

    input("按任意键退出...")