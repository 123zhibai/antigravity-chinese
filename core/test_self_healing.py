import os
import shutil
import time
from config import get_paths, sha256_file
from state import get_current_status, check_asar_is_patched
from engine.injector import perform_patch
from launcher import launch_antigravity

def test_full_healing_cycle():
    paths = get_paths()
    asar_path = paths['asar_path']
    clean_backup = paths['clean_backup_asar']

    print("=== 1. 验证当前安装状态 ===")
    assert os.path.exists(clean_backup), "官方备份不存在！"
    st1 = get_current_status()
    print("初始状态:", "已汉化" if st1['is_patched'] else "未汉化")

    print("\n=== 2. 模拟官方自动更新覆盖 (还原纯净版) ===")
    shutil.copy2(clean_backup, asar_path)
    is_p = check_asar_is_patched(asar_path)
    print("模拟覆盖后状态:", "已汉化" if is_p else "官方纯净原版")
    assert not is_p, "覆盖后不应处于汉化状态"

    print("\n=== 3. 模拟触发自愈机制 ===")
    ok, msg = perform_patch(force=True, is_self_healing=True)
    print("自愈结果:", ok, msg)
    assert ok, "自愈应该成功"

    print("\n=== 4. 检验自愈后状态 ===")
    st2 = get_current_status()
    print("自愈后状态:", "已汉化" if st2['is_patched'] else "未汉化")
    print("当前累计自愈次数:", st2['self_healing_count'])
    assert st2['is_patched'], "自愈后必须为汉化状态"
    print("\n[通过] 自愈核心机制全生命周期测试 100% 成功！")

if __name__ == '__main__':
    test_full_healing_cycle()
