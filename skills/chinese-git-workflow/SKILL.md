---
name: chinese-git-workflow
description: 规范化中文 Git 提交流程与版本发布助手。根据当前分支 git diff 变更自动生成规范的 Conventional Commits 中文提交信息，以及生成中文版本发布日志 (Changelog)。当用户需要提交代码、生成 commit message 或整理版本发布说明时使用。
---

# 规范化中文 Git 工作流助手 (Chinese Git Workflow)

本技能帮助开发者基于当前工作区的代码修改，生成清晰、规范且符合现代工程化团队标准的中文 Git 提交信息（Conventional Commits 规范）与发布日志。

---

## 1. 中文 Conventional Commits 提交格式

每次提交结构如下：

```text
<type>(<scope>): <精炼中文描述（不超过 50 字，动词开头）>

[可选详细说明正文，说明修改背景、解决的核心痛点与逻辑设计]

[可选关联 ISSUE / PR，例如：Fixes #102]
```

### Type 动词类型对照与示例

| 类型 | 语义说明 | 示例 |
| :--- | :--- | :--- |
| `feat` | 新增功能特性 | `feat(auth): 新增企业微信扫码登录支持` |
| `fix` | 修复缺陷与 Bug | `fix(payment): 修复跨时区订单超时重复扣款问题` |
| `docs` | 仅文档或注释修改 | `docs(readme): 更新本地 Docker Compose 部署步骤` |
| `style` | 代码格式调整（空格、格式化） | `style(lint): 统一前端 ESLint 与 Prettier 规则` |
| `refactor`| 代码重构（无功能与缺陷改变） | `refactor(user): 抽取通用权限校验中间件` |
| `perf` | 性能提升与内存优化 | `perf(search): 引入 Redis 缓存高频热点搜索结果` |
| `test` | 测试用例编写与完善 | `test(order): 增加退款流程的单元测试用例` |
| `chore` | 构建、脚手架或依赖维护 | `chore(deps): 升级 Next.js 至最新补丁版本` |
| `ci` | CI/CD 流水线与配置变更 | `ci(github): 添加 Windows 与 Linux 双平台自动化构建` |

---

## 2. 自动生成中文 Commit 的操作步骤

1. 检查当前暂存区和工作区的变更：
   ```bash
   git status --short
   git diff --staged
   ```
2. 分析所有改动文件的逻辑归属，识别核心影响模块（确定 `<scope>`）和核心行为（确定 `<type>`）。
3. 输出建议的中文提交指令，供用户直接复制或确认：
   ```bash
   git commit -m "feat(module): 精炼中文说明"
   ```
