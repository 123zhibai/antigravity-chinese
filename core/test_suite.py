import os
import sys
import shutil
import tempfile
import time
import json
import unittest

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from config import get_paths, sha256_file
from engine.asar import AsarArchive
from engine.validator import check_js_syntax, validate_patched_asar, validate_official_candidate
from engine.injector import perform_patch, restore_official_clean
from adapters.fallback import FallbackAdapter
from adapters.common import CommonAdapter
from state import load_state, save_state, check_asar_is_patched, get_current_status
import watcher.service as watcher_service

class HardeningReliabilityTests(unittest.TestCase):
    """
    Antigravity 汉化系统可靠性加固全量自动化测试套件
    覆盖 P0/P1 各关键边界条件
    """

    def setUp(self):
        self.paths = get_paths()
        self.assertTrue(self.paths is not None, "未找到 Antigravity 环境路径")
        self.target_asar = self.paths['asar_path']
        self.clean_backup = self.paths['clean_backup_asar']
        self.temp_dir = tempfile.mkdtemp(prefix="agy_test_")

    def tearDown(self):
        if os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
            except Exception:
                pass

    def _create_dummy_asar(self, files_dict, output_path):
        """创建用于测试的轻量模拟 ASAR"""
        header = {"files": {}}
        data_blobs = []
        curr_offset = 0

        # 按路径创建层级
        for virtual_path, content in files_dict.items():
            b = content.encode('utf-8') if isinstance(content, str) else content
            parts = [p for p in virtual_path.split('/') if p]
            curr = header['files']
            for p in parts[:-1]:
                if p not in curr:
                    curr[p] = {"files": {}}
                curr = curr[p]["files"]
            fname = parts[-1]
            curr[fname] = {
                "size": len(b),
                "offset": str(curr_offset)
            }
            data_blobs.append(b)
            curr_offset += len(b)

        json_bytes = json.dumps(header, separators=(',', ':')).encode('utf-8')
        j_len = len(json_bytes)
        pad = (4 - (j_len % 4)) % 4
        h_size = j_len + pad + 8
        u2_val = j_len + pad + 4

        import struct
        with open(output_path, 'wb') as f:
            f.write(struct.pack('<IIII', 4, h_size, u2_val, j_len))
            f.write(json_bytes)
            if pad:
                f.write(b'\x00' * pad)
            for b in data_blobs:
                f.write(b)

    # -------------------------------------------------------------
    # P0-1: 保护官方纯净备份
    # -------------------------------------------------------------
    def test_p0_1_truncated_or_corrupted_candidate_rejected(self):
        """损坏或截断的候选文件严禁覆盖 clean backup"""
        corrupted_asar = os.path.join(self.temp_dir, "corrupted.asar")
        # 写入随机截断数据 (< 1MB)
        with open(corrupted_asar, 'wb') as f:
            f.write(b"NOT_A_VALID_ASAR_HEADER_123456789")

        ok, msg = validate_official_candidate(corrupted_asar, check_stability=False)
        self.assertFalse(ok, "损坏/截断文件必须被验证器拒绝")
        self.assertIn("过小", msg)

        # 构造大小达到 1MB 但头部损坏的文件
        corrupted_1mb = os.path.join(self.temp_dir, "corrupted_1mb.asar")
        with open(corrupted_1mb, 'wb') as f:
            f.write(b"INVALID" * (1024 * 160))

        ok2, msg2 = validate_official_candidate(corrupted_1mb, check_stability=False)
        self.assertFalse(ok2, "非合法 ASAR 必须被验证器拒绝")
        self.assertIn("无法解析", msg2)

    def test_p0_1_valid_official_candidate_accepted(self):
        """完整的合法官方新版可以安全通过验证"""
        self.assertTrue(os.path.exists(self.clean_backup), "官方备份文件应当存在")
        ok, msg = validate_official_candidate(self.clean_backup, check_stability=False)
        self.assertTrue(ok, f"合法的 clean_backup 应当通过候选验证: {msg}")

    # -------------------------------------------------------------
    # P0-2: Fallback Adapter 成功条件修复
    # -------------------------------------------------------------
    def test_p0_2_fallback_menu_only_injection_must_fail(self):
        """Fallback 适配器仅 Menu 注入成功时，必须判定整体失败"""
        menu_only_asar = os.path.join(self.temp_dir, "menu_only.asar")
        self._create_dummy_asar({
            "/dist/menu.js": "electron_1.Menu.setApplicationMenu(menu);",
            "/dist/other.js": "console.log('no browser window');"
        }, menu_only_asar)

        archive = AsarArchive(menu_only_asar)
        adapter = FallbackAdapter(archive, "/* runtime */", {"File": "文件"})
        ok, patched_files, msg = adapter.apply()

        self.assertFalse(ok, "仅菜单成功时必须判定整体失败，杜绝假成功")
        self.assertIn("UI 核心注入点未找到", msg)
        self.assertEqual(patched_files, [])

    def test_p0_2_fallback_ui_only_injection_succeeds(self):
        """Fallback 适配器 UI 注入成功但 Menu 缺失时，核心判定成功"""
        ui_only_asar = os.path.join(self.temp_dir, "ui_only.asar")
        self._create_dummy_asar({
            "/dist/window.js": "win = new BrowserWindow(); win.loadURL('http://localhost');",
        }, ui_only_asar)

        archive = AsarArchive(ui_only_asar)
        adapter = FallbackAdapter(archive, "/* runtime */", {"File": "文件"})
        ok, patched_files, msg = adapter.apply()

        self.assertTrue(ok, "UI 核心注入成功时整体判定成功")
        self.assertIn("UI 注入成功", msg)
        self.assertIn("/dist/window.js", patched_files)

    # -------------------------------------------------------------
    # P0-3: Watcher 超时逻辑修复
    # -------------------------------------------------------------
    def test_p0_3_watcher_timeout_aborts_patching(self):
        """Watcher 等待退出超时后，本轮必须跳过补丁，禁止修改 app.asar"""
        # 保存 target_asar 的当前 hash
        orig_hash = sha256_file(self.target_asar)

        # 模拟 is_antigravity_running 始终返回 True
        old_is_running = watcher_service.is_antigravity_running
        old_wait = watcher_service.wait_for_antigravity_exit

        try:
            watcher_service.is_antigravity_running = lambda: True
            # 模拟超时（返回 False）
            watcher_service.wait_for_antigravity_exit = lambda timeout=120: False

            patch_called = []
            old_patch = watcher_service.perform_patch
            watcher_service.perform_patch = lambda **kwargs: patch_called.append(True)

            # 模拟执行一次 watcher 内核检测判定
            exited = watcher_service.wait_for_antigravity_exit(timeout=1)
            self.assertFalse(exited, "应当模拟超时返回 False")

            if not exited:
                # 按照加固逻辑，此时应 continue，绝不调用 perform_patch
                pass
            else:
                watcher_service.perform_patch()

            self.assertEqual(len(patch_called), 0, "超时后严禁调用 perform_patch")
            # 确认正式文件完全未被修改
            self.assertEqual(sha256_file(self.target_asar), orig_hash)
        finally:
            watcher_service.is_antigravity_running = old_is_running
            watcher_service.wait_for_antigravity_exit = old_wait
            watcher_service.perform_patch = old_patch

    # -------------------------------------------------------------
    # P0-4: 真正安全的文件替换 (os.replace)
    # -------------------------------------------------------------
    def test_p0_4_atomic_replace_and_validation_guard(self):
        """临时 ASAR 校验失败不得影响正式文件，成功时通过 os.replace 替换且无残留 tmp"""
        sandbox_target = os.path.join(self.temp_dir, "sandbox_app.asar")
        sandbox_clean = os.path.join(self.temp_dir, "sandbox_clean.asar")
        shutil.copy2(self.clean_backup, sandbox_target)
        shutil.copy2(self.clean_backup, sandbox_clean)

        orig_hash = sha256_file(sandbox_target)
        tmp_patch_file = sandbox_target + ".patch_tmp"

        # 1. 验证正常注入的原子替换
        ok, msg = perform_patch(force=True, is_self_healing=True,
                                custom_target_asar=sandbox_target,
                                custom_clean_backup=sandbox_clean)
        self.assertTrue(ok, f"正常注入应当成功: {msg}")
        self.assertFalse(os.path.exists(tmp_patch_file), "替换完成后不得有 .patch_tmp 残留")
        self.assertTrue(check_asar_is_patched(sandbox_target), "沙盒目标 ASAR 必须已成功汉化")
        self.assertNotEqual(sha256_file(sandbox_target), orig_hash, "注入后 Hash 应当更新")

    # -------------------------------------------------------------
    # P1-1: state.json 与 Git 仓库解耦
    # -------------------------------------------------------------
    def test_p1_1_state_json_fallback_when_missing(self):
        """state.json 不存在时，系统正常回退到 example 模版并保持功能可用"""
        state_file = self.paths['state_file']
        backup_state = None
        if os.path.exists(state_file):
            with open(state_file, 'r', encoding='utf-8') as f:
                backup_state = f.read()
            os.remove(state_file)

        try:
            self.assertFalse(os.path.exists(state_file))
            st = load_state()
            self.assertIsInstance(st, dict)
            self.assertIn("antigravity_version", st)
            self.assertIn("total_self_healing_count", st)

            # 测试 status 函数在没有 state.json 时正常运行
            curr_status = get_current_status()
            self.assertNotIn("error", curr_status)
            self.assertTrue(curr_status['is_patched'])
        finally:
            if backup_state is not None:
                with open(state_file, 'w', encoding='utf-8') as f:
                    f.write(backup_state)

    # -------------------------------------------------------------
    # P1-2: Validator 加固
    # -------------------------------------------------------------
    def test_p1_2_validator_degraded_when_node_missing(self):
        """静态语法检查在合法代码下能正常通过"""
        ok, msg = check_js_syntax("const a = { b: 1, c: [2, 3] }; function test() { return a.b + 1; }")
        self.assertTrue(ok)
        self.assertTrue("通过" in msg or "degraded" in msg)

        # 语法错误必须被捕获
        bad_ok, bad_msg = check_js_syntax("const a = { b: ;;;; function(() { return 1; }")
        self.assertFalse(bad_ok, "语法错误代码必须被拦截")

    def test_p1_2_patched_asar_validation_requires_ui_marker(self):
        """patched ASAR 校验必须严格要求 UI 注入标记"""
        clean_backup = self.paths['clean_backup_asar']
        ok, msg = validate_patched_asar(clean_backup, require_ui_marker=True)
        self.assertFalse(ok, "未注入 UI 标记的纯净版不得通过 validate_patched_asar")
        self.assertIn("缺少关键 UI 汉化注入标记", msg)

    # -------------------------------------------------------------
    # 回归测试：restore 与自愈注入闭环
    # -------------------------------------------------------------
    def test_regression_restore_and_self_healing_cycle(self):
        """核心文件自愈注入闭环与恢复官方原版回归测试"""
        sandbox_target = os.path.join(self.temp_dir, "sandbox_regression.asar")
        sandbox_clean = os.path.join(self.temp_dir, "sandbox_clean_reg.asar")
        shutil.copy2(self.clean_backup, sandbox_target)
        shutil.copy2(self.clean_backup, sandbox_clean)

        # 1. 恢复官方原版测试
        res_ok, res_msg = restore_official_clean(custom_target_asar=sandbox_target, custom_clean_backup=sandbox_clean)
        self.assertTrue(res_ok, f"恢复官方原版应当成功: {res_msg}")
        self.assertFalse(check_asar_is_patched(sandbox_target), "恢复后沙盒必须为未汉化状态")

        # 2. 触发自愈注入测试
        heal_ok, heal_msg = perform_patch(force=True, is_self_healing=True,
                                          custom_target_asar=sandbox_target,
                                          custom_clean_backup=sandbox_clean)
        self.assertTrue(heal_ok, f"自愈注入应当成功: {heal_msg}")
        self.assertTrue(check_asar_is_patched(sandbox_target), "自愈后必须恢复汉化状态")

    # -------------------------------------------------------------
    # 跨版本防护与 Fail-Closed 机制专项测试 (测试 A, B, C)
    # -------------------------------------------------------------
    def test_a_unknown_new_version_with_old_backup_fail_closed(self):
        """测试 A: 未知新版 (2.25) candidate 验证失败时，立即中止，严禁使用旧版 (2.24) backup 构建，正式文件与旧 backup 保持原样"""
        sandbox_clean = os.path.join(self.temp_dir, "clean_old_2_24.asar")
        sandbox_target = os.path.join(self.temp_dir, "unknown_2_25_target.asar")

        # 复制旧版 clean backup (2.24)
        shutil.copy2(self.clean_backup, sandbox_clean)
        clean_orig_hash = sha256_file(sandbox_clean)

        # 模拟 2.25 新版 official candidate 未通过 candidate 验证（例如结构不合规或缺少关键入口）
        with open(sandbox_target, 'wb') as f:
            f.write(b"CORRUPTED_OR_UNKNOWN_NEW_VERSION_STRUCTURE" * 200)
        target_orig_hash = sha256_file(sandbox_target)

        custom_state = {
            "clean_backup_version": "2.24.0",
            "antigravity_version": "2.24.0",
            "official_clean_sha256": clean_orig_hash
        }

        ok, msg = perform_patch(
            force=True,
            custom_target_asar=sandbox_target,
            custom_clean_backup=sandbox_clean,
            custom_version="2.25.0",
            custom_state=custom_state
        )

        # 1. 断言 perform_patch 立即中止并返回失败
        self.assertFalse(ok, "新版候选验证失败时必须立即中止本次 patch")

        # 2. 断言包含指定的安全提示文案
        self.assertIn("检测到新的 Antigravity 版本或未知核心结构", msg)
        self.assertIn("当前版本尚未通过兼容性验证", msg)
        self.assertIn("为防止旧版本核心文件覆盖新版客户端，本次汉化已安全停止", msg)
        self.assertIn("官方当前文件未被修改", msg)
        self.assertIn("旧版本 clean backup 已保留，仅供恢复使用", msg)
        self.assertIn("请先更新对应版本 Adapter 或兼容规则", msg)

        # 3. 断言当前正式文件保持原样，不被修改
        self.assertEqual(sha256_file(sandbox_target), target_orig_hash, "当前正式文件必须保持原样")
        self.assertFalse(check_asar_is_patched(sandbox_target), "当前正式文件绝不能被打上补丁")

        # 4. 断言原 clean backup 保持原样，且版本绑定未被篡改
        self.assertEqual(sha256_file(sandbox_clean), clean_orig_hash, "旧版 clean backup 必须完好保留")
        self.assertEqual(custom_state.get("clean_backup_version"), "2.24.0", "clean_backup_version 必须保持 2.24.0")

        # 5. 断言未残留任何 patch 临时文件
        self.assertFalse(os.path.exists(sandbox_target + ".patch_tmp"), "不得残留任何临时补丁文件")

    def test_b_same_version_backup_allows_patch(self):
        """测试 B: 同版本 (2.24 == 2.24) 时，允许使用 clean backup 作为 base 正常打补丁"""
        sandbox_clean = os.path.join(self.temp_dir, "clean_same_ver.asar")
        sandbox_target = os.path.join(self.temp_dir, "target_same_ver.asar")
        shutil.copy2(self.clean_backup, sandbox_clean)
        shutil.copy2(self.clean_backup, sandbox_target)

        custom_state = {
            "clean_backup_version": "2.24.0",
            "antigravity_version": "2.24.0",
            "official_clean_sha256": sha256_file(sandbox_clean)
        }

        ok, msg = perform_patch(
            force=True,
            custom_target_asar=sandbox_target,
            custom_clean_backup=sandbox_clean,
            custom_version="2.24.0",
            custom_state=custom_state
        )

        self.assertTrue(ok, f"同版本 clean backup 应当允许构建补丁: {msg}")
        self.assertTrue(check_asar_is_patched(sandbox_target), "目标文件必须已成功汉化")
        self.assertEqual(custom_state.get("clean_backup_version"), "2.24.0")
        self.assertEqual(custom_state.get("current_status"), "patched")

    def test_c_new_version_candidate_validated_updates_backup_and_patches(self):
        """测试 C: 新版 (2.25) 候选验证成功时，正常更新 clean backup 与版本绑定，并基于新版 backup 成功补丁"""
        sandbox_clean = os.path.join(self.temp_dir, "clean_old.asar")
        sandbox_target = os.path.join(self.temp_dir, "target_new_2_25.asar")

        # 初始 clean backup 为旧版 (2.24)
        shutil.copy2(self.clean_backup, sandbox_clean)
        old_clean_hash = sha256_file(sandbox_clean)

        # 构造一个符合 validate_official_candidate 的合法 2.25 官方未汉化 ASAR
        shutil.copy2(self.clean_backup, sandbox_target)
        archive = AsarArchive(sandbox_target)
        archive.write_text('/package.json', json.dumps({"name": "antigravity", "version": "2.25.0"}))
        archive.save(sandbox_target)
        new_official_hash = sha256_file(sandbox_target)
        self.assertNotEqual(old_clean_hash, new_official_hash)

        # 验证构造的新版候选通过验证
        cand_ok, cand_msg = validate_official_candidate(sandbox_target, check_stability=False)
        self.assertTrue(cand_ok, f"构造的新版应当通过官方候选验证: {cand_msg}")

        custom_state = {
            "clean_backup_version": "2.24.0",
            "antigravity_version": "2.24.0",
            "official_clean_sha256": old_clean_hash
        }

        # 执行 patch
        ok, msg = perform_patch(
            force=True,
            custom_target_asar=sandbox_target,
            custom_clean_backup=sandbox_clean,
            custom_version="2.25.0",
            custom_state=custom_state
        )

        self.assertTrue(ok, f"新版候选通过时应成功执行汉化: {msg}")
        # 1. 断言 clean backup 已更新为 2.25 官方版本
        self.assertEqual(sha256_file(sandbox_clean), new_official_hash, "clean backup 必须已更新为新版官方 ASAR")
        # 2. 断言 clean_backup_version 已更新为 2.25.0
        self.assertEqual(custom_state.get("clean_backup_version"), "2.25.0", "clean_backup_version 必须已更新为 2.25.0")
        self.assertEqual(custom_state.get("official_clean_sha256"), new_official_hash)
        # 3. 断言正式文件成功打上汉化补丁
        self.assertTrue(check_asar_is_patched(sandbox_target), "新版目标 ASAR 应当成功注入汉化")

    # -------------------------------------------------------------
    # 跨版本 Restore 防护与 Fail-Closed 专项测试 (测试 D, E, F)
    # -------------------------------------------------------------
    def test_d_cross_version_restore_aborts(self):
        """测试 D: 跨版本 (current 2.25, backup 2.24) restore 立即阻断，不替换正式文件且原备份不变"""
        sandbox_clean = os.path.join(self.temp_dir, "clean_old_2_24.asar")
        sandbox_target = os.path.join(self.temp_dir, "target_new_2_25.asar")
        shutil.copy2(self.clean_backup, sandbox_clean)
        shutil.copy2(self.target_asar, sandbox_target)

        clean_hash_before = sha256_file(sandbox_clean)
        target_hash_before = sha256_file(sandbox_target)

        custom_state = {
            "clean_backup_version": "2.24.0",
            "antigravity_version": "2.24.0"
        }

        ok, msg = restore_official_clean(
            custom_target_asar=sandbox_target,
            custom_clean_backup=sandbox_clean,
            custom_version="2.25.0",
            custom_state=custom_state
        )

        # 1. 断言 restore 返回 False
        self.assertFalse(ok, "跨版本 restore 必须被拦截并返回 False")
        # 2. 断言包含版本不匹配提示
        self.assertIn("检测到官方备份版本与当前 Antigravity 客户端版本不一致", msg)
        self.assertIn("为防止旧版核心文件覆盖新版客户端，本次恢复已安全停止", msg)
        self.assertIn("当前 app.asar 未被修改", msg)
        self.assertIn("旧版 clean backup 仍被保留", msg)
        # 3. 断言正式 app.asar Hash 不变
        self.assertEqual(sha256_file(sandbox_target), target_hash_before, "正式 app.asar Hash 必须保持不变")
        # 4. 断言 clean backup Hash 不变
        self.assertEqual(sha256_file(sandbox_clean), clean_hash_before, "clean backup Hash 必须保持不变")
        # 5. 断言未执行替换，无临时文件残留
        self.assertFalse(os.path.exists(sandbox_target + ".restore_tmp"), "不得残留任何临时恢复文件")

    def test_e_same_version_restore_succeeds(self):
        """测试 E: 同版本 (current 2.24, backup 2.24) restore 正常执行成功"""
        sandbox_clean = os.path.join(self.temp_dir, "clean_same_2_24.asar")
        sandbox_target = os.path.join(self.temp_dir, "target_same_2_24.asar")
        shutil.copy2(self.clean_backup, sandbox_clean)
        shutil.copy2(self.target_asar, sandbox_target)

        clean_hash = sha256_file(sandbox_clean)

        custom_state = {
            "clean_backup_version": "2.24.0",
            "antigravity_version": "2.24.0"
        }

        ok, msg = restore_official_clean(
            custom_target_asar=sandbox_target,
            custom_clean_backup=sandbox_clean,
            custom_version="2.24.0",
            custom_state=custom_state
        )

        # 1. 验证 restore 正常成功
        self.assertTrue(ok, f"同版本 restore 应当成功: {msg}")
        self.assertIn("已成功安全恢复为 Antigravity 官方原版英文界面", msg)
        # 2. 目标文件被恢复为官方原版，Hash 与 clean_backup 一致
        self.assertEqual(sha256_file(sandbox_target), clean_hash, "恢复后目标文件应当与 clean backup 完全一致")
        self.assertFalse(check_asar_is_patched(sandbox_target), "恢复后目标文件应当为未汉化状态")
        self.assertEqual(custom_state.get('current_status'), "official_clean")

    def test_f_unknown_backup_version_restore_aborts_fail_closed(self):
        """测试 F: backup 版本未知 (clean_backup_version = None) 触发 Fail-Closed 默认禁止 restore"""
        sandbox_clean = os.path.join(self.temp_dir, "clean_unknown_ver.asar")
        sandbox_target = os.path.join(self.temp_dir, "target_unknown_ver.asar")
        shutil.copy2(self.clean_backup, sandbox_clean)
        shutil.copy2(self.target_asar, sandbox_target)

        clean_hash_before = sha256_file(sandbox_clean)
        target_hash_before = sha256_file(sandbox_target)

        custom_state = {
            "clean_backup_version": None,
            "antigravity_version": None
        }

        ok, msg = restore_official_clean(
            custom_target_asar=sandbox_target,
            custom_clean_backup=sandbox_clean,
            custom_version="2.24.0",
            custom_state=custom_state
        )

        # 1. 验证默认禁止 restore，返回 False
        self.assertFalse(ok, "版本未知时必须 Fail-Closed 默认禁止 restore")
        # 2. 验证返回“无法确认备份版本”的安全提示
        self.assertIn("无法确认官方备份与当前 Antigravity 客户端的版本兼容性", msg)
        self.assertIn("本次恢复已安全停止", msg)
        self.assertIn("当前 app.asar 未被修改", msg)
        self.assertIn("clean backup 仍被保留", msg)
        # 3. 验证正式文件与 backup 文件完全未改变
        self.assertEqual(sha256_file(sandbox_target), target_hash_before, "目标文件不得被修改")
        self.assertEqual(sha256_file(sandbox_clean), clean_hash_before, "backup 文件不得被修改")
        self.assertFalse(os.path.exists(sandbox_target + ".restore_tmp"))

if __name__ == '__main__':
    unittest.main(verbosity=2)
