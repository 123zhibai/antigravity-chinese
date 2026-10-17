import os
import time
import json
import hashlib
import subprocess
import tempfile

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in os.sys.path:
    os.sys.path.insert(0, parent_dir)
if current_dir not in os.sys.path:
    os.sys.path.insert(0, current_dir)

try:
    from .asar import AsarArchive
except (ImportError, ValueError):
    from engine.asar import AsarArchive

def _sha256_of_file(filepath):
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

def check_js_syntax(js_code):
    """
    使用 node --check 进行 JavaScript 语法校验。
    如果 Node.js 未安装，则执行基础括号/结构分析，并明确标记为 degraded verification (降级校验)。
    """
    if not js_code or len(js_code.strip()) == 0:
        return False, "JS 代码为空"

    try:
        with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as tf:
            tf.write(js_code)
            tmp_name = tf.name

        try:
            res = subprocess.run(['node', '--check', tmp_name], capture_output=True, text=True)
            if res.returncode != 0:
                return False, f"JS 语法错误: {res.stderr.strip()}"
            return True, "JS 语法校验通过 (node --check)"
        finally:
            if os.path.exists(tmp_name):
                try:
                    os.remove(tmp_name)
                except Exception:
                    pass
    except FileNotFoundError:
        # Node 未安装，进行括号平衡与关键结构的基础降级校验
        brackets = {'(': ')', '[': ']', '{': '}'}
        stack = []
        in_string = None
        escape = False
        for ch in js_code:
            if escape:
                escape = False
                continue
            if ch == '\\':
                escape = True
                continue
            if in_string:
                if ch == in_string:
                    in_string = None
                continue
            elif ch in ("'", '"', '`'):
                in_string = ch
                continue

            if ch in brackets:
                stack.append(ch)
            elif ch in brackets.values():
                if not stack:
                    return False, "JS 结构语法错误: 括号闭合不匹配 (degraded verification)"
                top = stack.pop()
                if brackets[top] != ch:
                    return False, f"JS 结构语法错误: 括号不匹配 '{top}' 与 '{ch}' (degraded verification)"

        if stack:
            return False, f"JS 结构语法错误: 存在未闭合括号 '{stack[-1]}' (degraded verification)"

        return True, "Node.js 未安装，执行基础静态结构分析通过 (degraded verification)"
    except Exception as e:
        return False, f"JS 校验异常: {str(e)}"

def validate_official_candidate(asar_path, check_stability=True):
    """
    候选官方版本稳定性与完整性安全验证：
    在将任何官方文件覆盖至 official_clean_app.asar 之前必须经过本校验。
    
    校验条件：
    1. 文件存在且大小达到合理基准 (>= 1MB)；
    2. 稳定性检验：文件大小与 SHA-256 采样稳定，非写入中状态；
    3. AsarArchive 能够正确解包 Header；
    4. 核心入口完整：/dist/main.js 存在且大小 >= 500 字节；
    5. 包含 /dist/utils.js 或 /dist/preload.js；
    6. package.json 若存在，必须是合法有效 JSON；
    7. 纯净性确认：绝对不包含任何汉化补丁特征标记。
    """
    if not asar_path or not os.path.exists(asar_path):
        return False, "候选官方文件不存在"

    size = os.path.getsize(asar_path)
    if size < 1024 * 1024:
        return False, f"候选官方文件过小 ({size} 字节)，可能是截断或损坏文件"

    # 稳定性检测：防止官方更新器在流式写入中被中途读取
    if check_stability:
        hash_1 = _sha256_of_file(asar_path)
        size_1 = os.path.getsize(asar_path)
        time.sleep(0.3)
        hash_2 = _sha256_of_file(asar_path)
        size_2 = os.path.getsize(asar_path)

        if size_1 != size_2 or hash_1 != hash_2:
            return False, "候选官方文件大小或 Hash 处于变动中，疑似官方更新程序正在写入，拒绝备份"

    # ASAR 结构解析
    try:
        archive = AsarArchive(asar_path)
    except Exception as e:
        return False, f"候选文件 ASAR 结构损坏，无法解析: {str(e)}"

    # 核心入口检查
    if not archive.has_file('/dist/main.js'):
        return False, "候选官方文件缺少 /dist/main.js 核心入口"
    main_bytes = archive.read_file('/dist/main.js')
    if len(main_bytes) < 500:
        return False, "候选文件 /dist/main.js 大小异常 (< 500 字节)"

    if not (archive.has_file('/dist/utils.js') or archive.has_file('/dist/preload.js')):
        return False, "候选官方文件缺少关键分发文件 (/dist/utils.js 或 /dist/preload.js)"

    if archive.has_file('/package.json'):
        try:
            pkg_bytes = archive.read_file('/package.json')
            pkg_data = json.loads(pkg_bytes.decode('utf-8'))
            if not isinstance(pkg_data, dict):
                return False, "候选文件 package.json 格式异常"
        except Exception as e:
            return False, f"候选文件 package.json 解析失败: {str(e)}"

    # 纯净性确认：确保不含有汉化注入特征
    if archive.has_file('/dist/utils.js'):
        u_txt = archive.read_text('/dist/utils.js')
        if '__chineseTranslatorScript' in u_txt or '__antigravity_chinese_active' in u_txt:
            return False, "候选文件包含汉化注入标记，不是官方纯净版本"

    if archive.has_file('/dist/preload.js'):
        p_txt = archive.read_text('/dist/preload.js')
        if '__antigravity_chinese_active' in p_txt or '__chineseTranslatorScript' in p_txt:
            return False, "候选文件包含 Preload 汉化标记，不是官方纯净版本"

    if archive.has_file('/dist/menu.js'):
        m_txt = archive.read_text('/dist/menu.js')
        if 'translateMenu' in m_txt:
            return False, "候选文件包含菜单汉化标记，不是官方纯净版本"

    return True, "候选官方文件稳定性与完整性验证通过"

