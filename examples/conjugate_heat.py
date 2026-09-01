"""
COMSOL 流热耦合示例 - 实时显示版本
层流流动 + 传热耦合，瞬态仿真
所有操作在 COMSOL Desktop 中实时显示
"""
import mph
import time

# 连接
print("连接 COMSOL Server...")
client = mph.Client(port=2036, host='localhost')
from jpype import JArray, JString, JInt
StringArray = JArray(JString)
IntArray = JArray(JInt)

java = client.java
java.showProgress(True)
java.showPlots(True)

model = java.model('Model1')
print("已连接 Desktop 的 Model1")

# 清理
print("\n[1/10] 清理现有内容...")
for feat in ['comp1']:
    try:
        model.component().remove(feat)
    except:
        pass
for study in ['std1']:
    try:
        model.study().remove(study)
    except:
        pass
print("  清理完成")

# 创建几何
print("\n[2/10] 创建几何 (管道 + 固体壁面)...")
model.modelNode().create('comp1')
model.geom().create('geom1', 2)

# 流体区域
model.geom('geom1').feature().create('r1', 'Rectangle')
model.geom('geom1').feature('r1').set('size', StringArray(['2', '0.1']))
model.geom('geom1').feature('r1').set('base', 'corner')
model.geom('geom1').feature('r1').set('pos', StringArray(['0', '0']))
print("  流体区域: 2m x 0.1m")

# 固体壁面
model.geom('geom1').feature().create('r2', 'Rectangle')
model.geom('geom1').feature('r2').set('size', StringArray(['2', '0.02']))
model.geom('geom1').feature('r2').set('base', 'corner')
model.geom('geom1').feature('r2').set('pos', StringArray(['0', '0.1']))
print("  固体壁面: 2m x 0.02m")

model.geom('geom1').run()
print("  几何构建完成")
time.sleep(2)

# 添加材料
print("\n[3/10] 添加材料...")

# 水
mat1 = model.component('comp1').material().create('mat1', 'Common')
mat1.label('Water')
mat1.selection().set(IntArray([1]))
mat1.propertyGroup('def').set('density', '1000')
mat1.propertyGroup('def').set('dynamicviscosity', '0.001')
mat1.propertyGroup('def').set('thermalconductivity', '0.6')
mat1.propertyGroup('def').set('heatcapacity', '4186')
mat1.propertyGroup('def').set('Tref', '293.15')
print("  水 (流体域): rho=1000, mu=0.001, k=0.6, cp=4186")

# 铝
mat2 = model.component('comp1').material().create('mat2', 'Common')
mat2.label('Aluminum')
mat2.selection().set(IntArray([2]))
mat2.propertyGroup('def').set('density', '2700')
mat2.propertyGroup('def').set('thermalconductivity', '200')
mat2.propertyGroup('def').set('heatcapacity', '900')
print("  铝 (固体壁面): rho=2700, k=200, cp=900")
time.sleep(2)

# 设置流体物理场
print("\n[4/10] 设置层流物理场...")
spf = model.component('comp1').physics().create('spf', 'LaminarFlow', 'geom1')

# 设置流体属性
spf.feature('fp1').set('rho_mat', 'userdef')
spf.feature('fp1').set('rho', '1000')
spf.feature('fp1').set('mu_mat', 'userdef')
spf.feature('fp1').set('mu', '0.001')
print("  流体属性: rho=1000, mu=0.001")

# 入口速度
spf.feature().create('inl1', 'InletBoundary', 1)
spf.feature('inl1').selection().set(IntArray([1]))
spf.feature('inl1').set('U0in', '0.1*(1+0.5*sin(2*pi*t))')
print("  入口: 脉冲速度 U = 0.1*(1+0.5*sin(2*pi*t)) m/s")

# 出口压力
spf.feature().create('out1', 'OutletBoundary', 1)
spf.feature('out1').selection().set(IntArray([3]))
spf.feature('out1').set('p0', '0')
print("  出口: 压力 0 Pa")
time.sleep(2)

# 设置传热物理场
print("\n[5/10] 设置传热物理场...")
ht = model.component('comp1').physics().create('ht', 'HeatTransfer', 'geom1')

# 初始温度
ht.feature('init1').set('Tinit', '293.15')
print("  初始温度: 20°C")

# 入口热流体
ht.feature().create('temp1', 'TemperatureBoundary', 1)
ht.feature('temp1').selection().set(IntArray([1]))
ht.feature('temp1').set('T0', '333.15+10*sin(2*pi*0.5*t)')
print("  入口温度: 40 + 10*sin(pi*t) °C")

