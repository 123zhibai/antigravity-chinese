import sys
import os
import argparse

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from .config import get_paths, sha256_file
    from .state import get_current_status, check_asar_is_patched
    from .engine.injector import perform_patch, restore_official_clean
    from .engine.validator import check_js_syntax, validate_patched_asar
    from .engine.asar import AsarArchive
    from .launcher import launch_antigravity
    from .watcher.service import run_watcher
except ImportError:
    from config import get_paths, sha256_file
    from state import get_current_status, check_asar_is_patched
    from engine.injector import perform_patch, restore_official_clean
    from engine.validator import check_js_syntax, validate_patched_asar
    from engine.asar import AsarArchive
    from launcher import launch_antigravity
    from watcher.service import run_watcher

def cmd_status(args):
    print("\n=======================================================")
    print("      Antigravity 中文汉化套件 - 系统状态")
    print("=======================================================")
    st = get_current_status()
    if "error" in st:
        print(f"[错误] {st['error']}")
        return

    print(f"安装目录:     {st['antigravity_dir']}")
    print(f"客户端版本:   {st['version'] or '未知'}")
    print(f"文件 SHA256:  {st['current_hash']}")
    
    status_text = "\033[92m已成功汉化 (生效中)\033[0m" if st['is_patched'] else "\033[93m官方英文原版 (未汉化)\033[0m"
    print(f"当前汉化状态: {status_text}")
    print(f"官方纯净备份: {'存在 (' + st['clean_hash'][:10] + '...)' if st['clean_backup_exists'] else '未创建'}")
    
    if st['has_update']:
        print(f"\033[91m[提示] 检测到官方程序发生了版本更新，当前汉化已脱轨，建议运行 repair 或使用 launcher 启动！\033[0m")

    print(f"上次注入时间: {st['last_patch_time'] or '无记录'}")
    print(f"上次使用适配: {st['last_patch_adapter'] or '无'}")
    print(f"已打补丁文件: {', '.join(st['patched_files']) if st['patched_files'] else '无'}")
    print(f"累计自愈次数: {st['self_healing_count']} 次")
    print("=======================================================\n")

def cmd_verify(args):
    print("\n[开始审计] 正在深度检验当前 Antigravity 汉化健康度...")
    paths = get_paths()
    if not paths:
        print("[错误] 未找到 Antigravity 路径。")
        return

    asar_path = paths['asar_path']
    if not os.path.exists(asar_path):
        print(f"[错误] 目标 ASAR 不存在: {asar_path}")
        return

    ok, vmsg = validate_patched_asar(asar_path)
    if not ok:
        print(f"\033[91m[失败] ASAR 结构完整性校验未通过: {vmsg}\033[0m")
        return
    print(f"• ASAR 结构与核心文件: \033[92m正常\033[0m")

    archive = AsarArchive(asar_path)
    ui_injected = False
    menu_injected = False

    if archive.has_file('/dist/utils.js'):
        txt = archive.read_text('/dist/utils.js')
        if '__chineseTranslatorScript' in txt:
            ui_injected = True
            ok_syn, smsg = check_js_syntax(txt)
            color = "\033[93m" if "degraded" in smsg else "\033[92m"
            print(f"• 主渲染调度注入 (/dist/utils.js): {color}{smsg}\033[0m")
        else:
            print(f"• 主渲染调度注入 (/dist/utils.js): \033[93m未检测到\033[0m")

    if archive.has_file('/dist/preload.js'):
        txt = archive.read_text('/dist/preload.js')
        if '__antigravity_chinese_active' in txt:
            ui_injected = True
            ok_syn, smsg = check_js_syntax(txt)
            color = "\033[93m" if "degraded" in smsg else "\033[92m"
            print(f"• Preload 渲染注入 (/dist/preload.js): {color}{smsg}\033[0m")

    if archive.has_file('/dist/menu.js'):
        txt = archive.read_text('/dist/menu.js')
        if 'translateMenu' in txt:
            menu_injected = True
            ok_syn, smsg = check_js_syntax(txt)
            color = "\033[93m" if "degraded" in smsg else "\033[92m"
            print(f"• 原生应用菜单汉化 (/dist/menu.js): {color}{smsg}\033[0m")
        else:
            print(f"• 原生应用菜单汉化 (/dist/menu.js): \033[93m未检测到\033[0m")

    print("\n-------------------------------------------------------")
    if ui_injected and menu_injected:
        print("\033[92m[结论] 汉化系统状态极佳！所有注入层均通过语法与签名审计。\033[0m")
    elif ui_injected:
        print("\033[92m[结论] 界面核心汉化已生效，主菜单未注入。\033[0m")
    else:
        print("\033[91m[结论] 汉化处于失效状态，请运行 python cli.py repair 重新注入。\033[0m")
    print("-------------------------------------------------------\n")

def cmd_install(args):
    print("[执行] 正在安装 Antigravity 中文汉化套件...")
    ok, msg = perform_patch(force=True, is_self_healing=False)
    if ok:
        print(f"\n\033[92m{msg}\033[0m")
        print("提示：重新启动 Antigravity 客户端即可体验全新中文界面！")
    else:
        print(f"\n\033[91m[失败] {msg}\033[0m")

def cmd_repair(args):
    print("[执行] 正在重新执行汉化注入与自愈修复...")
    ok, msg = perform_patch(force=True, is_self_healing=True)
    if ok:
        print(f"\n\033[92m[成功] {msg}\033[0m")
        print("提示：请重新启动 Antigravity 客户端生效。")
    else:
        print(f"\n\033[91m[失败] {msg}\033[0m")

def cmd_restore(args):
    print("[执行] 正在安全恢复官方原版英文界面...")
    ok, msg = restore_official_clean()
    if ok:
        print(f"\n\033[92m[成功] {msg}\033[0m")
    else:
        print(f"\n\033[91m[失败] {msg}\033[0m")

def cmd_watch(args):
    run_watcher()

def cmd_launch(args):
    launch_antigravity(args.extra_args if hasattr(args, 'extra_args') else None)

def main():
    parser = argparse.ArgumentParser(description="Antigravity 简体中文自愈汉化系统 CLI 管理工具")
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    subparsers.add_parser("status", help="查看 Antigravity 版本与汉化状态")
    subparsers.add_parser("verify", help="验证汉化文件完整性与语法健康度")
    subparsers.add_parser("install", help="安装汉化补丁")
    subparsers.add_parser("repair", help="强制重新注入并自愈修复")
    subparsers.add_parser("restore", help="安全恢复官方纯净原版")
    subparsers.add_parser("watch", help="启动后台自动自愈监听守护服务")
    launch_p = subparsers.add_parser("launch", help="通过智能自愈启动器拉起 Antigravity")
    launch_p.add_argument('extra_args', nargs=argparse.REMAINDER, help="传递给客户端的额外参数")

    if len(sys.argv) == 1:
        parser.print_help()
        return

    args = parser.parse_args()

    handlers = {
        "status": cmd_status,
        "verify": cmd_verify,
        "install": cmd_install,
        "repair": cmd_repair,
        "restore": cmd_restore,
        "watch": cmd_watch,
        "launch": cmd_launch
    }

    if args.command in handlers:
        handlers[args.command](args)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
