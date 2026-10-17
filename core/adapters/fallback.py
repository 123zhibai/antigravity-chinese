import re
import json

class FallbackAdapter:
    """
    兜底自适应适配器 (Fallback Adapter)
    当版本适配器和 common 适配器无法完全匹配时，遍历并分析 ASAR 内部所有 JS 文件，
    通过 AST-like 特征推断出主窗口、Preload 与主菜单，完成容灾挂载。
    """
    name = "fallback"

    def __init__(self, archive, runtime_script, menu_map):
        self.archive = archive
        self.runtime_script = runtime_script
        self.menu_map = menu_map
        self.patched_files = []

    def can_apply(self):
        return True

    def apply(self):
        self.patched_files = []
        injected_ui = False
        injected_menu = False

        all_files = [f for f in self.archive.list_files() if f.endswith('.js')]

        escaped_code = json.dumps(self.runtime_script)
        injection_code = f"""
// --- Fallback UI Chinese Localization ---
const __chineseTranslatorScript = {escaped_code};
function __injectChinese(win) {{
    if (!win || !win.webContents) return;
    win.webContents.on('dom-ready', () => {{
        void win.webContents.executeJavaScript(__chineseTranslatorScript);
    }});
    win.webContents.on('did-finish-load', () => {{
        void win.webContents.executeJavaScript(__chineseTranslatorScript);
    }});
}}
"""

        # 遍历 JS 文件寻找 BrowserWindow 创建点
        for path in all_files:
            if injected_ui:
                break
            txt = self.archive.read_text(path)
            if 'BrowserWindow' in txt and ('loadURL' in txt or 'webContents' in txt):
                # 寻找 window 变量声明与创建
                m = re.search(r"(\w+)\s*=\s*new\s+\w*BrowserWindow\b", txt)
                if m:
                    win_var = m.group(1)
                    # 在创建后寻找合适的注入点，比如 loadURL 之前
                    load_m = re.search(rf"(\b{win_var}\.loadURL\b)", txt)
                    if load_m:
                        hook = f"__injectChinese({win_var});\n    "
                        txt = injection_code + "\n" + txt.replace(load_m.group(1), hook + load_m.group(1), 1)
                        self.archive.write_text(path, txt)
                        injected_ui = True
                        self.patched_files.append(path)
                        break

        # 遍历 JS 文件寻找 Menu.setApplicationMenu
        for path in all_files:
            if injected_menu:
                break
            txt = self.archive.read_text(path)
            if 'setApplicationMenu' in txt:
                m = re.search(r"(\b\w+\.setApplicationMenu\s*\(\s*(\w+)\s*\);)", txt)
                if m:
                    menu_call = m.group(1)
                    menu_arg = m.group(2)
                    menu_json_str = json.dumps(self.menu_map, ensure_ascii=False)
                    patch = f"""
// --- Fallback Menu Localization ---
const __menuMap = {menu_json_str};
function __patchMenu(m) {{
    if (!m || !m.items) return;
    m.items.forEach(it => {{
        if (__menuMap[it.label]) it.label = __menuMap[it.label];
        if (it.submenu) __patchMenu(it.submenu);
    }});
}}
__patchMenu({menu_arg});
{menu_call}
"""
                    txt = txt.replace(menu_call, patch, 1)
                    self.archive.write_text(path, txt)
                    injected_menu = True
                    self.patched_files.append(path)
                    break

        if injected_ui or injected_menu:
            return True, self.patched_files, "兜底自适应适配器注入成功"
        return False, [], "兜底自适应适配器未找到可用入口"
