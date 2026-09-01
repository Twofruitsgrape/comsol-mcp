# COMSOL Desktop 实时同步自动化操作 完整说明文档

## ⚡ 快速参考卡片（新必读）

### 启动命令（由 AI 自动执行，用户无需手动操作）

```powershell
# AI 会自动执行以下命令：
# 1. 启动服务器（带 -graphics）
comsolmphserver.exe -port 2036 -multi on -graphics

# 2. 启动 Desktop（带 -host）
comsolmphclient.exe -host 127.0.0.1 -port 2036

# 3. Python 连接并操作
client = mph.Client(port=2036, host='localhost')
```

**用户只需**：告诉 AI 你想做什么（如"创建一个热传导模型"），AI 会自动处理所有启动和操作。

### ⚠️ 关键点
1. **服务器必须带 `-graphics` 参数**
2. **Python 必须调用 `java.showProgress(True)`**
3. **不要用 `client.create()` 创建新模型，用 `java.model('Model1')`**
4. **绘图不要调用 `.run()`，用 `set('window', 'graphics')`**

---

## 一、方案概述

本方案实现了 **Python 自动化操作 COMSOL 时，Desktop 界面实时同步显示所有操作过程** 的功能。用户可以在 COMSOL Desktop 中实时看到：

- 几何创建过程
- 材料添加过程
- 物理场设置过程
- 网格划分过程
- 求解计算过程（含进度窗口和日志）
- 结果云图显示（在 Desktop 内部 Graphics 窗口）

### 核心原理

```
┌─────────────────────────────────────────────────────────────┐
│                    COMSOL Server                             │
│              comsolmphserver.exe -port 2036                  │
│              -multi on -graphics                             │
│                                                              │
│  ┌──────────────────┐    ┌──────────────────┐               │
│  │    Model1        │◄───│   Python API     │               │
│  │  (Desktop的模型)  │    │  修改 Model1     │               │
│  └────────┬─────────┘    └──────────────────┘               │
│           │                                                  │
│           ▼                                                  │
│  ┌──────────────────┐                                       │
│  │  Desktop GUI     │                                       │
│  │  实时刷新显示     │                                       │
│  └──────────────────┘                                       │
└─────────────────────────────────────────────────────────────┘
```

**关键突破**：不要用 `client.create('NewModel')` 创建新模型，而是用 `java.model('Model1')` 获取 Desktop 已打开的模型，直接修改它。这样 Desktop 会自动刷新显示。

---

## 二、环境要求

### 软件要求

| 软件 | 版本 | 说明 |
|------|------|------|
| COMSOL Multiphysics | 6.2 或更高 | 需要完整安装 |
| Python | 3.10+ | 推荐 3.12 |
| MPh (mph) | 1.4.0+ | Python COMSOL 接口库 |
| JPype1 | 1.7.1+ | Java 虚拟机桥接 |

### 安装依赖

```bash
pip install mph jpype1
```

### COMSOL 安装路径

默认安装路径（根据实际安装调整）：
```
C:\D\Program Files\COMSOL\COMSOL62\Multiphysics\bin\win64\
```

需要的可执行文件：
- `comsolmphserver.exe` - COMSOL 服务器
- `comsolmphclient.exe` - COMSOL Desktop 客户端

---

## 三、启动流程（AI 自动执行，用户无需手动操作）

### ⚠️ 重要说明

**所有启动步骤都由 AI 自动完成**，用户只需告诉 AI 你想做什么。

AI 会使用 `bash` 工具执行以下命令：
1. 检查服务器是否已启动
2. 如未启动，自动启动 `comsolmphserver.exe -port 2036 -multi on -graphics`
3. 启动 `comsolmphclient.exe -host 127.0.0.1 -port 2036`
4. 使用 Python 连接并操作

### AI 自动执行的启动流程

```powershell
# 步骤 1：检查端口是否被占用
netstat -ano | findstr ":2036"

# 步骤 2：如未启动，启动服务器
Start-Process -FilePath "C:\D\Program Files\COMSOL\COMSOL62\Multiphysics\bin\win64\comsolmphserver.exe" -ArgumentList "-port 2036 -multi on -graphics"

# 步骤 3：启动 Desktop 客户端
Start-Process -FilePath "C:\D\Program Files\COMSOL\COMSOL62\Multiphysics\bin\win64\comsolmphclient.exe" -ArgumentList "-host 127.0.0.1 -port 2036"

# 步骤 4：等待几秒让服务启动
Start-Sleep -Seconds 3

# 步骤 5：Python 连接并操作
python -c "import mph; client = mph.Client(port=2036, host='localhost')"
```

