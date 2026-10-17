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
    from .validator import check_js_syntax, validate_patched_asar, validate_official_candidate
    from ..adapters import get_adapter
    from ..state import load_state, save_state, check_asar_is_patched
    from ..logger import log_event
except (ImportError, ValueError):
    from config import get_paths, sha256_file, get_exe_version
    from engine.asar import AsarArchive
    from engine.runtime_builder import build_runtime_script
    from engine.validator import check_js_syntax, validate_patched_asar, validate_official_candidate
    from adapters import get_adapter
    from state import load_state, save_state, check_asar_is_patched
    from logger import log_event

def restore_official_clean(custom_target_asar=None, custom_clean_backup=None):
    """从独立备份区恢复官方纯净原版"""
    paths = get_paths()
    if not paths:
        return False, "未找到路径配置"

    clean_backup = custom_clean_backup or paths['clean_backup_asar']
    target_asar = custom_target_asar or paths['asar_path']

    if not os.path.exists(clean_backup):
        msg = f"未找到官方纯净备份文件: {clean_backup}"
        log_event("ROLLBACK", msg, is_error=True)
        return False, msg

    try:
        # 使用安全的原子替换恢复官方原版
        tmp_restore = target_asar + ".restore_tmp"
        shutil.copy2(clean_backup, tmp_restore)
        os.replace(tmp_restore, target_asar)

        if not custom_target_asar:
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
        if os.path.exists(target_asar + ".restore_tmp"):
            try: os.remove(target_asar + ".restore_tmp")
            except Exception: pass
        return False, err

UNSUPPORTED_VERSION_MSG = (
    "检测到新的 Antigravity 版本或未知核心结构。\n\n"
    "当前版本尚未通过兼容性验证。\n"
    "为防止旧版本核心文件覆盖新版客户端，本次汉化已安全停止。\n\n"
    "官方当前文件未被修改。\n"
    "旧版本 clean backup 已保留，仅供恢复使用。\n\n"
    "请先更新对应版本 Adapter 或兼容规则。"
)