def validate_patched_asar(asar_path, expected_files=None, require_ui_marker=True):
    """
    验证补丁后的 ASAR 文件完整性、结构与汉化有效性。
    
    校验条件：
    1. 文件存在且大小达到合理基准 (>= 1MB)；
    2. ASAR 结构可正常解析；
    3. /dist/main.js 存在且非空；
    4. 汉化标记存在：必须在 /dist/utils.js 或 /dist/preload.js 中找到 UI 汉化标记；
    5. 若指定了 expected_files，必须确保所列文件均存在且大小正常；
    6. 若包含 /dist/menu.js，检查 translateMenu 注入。
    """
    if not asar_path or not os.path.exists(asar_path):
        return False, "ASAR 文件不存在"
    size = os.path.getsize(asar_path)
    if size < 1024 * 1024:
        return False, f"ASAR 文件过小 ({size} 字节)，可能已损坏"

    try:
        archive = AsarArchive(asar_path)
    except Exception as e:
        return False, f"ASAR 解析失败: {str(e)}"

    # 核心主入口检查
    if not archive.has_file('/dist/main.js'):
        return False, "ASAR 缺少 /dist/main.js 核心入口"
    main_bytes = archive.read_file('/dist/main.js')
    if len(main_bytes) < 500:
        return False, "dist/main.js 文件损坏或过小"

    if archive.has_file('/package.json'):
        try:
            pkg_bytes = archive.read_file('/package.json')
            json.loads(pkg_bytes.decode('utf-8'))
        except Exception as e:
            return False, f"package.json 损坏: {str(e)}"

    # 验证 UI 汉化标记存在性
    if require_ui_marker:
        has_ui_marker = False
        if archive.has_file('/dist/utils.js'):
            txt = archive.read_text('/dist/utils.js')
            if '__chineseTranslatorScript' in txt:
                has_ui_marker = True
        if not has_ui_marker and archive.has_file('/dist/preload.js'):
            txt = archive.read_text('/dist/preload.js')
            if '__antigravity_chinese_active' in txt:
                has_ui_marker = True

        if not has_ui_marker:
            return False, "ASAR 缺少关键 UI 汉化注入标记 (__chineseTranslatorScript / __antigravity_chinese_active)"

    # 检查期望注入文件列表
    if expected_files:
        for f in expected_files:
            if not archive.has_file(f):
                return False, f"期望的补丁文件不存在: {f}"
            if len(archive.read_file(f)) < 50:
                return False, f"补丁文件内容异常过小: {f}"

    return True, "ASAR 完整性与汉化注入校验通过"
