/**
 * Antigravity 简体中文界面汉化引擎 (Inlined Preload Engine) v3.0
 * 全面支持主界面、侧边栏、对话面板、设置中心所有选项卡、弹窗菜单及动态状态
 */
(function initAntigravityChineseUI() {
  if (window.__antigravity_chinese_active) return;
  window.__antigravity_chinese_active = true;

  const EXACT_MAP = {
  "New Conversation": "新建对话",
  "+ New Conversation": "+ 新建对话",
  "Conversation History": "对话历史",
  "Automations": "自动化",
  "Customizations": "自定义扩展",
  "Projects": "项目列表",
  "CLI Project": "CLI 项目",
  "CLI 项目": "CLI 项目",
  "No conversations yet": "暂无对话记录",
  "Conversations": "历史对话",
  "Settings": "设置",
  "Workspaces": "工作区",
  "Recent Workspaces": "最近工作区",
  "Open Workspace": "打开工作区",
  "Open Folder": "打开文件夹",
  "Open folder": "打开文件夹",
  "Archive Workspace": "归档工作区",
  "Delete Workspace": "删除工作区",
  "Active Agents": "活跃智能体",
  "Model Selection": "模型选择",
  "Subagents": "子智能体",
  "Background Tasks": "后台任务",
  "Background Task Output": "后台任务输出",
  "Cancel Task": "取消任务",
  "Cancel All Tasks": "取消所有任务",
  "Artifacts": "生成产物",
  "Files Changed": "文件变更",
  "Branch Changes": "分支变更",
  "Terminals": "终端列表",
  "Terminal": "终端",
  "Close Terminal Tab": "关闭终端标签",
  "Logs": "运行日志",
  "Plugins": "插件中心",
  "Installed": "已安装",
  "Marketplace": "插件市场",
  "Rules": "全局规则",
  "Skills": "技能库",
  "MCP Servers": "MCP 协议服务",
  "Agents": "智能体",
  "Agent Team": "智能体团队",
  "Custom Agents": "自定义智能体",
  "Agent Behavior": "智能体行为",
  "Agent Edits": "智能体编辑",
  "Delete Conversation": "删除对话",
  "Clear History": "清空历史记录",
  "Shortcuts": "快捷键",
  "Provide Feedback": "提供反馈",
  "Sign Out": "退出登录",
  "Add Context": "添加上下文",
  "Add context": "添加上下文",
  "Media": "媒体文件",
  "Mentions": "提及与引用",
  "Actions": "快捷操作",
  "Browser": "内置浏览器",
  "Create Project": "创建项目",
  "Command Palette": "命令面板",
  "New Project": "新建项目",
  "Quick Start": "快速开始",
  "File Access Rules": "文件访问规则",
  "Configure allowed and denied paths for file reads and writes.": "配置文件读写的允许与拒绝路径。",
  "Also includes": "在此项目中工作时还包含",
  "when working in this project.": "。",
  "See Activity": "查看明细",
  "Send message": "发送消息",
  "Stop generating": "停止生成",
  "Thinking...": "思考中...",
  "Planning...": "规划中...",
  "Generating...": "生成中...",
  "Accept": "接受变更",
  "Reject": "拒绝变更",
  "Keep editing": "继续编辑",
  "Submit": "提交",
  "Cancel": "取消",
  "Confirm": "确认",
  "Retry": "重试",
  "Undo": "撤销",
  "Redo": "重做",
  "Copy": "复制",
  "Copied": "已复制",
  "Copy File Path": "复制文件路径",
  "Copy File Name": "复制文件名",
  "Copy Command": "复制命令",
  "Copy Config File Path": "复制配置文件路径",
  "Run Command": "执行命令",
  "Always Allow": "始终允许",
  "Allow": "允许",
  "Deny": "拒绝",
  "Review": "审查变更",
  "Review Changes": "审查变更",
  "Save": "保存",
  "Save All": "全部保存",
  "Delete": "删除",
  "Rename": "重命名",
  "Clear": "清空",
  "Close": "关闭",
  "Close Tab": "关闭标签页",
  "Close other tabs": "关闭其他标签页",
  "Close tabs to the right": "关闭右侧所有标签页",
  "Collapse All Folders": "折叠所有文件夹",
  "Expand All Folders": "展开所有文件夹",
  "All Files": "所有文件",
  "Filter": "筛选",
  "Search": "搜索",
  "Browse": "浏览",
  "Refresh": "刷新",
  "Discard": "放弃更改",
  "Discard changes": "放弃所有更改",
  "Apply": "应用",
  "Commit": "提交 (Commit)",
  "Commit succeeded": "提交成功",
  "Branch": "分支",
  "Configure Branches": "配置分支",
  "Connected": "已连接",
  "Disconnected": "已断开",
  "Running": "运行中",
  "Idle": "空闲",
  "Completed": "已完成",
  "Failed": "失败",
  "Error": "错误",
  "Warning": "警告",
  "Success": "成功",
  "Help": "帮助",
  "Documentation": "官方文档",
  "Feedback": "用户反馈",
  "Report Bug": "报告问题",
  "About Antigravity": "关于 Antigravity",
  "Version": "版本",
  "Proxy Settings": "代理设置",
  "Keyboard Shortcuts": "快捷键",
  "Advanced Settings": "高级设置",
  "Chat Settings": "对话设置",
  "Close Settings": "关闭设置",
  "Auto-Update": "自动更新",
  "Check for Updates": "检查更新",
  "General": "常规设置",
  "Application": "应用设置",
  "Appearance": "外观设置",
  "Models": "模型与用量",
  "Models & Usage": "模型与用量",
  "Not in Project": "非项目环境",
  "Outside of Project": "非项目环境",
  "Outside of project": "非项目环境",
  "Account": "账号设置",
  "Manage Antigravity app settings.": "管理 Antigravity 应用程序设置。",
  "Prevent Sleep": "阻止休眠",
  "Prevent the computer from sleeping while the app is running.": "应用运行时阻止计算机进入休眠状态。",
  "Keep In Menu Bar": "常驻菜单栏/托盘",
  "Keep the app accessible from the menu bar and running in the background when all windows are closed.": "当所有窗口关闭后保持应用在后台运行，并可从托盘快速唤出。",
  "Remote Control": "远程控制",
  "Enable Remote Control": "启用远程控制",
  "Work with local agents from another device.": "支持从其他设备访问并控制本地智能体。",
  "Notifications": "通知设置",
  "Notification Settings": "通知首选项",
  "To modify notification settings, open your operating system's system preferences.": "如需修改系统通知权限，请打开操作系统的系统设置。",
  "Open System Preferences": "打开系统首选项",
  "App version": "应用程序版本",
  "Configure the agent's visual theme and display preferences.": "配置智能体的视觉主题与界面显示偏好。",
  "Theme": "主题模式",
  "Dark": "深色模式",
  "Light": "浅色模式",
  "System": "跟随系统",
  "Contrast": "对比度",
  "Default": "默认",
  "Strong": "增强",
  "Light Theme": "浅色主题",
  "Dark Theme": "深色主题",
  "Preset": "色彩预设",
  "Default Light": "默认浅色",
  "Default Dark": "默认深色",
  "Background": "背景颜色",
  "Foreground": "文本颜色",
  "Accent": "强调高亮色",
  "Verbose Agent Chat": "展示详细智能体对话过程",
  "Display and preserve intermediate thinking steps.": "实时展示并持久化保留中间推理步骤与思考过程。",
  "Conversation Width": "对话面板宽度",
  "Configure the maximum width of the conversation panel.": "配置文件与聊天区域的最大宽度限制。",
  "Narrow": "紧凑",
  "Wide": "宽屏",
  "Execution": "执行偏好",
  "Queued Messages": "排队消息处理",
  "Configure when follow-up messages are sent.": "配置后续追加消息何时发送给智能体。",
  "Queue": "排队等待",
  "Send Immediately": "立即发送",
  "Global Permissions": "全局权限",
  "Security Preset": "安全预设",
  "Controls the actions the agent can take.": "控制智能体在当前环境下可以执行的操作级别。",
  "Turbo Mode": "Turbo 极速模式",
  "Turbo mode": "Turbo 极速模式",
  "Tool Permissions": "工具权限",
  "Modify permissions for file, terminal, and MCP tools.": "配置文件读写、终端命令及 MCP 工具的精细权限。",
  "Plan Review Policy": "计划审查策略",
  "Whether the agent asks you to review its documents.": "智能体在执行前是否要求您审查其方案文档。",
  "Always Proceed": "直接继续",
  "Request Review": "请求审查",
  "Always Review": "始终审查",
  "Never Review": "从不审查",
  "Review When Modified": "有修改时审查",
  "Inherit Global": "继承全局设置",
  "Network Permissions": "网络权限",
  "Network Access Rules": "网络访问规则",
  "Configure allowed and denied URLs for reading.": "配置允许或拒绝智能体读取的网络 URL 地址。",
  "Terminal & Tooling Permissions": "终端与工具权限",
  "Terminal Commands": "终端命令",
  "Configure allowed terminal commands.": "配置允许智能体在终端中执行的白名单命令。",
  "Commands Outside Sandbox": "沙箱外命令",
  "Configure allowed commands outside the sandbox.": "配置允许智能体在安全沙箱外部执行的系统命令。",
  "MCP Tools": "MCP 协议工具",
  "Configure external tools via Model Context Protocol.": "通过模型上下文协议 (MCP) 配置与调用外部工具。",
  "Browser Javascript Execution Policy": "浏览器脚本执行策略",
  "Controls whether the agent can run custom JavaScript to automate complex browser actions.": "控制智能体是否可以在浏览器中运行自定义 JavaScript 执行自动化任务。",
  "Browser Actuation Rules": "浏览器操作规则",
  "Configure allowed and denied URLs for browser actuation.": "配置允许或拒绝智能体进行自动化操作的网页 URL。",
  "Edit": "编辑规则",
  "Open": "打开配置",
  "Manage your model quota and credits.": "管理您的模型使用配额与 AI 积分点数。",
  "Plan": "当前套餐",
  "Upgrade": "升级套餐",
  "Model Credits": "模型积分 (AI Credits)",
  "Enable AI Credit Overages": "启用 AI 积分超额自动抵扣",
  "Gemini Models": "Gemini 系列模型",
  "Weekly Limit Remaining": "每周剩余额度",
  "Five Hour Limit Remaining": "5 小时剩余额度",
  "Claude and GPT models": "Claude 与 GPT 系列模型",
  "You can upgrade to a Google AI Ultra plan to receive higher rate limits.": "您可以升级到 Google AI Ultra 套餐以获取更高的速率限制与并发配额。",
  "When toggled on, Antigravity will use your AI credits to fulfill model requests once you're out of model quota. Antigravity will always use your model quota first before using AI credits.": "开启后，当模型免费/套餐配额用尽时，Antigravity 将自动使用您的 AI 积分继续完成请求。系统始终会优先消耗套餐配额。",
  "Your Plan:": "当前套餐：",
  "Your Plan: ": "当前套餐：",
  "Manage project folders, agent settings, and permissions.": "管理项目文件夹路径、智能体行为及权限策略。",
  "Folders": "项目文件夹",
  "No folders added yet.": "尚未添加任何项目文件夹。",
  "Add Folder": "添加文件夹",
  "+ Add Folder": "+ 添加文件夹",
  "Agent Settings": "智能体设置",
  "Local Permissions": "本地独立权限",
  "Other Customizations": "其他自定义配置",
  "Mcp Tools": "MCP 工具",
  "Danger Zone": "危险区域",
  "Delete Project": "删除此项目",
  "Permanently delete CLI 项目.": "永久删除此 CLI 项目。",
  "删除 Project": "删除项目",
  "Learn more": "了解更多",
  "Learn more.": "了解更多。",
  "Learn more about": "了解更多关于",
  "Also includes Global Permissions when working in this project. Learn more.": "在此项目中工作时还包含全局权限。了解更多。",
  "Also includes Global Permissions when working in this project.": "在此项目中工作时还包含全局权限。",
  "Agent settings and permissions for conversations outside of projects.": "针对项目外部独立会话的智能体行为与权限策略。",
  "Manage your plan, credentials, and general preferences.": "管理您的套餐、凭据以及常规偏好。",
  "Enable Telemetry": "启用使用情况统计与遥测",
  "When toggled on, Antigravity collects usage data to help Google enhance performance and features.": "开启后，Antigravity 将收集匿名使用数据以帮助 Google 提升产品性能与功能体验。",
  "Marketing Emails": "营销与活动邮件",
  "Receive product updates, tips, and promotions from Google Antigravity via email.": "通过电子邮件接收来自 Google Antigravity 的产品更新、使用技巧和最新动态。",
  "Email": "电子邮箱",
  "By using this app, you agree to its": "使用此应用即表示您同意其",
  "Terms of Service": "服务条款",
  "Keyboard shortcuts": "键盘快捷键",
  "Keyboard shortcuts for quick navigation and control.": "用于快速导航和操作的快捷键。",
  "Type": "输入",
  "and select": "并选择",
  "to have the agent generate a plan.": "以让智能体生成实施计划。",
  "Configure the browser subagent. It requires": "配置浏览器子智能体。此功能需要安装",
  "to be installed.": "。",
  "The browser subagent can be invoked by typing /browser in the conversation input box.": "在对话输入框中输入 /browser 即可调用浏览器子智能体。",
  "Configure agent execution, queued message delivery, and permissions.": "配置智能体执行、排队消息发送及权限设置。",
  "Feedback Type": "反馈类型",
  "Bug Report": "缺陷报告",
  "Feature Request": "功能需求",
  "General Feedback": "常规反馈",
  "Remote Control Issue": "远程控制问题",
  "Description": "详细描述",
  "Steps to Reproduce": "重现步骤",
  "Steps to reproduce the issue": "重现问题的操作步骤",
  "Expected behavior": "期望表现",
  "Actual behavior": "实际表现",
  "Attach Antigravity server logs": "附加 Antigravity 服务端日志",
  "Attach a screenshot (optional)": "附带截屏（可选）",
  "Please describe the issue in detail. The more actionable your feedback, the quicker our team can address your request. Some helpful information includes:": "请详细描述您遇到的问题。提供的信息越具体，我们越能快速解决。建议包含：",
  "Any error messages": "任何相关的报错信息",
  "Any relevant information": "任何其他相关信息",
  "Navigation": "页面导航",
  "Conversation": "会话操作",
  "Developer": "开发者工具",
  "Open Conversation Picker": "打开会话选择器",
  "Open File Search": "打开文件搜索",
  "Open Settings": "打开设置",
  "Select Next Conversation": "切换到下一个会话",
  "Select Previous Conversation": "切换到上一个会话",
  "Toggle Sidebar": "展开/折叠侧边栏",
  "Toggle Auxiliary Pane": "展开/折叠辅助面板",
  "Toggle Terminal": "打开/关闭内置终端",
  "Toggle Voice Recording": "开启/停止语音输入",
  "Next Pane Tab": "切换到下一个标签页",
  "Previous Pane Tab": "切换到上一个标签页",
  "Find in Pane": "在当前面板中查找",
  "Focus Input": "聚焦到对话输入框",
  "Show Selection Actions": "显示选中操作浮层",
  "Show \"Edit\" and \"Chat\" buttons when selecting text in the editor.": "在编辑器中选中文本时显示“编辑”和“对话”浮层按钮。",
  "Choose the experience that fits how you work.": "选择最适合您工作流的界面风格。",
  "Choose between the Default and Project 4K experience.": "在默认界面模式与 Project 4K 沉浸视图之间切换。",
  "Customize": "自定义配置",
  "Open Editor Settings": "打开编辑器设置",
  "Setup Jetski Chat": "配置对话面板",
  "No changes to review": "暂无需要审查的代码变更",
  "No active terminals": "暂无活跃终端",
  "No active terminals. Click + to create one.": "暂无运行中的终端，点击 + 创建新终端。",
  "No files or folders found": "未找到匹配的文件或文件夹",
  "No folder selected": "未选择文件夹",
  "No models available": "暂无可用模型",
  "No quota information available.": "暂无可用配额信息。",
  "No Model Selected": "未选择模型",
  "Purchase Credits": "购买 AI 积分",
  "Get More AI Credits": "获取更多 AI 积分",
  "Insufficient AI Credits": "AI 积分余额不足",
  "Model quota reached": "已达到模型使用限额",
  "Token Usage": "Token 用量",
  "Context usage": "上下文占用",
  "Loading models...": "正在加载可用模型...",
  "Loading token usage...": "正在获取 Token 统计...",
  "Resolving permissions...": "正在解析权限设置...",
  "Connecting to terminal...": "正在连接到终端...",
  "Creating terminal...": "正在创建新终端...",
  "Failed to create terminal": "创建终端失败",
  "Failed to load media": "加载媒体文件失败",
  "Exploring files, running commands, editing file": "浏览文件、执行命令与编辑代码",
  "The breakdown below shows token usage from customizations like rules, skills, and MCP. If a budget is exceeded, large rules are demoted to path pointers and large customizations are excluded automatically.": "下方的明细展示了来自规则、技能和 MCP 等自定义扩展的 Token 用量。如果超出配额预算，大型规则将被降级为路径指针，大型自定义扩展将被自动排除。"
};

  const PLACEHOLDER_MAP = {
  "Ask anything, @ to mention, / for workflows": "输入任何问题，@ 提及文件/符号，/ 调用工作流...",
  "Ask anything, @ to mention, / for actions": "输入任何问题，@ 提及文件/符号，/ 调用操作...",
  "Ask a question...": "向 Antigravity 提问...",
  "Search...": "搜索...",
  "Filter...": "筛选...",
  "Type a message...": "输入消息...",
  "Search files...": "搜索文件...",
  "Search plugins...": "搜索插件...",
  "Type absolute path or navigate folders...": "输入绝对路径或浏览文件夹...",
  "Steps to reproduce the issue": "重现问题的操作步骤...",
  "Expected behavior": "期望的正确表现...",
  "Actual behavior": "实际出现的异常表现..."
};

  function translateDuration(str) {
    if (!str) return str;
    return str
      .replace(/(\d+)\s+days?/gi, '$1 天')
      .replace(/(\d+)\s+hours?/gi, '$1 小时')
      .replace(/(\d+)\s+minutes?/gi, '$1 分钟')
      .replace(/(\d+)\s+seconds?/gi, '$1 秒')
      .replace(/,\s*/g, ' ')
      .trim();
  }

  const PATTERN_RULES = [
    // Your Plan: Google AI Pro
    {
      regex: /^Your Plan:\s*(.+)$/i,
      replace: (match, p1) => '当前套餐：' + p1
    },
    // You have used some of your weekly / 5-hour limit, it will fully refresh in ...
    {
      regex: /^You have used some of your\s+([\w\-]+)\s+limit,\s*it will fully refresh in\s+(.+?)\.?$/i,
      replace: (match, limitType, duration) => {
        const lt = limitType.toLowerCase().includes('5-hour') ? '5 小时' : '每周';
        return '您已使用部分 ' + lt + ' 额度，将在 ' + translateDuration(duration) + ' 后完全刷新。';
      }
    },
    {
      regex: /^it will fully refresh in\s+(.+?)\.?$/i,
      replace: (match, duration) => '将在 ' + translateDuration(duration) + ' 后完全刷新。'
    },
    // Available AI Credits: 0
    {
      regex: /^Available AI Credits:\s*(\d+.*)$/i,
      replace: (match, count) => '可用 AI 积分：' + count
    },
    // Show 2 breakdowns / Show 1 breakdown
    {
      regex: /^Show\s+(\d+)\s+breakdowns?$/i,
      replace: (match, count) => '查看 ' + count + ' 项明细'
    },
    // Permanently delete XXX.
    {
      regex: /^Permanently delete\s+(.+?)\.?$/i,
      replace: (match, target) => '永久删除 ' + target + '。'
    },
    // Learn more about XXX
    {
      regex: /^Learn more about\s+(.+)$/i,
      replace: (match, topic) => '了解关于 ' + topic + ' 的更多信息'
    },
    // Thought for 14s / Thinking for 12s
    {
      regex: /^(?:Thought|Thinking)\s+for\s+(\d+.*)$/i,
      replace: (match, dur) => '思考耗时 ' + dur
    },
    // Analyzed / Edited / Created / Running
    {
      regex: /^Analyzed\s+(.+)$/i,
      replace: (match, target) => '分析 ' + target
    },
    {
      regex: /^Edited\s+(.+)$/i,
      replace: (match, target) => '编辑 ' + target
    },
    {
      regex: /^Created\s+(.+)$/i,
      replace: (match, target) => '创建 ' + target
    },
    // X files changed / modified
    {
      regex: /^(\d+)\s+files?\s+changed$/i,
      replace: (match, count) => count + ' 个文件变更'
    },
    {
      regex: /^(\d+)\s+files?\s+modified$/i,
      replace: (match, count) => count + ' 个文件修改'
    }
  ];

  const IGNORED_TAGS = new Set(['PRE', 'CODE', 'SCRIPT', 'STYLE', 'SVG', 'TEXTAREA']);
  const IGNORED_SELECTORS = '.monaco-editor, .prism-code, .xterm, pre, code, [contenteditable="true"]';

  let isTranslating = false;

  function shouldSkip(node) {
    if (!node) return true;
    const el = node.nodeType === 1 ? node : node.parentElement;
    if (!el) return false;
    if (IGNORED_TAGS.has(el.tagName)) return true;
    if (el.closest && el.closest(IGNORED_SELECTORS)) return true;
    return false;
  }

  function translateTextNode(node) {
    if (shouldSkip(node)) return;
    const text = node.nodeValue;
    if (!text) return;

    const trimmed = text.trim();
    if (!trimmed) return;

    // 如果包含中文，除非是特殊动态前缀，否则跳过
    if (/[\u4e00-\u9fa5]/.test(trimmed)) {
      if (!/^(?:Thought|Thinking|Analyzed|Edited|Created)\b/i.test(trimmed)) {
        return;
      }
    }

    // 1. 精确词条替换
    if (EXACT_MAP[trimmed]) {
      node.nodeValue = text.replace(trimmed, EXACT_MAP[trimmed]);
      return;
    }

    // 2. 正则模式替换
    for (let i = 0; i < PATTERN_RULES.length; i++) {
      const rule = PATTERN_RULES[i];
      if (rule.regex.test(trimmed)) {
        const replaced = trimmed.replace(rule.regex, rule.replace);
        node.nodeValue = text.replace(trimmed, replaced);
        return;
      }
    }
  }

  function translateAttributes(el) {
    if (shouldSkip(el)) return;
    if (el.hasAttribute('placeholder')) {
      const ph = el.getAttribute('placeholder');
      if (PLACEHOLDER_MAP[ph]) el.setAttribute('placeholder', PLACEHOLDER_MAP[ph]);
    }
    if (el.hasAttribute('title')) {
      const t = el.getAttribute('title');
      if (EXACT_MAP[t]) el.setAttribute('title', EXACT_MAP[t]);
    }
    if (el.hasAttribute('aria-label')) {
      const a = el.getAttribute('aria-label');
      if (EXACT_MAP[a]) el.setAttribute('aria-label', EXACT_MAP[a]);
    }
  }

  function translateTree(root) {
    if (!root || shouldSkip(root)) return;
    if (root.nodeType === 1) translateAttributes(root);

    const walker = document.createTreeWalker(
      root,
      NodeFilter.SHOW_TEXT | NodeFilter.SHOW_ELEMENT,
      {
        acceptNode: (n) => (shouldSkip(n) ? NodeFilter.FILTER_REJECT : NodeFilter.FILTER_ACCEPT)
      }
    );

    let curr = walker.nextNode();
    while (curr) {
      if (curr.nodeType === 3) {
        translateTextNode(curr);
      } else if (curr.nodeType === 1) {
        translateAttributes(curr);
      }
      curr = walker.nextNode();
    }
  }

  function start() {
    if (!document.body) return;
    translateTree(document.body);

    const observer = new MutationObserver((mutations) => {
      if (isTranslating) return;
      isTranslating = true;
      try {
        for (let i = 0; i < mutations.length; i++) {
          const m = mutations[i];
          if (m.type === 'childList') {
            for (let j = 0; j < m.addedNodes.length; j++) {
              translateTree(m.addedNodes[j]);
            }
          } else if (m.type === 'characterData') {
            translateTextNode(m.target);
          } else if (m.type === 'attributes') {
            translateAttributes(m.target);
          }
        }
      } finally {
        isTranslating = false;
      }
    });

    observer.observe(document.body, {
      childList: true,
      subtree: true,
      characterData: true,
      attributes: true,
      attributeFilter: ['placeholder', 'title', 'aria-label']
    });

    // 交互即时响应：点击与按键后快速全量/局部补扫一次
    window.addEventListener('click', () => {
      setTimeout(() => translateTree(document.body), 60);
      setTimeout(() => translateTree(document.body), 300);
    }, true);

    // 周期性空闲兜底扫描（每 1 秒一次），确保异步网络数据与动态弹层彻底汉化
    setInterval(() => {
      translateTree(document.body);
    }, 1000);

    console.log('[Antigravity-Chinese] 简体中文界面汉化引擎 v3.0 已全面激活！');
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', start);
  } else {
    start();
  }
})();
