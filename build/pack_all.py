# build/pack_all.py
import sys
from pathlib import Path

# 添加构建脚本到路径
sys.path.append(str(Path(__file__).parent))

from pack_updater import pack_updater
from pack_manager import pack_manager


def pack_all():
    """一键打包所有程序"""
    print("=" * 50)
    print("开始打包魔兽世界插件管理系统")
    print("=" * 50)

    success_count = 0
    total_count = 2

    # 打包更新器
    print("\n🔨 1. 打包更新器...")
    if pack_updater():
        success_count += 1
        print("✅ 更新器打包完成")
    else:
        print("❌ 更新器打包失败")

    print("\n" + "-" * 30)

    # 打包管理器
    print("\n🔨 2. 打包管理器...")
    if pack_manager():
        success_count += 1
        print("✅ 管理器打包完成")
    else:
        print("❌ 管理器打包失败")

    # 总结
    print("\n" + "=" * 50)
    print(f"打包完成! 成功: {success_count}/{total_count}")
    print("=" * 50)

    if success_count > 0:
        print("\n📂 输出文件位置:")
        root_dir = Path(__file__).parent.parent
        dist_dir = root_dir / "dist"

        for exe_file in dist_dir.glob("*.exe"):
            if exe_file.exists():
                size_mb = exe_file.stat().st_size / (1024 * 1024)
                print(f"  📄 {exe_file.name} ({size_mb:.1f} MB)")

    return success_count == total_count


if __name__ == "__main__":
    success = pack_all()
    input("\n按回车键退出...")
    sys.exit(0 if success else 1)