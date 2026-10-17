# Antigravity 简体中文汉化与自愈增强套件 (Antigravity Chinese Pack)

本仓库是为 Google Antigravity 2.0 桌面端及智能体深度定制的**官方更新自适应、可自愈简体中文本地化完整解决方案**。

---

## 📖 一、 当前插件用途

1. **桌面客户端全界面汉化**：将 Antigravity 桌面应用的主窗口、侧边栏、所有设置选项卡（常规、对话、CLI 项目、模型与用量）、加号上下文菜单、顶部项目面包屑及原生应用主菜单深度汉化为现代简体中文。
2. **官方更新自愈系统 (Self-Healing)**：自动感知 Antigravity 官方静默升级，自动比对文件 SHA-256，利用智能启动器或后台守护模式实现 1 秒内无感自动重打汉化补丁。
3. **原生智能体中文规范与研发技能**：提供系统级中文默认应答规则、报错三段式中文排查规范，以及符合 Conventional Commits 规范的自动化中文 Git 提交工作流。

---

## 🏷️ 二、 当前版本状态

- **插件版本**：`v3.1.0-hardened-baseline`
- **适配宿主版本**：Google Antigravity 2.24.0 (Windows x64 Desktop)
- **基线状态**：可靠性加固稳定基线版本（已通过候选版本安全性验证、超时熔断、原子替换、语法分析与 10 项核心边界自动化测试）。

---

## ⚙️ 三、 汉化实现原理

本系统采用**双层解耦挂载与 DOM 动态捕获机制**：

```text
Antigravity 启动 (app.asar)
  ├── 主进程层 (/dist/utils.js 或 /dist/preload.js)
  │     └── 注入生命周期监听：win.webContents.on('dom-ready' / 'did-finish-load')
  │           └── 调度执行：__chineseTranslatorScript (前端 DOM 翻译引擎)
  ├── 应用菜单层 (/dist/menu.js)
  │     └── 拦截 Menu.setApplicationMenu(menu) ➔ 递归映射中文并追加快捷键助记符
  └── 渲染进程层 (BrowserWindow DOM)
        ├── TreeWalker：初始全树高效扫描替换叶子文本节点与特定属性
        ├── MutationObserver：监听动态新增 DOM 节点与属性变更
        ├── 交互补扫：全局 click 事件微延迟触发防抖复扫
        ├── 周期兜底：1000ms 空闲轮询补扫（捕获云端异步延时数据）
        └── 正则模式引擎：动态提取倒计时（X 天 Y 小时）、套餐类型、Token 配额
```

---

## 🚀 四、 如何安装与加载

### 1. 智能启动器启动 (推荐日常使用)
直接双击运行：
```cmd
core\agy-launch.bat
```
或通过命令行拉起：
```bash
python core/launcher.py
```
> **启动器行为**：启动前毫秒级检测当前客户端版本与 Hash。若发现官方刚更新或汉化失效，自动在 1 秒内无感自愈完成，随后顺畅启动 Antigravity。

### 2. 命令行管理工具 (`core/cli.py`)
```bash
# 查看版本与当前汉化状态
python core/cli.py status

# 深度审计注入层完整性与语法健康度
python core/cli.py verify

# 重新注入 / 手动强制自愈
python core/cli.py repair

# 安全恢复为官方英文原版
python core/cli.py restore

# 启动后台守护监听进程 (检测更新并在客户端退出后自动重打补丁)
python core/cli.py watch
```

### 3. 作为原生扩展插件安装
将本仓库所在目录放置于 Antigravity 插件配置目录：
```text
~/.gemini/config/plugins/antigravity-chinese-pack/
```
Antigravity 启动时将自动识别并加载 `plugin.json`、`rules/AGENTS.md` 与相关开发技能。

---

## 📂 五、 主要目录结构

