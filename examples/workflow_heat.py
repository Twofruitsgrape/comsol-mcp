"""
Full workflow - complete heat transfer simulation.
Demonstrates real-time Desktop updates as Python automates COMSOL.
"""
import mph
import time

# Connect to existing server (this starts JVM)
client = mph.Client(port=2036, host='localhost')

# Import JPype AFTER client connects
from jpype import JArray, JString, JInt
StringArray = JArray(JString)

java = client.java
print('Connected to server')

# Create a fresh model
print('\nCreating fresh model...')
model = java.create('HeatDemo')
print('Model created')

# ===== Step 1: Component + Geometry =====
print('\n[Step 1] Creating component and geometry...')
model.modelNode().create('comp1')
model.geom().create('geom1', 3)
model.geom('geom1').feature().create('blk1', 'Block')
model.geom('geom1').feature('blk1').set('size', StringArray(['0.1', '0.1', '0.1']))
model.geom('geom1').feature('blk1').set('base', 'center')
model.geom('geom1').run()
print('  -> Geometry built (0.1m x 0.1m x 0.1m block)')
time.sleep(2)

# ===== Step 2: Material =====
print('\n[Step 2] Adding copper material...')
mat = model.component('comp1').material().create('mat1', 'Common')
mat.label('Copper')
mat.selection().all()
mat.propertyGroup('def').set('thermalconductivity', '400')
mat.propertyGroup('def').set('density', '8960')
mat.propertyGroup('def').set('heatcapacity', '385')
print('  -> Copper: k=400, rho=8960, Cp=385')
time.sleep(2)

# ===== Step 3: Physics =====
print('\n[Step 3] Adding Heat Transfer physics...')
ht = model.component('comp1').physics().create('ht', 'HeatTransfer', 'geom1')
ht.feature().create('temp1', 'TemperatureBoundary', 2)
IntArray = JArray(JInt)
ht.feature('temp1').selection().set(IntArray([2]))
ht.feature('temp1').set('T0', '373.15')
ht.feature().create('hs1', 'HeatSource', 3)
ht.feature('hs1').set('Q0', '1e6')
print('  -> Heat Transfer with BCs')
time.sleep(2)

# ===== Step 4: Mesh =====
print('\n[Step 4] Building mesh...')
model.component('comp1').mesh().create('mesh1')
model.component('comp1').mesh('mesh1').run()
print('  -> Mesh built')
time.sleep(3)

# ===== Step 5: Study + Solve =====
print('\n[Step 5] Creating study and solving...')
model.study().create('std1')
model.study('std1').create('stat', 'Stationary')
model.study('std1').run()
print('  -> Solved!')

# ===== Step 6: Temperature Plot =====
print('\n[Step 6] Adding temperature plot...')
model.result().create('pg1', 'PlotGroup3D')
model.result('pg1').create('surf1', 'Surface')
model.result('pg1').feature('surf1').set('expr', 'T')
model.result('pg1').feature('surf1').set('unit', 'K')
model.result('pg1').run()
print('  -> Temperature plot created')

print('\n' + '='*50)
print('FULL WORKFLOW COMPLETE!')
print('Desktop should show HeatDemo model with:')
print('  1. 3D block geometry')
print('  2. Copper material')
print('  3. Heat Transfer physics')
print('  4. Mesh')
print('  5. Solved temperature results')
print('  6. Temperature surface plot')
print('='*50)
