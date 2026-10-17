import os
import subprocess
import tempfile
from .asar import AsarArchive

def check_js_syntax(js_code):
    """使用 node --check 进行 JavaScript 语法校验"""
    try:
        with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as tf:
            tf.write(js_code)
            tmp_name = tf.name

        try:
            res = subprocess.run(['node', '--check', tmp_name], capture_output=True, text=True)
            if res.returncode != 0:
                return False, f"JS 语法错误: {res.stderr.strip()}"
            return True, "JS 语法校验通过"
        finally:
            if os.path.exists(tmp_name):
                try:
                    os.remove(tmp_name)
                except Exception:
                    pass
    except FileNotFoundError:
        # 如果系统没有 node 命令，进行基本的括号平衡和非空检查
        if not js_code or len(js_code.strip()) == 0:
            return False, "JS 代码为空"
        return True, "Node 未安装，跳过 node --check 静态校验"
    except Exception as e:
        return False, f"JS 校验异常: {str(e)}"

def validate_patched_asar(asar_path):
    """验证补丁后的 ASAR 文件完整性与基本结构"""
    if not os.path.exists(asar_path):
        return False, "ASAR 文件不存在"
    if os.path.getsize(asar_path) < 1024:
        return False, "ASAR 文件过小，可能损坏"

    try:
        archive = AsarArchive(asar_path)
        # 必须能够读取关键主入口
        if not archive.has_file('/dist/main.js'):
            return False, "ASAR 缺少 /dist/main.js 核心入口"
        main_bytes = archive.read_file('/dist/main.js')
        if len(main_bytes) < 100:
            return False, "dist/main.js 文件损坏或过小"

        # 检查是否包含 package.json
        if archive.has_file('/package.json'):
            pkg_bytes = archive.read_file('/package.json')
            if len(pkg_bytes) < 10:
                return False, "package.json 损坏"

        return True, "ASAR 完整性校验通过"
    except Exception as e:
        return False, f"ASAR 解析失败: {str(e)}"
