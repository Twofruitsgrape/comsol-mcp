"""
COMSOL 传热示例 - 实时显示版本
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
print("\n[1/7] 清理现有内容...")
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
print("\n[2/7] 创建几何 (0.1m x 0.1m x 0.1m 立方体)...")
model.modelNode().create('comp1')
model.geom().create('geom1', 3)
model.geom('geom1').feature().create('blk1', 'Block')
model.geom('geom1').feature('blk1').set('size', StringArray(['0.1', '0.1', '0.1']))
model.geom('geom1').feature('blk1').set('base', 'center')
model.geom('geom1').run()
print("  几何构建完成")
time.sleep(2)

# 添加材料
print("\n[3/7] 添加铜材料...")
mat = model.component('comp1').material().create('mat1', 'Common')
mat.label('Copper')
mat.selection().all()
mat.propertyGroup('def').set('thermalconductivity', '400')
mat.propertyGroup('def').set('density', '8960')
mat.propertyGroup('def').set('heatcapacity', '385')
print("  铜材料添加完成")
time.sleep(2)

# 设置物理场
print("\n[4/7] 设置传热物理场...")
ht = model.component('comp1').physics().create('ht', 'HeatTransfer', 'geom1')

# 底面恒温 100°C
ht.feature().create('temp1', 'TemperatureBoundary', 2)
ht.feature('temp1').selection().set(IntArray([1]))
ht.feature('temp1').set('T0', '373.15')
print("  底面: 100°C 恒温")

# 顶面恒温 20°C
ht.feature().create('temp2', 'TemperatureBoundary', 2)
ht.feature('temp2').selection().set(IntArray([6]))
ht.feature('temp2').set('T0', '293.15')
print("  顶面: 20°C 恒温")

# 内部热源
ht.feature().create('hs1', 'HeatSource', 3)
ht.feature('hs1').selection().all()
ht.feature('hs1').set('Q0', '1e6')
print("  内部热源: 1 MW/m^3")
time.sleep(2)

# 划分网格
print("\n[5/7] 划分网格...")
model.component('comp1').mesh().create('mesh1')
model.component('comp1').mesh('mesh1').run()
print("  网格划分完成")
time.sleep(3)

# 求解
print("\n[6/7] 求解计算...")
model.study().create('std1')
model.study('std1').create('stat', 'Stationary')
print("  开始求解 (Desktop 将显示进度窗口)...")
start = time.time()
model.study('std1').run()
elapsed = time.time() - start
print(f"  求解完成! 耗时 {elapsed:.1f} 秒")

# 创建结果图
print("\n[7/7] 创建结果绘图...")
java.closeWindows()

model.result().create('pg1', 'PlotGroup3D')
model.result('pg1').create('surf1', 'Surface')
model.result('pg1').feature('surf1').set('expr', 'T')
model.result('pg1').feature('surf1').set('unit', 'K')
model.result('pg1').set('window', 'graphics')
print("  温度云图创建完成")

# 保存
model.save("heat_transfer_example.mph")
print("\n模型已保存: heat_transfer_example.mph")

print("\n" + "="*50)
print("传热示例完成!")
print("="*50)
print("请在 Desktop 中查看:")
print("  - Study 1: 求解结果")
print("  - 3D Plot Group 1: 温度云图")
print("="*50)
