# COMSOL MCP - 实时显示版

基于 Python mph 库的 COMSOL 自动化工具，所有操作在 COMSOL Desktop 中实时显示。

## ✨ 特性

- 🔄 **实时显示** - 所有操作在 COMSOL Desktop 中实时可见
- 📊 **进度窗口** - 求解过程显示详细进度
- 🎯 **探针功能** - 支持实时监测物理量
- 🔥 **多物理场** - 支持流热耦合、结构力学等
- ⏱️ **瞬态仿真** - 支持稳态和瞬态分析

## 📦 安装

### 1. 克隆仓库

```bash
git clone https://github.com/YOUR_USERNAME/comsol-mcp.git
cd comsol-mcp
```

### 2. 安装 Python 依赖

```bash
pip install mph jpype1
```

### 3. 配置 COMSOL 路径

编辑 `config/comsol_path.bat`，设置你的 COMSOL 安装路径：

```batch
set COMSOL_PATH=C:\Program Files\COMSOL\COMSOL62\Multiphysics
```

## 🚀 使用方法

### 方法一：直接运行

```batch
# 启动 COMSOL
scripts\start_comsol.bat

# 运行示例
python examples\heat_transfer.py
```

### 方法二：在 AI Agent 中使用

在 OpenCode、Cursor、Claude 等 AI Agent 中配置：

1. 复制 `config/opencode.json` 到你的配置目录
2. 修改 COMSOL 路径
3. 对 AI 说：`启动 COMSOL，我要做一个传热仿真`

## 📁 目录结构

```
comsol-mcp/
├── README.md                    # 说明文档
├── scripts/
│   ├── start_comsol.bat        # 启动脚本（Windows）
│   └── start_comsol.sh         # 启动脚本（Linux/Mac）
├── examples/
│   ├── heat_transfer.py        # 传热示例
│   ├── laminar_flow.py         # 层流示例
│   ├── conjugate_heat.py       # 流热耦合示例
│   └── transient_probe.py      # 瞬态+探针示例
├── config/
│   ├── comsol_path.bat         # COMSOL 路径配置
│   └── opencode.json           # OpenCode 配置示例
└── docs/
    └── COMSOL_GUIDE.md         # 详细使用指南
```

## 🔧 工作原理

```
┌─────────────────────────────────────────────────────────┐
│                    COMSOL Server                         │
│              comsolmphserver.exe -port 2036              │
│                                                          │
│  ┌──────────────────┐    ┌──────────────────┐           │
│  │    Model1        │◄───│   Python API     │           │
│  │  (Desktop的模型)  │    │  修改 Model1     │           │
│  └────────┬─────────┘    └──────────────────┘           │
│           │                                              │
│           ▼                                              │
│  ┌──────────────────┐                                   │
│  │  Desktop GUI     │                                   │
│  │  实时刷新显示     │                                   │
│  └──────────────────┘                                   │
└─────────────────────────────────────────────────────────┘
```

**关键点**：
- Python 通过 `mph` 库连接 COMSOL Server
- 直接操作 Desktop 的 `Model1` 对象
- Desktop 自动实时刷新显示所有操作

## 📝 示例代码

```python
import mph

# 连接
client = mph.Client(port=2036, host='localhost')
java = client.java
java.showProgress(True)
java.showPlots(True)
model = java.model('Model1')

# 创建几何
model.geom().create('geom1', 3)
model.geom('geom1').feature().create('blk1', 'Block')
model.geom('geom1').feature('blk1').set('size', ['0.1', '0.1', '0.1'])
model.geom('geom1').run()

# 添加材料
mat = model.component('comp1').material().create('mat1', 'Common')
mat.propertyGroup('def').set('density', '1000')
mat.propertyGroup('def').set('thermalconductivity', '0.6')

# 设置物理场
ht = model.component('comp1').physics().create('ht', 'HeatTransfer', 'geom1')

# 求解
model.study().create('std1')
model.study('std1').create('stat', 'Stationary')
model.study('std1').run()

# 保存
model.save("my_model.mph")
```

## 🤖 AI Agent 配置

### OpenCode

将以下内容添加到 `~/.config/opencode/instructions.md`：

```markdown
## COMSOL 使用指南

当用户提到 "COMSOL"、"仿真"、"传热"、"流体" 等关键词时：

1. 运行 `scripts/start_comsol.bat` 启动 COMSOL
2. 使用 Python `mph` 库连接 Server
3. 创建模型，所有操作在 Desktop 中实时显示
4. 保存到 `models/` 目录
```

### Cursor

在 `.cursorrules` 中添加：

```
当用户要求做 COMSOL 仿真时：
1. 运行 start_comsol.bat 启动 COMSOL
2. 使用 Python mph 库连接 port=2036
3. 操作 Model1 对象，Desktop 实时显示
```

## ❓ 常见问题

### Q: COMSOL 启动失败？

检查：
- COMSOL 路径是否正确
- 端口 2036 是否被占用
- 以管理员身份运行

### Q: Python 连接失败？

确保：
- COMSOL Server 已启动
- `mph` 库已安装：`pip install mph`

### Q: Desktop 不显示？

确保：
- 使用 `java.model('Model1')` 而不是 `client.create()`
- 调用 `java.showProgress(True)`

## 📄 许可证

MIT License

## 🙏 致谢

- [MPh](https://mph.readthedocs.io/) - Python COMSOL 接口
- [COMSOL](https://www.comsol.com/) - 多物理场仿真软件
