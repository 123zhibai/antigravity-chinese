# Antigravity 汉化系统当前运行状态与审计基线 (CURRENT_STATE)

> **审计目的**：供开发者与 AI 审计工具直接读取，以核查当前工程真实实现状态、识别薄弱环节并指导后续针对性升级。  
> **记录基准时间**：2026-10-17  
> **基线维护版本**：`v3.2.0-cross-version-guarded`  
> **前置 Commit**：`452e14e docs: align audit baseline with verified capabilities`  
> **当前维护状态**：已完成全部 P0 核心安全链路、P1 维护性加固，以及**跨版本 Fail-Closed 隔离防护专项升级（禁止旧版 clean backup 跨版本用于未知新版打补丁）**，全量自动化套件 13 项测试 100% 通过。

---

## 一、 环境与版本信息

- **宿主程序版本**：Google Antigravity `2.24.0` (`ProductVersion: 2.24.0.0`, `FileVersion: 2.24.0`)
- **宿主架构**：Windows x64 Desktop (Electron)
- **汉化系统版本**：`v3.2.0-cross-version-guarded`
- **Clean Backup 绑定版本**：`2.24.0`
- **当前官方核心文件 SHA-256**：`bd10a0054ca3ad469142b2c2757566493ecc0afb934b9a61ce45d38a4d09316e` (4,486,221 字节)
- **补丁注入后核心文件 SHA-256**：`d031dc1e5465b6b1c5fc8fa340ed9e4045a58f0267bdae710f980bb8763fd7d5`

---

## 二、 当前可正常工作的功能

1. **界面静态元素汉化**：
   - 左侧主导航与历史对话列表（新建对话、对话历史、自动化、自定义扩展、设置等）；
   - 输入框浮层上下文菜单（添加上下文、媒体文件、提及与引用、快捷操作、内置浏览器）；
   - 顶部面包屑与项目菜单（新建项目、快速开始等）；
   - 设置中心所有选项卡：`常规设置`、`应用设置`、`历史对话`、`CLI 项目`、`模型与用量`；
   - 底部输入区及占位符提示（`输入任何问题，@ 提及文件/符号，/ 调用操作...`）。
2. **动态渲染与异步流处理**：
   - 动态模型套餐识别（如 `Your Plan: Google AI Pro` ➔ `当前套餐：Google AI Pro`）；
   - 动态限额倒计时解析（自动将 `weekly limit, which fully refreshes in 4 days, 15 hours` 转换为自然中文时段表达）；
   - 智能体思考耗时（`Thinking for 12s` ➔ `思考耗时 12s`）；
   - 文件与命令执行状态（已分析、已编辑、已创建、正在执行）。
3. **加固后的自愈与安全保护体系**：
   - **官方纯净备份严格准入 (P0-1)**：在更新 clean backup 前强制执行多重采样稳定性检测（大小与 SHA-256 采样一致性）、ASAR 解包解析、关键入口（`dist/main.js`、`dist/utils.js`）与纯净性验证，彻底防止更新写入中或损坏文件污染备份；
   - **严格成功判定标准 (P0-2)**：Fallback 与 Common 适配器强制以 UI 注入成功为最低且必要条件，仅菜单成功时严禁判定整体成功，彻底杜绝假成功；
   - **Watcher 退出超时熔断 (P0-3)**：`wait_for_antigravity_exit()` 超时返回 False 时立即阻断当轮补丁并记录 warning 日志，严禁在客户端运行中强改 `app.asar`；
   - **真正安全的原子文件替换 (P0-4)**：`构建临时文件 ➔ 完整性与汉化 Marker 校验 ➔ 同目录临时文件 ➔ os.replace()`，确保校验失败或异常时正式文件丝毫不受损，无残留 `.patch_tmp`；
   - **仓库基线解耦 (P1-1)**：`core/state.json` 已移入 `.gitignore`，新增 `core/state.example.json`，即使全新 clone 无 state 文件系统亦能平滑自初始化并正常运行；
   - **增强校验器 (P1-2)**：增加 UI marker 校验、expected_files 检查，并在缺少 Node.js 时返回明确的 `degraded verification` 标识；
   - **跨版本 Fail-Closed 隔离防护**：强制给 clean backup 绑定宿主版本（`clean_backup_version`），严禁跨版本默认作为 patch base。当未汉化文件未通过候选验证时，立即中止补丁、保持正式文件与旧备份原样，并给出安全停机提示；
   - **综合测试套件**：自动化测试套件扩充至 13 项（含测试 A：未知新版+旧 backup 阻断拦截；测试 B：同版本 backup 正常注入；测试 C：新版候选验证成功后更新 backup 与版本绑定并注入），全部测试 100% 通过。
