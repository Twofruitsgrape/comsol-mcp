"""
COMSOL 瞬态传热+探针示例 - 实时显示版本
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
print("\n[1/9] 清理现有内容...")
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
print("\n[2/9] 创建几何 (金属板 1m x 0.5m x 0.02m)...")
model.modelNode().create('comp1')
model.geom().create('geom1', 3)
model.geom('geom1').feature().create('blk1', 'Block')
model.geom('geom1').feature('blk1').set('size', StringArray(['1', '0.5', '0.02']))
model.geom('geom1').feature('blk1').set('base', 'center')
model.geom('geom1').run()
print("  几何构建完成 (金属板)")
time.sleep(2)

# 添加材料
print("\n[3/9] 添加钢材料...")
mat = model.component('comp1').material().create('mat1', 'Common')
mat.label('Steel')
mat.selection().all()
mat.propertyGroup('def').set('thermalconductivity', '50')
mat.propertyGroup('def').set('density', '7800')
mat.propertyGroup('def').set('heatcapacity', '500')
print("  钢材料添加完成")
print("    - 热导率: 50 W/(m*K)")
print("    - 密度: 7800 kg/m^3")
print("    - 比热容: 500 J/(kg*K)")
time.sleep(2)

# 设置物理场
print("\n[4/9] 设置传热物理场...")
ht = model.component('comp1').physics().create('ht', 'HeatTransfer', 'geom1')

# 初始温度 20°C
ht.feature('init1').set('Tinit', '293.15')
print("  初始温度: 20°C")

# 左侧面: 随时间变化的热源 (脉冲加热)
ht.feature().create('hf1', 'HeatFluxBoundary', 2)
ht.feature('hf1').selection().set(IntArray([4]))
ht.feature('hf1').set('HeatFluxType', 'HeatRate')
ht.feature('hf1').set('P0', '1000*sin(2*pi*0.5*t)+1000')
print("  左侧面: 脉冲热源 P = 1000 + 1000*sin(pi*t) W")

# 右侧面: 对流冷却
ht.feature().create('hf2', 'HeatFluxBoundary', 2)
ht.feature('hf2').selection().set(IntArray([2]))
ht.feature('hf2').set('HeatFluxType', 'ConvectiveHeatFlux')
ht.feature('hf2').set('h', '50')
ht.feature('hf2').set('Text', '293.15')
print("  右侧面: 对流冷却 h=50 W/(m^2*K), T_env=20°C")

# 上下面: 绝热 (默认)
print("  上下面: 绝热 (默认)")
time.sleep(2)

# 创建探针
print("\n[5/9] 创建温度探针...")

# 清理现有探针
for prb in ['prb1', 'prb2', 'prb3']:
    try:
        model.component('comp1').probe().remove(prb)
    except:
        pass

# 探针1: 全域平均温度
model.component('comp1').probe().create('prb1', 'Domain')
model.component('comp1').probe('prb1').set('expr', 'T')
model.component('comp1').probe('prb1').set('descr', '平均温度')
print("  探针1: 全域平均温度")

# 探针2: 全域平均速度 (如果有流体)
model.component('comp1').probe().create('prb2', 'Domain')
model.component('comp1').probe('prb2').set('expr', 'T')
model.component('comp1').probe('prb2').set('descr', '平均温度2')
print("  探针2: 全域平均温度2")

# 探针3: 温度变化率
model.component('comp1').probe().create('prb3', 'Domain')
model.component('comp1').probe('prb3').set('expr', 'ht.tt')
model.component('comp1').probe('prb3').set('descr', '温度变化率')
print("  探针3: 温度变化率")

time.sleep(2)

# 划分网格
print("\n[6/9] 划分网格...")
model.component('comp1').mesh().create('mesh1')
model.component('comp1').mesh('mesh1').run()
print("  网格划分完成")
time.sleep(3)

# 创建瞬态研究
print("\n[7/9] 创建瞬态研究...")
model.study().create('std1')
model.study('std1').create('time', 'Transient')
model.study('std1').feature('time').set('tlist', 'range(0,0.1,10)')
print("  瞬态研究: 0-10秒, 步长0.1秒")
print("  共101个时间步")
time.sleep(2)

# 求解
print("\n[8/9] 求解瞬态分析...")
print("  开始求解 (Desktop 将显示进度窗口)...")
print("  这将需要更长时间，因为是瞬态分析...")
start = time.time()
model.study('std1').run()
elapsed = time.time() - start
print(f"  求解完成! 耗时 {elapsed:.1f} 秒")

# 创建动画和结果图
print("\n[9/9] 创建结果绘图和动画...")
java.closeWindows()

# 温度云图 (动画)
model.result().create('pg1', 'PlotGroup3D')
model.result('pg1').create('surf1', 'Surface')
model.result('pg1').feature('surf1').set('expr', 'T')
model.result('pg1').feature('surf1').set('unit', 'K')
model.result('pg1').set('window', 'graphics')
print("  温度云图创建完成 (可播放动画)")

# 保存
model.save("transient_probe_example.mph")
print("  模型已保存: transient_probe_example.mph")

print("\n" + "="*60)
print("瞬态传热+探针示例完成!")
print("="*60)
print("")
print("模型参数:")
print("  - 几何: 1m x 0.5m x 0.02m 金属板")
print("  - 材料: 钢 (k=50, rho=7800, cp=500)")
print("  - 初始温度: 20°C")
print("  - 左侧面: 脉冲热源 P=1000+1000*sin(pi*t) W")
print("  - 右侧面: 对流冷却 h=50 W/(m^2*K)")
print("  - 仿真时间: 0-10秒, 步长0.1秒")
print("")
print("探针监测:")
print("  - 探针1: 平均温度")
print("  - 探针2: 平均温度2")
print("  - 探针3: 温度变化率")
print("")
print("请在 Desktop 中查看:")
print("  - Study 1: 瞬态求解结果")
print("  - 探针: 温度随时间变化曲线")
print("  - 3D Plot Group 1: 温度云图动画")
print("  - 右键点击 '3D Plot Group 1' -> '播放' 查看动画")
print("="*60)
