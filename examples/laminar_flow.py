"""
COMSOL 层流示例 - 实时显示版本
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
print("\n[2/7] 创建几何 (1m x 0.1m 管道)...")
model.modelNode().create('comp1')
model.geom().create('geom1', 2)
model.geom('geom1').feature().create('r1', 'Rectangle')
model.geom('geom1').feature('r1').set('size', StringArray(['1', '0.1']))
model.geom('geom1').feature('r1').set('base', 'corner')
model.geom('geom1').feature('r1').set('pos', StringArray(['0', '0']))
model.geom('geom1').run()
print("  几何构建完成")
time.sleep(2)

# 添加材料
print("\n[3/7] 添加水材料...")
mat = model.component('comp1').material().create('mat1', 'Common')
mat.label('Water')
mat.selection().all()
mat.propertyGroup('def').set('density', '1000')
mat.propertyGroup('def').set('dynamicviscosity', '0.001')
print("  水材料添加完成")
time.sleep(2)

# 设置物理场
print("\n[4/7] 设置层流物理场...")
spf = model.component('comp1').physics().create('spf', 'LaminarFlow', 'geom1')

# 入口
spf.feature().create('inl1', 'InletBoundary', 1)
spf.feature('inl1').selection().set(IntArray([1]))
spf.feature('inl1').set('U0in', '0.1')
print("  入口: 0.1 m/s")

# 出口
spf.feature().create('out1', 'OutletBoundary', 1)
spf.feature('out1').selection().set(IntArray([3]))
spf.feature('out1').set('p0', '0')
print("  出口: 0 Pa")
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

model.result().create('pg1', 'PlotGroup2D')
model.result('pg1').create('surf1', 'Surface')
model.result('pg1').feature('surf1').set('expr', 'spf.U')
model.result('pg1').feature('surf1').set('unit', 'm/s')
model.result('pg1').set('window', 'graphics')
print("  速度云图创建完成")

# 保存
model.save("laminar_flow_example.mph")
print("\n模型已保存: laminar_flow_example.mph")

print("\n" + "="*50)
print("层流示例完成!")
print("="*50)
print("请在 Desktop 中查看:")
print("  - Study 1: 求解结果")
print("  - 2D Plot Group 1: 速度云图")
print("="*50)