4. **代码与终端环境防护**：
   - 严格排除 `.monaco-editor`、`.monaco-diff-editor`、`.prism-code`、`.xterm`、`<pre>`、`<code>`，用户编码与命令行输入输出绝对不受汉化篡改。

---

## 三、 已知失效 / 不稳定功能与边界条件

1. **运行期热替换感知滞后**：
   - 由于 Electron 主进程在启动时即将 `dist/utils.js` 和 `dist/menu.js` 加载入 Node 模块缓存，若在客户端运行途中由更新程序替换了 `app.asar`，必须关闭并重新打开 Antigravity，补丁代码方能被主进程初始化。
2. **Windows 独占锁定限制**：
   - 当 Antigravity.exe 正在前台运行时，Windows 操作系统会锁定 `app.asar`。此时直接执行 `os.replace` 会被系统拒绝访问（WinError 5）。因此自愈与补丁必须且只能在应用完全退出后执行（Watcher 与 Launcher 已严格保证该时序）。

---

## 四、 汉化覆盖范围

- **词库精确条目**：324 条静态高频界面词条；
- **输入框占位符条目**：12 组输入框文本映射；
- **动态正则规则**：9 组核心动态模式解析器（时长、套餐、限额、操作状态）；
- **原生应用菜单**：涵盖 Windows 标题栏菜单 `File`, `Edit`, `View`, `Window`, `Help` 及其所有标准二级子项与快捷键助记符（带 `(&F)`, `(&E)` 等快捷键标识）。

---

## 五、 核心实现方案与技术选型

1. **宿主解耦**：所有汉化逻辑、独立备份、状态库与日志均位于独立插件目录 `~/.gemini/config/plugins/antigravity-chinese-pack/core/`，官方安装目录仅作为受托注入宿主。
2. **纯 Python 高性能 ASAR 引擎**：自研 `core/engine/asar.py`，摆脱外部 Node `asar` 命令行依赖，直接在二进制流层面解析 JSON Header、校验 Offset 与 SHA-256 integrity block，零依赖即可完成安全重构。
3. **基于特征的多锚点适配器架构 (Adapters Pattern)**：
   - `v2_24.py`：针对 2.24.x 专有特征；
   - `common.py`：通用启发式匹配；
   - `fallback.py`：全包扫描容灾兜底。
4. **防御性安全机制 (Fail-Safe)**：
   - 注入前对候选版本严格执行稳定性与完整性分析；
   - 修改后强制通过 JS 语法分析与 Marker 校验；
   - 目标目录构建 ➔ 校验 ➔ `os.replace` 原子替换；
   - 任意环节异常自动触发回滚或保留原文件，保证官方程序随时可用。

---

## 六、 最容易因 Antigravity 官方更新而失效的位置

1. **官方更新完全覆盖 `app.asar`**：
   - **风险**：官方安装程序覆盖 `resources/app.asar`，导致注入代码被抹除；
   - **应对**：已通过 `core/launcher.py`（启动时检测并自动秒级重打）和 `core/watcher/service.py`（后台监听）解决。
2. **`dist/utils.js` 内部窗口创建函数签名变动**：
   - **风险**：若官方将 `BrowserWindow` 实例的创建迁移至独立类或模块，旧正则可能无法匹配；
   - **应对**：`adapters/common.py` 与 `adapters/fallback.py` 具备跨文件扫描与 Preload 注入回退能力。