### 用户只需说

- "帮我创建一个热传导模型"
- "做一个参数化扫描"
- "求解一个流体问题"

AI 会自动处理所有启动和操作步骤。
- Desktop 窗口应自动打开
- 初始状态应为空白（无模型加载）
- Desktop 会自动创建 `Model1`

### 步骤 3：Python 连接服务器

```python
import mph

# 连接到已运行的服务器
client = mph.Client(port=2036, host='localhost')
print('已连接到服务器')

# 获取 Java 接口
java = client.java

# 关键：获取 Desktop 的 Model1（不要创建新模型！）
model = java.model('Model1')
print('已获取 Desktop 的 Model1')
```

**⚠️ 重要警告：**
```python
# ❌ 错误做法：创建新模型（Desktop 不会显示）
model = client.create('NewModel')  # Desktop 仍然空白！

# ✅ 正确做法：获取 Desktop 的 Model1
model = java.model('Model1')  # Desktop 实时更新！
```

---

## 四、完整工作流示例

### 4.1 基础示例：简单热传导模型

```python
"""
完整工作流：创建简单热传导模型
Desktop 实时显示所有操作过程
"""
import mph
import time

# ============================================================
# 第一部分：连接和初始化
# ============================================================

# 连接服务器
client = mph.Client(port=2036, host='localhost')

# 导入 JPype（必须在 client 连接之后）
from jpype import JArray, JString, JInt
StringArray = JArray(JString)
IntArray = JArray(JInt)

java = client.java
print('已连接到服务器')

# 启用进度显示
java.showProgress(True)
java.showPlots(True)

# 获取 Desktop 的 Model1
model = java.model('Model1')
print('已获取 Model1')

# ============================================================
# 第二部分：创建几何
# ============================================================

print('\n[步骤 1] 创建几何...')

# 创建组件
try:
    model.modelNode().create('comp1')
except:
    print('  comp1 已存在')

# 创建 3D 几何
try:
    model.geom().create('geom1', 3)
except:
    print('  geom1 已存在')

# 创建长方体
try:
    model.geom('geom1').feature().create('blk1', 'Block')
except:
    print('  blk1 已存在')

# 设置尺寸（0.1m x 0.1m x 0.1m）
model.geom('geom1').feature('blk1').set('size', StringArray(['0.1', '0.1', '0.1']))
model.geom('geom1').feature('blk1').set('base', 'center')

# 构建几何
model.geom('geom1').run()
print('  几何构建完成')
time.sleep(2)

# ============================================================
# 第三部分：添加材料
# ============================================================

print('\n[步骤 2] 添加材料...')

# 创建材料
try:
    mat = model.component('comp1').material().create('mat1', 'Common')
except:
    mat = model.component('comp1').material('mat1')

mat.label('铜')
mat.selection().all()

# 设置材料属性
mat.propertyGroup('def').set('thermalconductivity', '400')  # 热导率 W/(m·K)
mat.propertyGroup('def').set('density', '8960')              # 密度 kg/m³
mat.propertyGroup('def').set('heatcapacity', '385')           # 比热容 J/(kg·K)

print('  铜材料添加完成')
time.sleep(2)

# ============================================================
# 第四部分：设置物理场
# ============================================================

print('\n[步骤 3] 设置物理场...')

# 创建热传导物理场
try:
    ht = model.component('comp1').physics().create('ht', 'HeatTransfer', 'geom1')
except:
    ht = model.component('comp1').physics('ht')

# 温度边界条件（底面 100°C）
try:
    ht.feature().create('temp1', 'TemperatureBoundary', 2)
except:
    pass
ht.feature('temp1').selection().set(IntArray([1]))
ht.feature('temp1').set('T0', '373.15')

# 热源（整个域 1 MW/m³）
try:
    ht.feature().create('hs1', 'HeatSource', 3)
except:
    pass
ht.feature('hs1').selection().all()
ht.feature('hs1').set('Q0', '1e6')

print('  物理场设置完成')
time.sleep(2)

# ============================================================
# 第五部分：划分网格
# ============================================================

print('\n[步骤 4] 划分网格...')

try:
    model.component('comp1').mesh().create('mesh1')
except:
    pass

model.component('comp1').mesh('mesh1').run()
print('  网格划分完成')
time.sleep(3)

# ============================================================
# 第六部分：求解计算
# ============================================================

print('\n[步骤 5] 求解计算...')

# 创建研究
try:
    model.study().remove('std1')
except:
    pass
model.study().create('std1')
model.study('std1').create('stat', 'Stationary')

# 求解（会显示进度窗口和日志）
start = time.time()
model.study('std1').run()
elapsed = time.time() - start
print(f'  求解完成！耗时 {elapsed:.1f} 秒')

# ============================================================
# 第七部分：创建结果绘图
# ============================================================

print('\n[步骤 6] 创建结果绘图...')

# 关闭之前的绘图窗口
java.closeWindows()

# 创建 3D 绘图组
try:
    model.result().create('pg1', 'PlotGroup3D')
except:
    pass

# 添加温度表面图
try:
    model.result('pg1').create('surf1', 'Surface')
except:
    pass
model.result('pg1').feature('surf1').set('expr', 'T')
model.result('pg1').feature('surf1').set('unit', 'K')

# 设置在 Desktop Graphics 窗口显示（不要调用 .run()！）
model.result('pg1').set('window', 'graphics')

print('  绘图创建完成')
print('  请在 Desktop 中点击 "3D Plot Group 1" 查看温度分布')

# ============================================================
# 完成
# ============================================================

print('\n' + '='*60)
print('工作流完成！')
print('='*60)
print('Desktop 应显示：')
print('  1. 组件 1 + 3D 长方体几何')
print('  2. 铜材料')
print('  3. 热传导物理场 + 边界条件')
print('  4. 网格')
print('  5. 求解结果')
print('  6. 点击 "3D Plot Group 1" 查看温度云图')
print('='*60)
```