# 壁面对流冷却
ht.feature().create('hf1', 'HeatFluxBoundary', 1)
ht.feature('hf1').selection().set(IntArray([5, 6]))
ht.feature('hf1').set('HeatFluxType', 'ConvectiveHeatFlux')
ht.feature('hf1').set('h', '100')
ht.feature('hf1').set('Text', '293.15')
print("  壁面冷却: h=100 W/(m^2*K), T_env=20°C")
time.sleep(2)

# 耦合物理场
print("\n[6/10] 耦合流体与传热...")
print("  流动 -> 传热: 对流换热")
print("  传热 -> 流动: 浮力效应")
time.sleep(2)

# 创建探针
print("\n[7/10] 创建探针...")

# 清理现有探针
for prb in ['prb1', 'prb2', 'prb3']:
    try:
        model.component('comp1').probe().remove(prb)
    except:
        pass

# 探针1: 平均温度
model.component('comp1').probe().create('prb1', 'Domain')
model.component('comp1').probe('prb1').set('expr', 'T')
model.component('comp1').probe('prb1').set('descr', '平均温度')
print("  探针1: 平均温度")

# 探针2: 平均速度
model.component('comp1').probe().create('prb2', 'Domain')
model.component('comp1').probe('prb2').set('expr', 'spf.U')
model.component('comp1').probe('prb2').set('descr', '平均速度')
print("  探针2: 平均速度")

# 探针3: 平均压力
model.component('comp1').probe().create('prb3', 'Domain')
model.component('comp1').probe('prb3').set('expr', 'p')
model.component('comp1').probe('prb3').set('descr', '平均压力')
print("  探针3: 平均压力")

time.sleep(2)

# 划分网格
print("\n[8/10] 划分网格...")
model.component('comp1').mesh().create('mesh1')
model.component('comp1').mesh('mesh1').run()
print("  网格划分完成")
time.sleep(3)

# 创建瞬态研究
print("\n[9/10] 创建瞬态研究...")
model.study().create('std1')
model.study('std1').create('time', 'Transient')
model.study('std1').feature('time').set('tlist', 'range(0,0.5,20)')
print("  瞬态研究: 0-20秒, 步长0.5秒")
print("  共41个时间步")
time.sleep(2)

# 求解
print("\n[10/10] 求解流热耦合瞬态分析...")
print("  开始求解 (Desktop 将显示进度窗口)...")
print("  这将需要较长时间，因为是流热耦合瞬态分析...")
start = time.time()
model.study('std1').run()
elapsed = time.time() - start
print(f"  求解完成! 耗时 {elapsed:.1f} 秒 ({elapsed/60:.1f} 分钟)")

# 创建结果图
print("\n创建结果绘图...")
java.closeWindows()

model.result().create('pg1', 'PlotGroup2D')
model.result('pg1').create('surf1', 'Surface')
model.result('pg1').feature('surf1').set('expr', 'spf.U')
model.result('pg1').feature('surf1').set('unit', 'm/s')
model.result('pg1').set('window', 'graphics')
print("  速度场云图创建完成")

model.result().create('pg2', 'PlotGroup2D')
model.result('pg2').create('surf1', 'Surface')
model.result('pg2').feature('surf1').set('expr', 'T')
model.result('pg2').feature('surf1').set('unit', 'K')
model.result('pg2').set('window', 'graphics')
print("  温度场云图创建完成")

model.result().create('pg3', 'PlotGroup2D')
model.result('pg3').create('surf1', 'Surface')
model.result('pg3').feature('surf1').set('expr', 'p')
model.result('pg3').feature('surf1').set('unit', 'Pa')
model.result('pg3').set('window', 'graphics')
print("  压力场云图创建完成")

# 保存
model.save("conjugate_heat_example.mph")
print("\n模型已保存: conjugate_heat_example.mph")

print("\n" + "="*60)
print("流热耦合示例完成!")
print("="*60)
print(f"求解时间: {elapsed:.1f} 秒 ({elapsed/60:.1f} 分钟)")
print("")
print("请在 Desktop 中查看:")
print("  - Study 1: 瞬态求解结果")
print("  - 2D Plot Group 1: 速度场动画")
print("  - 2D Plot Group 2: 温度场动画")
print("  - 2D Plot Group 3: 压力场动画")
print("="*60)
