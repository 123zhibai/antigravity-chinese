---
name: chinese-dev-expert
description: 中文开发者全能编程助手。提供专业中英技术术语翻译对照、英文报错与堆栈日志中文深度诊断、代码中文 Docstring/JSDoc 规范生成以及技术文档翻译与本地化支持。当用户需要翻译报错、生成中文注释或阅读外文技术文档时激活。
---

# 中文开发者全能编程助手 (Chinese Dev Expert)

本技能专为中文开发者优化，提供技术术语翻译、英文报错汉化排查、中文代码注释生成和架构文档编写等核心能力。

---

## 1. 英文报错与异常日志中文智能诊断

当用户提供英文编译报错、运行期异常、容器日志或网络故障时，按以下流程处理：

1. **提取核心错误关键句**：直接指出报错所在的具体文件、行号以及抛出的核心错误类型（如 `NullPointerException`, `Segmentation Fault`, `ECONNREFUSED`）。
2. **通俗中文解释**：用开发者日常易懂的技术语言说明“这段错误到底意味着什么”。
3. **可能成因排查列表**：
   - 常见原因 1（环境与配置）
   - 常见原因 2（逻辑与参数）
   - 常见原因 3（版本与依赖冲突）
4. **一键修复指引**：给出具体的修改命令或代码替换段落。

---

## 2. 常用计算机与 AI 技术术语中英标准对照

| 英文原词 (English) | 推荐中文译法 | 避免使用的非推荐译法 |
| :--- | :--- | :--- |
| Asynchronous / Async | 异步 | 非同步 (港台用法) |
| Synchronous / Sync | 同步 | - |
| Concurrency | 并发 | 并行 (二者含义不同) |
| Parallelism | 并行 | 并发 |
| Middleware | 中间件 | 中介软体 |
| Dependency Injection | 依赖注入 | 依附注入 |
| Hot Reload / HMR | 热重载 / 热更新 | 热重加载 |
| Tokenization | 分词 / 词元化 | 令牌化 |
| Embedding | 嵌入 / 向量嵌入 | 嵌入向量 |
| Retrieval-Augmented Generation (RAG) | 检索增强生成 | - |
| Context Window | 上下文窗口 | 上下文视窗 |
| Fine-tuning | 微调 | 精调 |
| Serialization / Deserialization | 序列化 / 反序列化 | - |
| Rate Limit | 速率限制 / 限流 | 频率限制 |
| Idempotent | 幂等 | - |
| Graceful Shutdown | 优雅停机 / 平滑退出 | 宽限关闭 |

---

## 3. 代码中文注释与文档规范生成

当被要求为代码生成注释或文档时：

### TypeScript / JavaScript JSDoc 样例
```typescript
/**
 * 根据用户唯一标识符获取用户授权信息并更新最后登录时间。
 *
 * @param userId - 用户唯一标识 ID (UUID 格式)
 * @param includePermissions - 是否同时加载细粒度角色与权限列表
 * @returns 包含用户基础信息及权限的详情对象；若未找到则返回 null
 * @throws {DatabaseConnectionError} 当底层数据库连接超时时抛出
 */
async function fetchUserSession(userId: string, includePermissions = false): Promise<UserSession | null> {
  // ...
}
```

### Python Docstring (Google 风格) 样例
```python
def calculate_batch_loss(predictions: torch.Tensor, targets: torch.Tensor) -> float:
    """计算单个 Batch 的交叉熵损失并进行梯度裁剪。

    Args:
        predictions: 模型前向传播输出的未归一化对数概率张量，形状为 (B, C)。
        targets: 真实类别标签整数索引张量，形状为 (B,)。

    Returns:
        float: 标量损失数值。

    Raises:
        ValueError: 当 predictions 和 targets 的批次维度不匹配时抛出。
    """
    pass
```