### 4.2 进阶示例：参数化扫描

```python
"""
参数化扫描：研究不同热通量下的温度分布
"""
import mph
import time

client = mph.Client(port=2036, host='localhost')
from jpype import JArray, JString, JInt
StringArray = JArray(JString)
IntArray = JArray(JInt)

java = client.java
model = java.model('Model1')

# 启用进度
java.showProgress(True)

# ============================================================
# 添加参数
# ============================================================

print('\n[添加参数] 定义热通量参数...')
try:
    model.param().remove('q_flux')
except:
    pass
model.param().set('q_flux', '1000')  # 初始值 1000 W/m²
print('  参数 q_flux = 1000 W/m²')

# ============================================================
# 更新物理场使用参数
# ============================================================

print('\n[更新物理场] 热通量使用参数...')
ht = model.component('comp1').physics('ht')

# 删除现有热通量边界
try:
    ht.feature().remove('hf1')
except:
    pass

# 创建新的热通量边界（使用参数）
ht.feature().create('hf1', 'HeatFluxBoundary', 2)
ht.feature('hf1').selection().set(IntArray([6]))  # 顶面
ht.feature('hf1').set('q0', 'q_flux')  # 使用参数
print('  热通量 = q_flux')

# ============================================================
# 创建参数化研究
# ============================================================

print('\n[创建参数化研究] 扫描 5 个热通量值...')

# 删除现有研究
try:
    model.study().remove('std1')
except:
    pass

# 创建新研究
model.study().create('std1')
model.study('std1').create('stat', 'Stationary')

# 添加参数化扫描
try:
    model.study('std1').create('param', 'Parametric')
except:
    pass

# 设置扫描参数和值
model.study('std1').feature('param').set('pname', 'q_flux')
model.study('std1').feature('param').set('plist', '1000 2000 3000 4000 5000')
print('  扫描值: 1000, 2000, 3000, 4000, 5000 W/m²')

# ============================================================
# 求解参数化研究
# ============================================================

print('\n[求解] 运行参数化研究（5 个解）...')
start = time.time()
model.study('std1').run()
elapsed = time.time() - start
print(f'  参数化研究完成！总耗时 {elapsed:.1f} 秒')
print(f'  平均每个解: {elapsed/5:.1f} 秒')

# ============================================================
# 为每个解创建绘图
# ============================================================

print('\n[创建绘图] 为每个参数值创建温度图...')

# 关闭之前的窗口
java.closeWindows()

for i, q_val in enumerate([1000, 2000, 3000, 4000, 5000], 1):
    # 创建绘图组
    try:
        model.result().create(f'pg{i}', 'PlotGroup3D')
    except:
        pass
    
    # 添加表面图
    try:
        model.result(f'pg{i}').create('surf1', 'Surface')
    except:
        pass
    
    model.result(f'pg{i}').feature('surf1').set('expr', 'T')
    model.result(f'pg{i}').feature('surf1').set('unit', 'K')
    
    # 设置在 Desktop 内显示
    model.result(f'pg{i}').set('window', 'graphics')
    
    print(f'  绘图 {i} 创建完成 (q_flux = {q_val} W/m²)')

print('\n请在 Desktop 中依次点击各个绘图组查看结果')
```

