<!-- 计划功能：项目总览文档，用于说明漏洞自动化复现与差分验证框架的目标、模块划分、使用方式与开发约定。 -->

# AgentsForCVE

一个面向单个 CVE 场景的漏洞自动化复现与差分验证 MVP。

项目的当前目标不是构建一个“大而全”的平台，而是先把一条最小主流程跑通：

`knowledge -> build -> poc -> verify`

这条主流程围绕一个核心问题展开：

给定一个 CVE 任务输入，系统能否自动整理漏洞知识、生成最小构建环境、生成最小 PoC，并基于修复前后日志给出差分验证结论。

## 1. 当前版本能做什么

当前仓库已经实现了一个“离线可运行的 mock 初版”，重点解决的是流程闭环问题，而不是外部能力接入问题。

它现在可以完成下面这些事情：

- 读取 `data/tasks/demo.yaml` 中的单个任务输入
- 初始化工作区并创建阶段目录
- 通过 `LangGraph` 或本地回退执行器串起四阶段流程
- 在 `knowledge` 阶段生成结构化 `KnowledgeModel`
- 在 `build` 阶段生成最小 Dockerfile、构建脚本和构建产物描述
- 在 `poc` 阶段生成最小 PoC、运行脚本以及修复前后日志
- 在 `verify` 阶段根据日志和知识特征做确定性判定
- 把各阶段提示词、日志、JSON 产物写入 `workspaces/<task_id>/`
- 通过 `unittest` 跑最小测试集

需要特别说明的是：

- 当前版本默认是 `mock/offline` 模式
- 不依赖真实 LLM、真实 Docker、真实网页抓取
- 更关注模块边界、schema 一致性和流程连通性

这使得项目在非常早期的阶段就可以被运行、调试、测试和继续扩展。

## 2. 项目设计理念

项目遵循下面这些模块边界：

- `agents`
  - 负责推理、组装上下文、输出结构化结果
- `tools`
  - 负责执行动作，比如文件写入、日志处理、进程调用、抓取、Docker、Git
- `schemas`
  - 负责定义阶段之间的唯一数据接口
- `orchestrator / graph`
  - 负责阶段调度、状态维护和路由控制
- `workspace`
  - 负责保存任务原始输入、中间工件、日志和最终结果

这套设计的价值在于：

- 后续接入真实 LLM 时，不必重写 graph
- 后续接入真实 Docker/Git/Web 能力时，不必重写 schema
- 后续替换单个 agent 的策略时，不会破坏上下游接口

## 3. 目录结构说明

```text
AgentsForCVE/
├─ app/
│  ├─ agents/          # 四阶段智能体与评审智能体
│  ├─ config.py        # 项目路径与默认配置
│  ├─ compat.py        # 轻量模型兼容层，缺少 pydantic 时也可运行
│  ├─ main.py          # 命令行入口
│  ├─ nodes/           # graph 节点
│  ├─ orchestrator/    # graph、router、state、stage enum
│  ├─ prompts/         # 各阶段提示词模板
│  ├─ schemas/         # 阶段输入输出 schema
│  ├─ templates/       # Dockerfile、build.sh、run.sh 模板
│  └─ tools/           # 文件、日志、Docker、抓取等执行工具
├─ data/
│  ├─ samples/         # 样例数据占位
│  └─ tasks/           # 任务输入，当前包含 demo.yaml
├─ reports/            # 汇总报告输出目录
├─ tests/              # 最小测试集
├─ workspaces/         # 各任务运行时工件目录
├─ AGENTS.md           # 项目约束与开发规则
├─ PROJECT_STATUS.md   # 项目状态记录
├─ README.md
└─ requirements.txt
```

## 4. 主流程详解

### 4.1 knowledge 阶段

输入：

- `TaskModel`

输出：

- `KnowledgeModel`

当前实现做了这些事情：

- 从任务里收集 `cve_url`、`repo_url`、`references`
- 使用本地 mock 抓取器生成参考页面
- 清洗文本并整理为中间知识文档
- 生成结构化漏洞知识
- 落盘：
  - `knowledge/prompt.txt`
  - `knowledge/fetched_pages.json`
  - `knowledge/documents.json`
  - `knowledge/knowledge.json`
  - `logs/knowledge_summary.log`

### 4.2 build 阶段

输入：

- `KnowledgeModel`

输出：

- `BuildArtifact`

当前实现做了这些事情：

- 根据知识信息推断最小依赖和构建命令
- 基于模板生成 `Dockerfile` 和 `build.sh`
- 通过 mock Docker 工具生成构建日志
- 落盘：
  - `build/prompt.txt`
  - `build/Dockerfile`
  - `build/build.sh`
  - `build/artifact.json`
  - `logs/build_build.log`

### 4.3 poc 阶段

输入：

- `KnowledgeModel`
- `BuildArtifact`

输出：

- `PoCArtifact`

当前实现做了这些事情：

- 生成最小 PoC 文件和运行脚本
- 生成修复前 `pre_patch.log` 与修复后 `post_patch.log`
- 通过 mock 容器执行器生成运行日志
- 落盘：
  - `poc/prompt.txt`
  - `poc/poc.py`
  - `poc/run.sh`
  - `poc/pre_patch.log`
  - `poc/post_patch.log`
  - `poc/artifact.json`
  - `logs/poc_execution.log`

### 4.4 verify 阶段

输入：

- `KnowledgeModel`
- `PoCArtifact`

输出：

- `VerifyResult`

当前实现做了这些事情：

- 读取前后版本日志
- 按 `expected_error_patterns` 与 `expected_stack_keywords` 做确定性匹配
- 给出：
  - 修复前是否触发
  - 修复后是否干净
  - 命中的错误模式
  - 命中的栈关键词
  - 最终 verdict 和原因