def perform_patch(force=False, is_self_healing=False, custom_target_asar=None, custom_clean_backup=None, custom_version=None, custom_state=None):
    """
    执行汉化注入流程（支持自愈重打、纯净备份安全保护、跨版本防护与真正的原子替换）
    """
    paths = get_paths()
    if not paths and not custom_target_asar:
        return False, "未找到 Antigravity 安装目录"

    target_asar = custom_target_asar or (paths['asar_path'] if paths else None)
    clean_backup = custom_clean_backup or (paths['clean_backup_asar'] if paths else None)

    if not target_asar or not os.path.exists(target_asar):
        return False, f"未找到核心文件: {target_asar}"

    current_ver = custom_version or (get_exe_version(paths['exe_path']) if paths else None) or "unknown"
    current_hash = sha256_file(target_asar)
    is_already_patched = check_asar_is_patched(target_asar)

    # 如果已经汉化且非强制执行，直接返回成功
    if is_already_patched and not force:
        return True, "当前 Antigravity 已经是最新汉化版本，无需重复注入"

    state = custom_state if custom_state is not None else load_state()
    clean_backup_version = state.get("clean_backup_version")
    if not clean_backup_version and state.get("antigravity_version"):
        # 平滑兼容既有 state 历史记录
        clean_backup_version = state.get("antigravity_version")

    # 1. 备份机制与跨版本安全防御：严格验证候选官方版本，杜绝半写入、损坏或未知新版污染 (Fail-Closed)
    if not is_already_patched:
        log_event("PATCH", "检测到未汉化文件，正在进行候选官方版本稳定性与完整性验证...")
        cand_ok, cand_msg = validate_official_candidate(target_asar, check_stability=(custom_target_asar is None))
        if not cand_ok:
            log_event("PATCH", f"当前文件未通过官方候选验证 ({cand_msg})，触发跨版本安全保护停止注入！", is_error=True)
            log_event("PATCH", UNSUPPORTED_VERSION_MSG, is_error=True)
            # 立即终止本次 perform_patch，返回明确失败状态，正式文件与 clean backup 均保持原样
            return False, UNSUPPORTED_VERSION_MSG

        # 候选版本验证通过：说明当前是合法稳定的新版官方原版，安全更新独立隔离备份区
        need_backup_update = True
        if clean_backup and os.path.exists(clean_backup):
            clean_hash = sha256_file(clean_backup)
            if clean_hash == current_hash and clean_backup_version == current_ver:
                need_backup_update = False

        if need_backup_update and clean_backup:
            log_event("PATCH", f"官方纯净版本验证通过 (版本: {current_ver}, Hash: {current_hash[:10]}...)，正在安全更新官方纯净备份...")
            try:
                tmp_backup = clean_backup + ".tmp"
                shutil.copy2(target_asar, tmp_backup)
                os.replace(tmp_backup, clean_backup)
                clean_backup_version = current_ver
                state["clean_backup_version"] = current_ver
                state["official_clean_sha256"] = current_hash
                if custom_state is None and not custom_target_asar:
                    save_state(state)
            except Exception as e:
                log_event("PATCH", f"备份官方原版失败: {e}", is_error=True)
                if os.path.exists(clean_backup + ".tmp"):
                    try: os.remove(clean_backup + ".tmp")
                    except Exception: pass
                return False, f"备份官方原版失败: {e}"

    # 2. 读取词库与生成运行时代码
    try:
        dict_path = paths['dictionary_json'] if paths else os.path.join(current_dir, '..', 'translations', 'dictionary.json')
        menu_path = paths['menu_json'] if paths else os.path.join(current_dir, '..', 'translations', 'menu.json')
        runtime_script = build_runtime_script(dict_path)
        with open(menu_path, 'r', encoding='utf-8') as f:
            menu_map = json.load(f)
    except Exception as e:
        err = f"读取词库或生成运行时代码失败: {str(e)}"
        log_event("PATCH", err, is_error=True)
        return False, err

    # 3. 确定构建源文件（旧版 clean backup 仅限恢复用途，严禁跨版本作为 patch base）
    if clean_backup and os.path.exists(clean_backup):
        # 严格宿主版本绑定检查：如果 clean backup 的版本与当前 EXE 版本不一致，直接停止
        if clean_backup_version and current_ver != "unknown" and clean_backup_version != current_ver:
            err_msg = f"检测到 clean backup 绑定版本 ({clean_backup_version}) 与当前客户端版本 ({current_ver}) 错配，严禁跨版本作为 patch base！"
            log_event("PATCH", err_msg, is_error=True)
            log_event("PATCH", UNSUPPORTED_VERSION_MSG, is_error=True)
            return False, UNSUPPORTED_VERSION_MSG
        base_source_asar = clean_backup
    else:
        base_source_asar = target_asar

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

    # 5. 安全校验：JavaScript 语法检测 (node --check / 结构降级检测)
    for p in patched_files:
        code_text = archive.read_text(p)
        ok, vmsg = check_js_syntax(code_text)
        if not ok:
            log_event("VALIDATE", f"JS 语法校验失败: {p} - {vmsg}", is_error=True)
            log_event("ROLLBACK", "触发安全回滚保护机制...")
            restore_official_clean()
            return False, f"语法校验失败并已自动回滚: {vmsg}"

    # 6. 保存为同目录临时 ASAR 并进行完整性与注入标记校验 (P0-4)
    tmp_asar = target_asar + ".patch_tmp"
    try:
        archive.save(tmp_asar)
    except Exception as e:
        log_event("PATCH", f"保存临时 ASAR 失败: {str(e)}", is_error=True)
        if os.path.exists(tmp_asar):
            try: os.remove(tmp_asar)
            except Exception: pass
        return False, f"保存 ASAR 失败: {str(e)}"

    # 对临时文件进行全量检验（结构、关键入口、UI 注入标记及期望注入文件）
    ok, vmsg = validate_patched_asar(tmp_asar, expected_files=patched_files, require_ui_marker=True)
    if not ok:
        log_event("VALIDATE", f"临时 ASAR 完整性或汉化标记校验失败: {vmsg}", is_error=True)
        if os.path.exists(tmp_asar):
            try: os.remove(tmp_asar)
            except Exception: pass
        log_event("ROLLBACK", "临时文件校验未通过，正式文件保持未修改原样。")
        return False, f"ASAR 校验失败，已放弃替换以保护正式文件: {vmsg}"

    # 7. 真正安全的原子替换 (os.replace) (P0-4)
    try:
        os.replace(tmp_asar, target_asar)
    except Exception as e:
        log_event("PATCH", f"原子替换正式 app.asar 失败 (可能文件被占用): {str(e)}", is_error=True)
        if os.path.exists(tmp_asar):
            try: os.remove(tmp_asar)
            except Exception: pass
        return False, f"文件替换失败 (请确保 Antigravity 完全退出后重试): {str(e)}"

    # 8. 更新状态数据库与日志
    new_hash = sha256_file(target_asar)
    clean_hash = sha256_file(clean_backup) if (clean_backup and os.path.exists(clean_backup)) else None
    healing_count = state.get('total_self_healing_count', 0)
    if is_self_healing:
        healing_count += 1

    state_update = {
        "antigravity_version": current_ver,
        "clean_backup_version": clean_backup_version or current_ver,
        "official_clean_sha256": clean_hash or state.get("official_clean_sha256"),
        "patched_sha256": new_hash,
        "current_status": "patched",
        "last_patch_time": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "last_patch_adapter": adapter.name,
        "patched_files": patched_files,
        "total_self_healing_count": healing_count
    }
    state.update(state_update)

    if custom_state is None and not custom_target_asar:
        save_state(state)

    success_msg = f"汉化注入完成！(版本: {current_ver}, 适配器: {adapter.name}, 自愈累计: {healing_count} 次)"
    log_event("PATCH", success_msg)
    return True, success_msg
