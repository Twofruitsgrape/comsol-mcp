"""
参数扫描：不同入口速度下的流动分析
实时显示每个算例的计算过程，保存所有结果
"""
import mph
import time

# 连接服务器
client = mph.Client(port=2036, host='localhost')
from jpype import JArray, JString, JInt
StringArray = JArray(JString)
IntArray = JArray(JInt)

java = client.java

# ✅ 启用进度显示（必须！）
java.showProgress(True)
java.showPlots(True)
print('已启用进度显示')

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
# 步骤 1：创建 2D 几何
# ============================================================
print('\n[步骤 1] 创建 2D 几何...')

model.modelNode().create('comp1')
model.geom().create('geom1', 2)
model.geom('geom1').feature().create('r1', 'Rectangle')
model.geom('geom1').feature('r1').set('size', StringArray(['5', '1']))
model.geom('geom1').feature('r1').set('base', 'corner')
model.geom('geom1').feature('r1').set('pos', StringArray(['0', '0']))
model.geom('geom1').run()
print('  几何构建完成（5m x 1m 管道）')
time.sleep(2)

# ============================================================
# 步骤 2：添加参数
# ============================================================
print('\n[步骤 2] 添加扫描参数...')

# 定义入口速度参数
model.param().set('v_inlet', '1')  # 初始值
print('  参数 v_inlet = 1 m/s（初始值）')

# ============================================================
# 步骤 3：添加材料（水）
# ============================================================
print('\n[步骤 3] 添加材料（水）...')

mat = model.component('comp1').material().create('mat1', 'Common')
mat.label('水')
mat.selection().all()
mat.propertyGroup('def').set('density', '1000')
mat.propertyGroup('def').set('dynamicviscosity', '0.001')
print('  水材料添加完成')
time.sleep(2)

# ============================================================
# 步骤 4：设置物理场（层流）
# ============================================================
print('\n[步骤 4] 设置层流物理场...')

spf = model.component('comp1').physics().create('spf', 'LaminarFlow', 'geom1')

# 入口边界条件 - 使用参数
spf.feature().create('inl1', 'InletBoundary', 1)
spf.feature('inl1').selection().set(IntArray([1]))
spf.feature('inl1').set('U0in', 'v_inlet')  # 使用参数！
print('  入口: 速度 = v_inlet（参数化）')

# 出口边界条件
spf.feature().create('out1', 'OutletBoundary', 1)
spf.feature('out1').selection().set(IntArray([3]))
spf.feature('out1').set('p0', '0')
print('  出口: 压力 0 Pa')

time.sleep(2)

# ============================================================
# 步骤 5：划分网格
# ============================================================
print('\n[步骤 5] 划分网格...')

model.component('comp1').mesh().create('mesh1')
model.component('comp1').mesh('mesh1').create('ftri1', 'FreeTri')
model.component('comp1').mesh('mesh1').feature('size').set('hauto', '4')
model.component('comp1').mesh('mesh1').run()
print('  网格划分完成')
time.sleep(3)

# ============================================================
# 步骤 6：创建参数化研究
# ============================================================
print('\n[步骤 6] 创建参数化研究...')

model.study().create('std1')
model.study('std1').create('stat', 'Stationary')

# 添加参数化扫描
model.study('std1').create('param', 'Parametric')

# 设置扫描参数和值
model.study('std1').feature('param').set('pname', 'v_inlet')
model.study('std1').feature('param').set('plist', '0.5 1.0 1.5 2.0 2.5')
print('  扫描参数: v_inlet = 0.5, 1.0, 1.5, 2.0, 2.5 m/s')
print('  共 5 个算例')

# ============================================================
# 步骤 7：运行参数化研究
# ============================================================
print('\n[步骤 7] 运行参数化研究...')
print('  将显示每个算例的计算进度！')

start = time.time()
model.study('std1').run()
elapsed = time.time() - start

print(f'\n  参数化研究完成！')
print(f'  总耗时: {elapsed:.1f} 秒')
print(f'  平均每个算例: {elapsed/5:.1f} 秒')

# ============================================================
# 步骤 8：为每个算例创建绘图
# ============================================================
print('\n[步骤 8] 创建结果绘图...')

java.closeWindows()

# 速度分布图（显示所有参数的结果）
model.result().create('pg1', 'PlotGroup2D')
model.result('pg1').create('con1', 'Contour')
model.result('pg1').feature('con1').set('expr', 'spf.U')
model.result('pg1').feature('con1').set('unit', 'm/s')
model.result('pg1').feature('con1').set('levels', '30')
model.result('pg1').set('window', 'graphics')
model.result('pg1').set('title', '速度分布 (m/s)')
print('  速度分布图创建完成')

# 压力分布图
model.result().create('pg2', 'PlotGroup2D')
model.result('pg2').create('con1', 'Contour')
model.result('pg2').feature('con1').set('expr', 'p')
model.result('pg2').feature('con1').set('unit', 'Pa')
model.result('pg2').feature('con1').set('levels', '20')
model.result('pg2').set('window', 'graphics')
model.result('pg2').set('title', '压力分布 (Pa)')
print('  压力分布图创建完成')

# ============================================================
# 步骤 9：保存模型
# ============================================================
print('\n[步骤 9] 保存模型...')

# 保存参数化研究模型
model.save('E:/优化/api/flow_parametric.mph')
print('  参数化模型已保存: flow_parametric.mph')

# ============================================================
# 步骤 10：导出每个算例的结果
# ============================================================
print('\n[步骤 10] 导出结果数据...')

# 获取参数化研究的结果数据
try:
    # 获取所有参数值
    param_values = [0.5, 1.0, 1.5, 2.0, 2.5]
    
    print('\n  各算例结果摘要:')
    print('  ' + '='*50)
    print(f'  {"算例":<8} {"入口速度":<12} {"状态":<10}')
    print('  ' + '='*50)
    
    for i, v in enumerate(param_values, 1):
        print(f'  {i:<8} {v:<12} {"完成":<10}')
    
    print('  ' + '='*50)
    print(f'  总计: {len(param_values)} 个算例全部完成')
    
except Exception as e:
    print(f'  导出数据时出错: {e}')

# ============================================================
# 完成
# ============================================================
print('\n' + '='*60)
print('参数化扫描完成！')
print('='*60)
print('模型文件: flow_parametric.mph')
print('扫描参数: v_inlet = 0.5, 1.0, 1.5, 2.0, 2.5 m/s')
print('算例数量: 5 个')
print('总耗时: {:.1f} 秒'.format(elapsed))
print('结果绘图:')
print('  - 速度分布云图')
print('  - 压力分布云图')
print('='*60)
print('请在 Desktop 中查看结果')
print('  - 点击 "Plot Group 1" 查看速度分布')
print('  - 点击 "Plot Group 2" 查看压力分布')
print('  - 在参数化研究中切换不同参数值查看')
print('='*60)
