import os
import sys
import hashlib
import json
import subprocess

CORE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKUP_DIR = os.path.join(CORE_DIR, "backups")
LOGS_DIR = os.path.join(CORE_DIR, "logs")
TRANSLATIONS_DIR = os.path.join(CORE_DIR, "translations")
STATE_FILE = os.path.join(CORE_DIR, "state.json")
CLEAN_BACKUP_ASAR = os.path.join(BACKUP_DIR, "official_clean_app.asar")

os.makedirs(BACKUP_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

def sha256_file(filepath):
    """计算文件的 SHA-256 哈希值"""
    if not filepath or not os.path.exists(filepath):
        return None
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()

def find_antigravity_dir():
    """多策略自动探测 Antigravity 安装目录"""
    # 策略 1: 检查环境变量中的 LOCALAPPDATA
    local_app_data = os.environ.get('LOCALAPPDATA', '')
    if local_app_data:
        p = os.path.join(local_app_data, 'Programs', 'antigravity')
        if os.path.exists(os.path.join(p, 'Antigravity.exe')):
            return p

    # 策略 2: 检查用户目录
    home = os.path.expanduser('~')
    p = os.path.join(home, 'AppData', 'Local', 'Programs', 'antigravity')
    if os.path.exists(os.path.join(p, 'Antigravity.exe')):
        return p

    # 策略 3: 检查运行中进程的路径
    try:
        cmd = "Get-Process -Name 'Antigravity' -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty Path"
        out = subprocess.check_output(['powershell', '-NoProfile', '-Command', cmd], text=True, stderr=subprocess.DEVNULL).strip()
        if out and os.path.exists(out):
            return os.path.dirname(out)
    except Exception:
        pass

    # 策略 4: 检查常见 Program Files 路径
    for env_var in ['ProgramFiles', 'ProgramFiles(x86)']:
        pf = os.environ.get(env_var, '')
        if pf:
            p = os.path.join(pf, 'Antigravity')
            if os.path.exists(os.path.join(p, 'Antigravity.exe')):
                return p

    return None

def get_paths():
    """获取系统所有关键路径"""
    install_dir = find_antigravity_dir()
    if not install_dir:
        return None

    resources_dir = os.path.join(install_dir, 'resources')
    asar_path = os.path.join(resources_dir, 'app.asar')
    exe_path = os.path.join(install_dir, 'Antigravity.exe')

    return {
        "install_dir": install_dir,
        "resources_dir": resources_dir,
        "asar_path": asar_path,
        "exe_path": exe_path,
        "core_dir": CORE_DIR,
        "backup_dir": BACKUP_DIR,
        "clean_backup_asar": CLEAN_BACKUP_ASAR,
        "logs_dir": LOGS_DIR,
        "patch_log": os.path.join(LOGS_DIR, "patch.log"),
        "watch_log": os.path.join(LOGS_DIR, "watch.log"),
        "state_file": STATE_FILE,
        "translations_dir": TRANSLATIONS_DIR,
        "dictionary_json": os.path.join(TRANSLATIONS_DIR, "dictionary.json"),
        "menu_json": os.path.join(TRANSLATIONS_DIR, "menu.json")
    }

def get_exe_version(exe_path):
    """读取 EXE 的文件版本与产品版本"""
    if not exe_path or not os.path.exists(exe_path):
        return None
    try:
        cmd = f"(Get-Item '{exe_path}').VersionInfo | Select-Object ProductVersion, FileVersion | ConvertTo-Json"
        out = subprocess.check_output(['powershell', '-NoProfile', '-Command', cmd], text=True, stderr=subprocess.DEVNULL).strip()
        data = json.loads(out)
        return data.get('FileVersion') or data.get('ProductVersion')
    except Exception:
        return None
