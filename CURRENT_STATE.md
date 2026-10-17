# Antigravity 汉化系统当前运行状态与审计基线 (CURRENT_STATE)

> **审计目的**：供开发者与 AI 审计工具直接读取，以核查当前工程真实实现状态、识别薄弱环节并指导后续针对性升级。  
> **记录基准时间**：2026-10-17  
> **基线 Commit 目标**：`chore: upload current stable antigravity chinese baseline`

---

## 一、 环境与版本信息

- **宿主程序版本**：Google Antigravity `2.24.0` (`ProductVersion: 2.24.0.0`, `FileVersion: 2.24.0`)
- **宿主架构**：Windows x64 Desktop (Electron)
- **汉化插件版本**：`v3.0.0-self-healing`
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
3. **自愈与版本检测机制**：
   - `core/cli.py status`：毫秒级输出版本、Hash、自愈次数、备份状态；
   - `core/cli.py verify`：静态解析 ASAR 并执行 `node --check` 语法与特征审计；
   - `core/cli.py repair` / `install`：纯 Python 流式构建与注入；
   - `core/cli.py restore`：一键无条件恢复官方纯净原版；
   - `core/launcher.py` / `agy-launch.bat`：智能自愈启动器；
   - `core/test_self_healing.py`：模拟官方覆盖全闭环测试 100% 通过。
4. **代码与终端环境防护**：
   - 严格排除 `.monaco-editor`、`.prism-code`、`.xterm`、`<pre>`、`<code>`，用户编码与命令行输入输出绝对不受汉化篡改。

---

## 三、 已知失效 / 不稳定功能

1. **运行期“热生效”需要重启窗口**：
   - 由于 Electron 主进程在启动时即将 `dist/utils.js` 和 `dist/menu.js` 加载入 Node 模块缓存，若在客户端运行途中由更新程序替换了 `app.asar`，必须关闭并重新打开 Antigravity，补丁代码方能被主进程初始化。
2. **子页面 / 外部 Webview 隔离**：
   - 某些独立 iframe 或插件面板（例如特定三方扩展自带的独立 UI 视图）若未继承主窗口注入逻辑，可能需要专属的 Preload 挂载点。

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
   - 注入前备份官方版本至外部隔离区；
   - 修改后强制通过 `node --check` 语法分析；
   - ASAR 头部有效性与入口关键文件校验；
   - 任意环节异常自动触发 `restore_official_clean()`，保证官方程序随时可用。

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
2. **Preload 独立直连机制尚未完全启用为第一优先级**：
   - 当前主要注入点为 `dist/utils.js` 的 `webContents.executeJavaScript`。Preload 注入作为备选机制。如果未来将 Preload 提升为主要注入点，将无需在主进程拦截 window 实例。
3. **跨平台适配**：
   - 当前主要针对 Windows 系统环境（路径探测、批处理启动器 `agy-launch.bat`）。后续可增加 macOS (`.sh` / `.command`) 与 Linux 启动器的开箱即用支持。

---

## 八、 最近一次修改内容

- **重构汉化系统为自愈式架构**：
  - 新增 `core/` 独立体系，解耦官方安装目录；
  - 新增版本与 SHA-256 检测与 `state.json` 状态库；
  - 新增 `AsarArchive` 纯 Python 二进制打包与完整性校验模块；
  - 新增 `common`, `fallback`, `v2.24` 多适配器分层设计；
  - 新增 `launcher.py`、`agy-launch.bat` 与后台守护服务 `watcher/service.py`；
  - 新增统一运维 CLI `cli.py` (`status`, `verify`, `repair`, `install`, `restore`, `watch`, `launch`)；
  - 完成全生命周期自愈与安全回滚端到端测试。