### 4.3 复杂模型示例：多物理场

```python
"""
复杂模型：热-结构耦合
"""
import mph
import time

client = mph.Client(port=2036, host='localhost')
from jpype import JArray, JString, JInt
StringArray = JArray(JString)
IntArray = JArray(JInt)

java = client.java
java.showProgress(True)
model = java.model('Model1')

# ============================================================
# 大尺寸几何
# ============================================================

print('\n[几何] 创建 5m x 5m x 0.5m 板...')

# 删除现有几何特征
try:
    model.geom('geom1').feature().remove('blk1')
except:
    pass

model.geom('geom1').feature().create('blk1', 'Block')
model.geom('geom1').feature('blk1').set('size', StringArray(['5', '5', '0.5']))
model.geom('geom1').feature('blk1').set('base', 'center')
model.geom('geom1').run()
print('  几何构建完成')

# ============================================================
# 更新材料为钢
# ============================================================

print('\n[材料] 更新为钢...')
mat = model.component('comp1').material('mat1')
mat.label('钢')
mat.propertyGroup('def').set('thermalconductivity', '50')
mat.propertyGroup('def').set('density', '7800')
mat.propertyGroup('def').set('heatcapacity', '500')
print('  钢材料设置完成')

# ============================================================
# 复杂边界条件
# ============================================================

print('\n[物理场] 设置复杂边界条件...')

ht = model.component('comp1').physics('ht')

# 删除现有边界条件
for feat in ['temp1', 'hf1', 'hf2', 'hs1']:
    try:
        ht.feature().remove(feat)
    except:
        pass

# 底面恒温 20°C
ht.feature().create('temp1', 'TemperatureBoundary', 2)
ht.feature('temp1').selection().set(IntArray([1]))
ht.feature('temp1').set('T0', '293.15')
print('  底面: 20°C 恒温')

# 顶面热通量 5000 W/m²
ht.feature().create('hf1', 'HeatFluxBoundary', 2)
ht.feature('hf1').selection().set(IntArray([6]))
ht.feature('hf1').set('q0', '5000')
print('  顶面: 5000 W/m² 热通量')

# 侧面对流换热
ht.feature().create('hf2', 'HeatFluxBoundary', 2)
ht.feature('hf2').selection().set(IntArray([2, 3, 4, 5]))
ht.feature('hf2').set('HeatFluxType', 'ConvectiveHeatFlux')
ht.feature('hf2').set('h', '25')  # 换热系数 25 W/(m²·K)
ht.feature('hf2').set('Text', '293.15')  # 环境温度 20°C
print('  侧面: 对流换热 h=25 W/(m²·K)')

# 内部热源
ht.feature().create('hs1', 'HeatSource', 3)
ht.feature('hs1').selection().all()
ht.feature('hs1').set('Q0', '50000')  # 50 kW/m³
print('  内部: 热源 50 kW/m³')

# ============================================================
# 求解和绘图
# ============================================================

print('\n[求解] 运行求解...')
model.study('std1').run()
print('  求解完成')

# 创建绘图
java.closeWindows()
model.result().create('pg1', 'PlotGroup3D')
model.result('pg1').create('surf1', 'Surface')
model.result('pg1').feature('surf1').set('expr', 'T')
model.result('pg1').feature('surf1').set('unit', 'K')
model.result('pg1').set('window', 'graphics')
print('  温度云图创建完成')
```

---

## 五、API 参考

### 5.1 连接和初始化

```python
# 连接服务器
client = mph.Client(port=2036, host='localhost')

# 获取 Java 接口
java = client.java

# 获取 Desktop 的模型
model = java.model('Model1')

# 启用进度显示
java.showProgress(True)

# 启用绘图显示
java.showPlots(True)

# 关闭所有绘图窗口
java.closeWindows()
```

### 5.2 几何操作

```python
# 创建组件
model.modelNode().create('comp1')

# 创建 3D 几何
model.geom().create('geom1', 3)

# 创建长方体
model.geom('geom1').feature().create('blk1', 'Block')
model.geom('geom1').feature('blk1').set('size', StringArray(['0.1', '0.1', '0.1']))
model.geom('geom1').feature('blk1').set('base', 'center')

# 创建圆柱体
model.geom('geom1').feature().create('cyl1', 'Cylinder')
model.geom('geom1').feature('cyl1').set('r', '0.05')
model.geom('geom1').feature('cyl1').set('h', '0.2')

# 构建几何（必须调用！）
model.geom('geom1').run()

# 删除几何特征
model.geom('geom1').feature().remove('blk1')
```

