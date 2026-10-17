import struct
import json
import hashlib
import os
import io
import shutil
import sys

def get_resources_dir():
    local_app_data = os.environ.get('LOCALAPPDATA', '')
    if local_app_data:
        default_p = os.path.join(local_app_data, 'Programs', 'antigravity', 'resources')
        if os.path.exists(default_p):
            return default_p
    home = os.path.expanduser('~')
    p = os.path.join(home, 'AppData', 'Local', 'Programs', 'antigravity', 'resources')
    if os.path.exists(p):
        return p
    return None

def calc_integrity(data_bytes):
    block_size = 4 * 1024 * 1024
    blocks = []
    for i in range(0, len(data_bytes), block_size):
        chunk = data_bytes[i:i+block_size]
        blocks.append(hashlib.sha256(chunk).hexdigest())
    if not blocks:
        blocks = [hashlib.sha256(b"").hexdigest()]
    return {
        "algorithm": "SHA256",
        "hash": hashlib.sha256(data_bytes).hexdigest(),
        "blockSize": block_size,
        "blocks": blocks
    }

def install():
    resources_dir = get_resources_dir()
    if not resources_dir:
        print("[错误] 未找到 Antigravity 安装目录下的 resources 文件夹！")
        return False

    target_asar = os.path.join(resources_dir, 'app.asar')
    backup_asar = os.path.join(resources_dir, 'app.asar.backup')
    if not os.path.exists(backup_asar):
        if os.path.exists(target_asar):
            print(f"正在备份原版 app.asar 到 {backup_asar}...")
            shutil.copy2(target_asar, backup_asar)
        else:
            print("[错误] 未找到 app.asar！")
            return False

    translator_src = os.path.join(os.path.dirname(__file__), 'ui-translator.js')
    with open(translator_src, "r", encoding="utf-8") as tf:
        translator_code = tf.read()
    escaped_code = json.dumps(translator_code)

    print("正在基于官方原版资源构建汉化核心...")
    with open(backup_asar, "rb") as f:
        buf = f.read(16)
        u1, h_size, u2, j_len = struct.unpack('<IIII', buf)
        header = json.loads(f.read(j_len).decode('utf-8'))
        pad = (4 - (j_len % 4)) % 4
        if pad: f.read(pad)
        base_offset = 16 + j_len + pad

        file_list = []
        def collect(node, p=''):
            for k, v in node.items():
                curr_p = f"{p}/{k}"
                if 'files' in v:
                    collect(v['files'], curr_p)
                elif not v.get('unpacked', False):
                    file_list.append((int(v['offset']), curr_p, v))
        collect(header['files'])
        file_list.sort(key=lambda x: x[0])

        new_data = io.BytesIO()
        current_offset = 0

        for old_off, path, node_ref in file_list:
            old_size = node_ref['size']
            f.seek(base_offset + old_off)
            b = f.read(old_size)

            if path == "/dist/utils.js":
                txt = b.decode('utf-8')
                injection = f"""
    // --- Antigravity UI Chinese Localization Injection ---
    const __chineseTranslatorScript = {escaped_code};
    win.webContents.on('dom-ready', () => {{
        void win.webContents.executeJavaScript(__chineseTranslatorScript);
    }});
    win.webContents.on('did-finish-load', () => {{
        void win.webContents.executeJavaScript(__chineseTranslatorScript);
    }});
"""
                target = "win.on('page-title-updated'"
                if target in txt:
                    txt = txt.replace(target, injection + "\n    " + target)
                    b = txt.encode('utf-8')
                    print(f"已成功注入汉化调度至 {path}！")

            elif path == "/dist/menu.js":
                txt = b.decode('utf-8')
                menu_patch = """
function translateMenu(m) {
    if (!m || !m.items) return;
    const map = {
        'File': '文件 (&F)', 'Edit': '编辑 (&E)', 'View': '视图 (&V)',
        'Window': '窗口 (&W)', 'Help': '帮助 (&H)', 'New Window': '新建窗口',
        'Docs': '官方文档', 'Close Window': '关闭窗口', 'Quit': '退出',
        'Undo': '撤销', 'Redo': '重做', 'Cut': '剪切', 'Copy': '复制',
        'Paste': '粘贴', 'Select All': '全选', 'Reload': '重新加载',
        'Toggle Developer Tools': '切换开发者工具', 'Actual Size': '实际大小',
        'Zoom In': '放大', 'Zoom Out': '缩小', 'Toggle Full Screen': '切换全屏',
        'Minimize': '最小化', 'Zoom': '缩放', 'Connect to WSL': '连接到 WSL'
    };
    m.items.forEach(it => {
        if (map[it.label]) it.label = map[it.label];
        if (it.submenu) translateMenu(it.submenu);
    });
}
"""
                target = "electron_1.Menu.setApplicationMenu(menu);"
                if target in txt:
                    txt = menu_patch + "\n" + txt.replace(target, "translateMenu(menu);\n    electron_1.Menu.setApplicationMenu(menu);")
                    b = txt.encode('utf-8')
                    print(f"已成功注入主菜单汉化至 {path}！")

            size = len(b)
            node_ref['size'] = size
            node_ref['offset'] = str(current_offset)
            node_ref['integrity'] = calc_integrity(b)
            new_data.write(b)
            current_offset += size

    json_str = json.dumps(header, separators=(',', ':'))
    json_bytes = json_str.encode('utf-8')
    j_len = len(json_bytes)
    pad = (4 - (j_len % 4)) % 4
    h_size = j_len + pad + 8
    u2_val = j_len + pad + 4

    temp_out = target_asar + ".tmp"
    with open(temp_out, "wb") as out:
        out.write(struct.pack('<IIII', 4, h_size, u2_val, j_len))
        out.write(json_bytes)
        if pad:
            out.write(b'\x00' * pad)
        out.write(new_data.getvalue())

    shutil.copy2(temp_out, target_asar)
    os.remove(temp_out)
    print("\n[成功] Antigravity 界面中文汉化补丁已成功安装并永久生效！")
    return True

def uninstall():
    resources_dir = get_resources_dir()
    if not resources_dir:
        return False
    target_asar = os.path.join(resources_dir, 'app.asar')
    backup_asar = os.path.join(resources_dir, 'app.asar.backup')
    if not os.path.exists(backup_asar):
        print("[错误] 未找到备份文件！")
        return False
    shutil.copy2(backup_asar, target_asar)
    print("\n[成功] 已恢复官方原版英文界面！")
    return True

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--uninstall':
        uninstall()
    else:
        install()