3. **`dist/menu.js` 菜单配置方式变动**：
   - **风险**：若官方不再通过 `Menu.setApplicationMenu` 统一应用菜单，菜单汉化可能需要适配新的注册钩子。

---

## 七、 当前仍存在的技术债

1. **前端 TreeWalker 全量重扫策略**：
   - 当前在 `window.addEventListener('click')` 时会微延迟执行一次 `translateTree(document.body)`。虽然在现代多核 CPU 上执行仅耗时数毫秒，但后续可优化为仅针对点击相关的局部容器进行定向补扫。
2. **跨平台启动器支持**：
   - 当前主要针对 Windows 系统环境（路径探测、批处理启动器 `agy-launch.bat`）。后续可增加 macOS (`.sh` / `.command`) 与 Linux 启动器的开箱即用支持。

---

## 八、 最近一次修改内容（P0 / P1 可靠性加固）

- **P0-1 官方纯净备份安全加固**：新增 `validate_official_candidate()`，防止官方更新写入途中将截断或损坏文件误当纯净备份覆盖。
- **P0-2 修复 Fallback 假成功**：修改 `fallback.py` 与 `common.py`，强制以 UI 注入成功作为核心成功的必要前提，仅菜单成功时判定整体失败。
- **P0-3 Watcher 超时熔断**：Watcher 等待退出超时后阻断当轮补丁操作并记录 warning 日志，严禁在客户端运行时并发修改核心文件。
- **P0-4 真正安全的原子替换**：同目录构建临时文件 ➔ 完整性与汉化 Marker 校验 ➔ `os.replace()` 原子替换，杜绝文件损坏风险。
- **P1-1 状态文件与仓库解耦**：`state.json` 加入 `.gitignore`，提供 `state.example.json`，实现无 state 状态下的平滑自初始化。
- **P1-2 Validator 增强**：强化 Marker 存在性检查与 `expected_files` 验证，缺少 Node 时明确标出 `degraded verification`。
- **P1-3 文档与测试口径校准**：将“全生命周期自愈测试 100% 通过”修正为“核心文件自愈注入闭环测试通过”，新建 `core/test_suite.py` 覆盖 10 项严苛边界用例并全部通过。

---

## 九、 跨版本安全防护与 Fail-Closed 策略专项升级

1. **旧版本 Clean Backup 明确定位**：
   - 确立为“恢复用途优先，严禁默认跨版本作为 patch base”。
   - 彻底移除了“候选校验失败后自动回退使用既有旧备份打补丁”的危险逻辑。
2. **宿主版本强绑定机制**：
   - 在状态体系中持久化记录 `clean_backup_version`。
   - 执行 patch 构建时必须校验 `current_ver == clean_backup_version`，一旦检测到错配直接熔断停机。
3. **未汉化新版候选校验 Fail-Closed 拦截**：
   - 当检测到未汉化的 `app.asar` 无法通过 `validate_official_candidate()` 时：
     - 立即终止本次 `perform_patch()`，返回明确失败；
     - 拒绝使用已有旧 clean backup 构建补丁；
     - 拒绝调用最终 `os.replace()`，正式 `app.asar` 保持未修改；
     - 原 clean backup 保持未修改，仅留作恢复用途；
     - 输出标准清晰的友好排查与升级提示。
4. **自动化测试套件扩充至 13 项且全部通过**：
   - **测试 A (`test_a_unknown_new_version_with_old_backup_fail_closed`)**：模拟 current 2.25 + backup 2.24 + 候选验证失败，断言立即中止、正式文件未修改、旧 backup 保留、安全提示完备；
   - **测试 B (`test_b_same_version_backup_allows_patch`)**：模拟 current 2.24 + backup 2.24，断言同版本正常基于 backup 构建且补丁生效；
   - **测试 C (`test_c_new_version_candidate_validated_updates_backup_and_patches`)**：模拟 current 2.25 + backup 2.24 + 候选验证通过，断言 clean backup 正常升级为 2.25、版本绑定同步更新至 2.25 并成功打补丁。