```text
antigravity-chinese/
├── plugin.json                 # Antigravity 插件清单文件
├── README.md                   # 仓库使用说明与架构文档
├── CURRENT_STATE.md            # 当前运行状态与审计基线记录
├── .gitignore                  # Git 忽略规则
├── assets/
│   └── logo.png                # 插件图标
├── rules/
│   └── AGENTS.md               # 简体中文全局交互与报错诊断规则
├── skills/
│   ├── chinese-dev-expert/     # 中文开发专家技能
│   │   └── SKILL.md
│   └── chinese-git-workflow/   # 规范化中文 Git 工作流技能
│       └── SKILL.md
├── core/                       # [核心] 自愈汉化系统
│   ├── agy-launch.bat          # 智能启动器批处理入口
│   ├── launcher.py             # 智能启动器 Python 核心
│   ├── cli.py                  # 统一管理 CLI 工具
│   ├── config.py               # 路径探测、版本获取与路径配置
│   ├── state.py                # 版本与 Hash 状态数据库操作
│   ├── state.example.json      # 运行期状态模版 (已与 Git 仓库基线解耦)
│   ├── logger.py               # 规范日志记录器
│   ├── test_suite.py           # 可靠性加固全量自动化测试套件 (覆盖 10 项严苛边界条件)
│   ├── test_self_healing.py    # 核心文件自愈注入闭环测试
│   ├── backups/                # 独立官方原版备份隔离区 (防止被覆盖)
│   │   └── .gitkeep
│   ├── logs/                   # 持久化审计日志 (patch.log, watch.log)
│   │   └── .gitkeep
│   ├── translations/           # 汉化词库层
│   │   ├── dictionary.json     # 320+ 精确词条与输入框占位符映射
│   │   └── menu.json           # 原生应用菜单映射字典
│   ├── engine/                 # 通用引擎层
│   │   ├── asar.py             # 纯 Python 高性能 ASAR 解包/打包库
│   │   ├── runtime_builder.py  # 前端 DOM 汉化脚本编译生成器
│   │   ├── validator.py        # node --check 语法与 ASAR 结构校验器
│   │   └── injector.py         # 注入调度与安全回滚控制器
│   ├── adapters/               # 版本兼容适配器层
│   │   ├── common.py           # 通用多锚点特征适配器
│   │   ├── fallback.py         # 兜底容灾自适应适配器
│   │   └── versions/
│   │       └── v2_24.py        # Antigravity 2.24.x 专有适配器
│   └── watcher/
│       └── service.py          # 后台常驻守护服务
└── ui-localization/            # 独立免依赖脚本与旧版桥接
    ├── i18n-dictionary.json
    ├── ui-translator.js
    ├── patch_asar.py
    ├── install-ui-patch.ps1
    └── uninstall-ui-patch.ps1
```

---

## ⚠️ 六、 当前已知问题

1. **运行期热替换感知滞后**：Electron 主进程模块（`utils.js`、`menu.js`）在进程启动时已缓存进 V8 内存。若在 Antigravity 运行途中后台完成自愈重打，必须关闭并重新打开客户端（或在当前窗口执行热重载）方能完全呈现汉化。
2. **React 极度碎片化节点**：部分极其复杂的长句在 React 内部被拆分成多个独立的字词元素（如 `<span>` 嵌套 `<code>`），若词典未涵盖该碎片的组合，可能出现局部中英混显，需在词典中补录对应短语。

---

## 🔍 七、 Antigravity 更新后可能失效的关键原因

1. **官方更新机制覆盖 `app.asar`**：
   Antigravity 使用标准的 Electron 自动更新系统（`app-update.yml`）。官方版本发布时，更新器会静默下载新包并在客户端重启时**原子覆盖整个 `resources/app.asar`**，导致此前注入的主进程代码完全丢失。
2. **主窗口创建生命周期重构**：
   若官方未来改写窗口创建函数，或不再使用 `win.on('page-title-updated')` 或 `win.webContents.on('did-finish-load')` 等事件钩子，可能导致注入点特征失效。
3. **原生菜单设置位置变动**：
   若官方移除了 `Menu.setApplicationMenu(menu)` 或改由异步延迟设置，菜单汉化可能需要适配新的调用点。

---

## 🧩 八、 当前插件依赖的 Antigravity 结构与特征

| 依赖类别 | 具体依赖目标 | 用途说明 | 替代/容灾方案 |
| :--- | :--- | :--- | :--- |
| **安装目录** | `%LOCALAPPDATA%\Programs\antigravity\` | 官方二进制所在根路径 | 备选扫描注册表、快捷方式与运行中进程 |
| **核心资源包** | `resources/app.asar` | Electron 主程序包宿主 | 独立备份至 `core/backups/` 隔离区 |
| **主进程代码** | `app.asar` 内 `/dist/utils.js` | 窗口创建生命周期注入点 | 自动回退至 `/dist/preload.js` 或 `common/fallback` |
| **主菜单代码** | `app.asar` 内 `/dist/menu.js` | 原生顶层菜单拦截点 | 正则特征匹配 `setApplicationMenu` |
| **安全隔离区** | Monaco Editor (`.monaco-editor`)、XTerm (`.xterm`)、`<pre>`, `<code>` | 代码与终端渲染区域 | 严格过滤选择器，避免污染用户代码与命令 |
