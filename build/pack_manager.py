# build/pack_manager.py
import subprocess
import os
from pathlib import Path


def pack_manager():
    """打包管理器为单个exe文件"""
    print("开始打包管理器...")

    root_dir = Path(__file__).parent.parent
    manager_dir = root_dir / "manager"
    dist_dir = root_dir / "dist"
    shared_dir = root_dir / "shared"

    # 确保目录存在
    dist_dir.mkdir(exist_ok=True)

    # PyInstaller命令
    cmd = [
        "pyinstaller",
        "--onefile",  # 单文件打包
        "--windowed",  # 无控制台窗口
        "--name", "WoW-Addon-Manager",  # 程序名称
        f"--add-data={shared_dir};shared",  # 添加共享模块
        "--distpath", str(dist_dir),  # 输出目录
        "--workpath", str(root_dir / "build" / "temp"),  # 工作目录
        "--specpath", str(root_dir / "build"),  # spec文件位置
        "--clean",  # 清理临时文件
        str(manager_dir / "main.py")  # 主程序文件
    ]

    try:
        # 切换到manager目录
        os.chdir(manager_dir)

        print(f"执行命令: {' '.join(cmd)}")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)

        print("✅ 管理器打包成功!")
        print(f"📁 输出文件: {dist_dir / 'WoW-Addon-Manager.exe'}")

        # 显示文件大小
        exe_file = dist_dir / "WoW-Addon-Manager.exe"
        if exe_file.exists():
            size_mb = exe_file.stat().st_size / (1024 * 1024)
            print(f"📏 文件大小: {size_mb:.1f} MB")

        return True

    except subprocess.CalledProcessError as e:
        print("❌ 打包失败!")
        print(f"错误: {e}")
        print(f"输出: {e.stdout}")
        print(f"错误输出: {e.stderr}")
        return False


if __name__ == "__main__":
    pack_manager()