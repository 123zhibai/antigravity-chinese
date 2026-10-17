import os
import sys
import time
import subprocess

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from ..config import get_paths, sha256_file
    from ..state import load_state, check_asar_is_patched
    from ..engine.injector import perform_patch
    from ..logger import log_event
except (ImportError, ValueError):
    from config import get_paths, sha256_file
    from state import load_state, check_asar_is_patched
    from engine.injector import perform_patch
    from logger import log_event

def is_antigravity_running():
    """检测当前是否有 Antigravity 进程在运行"""
    try:
        cmd = "Get-Process -Name 'Antigravity' -ErrorAction SilentlyContinue | Measure-Object | Select-Object -ExpandProperty Count"
        out = subprocess.check_output(['powershell', '-NoProfile', '-Command', cmd], text=True, stderr=subprocess.DEVNULL).strip()
        count = int(out) if out.isdigit() else 0
        return count > 0
    except Exception:
        return False

def wait_for_antigravity_exit(timeout=120):
    """等待所有 Antigravity 进程完全退出"""
    start_t = time.time()
    while is_antigravity_running():
        time.sleep(1)
        if time.time() - start_t > timeout:
            return False
    # 额外等待 1 秒确保文件锁释放
    time.sleep(1)
    return True

def run_watcher(poll_interval=3):
    """
    后台 Watch 模式主循环：
    - 周期性比对 app.asar 的特征与 Hash
    - 当发现官方更新覆盖（导致汉化失效）时
    - 等待 Antigravity 客户端完全退出后，自动重新执行汉化
    """
    paths = get_paths()
    if not paths:
        print("[错误] 未找到 Antigravity 路径配置")
        return

    asar_path = paths['asar_path']
    print(f"[Watcher] 后台自愈守护进程已启动...")
    print(f"[Watcher] 正在监控核心文件: {asar_path}")
    print(f"[Watcher] 轮询间隔: {poll_interval}s。按 Ctrl+C 可停止守护。\n")
    log_event("WATCH", "后台守护服务已启动，正在监控核心文件变动...")

    last_known_hash = sha256_file(asar_path)
    last_known_patched = check_asar_is_patched(asar_path)

    try:
        while True:
            time.sleep(poll_interval)
            if not os.path.exists(asar_path):
                continue

            current_hash = sha256_file(asar_path)
            # 检查文件是否变动
            if current_hash != last_known_hash:
                log_event("WATCH", f"检测到核心文件 Hash 变动: {last_known_hash[:8]} -> {current_hash[:8]}")
                time.sleep(1)  # 等待写入完成
                is_patched = check_asar_is_patched(asar_path)

                if not is_patched:
                    print(f"\n[Watcher] 警告: 发现官方更新已覆盖核心文件！当前汉化已失效。")
                    log_event("WATCH", "检测到官方自动更新覆盖，准备执行后台自愈...")

                    if is_antigravity_running():
                        print("[Watcher] Antigravity 进程正在运行，等待客户端退出后自愈...")
                        wait_for_antigravity_exit()

                    print("[Watcher] 客户端已退出，开始执行自动重新汉化...")
                    ok, msg = perform_patch(force=True, is_self_healing=True)
                    if ok:
                        print(f"[Watcher] [成功] 自动无感重打汉化完成！{msg}")
                        log_event("WATCH", f"自愈完成: {msg}")
                    else:
                        print(f"[Watcher] [失败] 自动自愈失败: {msg}")
                        log_event("WATCH", f"自愈失败: {msg}", is_error=True)

                    current_hash = sha256_file(asar_path)
                    is_patched = check_asar_is_patched(asar_path)

                last_known_hash = current_hash
                last_known_patched = is_patched

    except KeyboardInterrupt:
        print("\n[Watcher] 守护服务已由用户退出。")
        log_event("WATCH", "后台守护服务已停止。")

if __name__ == '__main__':
    run_watcher()
