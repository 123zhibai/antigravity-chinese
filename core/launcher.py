import os
import sys
import subprocess

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from .config import get_paths
    from .state import get_current_status
    from .engine.injector import perform_patch
    from .logger import log_event
except ImportError:
    from config import get_paths
    from state import get_current_status
    from engine.injector import perform_patch
    from logger import log_event

def launch_antigravity(extra_args=None):
    """
    智能启动器：检查状态 -> 必要时自动修复/自愈 -> 启动 Antigravity
    """
    paths = get_paths()
    if not paths:
        print("[错误] 未找到 Antigravity 安装目录，请确认客户端已安装。")
        return False

    exe_path = paths['exe_path']
    if not os.path.exists(exe_path):
        print(f"[错误] 未找到可执行文件: {exe_path}")
        return False

    # 1. 检查当前状态
    status = get_current_status()

    # 2. 如果未汉化或检测到官方更新，执行秒级自愈
    if not status.get('is_patched') or status.get('has_update'):
        print("[自愈系统] 检测到 Antigravity 官方更新或汉化未生效，正在自动执行无感自愈补丁...")
        log_event("LAUNCH", "检测到官方版本更新或汉化失效，启动自动自愈...")
        ok, msg = perform_patch(force=True, is_self_healing=True)
        if ok:
            print(f"[自愈系统] 自愈成功！{msg}")
        else:
            print(f"[警告] 自愈遇到问题: {msg}，正在以安全模式启动原版 Antigravity。")

    # 3. 启动 Antigravity
    cmd = [exe_path]
    if extra_args:
        cmd.extend(extra_args)

    log_event("LAUNCH", f"正在拉起 Antigravity 客户端: {exe_path}")
    print("[启动器] 正在启动 Antigravity (简体中文版)...")

    # 使用 Windows DETACHED_PROCESS 或 Popen 异步启动，不挂起终端
    DETACHED_PROCESS = 0x00000008
    try:
        subprocess.Popen(cmd, creationflags=DETACHED_PROCESS, close_fds=True)
        return True
    except Exception as e:
        print(f"[错误] 启动进程失败: {e}")
        return False

if __name__ == '__main__':
    launch_antigravity(sys.argv[1:])