### 5.3 材料操作

```python
# 创建材料
mat = model.component('comp1').material().create('mat1', 'Common')
mat.label('自定义材料')

# 选择应用域
mat.selection().all()  # 所有域
# 或
mat.selection().set(IntArray([1]))  # 指定域

# 设置材料属性
mat.propertyGroup('def').set('thermalconductivity', '400')  # 热导率
mat.propertyGroup('def').set('density', '8960')              # 密度
mat.propertyGroup('def').set('heatcapacity', '385')           # 比热容
```

### 5.4 物理场操作

```python
# 创建热传导物理场
ht = model.component('comp1').physics().create('ht', 'HeatTransfer', 'geom1')

# 温度边界条件
ht.feature().create('temp1', 'TemperatureBoundary', 2)
ht.feature('temp1').selection().set(IntArray([1]))  # 选择面
ht.feature('temp1').set('T0', '373.15')  # 温度 (K)

# 热通量边界条件
ht.feature().create('hf1', 'HeatFluxBoundary', 2)
ht.feature('hf1').selection().set(IntArray([6]))
ht.feature('hf1').set('q0', '1000')  # 热通量 (W/m²)

# 对流换热边界条件
ht.feature().create('hf2', 'HeatFluxBoundary', 2)
ht.feature('hf2').selection().set(IntArray([2, 3, 4, 5]))
ht.feature('hf2').set('HeatFluxType', 'ConvectiveHeatFlux')
ht.feature('hf2').set('h', '10')  # 换热系数
ht.feature('hf2').set('Text', '293.15')  # 环境温度

# 内部热源
ht.feature().create('hs1', 'HeatSource', 3)
ht.feature('hs1').selection().all()
ht.feature('hs1').set('Q0', '1e6')  # 热源强度 (W/m³)

# 删除物理场特征
ht.feature().remove('temp1')
```

### 5.5 网格操作

```python
# 创建网格
model.component('comp1').mesh().create('mesh1')

# 构建网格（必须调用！）
model.component('comp1').mesh('mesh1').run()
```

### 5.6 研究和求解

```python
# 创建研究
model.study().create('std1')
model.study('std1').create('stat', 'Stationary')  # 稳态研究

# 删除研究
model.study().remove('std1')

# 求解（会显示进度窗口）
model.study('std1').run()

# 参数化研究
model.study('std1').create('param', 'Parametric')
model.study('std1').feature('param').set('pname', 'param_name')
model.study('std1').feature('param').set('plist', 'val1 val2 val3')
```

### 5.7 结果绘图

```python
# 关闭之前的绘图窗口
java.closeWindows()

# 创建 3D 绘图组
model.result().create('pg1', 'PlotGroup3D')

# 添加表面图
model.result('pg1').create('surf1', 'Surface')
model.result('pg1').feature('surf1').set('expr', 'T')  # 温度
model.result('pg1').feature('surf1').set('unit', 'K')

# ⚠️ 关键：设置在 Desktop Graphics 窗口显示
model.result('pg1').set('window', 'graphics')

# ⚠️ 重要：不要调用 .run()！
# model.result('pg1').run()  # ❌ 这会弹出单独窗口！

# 让用户在 Desktop 中点击查看绘图
```

### 5.8 参数操作

```python
# 设置参数
model.param().set('param_name', 'value')

# 删除参数
model.param().remove('param_name')
```

---

## 六、常见问题和解决方案

### 6.1 Desktop 不显示模型

**问题**：Python 操作后 Desktop 仍然空白

**原因**：使用了 `client.create('NewModel')` 创建新模型

**解决**：
```python
# ❌ 错误
model = client.create('NewModel')

# ✅ 正确
model = java.model('Model1')
```

### 6.2 计算没有进度窗口

**问题**：求解时没有显示进度窗口

**原因**：
1. 服务器未带 `-graphics` 参数启动
2. 未调用 `java.showProgress(True)`

**解决**：
```powershell
# 重启服务器（带 -graphics）
comsolmphserver.exe -port 2036 -multi on -graphics
```

```python
# 启用进度显示
java.showProgress(True)
```

### 6.3 结果绘图弹出单独窗口

