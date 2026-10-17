import os
import sys
import shutil
import json
import datetime

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from ..config import get_paths, sha256_file, get_exe_version
    from .asar import AsarArchive
    from .runtime_builder import build_runtime_script
    from .validator import check_js_syntax, validate_patched_asar
    from ..adapters import get_adapter
    from ..state import load_state, save_state, check_asar_is_patched
    from ..logger import log_event
except (ImportError, ValueError):
    from config import get_paths, sha256_file, get_exe_version
    from engine.asar import AsarArchive
    from engine.runtime_builder import build_runtime_script
    from engine.validator import check_js_syntax, validate_patched_asar
    from adapters import get_adapter
    from state import load_state, save_state, check_asar_is_patched
    from logger import log_event

def restore_official_clean():
    """从独立备份区恢复官方纯净原版"""
    paths = get_paths()
    if not paths:
        return False, "未找到路径配置"

    clean_backup = paths['clean_backup_asar']
    target_asar = paths['asar_path']

    if not os.path.exists(clean_backup):
        msg = f"未找到官方纯净备份文件: {clean_backup}"
        log_event("ROLLBACK", msg, is_error=True)
        return False, msg

    try:
        shutil.copy2(clean_backup, target_asar)
        state = load_state()
        state['current_status'] = "official_clean"
        state['patched_sha256'] = None
        save_state(state)
        msg = "已成功安全恢复为 Antigravity 官方原版英文界面！"
        log_event("ROLLBACK", msg)
        return True, msg
    except Exception as e:
        err = f"恢复官方版本时发生错误: {str(e)}"
        log_event("ROLLBACK", err, is_error=True)
        return False, err

def perform_patch(force=False, is_self_healing=False):
    """
    执行汉化注入流程（支持自愈重打与安全回滚）
    """
    paths = get_paths()
    if not paths:
        return False, "未找到 Antigravity 安装目录"

    target_asar = paths['asar_path']
    clean_backup = paths['clean_backup_asar']

    if not os.path.exists(target_asar):
        return False, f"未找到核心文件: {target_asar}"

    current_ver = get_exe_version(paths['exe_path']) or "unknown"
    current_hash = sha256_file(target_asar)
    is_already_patched = check_asar_is_patched(target_asar)

    # 如果已经汉化且非强制执行，直接返回成功
    if is_already_patched and not force:
        return True, "当前 Antigravity 已经是最新汉化版本，无需重复注入"

    # 1. 备份机制：若当前 target_asar 是未汉化的纯净版本，则备份至独立安全的备份区
    if not is_already_patched:
        log_event("PATCH", f"检测到官方纯净原版 (Hash: {current_hash[:10]}...)，正在备份到独立隔离区...")
        try:
            shutil.copy2(target_asar, clean_backup)
        except Exception as e:
            log_event("PATCH", f"备份官方原版失败: {e}", is_error=True)
            return False, f"备份失败: {e}"
    else:
        # 如果当前已经汉化，但备份区不存在官方原版，则提醒
        if not os.path.exists(clean_backup):
            log_event("PATCH", "警告: 独立备份区无官方纯净备份，本次将直接在当前基础上更新", is_error=False)

    # 2. 读取词库与生成运行时代码
    try:
        runtime_script = build_runtime_script(paths['dictionary_json'])
        with open(paths['menu_json'], 'r', encoding='utf-8') as f:
            menu_map = json.load(f)
    except Exception as e:
        err = f"读取词库或生成运行时代码失败: {str(e)}"
        log_event("PATCH", err, is_error=True)
        return False, err

    # 3. 优先基于官方纯净备份构建，若无备份则基于当前文件
    base_source_asar = clean_backup if os.path.exists(clean_backup) else target_asar
    log_event("PATCH", f"正在基于 {'官方备份' if base_source_asar == clean_backup else '当前文件'} 构建汉化核心...")

    try:
        archive = AsarArchive(base_source_asar)
    except Exception as e:
        err = f"解析 ASAR 文件失败: {str(e)}"
        log_event("PATCH", err, is_error=True)
        return False, err

    # 4. 选择最佳适配器执行特征注入
    adapter = get_adapter(current_ver, archive, runtime_script, menu_map)
    log_event("PATCH", f"匹配到最适合当前版本的适配器: [{adapter.name}]")

    success, patched_files, msg = adapter.apply()
    if not success:
        log_event("PATCH", f"适配器注入失败: {msg}", is_error=True)
        return False, f"适配器注入失败: {msg}"

    log_event("PATCH", f"成功注入补丁至关键文件: {', '.join(patched_files)}")

    # 5. 安全校验：JavaScript 语法检测 (node --check)
    for p in patched_files:
        code_text = archive.read_text(p)
        ok, vmsg = check_js_syntax(code_text)
        if not ok:
            log_event("VALIDATE", f"JS 语法校验失败: {p} - {vmsg}", is_error=True)
            log_event("ROLLBACK", "触发安全回滚保护机制...")
            restore_official_clean()
            return False, f"语法校验失败并已自动回滚: {vmsg}"

    # 6. 保存为临时 ASAR 并校验完整性
    tmp_asar = target_asar + ".patch_tmp"
    try:
        archive.save(tmp_asar)
    except Exception as e:
        log_event("PATCH", f"保存临时 ASAR 失败: {str(e)}", is_error=True)
        if os.path.exists(tmp_asar):
            try: os.remove(tmp_asar)
            except Exception: pass
        return False, f"保存 ASAR 失败: {str(e)}"

    ok, vmsg = validate_patched_asar(tmp_asar)
    if not ok:
        log_event("VALIDATE", f"ASAR 完整性校验失败: {vmsg}", is_error=True)
        if os.path.exists(tmp_asar):
            try: os.remove(tmp_asar)
            except Exception: pass
        log_event("ROLLBACK", "触发安全回滚保护机制...")
        restore_official_clean()
        return False, f"ASAR 校验失败并已自动回滚: {vmsg}"

    # 7. 原子替换为正式 app.asar
    try:
        shutil.copy2(tmp_asar, target_asar)
        os.remove(tmp_asar)
    except Exception as e:
        log_event("PATCH", f"覆盖正式 app.asar 失败 (可能文件被占用): {str(e)}", is_error=True)
        return False, f"文件写入失败 (请确保 Antigravity 完全退出后重试): {str(e)}"

    # 8. 更新状态数据库与日志
    new_hash = sha256_file(target_asar)
    clean_hash = sha256_file(clean_backup) if os.path.exists(clean_backup) else None
    state = load_state()
    healing_count = state.get('total_self_healing_count', 0)
    if is_self_healing:
        healing_count += 1

    state.update({
        "antigravity_version": current_ver,
        "official_clean_sha256": clean_hash or state.get("official_clean_sha256"),
        "patched_sha256": new_hash,
        "current_status": "patched",
        "last_patch_time": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "last_patch_adapter": adapter.name,
        "patched_files": patched_files,
        "total_self_healing_count": healing_count
    })
    save_state(state)

    success_msg = f"汉化注入完成！(版本: {current_ver}, 适配器: {adapter.name}, 自愈累计: {healing_count} 次)"
    log_event("PATCH", success_msg)
    return True, success_msg
