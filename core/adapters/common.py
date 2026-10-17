import re
import json

class CommonAdapter:
    """
    通用特征匹配适配器 (Common Adapter)
    适用于大多数基于 Electron 的 Antigravity 版本。
    采用多锚点启发式匹配，绝不依赖固定行号或文件偏移。
    """
    name = "common"

    def __init__(self, archive, runtime_script, menu_map):
        self.archive = archive
        self.runtime_script = runtime_script
        self.menu_map = menu_map
        self.patched_files = []

    def can_apply(self):
        """检查 archive 是否具备可注入的基础结构"""
        return self.archive.has_file('/dist/utils.js') or self.archive.has_file('/dist/preload.js') or self.archive.has_file('/dist/main.js')

    def apply(self):
        self.patched_files = []
        injected_ui = False
        injected_menu = False

        # 1. 尝试注入 UI 渲染层翻译器
        # 首选注入点：dist/utils.js (针对窗口生命周期注入 webContents.executeJavaScript)
        if self.archive.has_file('/dist/utils.js'):
            txt = self.archive.read_text('/dist/utils.js')
            if '__chineseTranslatorScript' in txt:
                injected_ui = True
                self.patched_files.append('/dist/utils.js')
            else:
                escaped_code = json.dumps(self.runtime_script)
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
                # 使用多种特征候选锚点
                anchors = [
                    re.compile(r"(win\.on\s*\(\s*['\"]page-title-updated['\"])"),
                    re.compile(r"(win\.webContents\.setWindowOpenHandler)"),
                    re.compile(r"(win\.webContents\.on\s*\(\s*['\"]did-finish-load['\"])"),
                    re.compile(r"(\bvoid\s+win\.loadURL\b)")
                ]
                for pattern in anchors:
                    match = pattern.search(txt)
                    if match:
                        txt = pattern.sub(lambda m: injection + "\n    " + m.group(1), txt, count=1)
                        self.archive.write_text('/dist/utils.js', txt)
                        injected_ui = True
                        self.patched_files.append('/dist/utils.js')
                        break

        # 备选注入点：dist/preload.js (如果 utils.js 注入未完成，挂载到 preload.js)
        if not injected_ui and self.archive.has_file('/dist/preload.js'):
            txt = self.archive.read_text('/dist/preload.js')
            if '__antigravity_chinese_active' not in txt:
                preload_injection = f"""
// --- Antigravity Preload Chinese Localization Injection ---
try {{
    {self.runtime_script}
}} catch (e) {{
    console.error('[Chinese-Localization] Preload injection error:', e);
}}
"""
                txt = preload_injection + "\n" + txt
                self.archive.write_text('/dist/preload.js', txt)
                injected_ui = True
                self.patched_files.append('/dist/preload.js')

        # 2. 尝试注入原生主菜单汉化 (dist/menu.js)
        if self.archive.has_file('/dist/menu.js'):
            txt = self.archive.read_text('/dist/menu.js')
            if 'translateMenu' in txt:
                injected_menu = True
                self.patched_files.append('/dist/menu.js')
            else:
                menu_json_str = json.dumps(self.menu_map, ensure_ascii=False, indent=2)
                menu_patch = f"""
// --- Antigravity Native Menu Chinese Localization ---
const __menuChineseMap = {menu_json_str};
function translateMenu(m) {{
    if (!m || !m.items) return;
    m.items.forEach(it => {{
        if (__menuChineseMap[it.label]) {{
            it.label = __menuChineseMap[it.label];
        }}
        if (it.submenu) {{
            translateMenu(it.submenu);
        }}
    }});
}}
"""
                # 特征匹配 Menu.setApplicationMenu
                menu_anchors = [
                    re.compile(r"(\w+\.Menu\.setApplicationMenu\s*\(\s*(\w+)\s*\);)"),
                    re.compile(r"(Menu\.setApplicationMenu\s*\(\s*(\w+)\s*\);)")
                ]
                for pattern in menu_anchors:
                    match = pattern.search(txt)
                    if match:
                        full_call = match.group(1)
                        menu_var = match.group(2)
                        replacement = f"translateMenu({menu_var});\n    {full_call}"
                        txt = menu_patch + "\n" + txt.replace(full_call, replacement, 1)
                        self.archive.write_text('/dist/menu.js', txt)
                        injected_menu = True
                        self.patched_files.append('/dist/menu.js')
                        break

        if injected_ui:
            return True, self.patched_files, "通用适配器注入成功"
        else:
            return False, [], "通用适配器未能匹配到渲染注入点"