**问题**：绘图在单独的弹出窗口中显示，而不是 Desktop 的 Graphics 窗口

**原因**：调用了 `model.result('pg1').run()`

**解决**：
```python
# ❌ 错误
model.result('pg1').run()  # 弹出单独窗口

# ✅ 正确
model.result('pg1').set('window', 'graphics')
# 不调用 .run()，让用户在 Desktop 中点击查看
```

### 6.4 JPype 数组类型错误

**问题**：`TypeError: No matching overloads found`

**解决**：
```python
from jpype import JArray, JString, JInt

# String 数组
StringArray = JArray(JString)
model.geom('geom1').feature('blk1').set('size', StringArray(['0.1', '0.1', '0.1']))

# Int 数组
IntArray = JArray(JInt)
ht.feature('temp1').selection().set(IntArray([1]))
```

### 6.5 材料属性设置失败

**问题**：求解时报错缺少材料属性

**解决**：确保设置所有必要的材料属性
```python
mat.propertyGroup('def').set('thermalconductivity', '400')  # 热导率
mat.propertyGroup('def').set('density', '8960')              # 密度
mat.propertyGroup('def').set('heatcapacity', '385')           # 比热容
```

### 6.6 Desktop 显示 Model1 但内容不更新

**问题**：之前测试的内容残留在 Model1 中

**解决**：清理 Model1 后重新创建
```python
# 清理现有内容
for feat in ['comp1']:
    try:
        model.component().remove(feat)
    except:
        pass

# 重新创建
model.modelNode().create('comp1')
```

---

## 七、高级技巧

### 7.1 等待用户操作

在关键步骤之间添加等待，让用户有时间查看 Desktop 更新：

```python
import time

# 创建几何后等待
model.geom('geom1').run()
time.sleep(2)  # 等待 2 秒

# 添加材料后等待
mat = model.component('comp1').material().create('mat1', 'Common')
time.sleep(2)

# 求解后等待
model.study('std1').run()
time.sleep(3)
```

### 7.2 错误处理

使用 try-except 处理已存在的节点：

```python
# 创建节点（如果已存在则跳过）
try:
    model.modelNode().create('comp1')
except:
    print('comp1 已存在')

# 创建几何特征（如果已存在则跳过）
try:
    model.geom('geom1').feature().create('blk1', 'Block')
except:
    print('blk1 已存在')
```

### 7.3 日志输出

在 Python 中输出详细的操作日志：

```python
print('\n' + '='*60)
print('[步骤 1] 创建几何...')
print('  创建长方体: 0.1m x 0.1m x 0.1m')
model.geom('geom1').run()
print('  几何构建完成')
print('='*60)
```

### 7.4 保存模型

```python
# 保存为 .mph 文件
model.save('E:/优化/api/my_model.mph')
print('模型已保存')
```

---

## 八、完整启动脚本

创建一个批处理文件 `start_comsol.bat`：

```batch
@echo off
echo ========================================
echo   启动 COMSOL 服务器和 Desktop
echo ========================================

echo.
echo [1/2] 启动 COMSOL 服务器...
start "COMSOL Server" "C:\D\Program Files\COMSOL\COMSOL62\Multiphysics\bin\win64\comsolmphserver.exe" -port 2036 -multi on -graphics

echo 等待服务器启动...
timeout /t 10 /nobreak > nul

echo.
echo [2/2] 启动 COMSOL Desktop...
start "COMSOL Desktop" "C:\D\Program Files\COMSOL\COMSOL62\Multiphysics\bin\win64\comsolmphclient.exe" -host 127.0.0.1 -port 2036

echo.
echo ========================================
echo   启动完成！
echo   服务器端口: 2036
echo   请等待 Desktop 完全打开后运行 Python 脚本
echo ========================================
pause
```

---

## 九、注意事项

1. **严格按顺序启动**：先服务器，再 Desktop，再 Python
2. **端口一致**：服务器、Desktop、Python 必须使用相同的端口号
3. **不要创建新模型**：始终使用 `java.model('Model1')` 获取 Desktop 的模型
4. **⚠️ 启用进度显示（重要！）**：
   - 服务器必须带 `-graphics` 参数启动
   - Python 代码中必须调用 `java.showProgress(True)` 和 `java.showPlots(True)`
   - 必须在 `model.study('std1').run()` 之前调用
   - 详见第九章"计算进度窗口详解"
5. **绘图不要调用 .run()**：创建绘图组后不要调用 `.run()`，让用户在 Desktop 中点击查看
6. **JPype 导入时机**：必须在 `mph.Client()` 连接之后再导入 JPype 的 JArray、JString 等

