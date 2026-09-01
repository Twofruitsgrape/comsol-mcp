# COMSOL 使用指南

## 概述

当用户提到 "COMSOL"、"仿真"、"传热"、"流体"、"耦合"、"探针"、"参数化" 等关键词时，使用此指南。

## 工作流程

**启动 COMSOL，使用 Python 脚本进行 [仿真类型] 仿真。**

### 工作模式：

1. **运行 start_comsol.bat 启动 COMSOL**
   - 启动 COMSOL Server（端口 2036）
   - 启动 COMSOL Desktop（连接到 Server）

2. **Python 脚本连接 Server 执行所有操作**
   - 创建模型和几何
   - 设置材料和物理场
   - 划分网格
   - 求解（Desktop 实时显示进度窗口）
   - 生成结果图（Desktop 实时显示）
   - 保存模型文件

3. **所有操作自动在 Desktop 中实时显示（无需关闭/重新打开）**

### 仿真参数（用户提供）：
- 几何：[几何描述]
- 材料：[材料名称和属性]
- 物理场：[物理场类型和边界条件]
- 求解类型：[稳态/瞬态]
- 探针：[需要监测的物理量]

### 保存路径：
`models/[模型名称].mph`

### 关键点

- **不要关闭 Desktop**：Desktop 一直保持打开状态
- **不要重新打开 Desktop**：所有操作实时显示
- **实时同步**：Python 操作 Server 时，Desktop 自动刷新

## 创建模型

### 几何
```python
# 2D 几何
model.geom().create('geom1', 2)
model.geom('geom1').feature().create('r1', 'Rectangle')
model.geom('geom1').feature('r1').set('size', ['1', '0.1'])
model.geom('geom1').run()

# 3D 几何
model.geom().create('geom1', 3)
model.geom('geom1').feature().create('blk1', 'Block')
model.geom('geom1').feature('blk1').set('size', ['0.1', '0.1', '0.1'])
model.geom('geom1').run()
```

### 材料
```python
mat = model.component('comp1').material().create('mat1', 'Common')
mat.label('Water')
mat.selection().all()
mat.propertyGroup('def').set('density', '1000')
mat.propertyGroup('def').set('dynamicviscosity', '0.001')
mat.propertyGroup('def').set('thermalconductivity', '0.6')
mat.propertyGroup('def').set('heatcapacity', '4186')
```

### 物理场
```python
# 层流
spf = model.component('comp1').physics().create('spf', 'LaminarFlow', 'geom1')
spf.feature().create('inl1', 'InletBoundary', 1)
spf.feature('inl1').set('U0in', '0.1')
spf.feature().create('out1', 'OutletBoundary', 1)
spf.feature('out1').set('p0', '0')

# 传热
ht = model.component('comp1').physics().create('ht', 'HeatTransfer', 'geom1')
ht.feature('init1').set('Tinit', '293.15')
ht.feature().create('temp1', 'TemperatureBoundary', 1)
ht.feature('temp1').set('T0', '373.15')
```

### 网格
```python
model.component('comp1').mesh().create('mesh1')
model.component('comp1').mesh('mesh1').run()
```

### 求解
```python
# 稳态
model.study().create('std1')
model.study('std1').create('stat', 'Stationary')
model.study('std1').run()

# 瞬态
model.study().create('std1')
model.study('std1').create('time', 'Transient')
model.study('std1').feature('time').set('tlist', 'range(0,0.1,10)')
model.study('std1').run()
```

### 探针
```python
# 域探针
model.component('comp1').probe().create('prb1', 'Domain')
model.component('comp1').probe('prb1').set('expr', 'T')
model.component('comp1').probe('prb1').set('descr', '平均温度')
```

### 结果绘图
```python
# 2D 云图
model.result().create('pg1', 'PlotGroup2D')
model.result('pg1').create('surf1', 'Surface')
model.result('pg1').feature('surf1').set('expr', 'T')
model.result('pg1').set('window', 'graphics')

# 3D 云图
model.result().create('pg1', 'PlotGroup3D')
model.result('pg1').create('surf1', 'Surface')
model.result('pg1').feature('surf1').set('expr', 'T')
model.result('pg1').set('window', 'graphics')
```

### 保存
```python
model.save("my_model.mph")
```

## 完整示例

```python
import mph
import time

# 连接
client = mph.Client(port=2036, host='localhost')
from jpype import JArray, JString, JInt
StringArray = JArray(JString)
IntArray = JArray(JInt)

java = client.java
java.showProgress(True)
java.showPlots(True)
model = java.model('Model1')

# 清理
for feat in ['comp1']:
    try: model.component().remove(feat)
    except: pass

# 创建几何
model.modelNode().create('comp1')
model.geom().create('geom1', 2)
model.geom('geom1').feature().create('r1', 'Rectangle')
model.geom('geom1').feature('r1').set('size', StringArray(['1', '0.1']))
model.geom('geom1').run()

# 添加材料
mat = model.component('comp1').material().create('mat1', 'Common')
mat.label('Water')
mat.selection().all()
mat.propertyGroup('def').set('density', '1000')
mat.propertyGroup('def').set('dynamicviscosity', '0.001')

# 设置物理场
spf = model.component('comp1').physics().create('spf', 'LaminarFlow', 'geom1')
spf.feature().create('inl1', 'InletBoundary', 1)
spf.feature('inl1').selection().set(IntArray([1]))
spf.feature('inl1').set('U0in', '0.1')
spf.feature().create('out1', 'OutletBoundary', 1)
spf.feature('out1').selection().set(IntArray([3]))
spf.feature('out1').set('p0', '0')

# 划分网格
model.component('comp1').mesh().create('mesh1')
model.component('comp1').mesh('mesh1').run()

# 求解
model.study().create('std1')
model.study('std1').create('stat', 'Stationary')
model.study('std1').run()

# 保存
model.save("my_model.mph")
```

## 注意事项

1. **启动顺序**: 先运行 start_comsol.bat，等待 15-20 秒
2. **实时显示**: 所有操作自动在 Desktop 中显示
3. **进度窗口**: 调用 `java.showProgress(True)` 启用
4. **探针类型**: 使用 `Domain` 类型（不是 `Boundary`）
5. **数组参数**: 使用 `StringArray` 和 `IntArray` 包装
6. **清理现有内容**: 创建前先清理 `comp1`、`std1` 等
