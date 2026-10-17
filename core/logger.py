import os
import sys
import datetime

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from .config import get_paths
except ImportError:
    from config import get_paths

def log_event(category, message, details=None, is_error=False):
    """
    统一持久化日志记录函数。
    category: 'PATCH', 'WATCH', 'ROLLBACK', 'VALIDATE', 'LAUNCH'
    """
    paths = get_paths()
    if not paths:
        return

    log_file = paths['patch_log'] if category != 'WATCH' else paths['watch_log']
    now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    level = "ERROR" if is_error else "INFO"

    entry = f"[{now_str}] [{level}] [{category}] {message}"
    if details:
        entry += f"\n  详情: {details}"

    try:
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(entry + "\n")
    except Exception:
        pass

    color = "\033[91m" if is_error else "\033[92m" if "成功" in message else "\033[93m" if "警告" in message else "\033[0m"
    reset = "\033[0m"
    print(f"[{category}] {color}{message}{reset}")
