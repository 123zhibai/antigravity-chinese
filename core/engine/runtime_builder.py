import json
import os

def build_runtime_script(dictionary_path, extra_rules=None):
    """
    根据翻译词典动态生成注入渲染进程的纯 JavaScript 汉化脚本。
    包含：
    1. 静态词典映射 (EXACT_MAP)
    2. 占位符映射 (PLACEHOLDER_MAP)
    3. 动态正则模式替换规则 (PATTERN_RULES)
    4. 动态时间、限额与单位转换函数 (translateDuration)
    5. 安全隔离：严格排除代码编辑器、终端和 pre/code
    6. 动态 DOM 监听：MutationObserver + 点击补扫 + 周期空闲兜底
    """
    with open(dictionary_path, 'r', encoding='utf-8') as f:
        dict_data = json.load(f)

    exact_map = dict_data.get('exact', {})
    placeholder_map = dict_data.get('placeholders', {})

    exact_json = json.dumps(exact_map, ensure_ascii=False, indent=2)
    placeholder_json = json.dumps(placeholder_map, ensure_ascii=False, indent=2)

    script = f"""/**
 * Antigravity 简体中文界面汉化引擎 (Inlined Preload Engine)
 * 自动生成自核心词库，具备 DOM 变动监听、正则动态解析与无感自愈能力
 */
(function initAntigravityChineseUI() {{
  if (window.__antigravity_chinese_active) return;
  window.__antigravity_chinese_active = true;

  const EXACT_MAP = {exact_json};
  const PLACEHOLDER_MAP = {placeholder_json};

  // 动态时长转换函数
  function translateDuration(str) {{
    if (!str) return str;
    return str
      .replace(/\\b(\\d+)\\s+days?\\b/gi, '$1 天')
      .replace(/\\b(\\d+)\\s+hours?\\b/gi, '$1 小时')
      .replace(/\\b(\\d+)\\s+minutes?\\b/gi, '$1 分钟')
      .replace(/\\b(\\d+)\\s+seconds?\\b/gi, '$1 秒')
      .replace(/,\\s*/g, ' ')
      .trim();
  }}

  // 动态正则模式与碎节点拼接规则
  const PATTERN_RULES = [
    // 动态套餐：Your Plan: Google AI Pro
    {{
      regex: /^Your\\s+Plan:\\s*(.*)$/i,
      replace: (match, plan) => `当前套餐：${{plan}}`
    }},
    // 动态额度倒计时：You have used some of your weekly limit, which fully refreshes in 4 days, 15 hours.
    {{
      regex: /^You have used some of your (weekly|\\d+-hour) limit,\\s*which fully refreshes in\\s*([\\d\\w\\s,]+)\\.$/i,
      replace: (match, limitType, duration) => {{
        const limitZh = limitType.toLowerCase() === 'weekly' ? '每周' : limitType.replace('-hour', ' 小时');
        const durationZh = translateDuration(duration);
        return `您已使用部分 ${{limitZh}} 额度，将在 ${{durationZh}} 后完全刷新。`;
      }}
    }},
    // 动态重置倒计时：Resets in 4 hours 30 minutes
    {{
      regex: /^Resets in\\s+([\\d\\w\\s,]+)$/i,
      replace: (match, dur) => `将在 ${{translateDuration(dur)}} 后刷新`
    }},
    // 动态耗时与统计：Thought for 12s / Thinking for 5s
    {{
      regex: /^(?:Thought|Thinking)\\s+for\\s+(\\d+(?:\\.\\d+)?s?)$/i,
      replace: (match, duration) => `思考耗时 ${{duration}}`
    }},
    // Analyzed file.ts
    {{
      regex: /^Analyzed\\s+(.+)$/i,
      replace: (match, path) => `已分析 ${{path}}`
    }},
    // Edited file.ts +10 -2
    {{
      regex: /^Edited\\s+(.+)$/i,
      replace: (match, path) => `已编辑 ${{path}}`
    }},
    // Created file.ts
    {{
      regex: /^Created\\s+(.+)$/i,
      replace: (match, path) => `已创建 ${{path}}`
    }},
    // Deleted file.ts
    {{
      regex: /^Deleted\\s+(.+)$/i,
      replace: (match, path) => `已删除 ${{path}}`
    }},
    // Running command
    {{
      regex: /^Running\\s+(.+)$/i,
      replace: (match, cmd) => `正在执行 ${{cmd}}`
    }}
  ];

  const SKIP_SELECTORS = [
    '.monaco-editor',
    '.monaco-diff-editor',
    '.prism-code',
    '.xterm',
    'pre',
    'code',
    '[contenteditable="true"]',
    'style',
    'script',
    'svg',
    'textarea',
    'input[type="text"]',
    'input[type="password"]',
    'input[type="search"]'
  ].join(',');

  let isTranslating = false;

  function shouldSkip(node) {{
    if (!node) return true;
    if (node.nodeType === 1) {{
      if (node.matches && node.matches(SKIP_SELECTORS)) return true;
      if (node.closest && node.closest(SKIP_SELECTORS)) return true;
    }} else if (node.parentElement) {{
      if (node.parentElement.matches && node.parentElement.matches(SKIP_SELECTORS)) return true;
      if (node.parentElement.closest && node.parentElement.closest(SKIP_SELECTORS)) return true;
    }}
    return false;
  }}

  function translateTextNode(node) {{
    if (!node || node.nodeType !== 3) return;
    const text = node.nodeValue;
    if (!text) return;
    const trimmed = text.trim();
    if (!trimmed) return;
    if (shouldSkip(node)) return;

    // 如果包含中文，除非是特殊动态前缀，否则跳过
    if (/[\\u4e00-\\u9fa5]/.test(trimmed)) {{
      if (!/^(?:Thought|Thinking|Analyzed|Edited|Created)\\b/i.test(trimmed)) {{
        return;
      }}
    }}

    // 1. 精确词条替换
    if (EXACT_MAP[trimmed]) {{
      node.nodeValue = text.replace(trimmed, EXACT_MAP[trimmed]);
      return;
    }}

    // 2. 正则模式替换
    for (let i = 0; i < PATTERN_RULES.length; i++) {{
      const rule = PATTERN_RULES[i];
      if (rule.regex.test(trimmed)) {{
        const replaced = trimmed.replace(rule.regex, rule.replace);
        node.nodeValue = text.replace(trimmed, replaced);
        return;
      }}
    }}
  }}

  function translateAttributes(el) {{
    if (shouldSkip(el)) return;
    if (el.hasAttribute('placeholder')) {{
      const ph = el.getAttribute('placeholder');
      if (PLACEHOLDER_MAP[ph]) el.setAttribute('placeholder', PLACEHOLDER_MAP[ph]);
    }}
    if (el.hasAttribute('title')) {{
      const t = el.getAttribute('title');
      if (EXACT_MAP[t]) el.setAttribute('title', EXACT_MAP[t]);
    }}
    if (el.hasAttribute('aria-label')) {{
      const a = el.getAttribute('aria-label');
      if (EXACT_MAP[a]) el.setAttribute('aria-label', EXACT_MAP[a]);
    }}
  }}

  function translateTree(root) {{
    if (!root || shouldSkip(root)) return;
    if (root.nodeType === 1) translateAttributes(root);

    const walker = document.createTreeWalker(
      root,
      NodeFilter.SHOW_TEXT | NodeFilter.SHOW_ELEMENT,
      {{
        acceptNode: (n) => (shouldSkip(n) ? NodeFilter.FILTER_REJECT : NodeFilter.FILTER_ACCEPT)
      }}
    );

    let curr = walker.nextNode();
    while (curr) {{
      if (curr.nodeType === 3) {{
        translateTextNode(curr);
      }} else if (curr.nodeType === 1) {{
        translateAttributes(curr);
      }}
      curr = walker.nextNode();
    }}
  }}

  function start() {{
    if (!document.body) return;
    translateTree(document.body);

    const observer = new MutationObserver((mutations) => {{
      if (isTranslating) return;
      isTranslating = true;
      try {{
        for (let i = 0; i < mutations.length; i++) {{
          const m = mutations[i];
          if (m.type === 'childList') {{
            for (let j = 0; j < m.addedNodes.length; j++) {{
              translateTree(m.addedNodes[j]);
            }}
          }} else if (m.type === 'characterData') {{
            translateTextNode(m.target);
          }} else if (m.type === 'attributes') {{
            translateAttributes(m.target);
          }}
        }}
      }} finally {{
        isTranslating = false;
      }}
    }});

    observer.observe(document.body, {{
      childList: true,
      subtree: true,
      characterData: true,
      attributes: true,
      attributeFilter: ['placeholder', 'title', 'aria-label']
    }});

    // 交互即时响应：点击后快速补扫两次
    window.addEventListener('click', () => {{
      setTimeout(() => translateTree(document.body), 60);
      setTimeout(() => translateTree(document.body), 300);
    }}, true);

    // 周期性空闲兜底扫描（每 1 秒一次）
    setInterval(() => {{
      translateTree(document.body);
    }}, 1000);

    console.log('[Antigravity-Chinese] 简体中文界面汉化引擎已激活！');
  }}

  if (document.readyState === 'loading') {{
    document.addEventListener('DOMContentLoaded', start);
  }} else {{
    start();
  }}
}})();
"""
    return script
