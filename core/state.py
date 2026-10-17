import os
import sys
import json
import datetime

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from .config import get_paths, sha256_file, get_exe_version
    from .engine.asar import AsarArchive
except ImportError:
    from config import get_paths, sha256_file, get_exe_version
    from engine.asar import AsarArchive

def load_state():
    paths = get_paths()
    default_state = {
        "antigravity_version": None,
        "clean_backup_version": None,
        "official_clean_sha256": None,
        "patched_sha256": None,
        "current_status": "uninitialized",
        "last_patch_time": None,
        "last_patch_adapter": None,
        "patched_files": [],
        "total_self_healing_count": 0
    }
    if not paths:
        return default_state

    state_file = paths['state_file']
    if os.path.exists(state_file):
        try:
            with open(state_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, dict):
                    merged = default_state.copy()
                    merged.update(data)
                    return merged
        except Exception:
            pass

    # 若 state.json 尚不存在，尝试加载 state.example.json 作为初始结构
    example_file = os.path.join(paths['core_dir'], 'state.example.json')
    if os.path.exists(example_file):
        try:
            with open(example_file, 'r', encoding='utf-8') as f:
                ex_data = json.load(f)
                if isinstance(ex_data, dict):
                    return ex_data
        except Exception:
            pass

    return default_state

def save_state(state_dict):
    paths = get_paths()
    if not paths:
        return
    with open(paths['state_file'], 'w', encoding='utf-8') as f:
        json.dump(state_dict, f, ensure_ascii=False, indent=2)

def check_asar_is_patched(asar_path):
    """通过解析 ASAR 内部判断是否已注入汉化脚本"""
    if not os.path.exists(asar_path):
        return False
    try:
        archive = AsarArchive(asar_path)
        if archive.has_file('/dist/utils.js'):
            txt = archive.read_text('/dist/utils.js')
            if '__chineseTranslatorScript' in txt:
                return True
        if archive.has_file('/dist/preload.js'):
            txt = archive.read_text('/dist/preload.js')
            if '__antigravity_chinese_active' in txt:
                return True
        return False
    except Exception:
        return False

def get_current_status():
    """
    全面检测当前环境的汉化与版本状态：
    返回 dict:
    - version: 当前 Antigravity 版本
    - current_hash: 当前 app.asar 的 sha256
    - is_patched: 当前是否已处于汉化状态
    - is_official_clean: 当前是否为官方纯净未修改版
    - has_update: 是否发生了官方更新（hash 变化且当前未汉化）
    - state: 历史状态记录
    """
    paths = get_paths()
    if not paths:
        return {"error": "未检测到 Antigravity 安装目录"}

    state = load_state()
    exe_ver = get_exe_version(paths['exe_path'])
    curr_hash = sha256_file(paths['asar_path'])
    is_patched = check_asar_is_patched(paths['asar_path'])

    # 如果有独立官方纯净备份，获取其 hash
    clean_hash = None
    if os.path.exists(paths['clean_backup_asar']):
        clean_hash = sha256_file(paths['clean_backup_asar'])

    has_update = False
    if not is_patched:
        if state.get('patched_sha256') and curr_hash != state.get('patched_sha256'):
            has_update = True
        elif state.get('antigravity_version') and exe_ver != state.get('antigravity_version'):
            has_update = True

    return {
        "antigravity_dir": paths['install_dir'],
        "version": exe_ver,
        "current_hash": curr_hash,
        "is_patched": is_patched,
        "clean_backup_exists": os.path.exists(paths['clean_backup_asar']),
        "clean_backup_version": state.get("clean_backup_version"),
        "clean_hash": clean_hash,
        "has_update": has_update,
        "last_patch_time": state.get('last_patch_time'),
        "last_patch_adapter": state.get('last_patch_adapter'),
        "patched_files": state.get('patched_files', []),
        "self_healing_count": state.get('total_self_healing_count', 0)
    }
