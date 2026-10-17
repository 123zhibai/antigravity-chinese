import os
import shutil
import tempfile
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from config import get_paths, sha256_file
from state import check_asar_is_patched
from engine.injector import perform_patch, restore_official_clean

def test_self_healing_cycle():
    """
    核心文件自愈注入闭环测试 (沙箱隔离安全模式)
    """
    paths = get_paths()
    clean_backup = paths['clean_backup_asar']
    assert os.path.exists(clean_backup), "官方备份不存在！"

    temp_dir = tempfile.mkdtemp(prefix="agy_heal_test_")
    try:
        sandbox_target = os.path.join(temp_dir, "app.asar")
        sandbox_clean = os.path.join(temp_dir, "clean.asar")
        shutil.copy2(clean_backup, sandbox_target)
        shutil.copy2(clean_backup, sandbox_clean)

        print("=== 1. 验证初始沙箱状态 ===")
        is_p1 = check_asar_is_patched(sandbox_target)
        print("初始状态:", "已汉化" if is_p1 else "官方纯净原版")
        assert not is_p1, "初始沙箱副本应为官方原版"

        print("\n=== 2. 触发自愈补丁注入 ===")
        ok, msg = perform_patch(force=True, is_self_healing=True,
                                custom_target_asar=sandbox_target,
                                custom_clean_backup=sandbox_clean)
        print("自愈结果:", ok, msg)
        assert ok, "自愈注入应当成功"

        print("\n=== 3. 检验自愈后状态 ===")
        is_p2 = check_asar_is_patched(sandbox_target)
        print("自愈后状态:", "已汉化" if is_p2 else "未汉化")
        assert is_p2, "自愈后必须恢复汉化状态"

        print("\n=== 4. 检验恢复官方原版 ===")
        res_ok, res_msg = restore_official_clean(custom_target_asar=sandbox_target,
                                                custom_clean_backup=sandbox_clean)
        assert res_ok, "恢复官方原版应当成功"
        assert not check_asar_is_patched(sandbox_target), "恢复后必须为官方纯净状态"

        print("\n[通过] 核心文件自愈注入闭环测试通过！")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == '__main__':
    test_self_healing_cycle()