---

## 九、计算进度窗口详解

### 9.1 什么是计算进度窗口

当 COMSOL 求解器运行时，会弹出一个**进度窗口**，显示：
- 当前计算阶段（编译方程、网格划分、求解等）
- 迭代次数和收敛信息
- 内存使用情况
- 计算时间
- 详细的求解器日志

这是 COMSOL Desktop 的原生功能，与 GUI 手动操作时看到的完全相同。

### 9.2 如何启用进度窗口

**必须同时满足两个条件：**

#### 条件 1：服务器必须带 `-graphics` 参数启动

```powershell
# ✅ 正确：带 -graphics 参数
comsolmphserver.exe -port 2036 -multi on -graphics

# ❌ 错误：没有 -graphics 参数（不会显示进度窗口）
comsolmphserver.exe -port 2036 -multi on
```

#### 条件 2：Python 代码中必须调用 `showProgress(True)`

```python
# 连接服务器
client = mph.Client(port=2036, host='localhost')
java = client.java

# ✅ 必须在求解前调用！
java.showProgress(True)
java.showPlots(True)

# 然后才能求解
model.study('std1').run()  # 这时会显示进度窗口
```

### 9.3 进度窗口显示的内容

进度窗口会显示以下信息：

```
顶点单元数：1662
边单元数：84
边界单元数：672
单元数：1662
最小单元质量：0.295

<---- 研究 1/解 1 (sol1) 中的"编译方程: 稳态" --------------------
开始于 2026年8月31日 下午6:35:15。
几何形函数: 二次拉格朗日单元
在 Intel64 Family 6 Model 183 Stepping 1, GenuineIntel 上运行。
在以下位置使用 1 个插槽： DESKTOP-MMK8IT2 上（共 16 个内核）。
可用内存：32.58 GB。
时间：2。
物理内存: 1.05 GB
虚拟内存: 1.09 GB
结束时间：2026年8月31日 下午6:35:17。

<---- 研究 1/解 1 (sol1) 中的"稳态求解器 1" --------------------
开始于 2026年8月31日 下午6:35:17。
线性求解器 
求解的自由度数：2935（加上 1518 个内部自由度）。
找到对称矩阵。
缩放因变量：
温度 (comp1.T): 2.9e+02
已使用正交零空间函数。
Iter      SolEst     Damping    Stepsize #Res #Jac #Sol   LinErr   LinRes
   1        0.52   1.0000000        0.52    1    1    1  5.1e-14  4.1e-13
求解时间：0 s。
物理内存: 1.07 GB
虚拟内存: 1.17 GB
结束时间：2026年8月31日 下午6:35:17。
```

### 9.4 完整示例代码

```python
"""
完整示例：带进度窗口的求解过程
"""
import mph
import time

# 连接服务器
client = mph.Client(port=2036, host='localhost')
from jpype import JArray, JString, JInt
StringArray = JArray(JString)
IntArray = JArray(JInt)

java = client.java

# ✅ 关键：启用进度显示（必须在求解前调用！）
java.showProgress(True)
java.showPlots(True)

# 获取 Desktop 的 Model1
model = java.model('Model1')

# ... 创建几何、材料、物理场、网格 ...

# 求解（会显示进度窗口）
print('开始求解...')
start = time.time()
model.study('std1').run()
elapsed = time.time() - start
print(f'求解完成！耗时 {elapsed:.1f} 秒')
```

### 9.5 常见问题

**问题 1：求解时没有进度窗口**

检查：
1. 服务器是否带 `-graphics` 参数启动？
2. Python 代码中是否调用了 `java.showProgress(True)`？
3. `showProgress(True)` 是否在 `model.study('std1').run()` 之前调用？

**问题 2：进度窗口一闪而过**

这是正常的。如果模型很简单（单元数少），求解会在几秒内完成，进度窗口会自动关闭。

**问题 3：进度窗口显示但内容不完整**

可能原因：
- 求解器日志级别设置为"简要"（默认）
- 可以在 COMSOL Desktop 中调整日志详细程度

### 9.6 与 GUI 操作的对比

| 特性 | GUI 手动操作 | Python API 自动化 |
|------|-------------|------------------|
| 进度窗口 | ✅ 自动显示 | ✅ 需要 `showProgress(True)` |
| 日志内容 | ✅ 完整显示 | ✅ 完整显示（相同内容） |
| 计算时间 | ✅ 可见 | ✅ 可见 |
| 结果显示 | ✅ 自动更新 | ✅ 需要创建绘图组 |

