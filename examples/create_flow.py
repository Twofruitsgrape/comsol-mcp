"""
创建简单射流模型 flow1.mph（简化版）
包含：几何、流体材料、层流物理场、网格、求解、保存
"""
import mph
import time

# 连接服务器
client = mph.Client(port=2036, host='localhost')
from jpype import JArray, JString, JInt
StringArray = JArray(JString)
IntArray = JArray(JInt)

java = client.java
java.showProgress(True)
print('已连接到服务器')

# 获取 Desktop 的 Model1
model = java.model('Model1')
print('已获取 Model1')

# ============================================================
# 清理现有内容
# ============================================================
print('\n[清理] 清除现有内容...')
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
for pg in ['pg1', 'pg2', 'pg3']:
    try:
        model.result().remove(pg)
    except:
        pass
print('  清理完成')

# ============================================================
# 步骤 1：创建 2D 几何（简单射流区域）
# ============================================================
print('\n[步骤 1] 创建 2D 射流几何...')

# 创建组件
model.modelNode().create('comp1')

# 创建 2D 几何
model.geom().create('geom1', 2)

# 主流动区域（长方形）5m x 1m
model.geom('geom1').feature().create('r1', 'Rectangle')
model.geom('geom1').feature('r1').set('size', StringArray(['5', '1']))
model.geom('geom1').feature('r1').set('base', 'corner')
model.geom('geom1').feature('r1').set('pos', StringArray(['0', '0']))

model.geom('geom1').run()
print('  几何构建完成（5m x 1m 管道）')
time.sleep(2)

# ============================================================
# 步骤 2：添加材料（水）
# ============================================================
print('\n[步骤 2] 添加材料（水）...')

mat = model.component('comp1').material().create('mat1', 'Common')
mat.label('水')
mat.selection().all()

# 水的物理属性
mat.propertyGroup('def').set('density', '1000')           # 密度 kg/m3
mat.propertyGroup('def').set('dynamicviscosity', '0.001')  # 动力粘度 Pa*s
print('  水材料添加完成')
time.sleep(2)

# ============================================================
# 步骤 3：设置物理场（层流）
# ============================================================
print('\n[步骤 3] 设置层流物理场...')

# 创建层流物理场
spf = model.component('comp1').physics().create('spf', 'LaminarFlow', 'geom1')

# 入口边界条件 - 速度入口（左侧）
spf.feature().create('inl1', 'InletBoundary', 1)
spf.feature('inl1').selection().set(IntArray([1]))  # 左边界
spf.feature('inl1').set('U0in', '1')  # 入口速度 1 m/s
print('  入口: 速度 1 m/s')

# 出口边界条件 - 压力出口（右侧）
spf.feature().create('out1', 'OutletBoundary', 1)
spf.feature('out1').selection().set(IntArray([3]))  # 右边界
spf.feature('out1').set('p0', '0')  # 压力 0 Pa
print('  出口: 压力 0 Pa')

# 壁面边界条件（默认无滑移，无需额外设置）
print('  壁面: 默认无滑移条件')

time.sleep(2)

# ============================================================
# 步骤 4：划分网格
# ============================================================
print('\n[步骤 4] 划分网格...')

model.component('comp1').mesh().create('mesh1')

# 使用自由三角形网格
model.component('comp1').mesh('mesh1').create('ftri1', 'FreeTri')

# 设置网格尺寸
model.component('comp1').mesh('mesh1').feature('size').set('hauto', '4')  # 中等网格

model.component('comp1').mesh('mesh1').run()
print('  网格划分完成')
time.sleep(3)

# ============================================================
# 步骤 5：求解计算
# ============================================================
print('\n[步骤 5] 求解计算...')

model.study().create('std1')
model.study('std1').create('stat', 'Stationary')

start = time.time()
model.study('std1').run()
elapsed = time.time() - start
print(f'  求解完成！耗时 {elapsed:.1f} 秒')

# ============================================================
# 步骤 6：创建结果绘图
# ============================================================
print('\n[步骤 6] 创建结果绘图...')

java.closeWindows()

# 速度大小云图
model.result().create('pg1', 'PlotGroup2D')
model.result('pg1').create('con1', 'Contour')
model.result('pg1').feature('con1').set('expr', 'spf.U')
model.result('pg1').feature('con1').set('unit', 'm/s')
model.result('pg1').feature('con1').set('levels', '30')
model.result('pg1').set('window', 'graphics')
model.result('pg1').set('title', '速度分布 (m/s)')
print('  速度云图创建完成')

# 压力云图
model.result().create('pg2', 'PlotGroup2D')
model.result('pg2').create('con1', 'Contour')
model.result('pg2').feature('con1').set('expr', 'p')
model.result('pg2').feature('con1').set('unit', 'Pa')
model.result('pg2').feature('con1').set('levels', '20')
model.result('pg2').set('window', 'graphics')
model.result('pg2').set('title', '压力分布 (Pa)')
print('  压力云图创建完成')

# ============================================================
# 步骤 7：保存模型
# ============================================================
print('\n[步骤 7] 保存模型...')

save_path = 'E:/优化/api/flow1.mph'
model.save(save_path)
print(f'  模型已保存到: {save_path}')

# ============================================================
# 完成
# ============================================================
print('\n' + '='*60)
print('射流模型创建完成！')
print('='*60)
print('模型文件: flow1.mph')
print('几何: 5m x 1m 管道')
print('材料: 水 (rho=1000, mu=0.001)')
print('物理场: 层流 (Laminar Flow)')
print('边界条件:')
print('  - 入口: 速度 1 m/s')
print('  - 出口: 压力 0 Pa')
print('  - 壁面: 无滑移')
print('结果绘图:')
print('  - 速度分布云图')
print('  - 压力分布云图')
print('  - 流线图')
print('='*60)
print('请在 Desktop 中查看结果（点击各个 Plot Group）')
print('='*60)