- 落盘：
  - `verify/prompt.txt`
  - `verify/result.json`
  - `logs/verify_summary.log`

## 5. 运行时状态与路由规则

主流程状态定义在 [app/orchestrator/state.py](/d:/a.OSLab/agentfv/AgentsForCVE/app/orchestrator/state.py)。

关键字段包括：

- `task`
- `knowledge`
- `build`
- `poc`
- `verify`
- `retry_count`
- `stage_history`
- `current_stage`
- `last_error`
- `final_status`

路由规则定义在 [app/orchestrator/routers.py](/d:/a.OSLab/agentfv/AgentsForCVE/app/orchestrator/routers.py)：

- `build_success=True` 时进入 `poc`
- `execution_success=True` 时进入 `verify`
- `verify.verdict == "success"` 时流程结束且状态为成功
- `build` 和 `poc` 支持有限重试

如果环境中没有安装 `langgraph`，项目会自动使用一个本地轻量回退执行器，保证开发阶段仍可运行。

## 6. 为什么现在可以“直接运行”

这个仓库一开始依赖 `PyYAML / Pydantic / LangGraph / pytest`，但当前环境里这些第三方包可能并不存在。

为了保证 MVP 真正可启动，当前版本增加了两类回退能力：

- `app/compat.py`
  - 提供最小 `BaseModel / Field` 兼容接口
- `app/orchestrator/graph.py`
  - 在缺少 `langgraph` 时使用本地状态图执行器
- `app/main.py`
  - 在缺少 `yaml` 时使用 `json` 兼容解析
- 测试使用 `unittest`
  - 因此即使没有 `pytest` 也可以执行

这意味着：

- 有第三方依赖时，项目可以继续向真实实现演进
- 没有第三方依赖时，项目仍能跑通 mock 主流程

## 7. 如何运行

### 7.1 运行 demo 任务

在项目根目录执行：

```powershell
python -m app.main
```

也可以显式指定任务文件：

```powershell
python -m app.main --task data/tasks/demo.yaml
```

运行后会打印最终状态 JSON，并在 `workspaces/demo-cve-0001/` 下生成阶段工件。

### 7.2 运行测试

当前测试基于标准库 `unittest`：

```powershell
python -m unittest discover -s tests -v
```

## 8. demo 任务说明

当前示例任务位于：

- [data/tasks/demo.yaml](/d:/a.OSLab/agentfv/AgentsForCVE/data/tasks/demo.yaml)

它是一个离线演示任务，字段包括：

- `task_id`
- `cve_id`
- `cve_url`
- `repo_url`
- `vulnerable_ref`
- `fixed_ref`
- `language`
- `references`

这个任务不会触发真实网络请求，而是驱动本地 mock 流程生成一套最小可验证工件。

## 9. 工作区输出说明

每次任务运行后，都会在：

- `workspaces/<task_id>/`

生成目录。以 demo 为例：

```text
workspaces/demo-cve-0001/
├─ knowledge/
├─ build/
├─ poc/
├─ verify/
└─ logs/
```

你可以直接从这些文件观察每个阶段的输入、输出和中间结果，而不必依赖控制台打印。

这对于后续做下面这些事情非常重要：

- 调试 prompt
- 对比 agent 输出
- 检查 schema 是否稳定
- 留存失败现场
- 生成任务报告

## 10. 测试覆盖内容

当前最小测试集包括：

- schema 基础实例化与序列化
- router 路由判断
- verifier 的确定性判断逻辑
- mock Docker 工具
- graph 主流程从 `knowledge` 跑到 `verify`

测试文件位于：

- [tests/test_schemas.py](/d:/a.OSLab/agentfv/AgentsForCVE/tests/test_schemas.py)
- [tests/test_router.py](/d:/a.OSLab/agentfv/AgentsForCVE/tests/test_router.py)
- [tests/test_verifier.py](/d:/a.OSLab/agentfv/AgentsForCVE/tests/test_verifier.py)
- [tests/test_docker_tools.py](/d:/a.OSLab/agentfv/AgentsForCVE/tests/test_docker_tools.py)
- [tests/test_graph_flow.py](/d:/a.OSLab/agentfv/AgentsForCVE/tests/test_graph_flow.py)

## 11. 当前局限

虽然现在已经能跑通，但这仍然只是第一版 MVP。

还没有接入的真实能力包括：

- 真实网页抓取
- 真实 reference 提取
- 真实 Git checkout / diff
- 真实 Docker build / run
- 真实 LLM structured output
- 真实 patch 分析
- 更强的 verifier 逻辑
- 报告汇总与导出

换句话说，现在解决的是“框架是否闭环”，而不是“结果是否具备生产可用性”。

## 12. 建议的下一步

建议按下面顺序推进：

1. 先把 `WorkspaceManager` 和阶段工件格式稳定下来
2. 把 `kb_agent` 从 mock 升级为真实网页资料收集 + 结构化知识提取
3. 接入真实 Git/Docker 工具层
4. 把 `build / poc / verify` 从 mock 升级为真实执行
5. 增加失败分支测试和报告输出

## 13. 开发约束

开发时请优先遵守：

- [AGENTS.md](/d:/a.OSLab/agentfv/AgentsForCVE/AGENTS.md)
- [PROJECT_STATUS.md](/d:/a.OSLab/agentfv/AgentsForCVE/PROJECT_STATUS.md)

核心原则是：

- 优先补全现有骨架
- schema 作为阶段之间唯一接口
- 先做最小可运行版本，再逐步增强

## 14. 一句话总结

当前版本已经把“单个 CVE 的最小自动化闭环”搭起来了。

虽然它还不是一个真正接入外部世界的漏洞复现系统，但它已经是一个可以运行、可以测试、可以观察产物、可以继续演进的工程起点。