**关键区别**：GUI 操作时进度窗口自动显示，Python API 需要显式调用 `showProgress(True)`。

---

## 十、技术参考

### 相关文档
- [COMSOL API 文档](https://doc.comsol.com/)
- [MPh Python 库文档](https://mph.readthedocs.io/)
- [JPype 文档](https://jpype.readthedocs.io/)

### 关键 API
- `ModelUtil.showProgress(boolean)` - 启用/禁用进度显示
- `ModelUtil.showPlots(boolean)` - 启用/禁用绘图显示
- `ModelUtil.closeWindows()` - 关闭所有绘图窗口
- `ModelUtil.model(tag)` - 获取指定标签的模型
- `ModelUtil.tags()` - 获取所有模型标签列表

### 项目文件
- `E:\优化\api\` - 项目根目录
- `E:\优化\api\workflow_heat.py` - 基础热传导工作流
- `E:\优化\api\workflow_parametric.py` - 参数化扫描示例
- `E:\优化\api\workflow_complex2.py` - 复杂模型示例
- `E:\优化\api\test_progress.py` - 进度窗口测试

---

## 十一、部署包说明

### 11.1 部署包内容

```
COMSOL_MCP_部署包/
├── install.ps1                    # 自动安装脚本（管理员运行）
├── start_comsol.ps1               # COMSOL 启动脚本
├── comsol-mcp.exe                 # MCP 可执行文件
├── comsol_mcp/                    # MCP Python 包
├── docs/
│   └── COMSOL_Desktop_实时同步自动化操作_说明文档.md
└── examples/
    ├── parametric_sweep.py        # 参数化扫描示例
    ├── create_flow.py             # 流体模型示例
    ├── workflow_heat.py           # 热传导示例
    └── workflow_parametric.py     # 参数化研究示例
```

### 11.2 部署步骤

#### 方法一：自动安装（推荐）

1. 解压 `COMSOL_MCP_部署包.zip`
2. 以**管理员身份**运行 `install.ps1`
3. 按提示输入 COMSOL 安装路径（默认 `C:\Program Files\COMSOL\COMSOL62\Multiphysics`）
4. 运行 `start_comsol.ps1` 启动服务
5. 打开 OpenCode，说："帮我创建一个 COMSOL 热传导模型"

#### 方法二：手动安装

```powershell
# 1. 安装 Python 依赖
pip install mph jpype1

# 2. 安装 COMSOL MCP
cd COMSOL_MCP_部署包
pip install -e comsol_mcp

# 3. 配置 OpenCode（添加到 ~/.config/opencode/opencode.json）
# 参考 README.md 中的配置说明

# 4. 启动 COMSOL 服务器
& "C:\Program Files\COMSOL\COMSOL62\Multiphysics\bin\win64\comsolmphserver.exe" -port 2036 -multi on -graphics

# 5. 启动 Desktop
& "C:\Program Files\COMSOL\COMSOL62\Multiphysics\bin\win64\comsolmphclient.exe" -host 127.0.0.1 -port 2036
```

### 11.3 系统要求

| 要求 | 最低配置 | 推荐配置 |
|------|---------|---------|
| 操作系统 | Windows 10 64位 | Windows 11 64位 |
| COMSOL | 6.2 | 6.2+ |
| Python | 3.10 | 3.12 |
| 内存 | 8 GB | 16 GB+ |
| 磁盘空间 | 500 MB | 1 GB+ |

### 11.4 验证安装

部署完成后，在 OpenCode 中测试：

```
用户: 帮我创建一个简单的热传导模型
AI: [自动启动服务器和Desktop，创建模型...]
用户: [在Desktop中看到实时操作过程]
```

**预期结果：**
- Desktop 自动打开
- 看到几何创建过程
- 看到材料添加过程
- 看到物理场设置过程
- 看到网格划分过程
- 看到计算进度窗口
- 看到结果云图

### 11.5 常见部署问题

**问题1：install.ps1 提示"需要管理员权限"**
- 解决：右键 PowerShell → "以管理员身份运行"

**问题2：COMSOL 路径不正确**
- 解决：修改 `install.ps1` 中的 `$ComsolPath` 参数

**问题3：端口 2036 被占用**
- 解决：修改 `start_comsol.ps1` 中的端口号，保持一致即可

---

**文档版本**：v1.1  
**最后更新**：2026年8月31日  
**适用环境**：COMSOL 6.2 + Python 3.12 + MPh 1.4.0
