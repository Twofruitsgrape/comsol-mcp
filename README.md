# COMSOL MCP

一个用于 **COMSOL Multiphysics** 的 Model Context Protocol (MCP) 服务器，让 AI 智能体（如 Claude Desktop / Codex）能够：

- **读写 `.mph` 模型文件**
- **实时控制 COMSOL 桌面 GUI**（GUI 内嵌桥接方式，操作在桌面上实时可见）
- 完成完整的 **建模 → 定义 → 计算 → 后处理** 流水线
- 在 **任意工作目录** 下使用（不依赖 cwd，自动探测 COMSOL 安装路径）
- 无需 COMSOL 时以 **dry-run 模式** 运行，便于开发与测试

---

## 架构

```
AI Agent ──MCP(stdio)──► comsol_mcp (Python) ──HTTP/JSON──► ComsolBridge (Java, 在 COMSOL JVM 内)
                                                    │
                                                    └──comsolbatch (无头回退)
```

- **GUI 内嵌桥接（实时控制）**：`launch_gui` 启动 COMSOL 桌面并在其 JVM 内加载 `ComsolBridge`，它开着本地 HTTP 服务并持有 `Model` 对象。MCP 通过它实时调用 COMSOL Java API，你在桌面上能看到几何/物理/求解进度实时变化。
- **无头批处理（回退/批量）**：没有 GUI 会话时，操作被累积成一个 Java 程序，用 `comsolcompile` + `comsolbatch` 运行。同一套建模逻辑在两种模式下通用。
- **dry-run**：本机未安装 COMSOL 时自动启用，所有工具仍可调用（返回模拟结果），便于导入与测试。

## 环境要求

- COMSOL Multiphysics 5.x / 6.x（标准桌面授权即含 Java API）
- Python 3.10+
- （可选）无需 Node —— 看板是纯静态 HTML

## 安装

```bash
cd comsol-mcp
pip install .
```

### ⚠️ 配置 COMSOL 路径（非默认安装必须填）

程序按以下顺序定位 COMSOL，但自动探测**只覆盖标准位置**：

1. 环境变量 `COMSOL_HOME`（最可靠，**推荐在配置 MCP 时显式给定**）
2. Windows 注册表（`COMSOLROOT`）
3. 标准目录：`C:\Program Files\COMSOL\COMSOLxx`、`D:/...`、`E:/...` 及其 WSL / Linux / macOS 对应路径

> 如果你的 COMSOL 装在**非默认盘或自定义目录**（例如 `C:\D\Program Files\COMSOL\COMSOL62\Multiphysics`），自动探测**扫不到**，必须设置 `COMSOL_HOME`。**强烈建议所有用户在配置 MCP 时都把 `COMSOL_HOME` 写进 `env`**，不要依赖自动探测——否则 agent 可能误判你没装 COMSOL 而退回 dry-run。

```bash
# Windows 示例：指向 Multiphysics 目录最简明（也兼容版本目录 .../COMSOL62 或根目录 .../COMSOL）
export COMSOL_HOME="C:\Program Files\COMSOL\COMSOL62\Multiphysics"
```

编译 Java 桥（需要 COMSOL 在 PATH 或 COMSOL_HOME 中）：

```bash
comsol-mcp compile-bridge
```

## 快速开始

在 MCP 客户端配置里加入（OpenCode 写在 `~/.config/opencode/opencode.json` 的 `mcp` 块；Claude Desktop 写在 `claude_desktop_config.json` 的 `mcpServers` 块）：

> **关键**：`COMSOL_HOME` 必须写进 `env`。**不要**让 AI 去探测/猜测某个固定默认路径（如 `C:\Program Files\COMSOL`）——自定义安装目录它扫不到，会误判为“未安装”并退回 dry-run。本机没装 COMSOL 时仍可 dry-run（`generate_model_java` 等无需 COMSOL 的工具照常可用）。

```json
{
  "mcp": {
    "comsol": {
      "type": "local",
      "command": ["C:\\path\\to\\comsol-mcp.exe"],
      "args": [],
      "env": { "COMSOL_HOME": "C:\\D\\Program Files\\COMSOL\\COMSOL62\\Multiphysics" }
    }
  }
}
```

然后让 AI 这样工作：

1. `launch_gui()` —— 打开 COMSOL 桌面并加载桥（实时可见）。
2. `new_model()` / `load_model("x.mph")`
3. `add_block("geom1", 3, [1,1,1], [0,0,0])`
4. `add_physics("ht", "ht")`（传热）
5. `build_mesh()` → `add_study("std1", "Stationary")` → `run_solver("std1")`
6. `evaluate("T")` 取结果，`save_model("out.mph")` 保存。

## MCP 工具列表

| 类别 | 工具 |
|------|------|
| 会话 / GUI | `launch_gui`, `connect_gui`, `gui_status`, `shutdown_gui` |
| 模型读写 | `load_model`, `save_model`, `new_model`, `model_info` |
| 几何 | `add_block`, `add_cylinder`, `add_sphere`, `boolean_op`, `import_geometry` |
| 物理 / 材料 | `add_physics`(ht/spf/tds/es/solid/…), `add_material` |
| 网格 / 研究 / 求解 | `build_mesh`, `add_study`(Stationary/TimeDependent/Parametric/Eigenfrequency), `run_solver`, `solver_status` |
| 后处理 | `evaluate`, `export_results` |
| 通用 | `exec_model_api`（直接运行任意 COMSOL Java API 代码） |
| 无 COMSOL 准备 | `generate_model_java`（生成可编译的 Java 模型源码，无需 COMSOL，用于拷到 COMSOL 机器编译成 .mph） |

详见 [USAGE.md](USAGE.md)。

## 干跑模式（dry-run）

当检测不到 COMSOL 时，包会自动进入 dry-run：工具返回模拟数据，MCP 仍可导入与测试。设置 `COMSOL_MCP_DRYRUN=1` 可强制开启。

> 没有 COMSOL 的机器也能用 `generate_model_java` 生成独立可编译的 Java 模型源码，之后在装有 COMSOL 的机器上 `comsolcompile` + `comsolbatch` 编译为 `.mph`。详见 [USAGE.md](USAGE.md) 的“两种运行模式”。

## 验证状态

- ✅ 在本机构建环境中：`py_compile` 全包通过、MCP 服务器可启动、dry-run 逻辑链可跑通。
- ⚠️ **真实 COMSOL 执行需在装有 COMSOL 的机器上验证**：运行 `comsol-mcp compile-bridge` 并实际跑一个模型。Java 桥按 COMSOL Java API 规范编写，但不同版本接口可能需微调（见 `comsol_mcp/bridge/ComsolBridge.java` 顶部说明）。

## 开源协议

MIT —— 见 [LICENSE](LICENSE)。
