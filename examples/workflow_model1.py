"""
Full workflow on Model1 - modify Desktop's active model directly.
This is the KEY: modify Model1, not create new models!
"""
import mph
import time

# Connect to existing server
client = mph.Client(port=2036, host='localhost')

# Import JPype AFTER client connects
from jpype import JArray, JString, JInt
StringArray = JArray(JString)
IntArray = JArray(JInt)

java = client.java
print('Connected to server')

# Get Desktop's active Model1
model = java.model('Model1')
print('Got Model1 reference')

# Clean up existing content by removing nodes
print('\nCleaning Model1...')
try:
    # Try to remove existing geometry, materials, etc.
    for i in range(10):
        try:
            model.component('comp1').geom('geom1').feature().remove(f'blk{i+1}')
        except:
            break
except:
    pass

# ===== Step 1: Component + Geometry =====
print('\n[Step 1] Creating component and geometry...')
try:
    model.modelNode().create('comp1')
except:
    print('  (comp1 already exists)')
try:
    model.geom().create('geom1', 3)
except:
    print('  (geom1 already exists)')
try:
    model.geom('geom1').feature().create('blk1', 'Block')
except:
    print('  (blk1 already exists)')
model.geom('geom1').feature('blk1').set('size', StringArray(['0.1', '0.1', '0.1']))
model.geom('geom1').feature('blk1').set('base', 'center')
model.geom('geom1').run()
print('  -> Geometry built (0.1m x 0.1m x 0.1m block)')
time.sleep(2)

# ===== Step 2: Material =====
print('\n[Step 2] Adding copper material...')
try:
    mat = model.component('comp1').material().create('mat1', 'Common')
except:
    mat = model.component('comp1').material('mat1')
mat.label('Copper')
mat.selection().all()
mat.propertyGroup('def').set('thermalconductivity', '400')
mat.propertyGroup('def').set('density', '8960')
mat.propertyGroup('def').set('heatcapacity', '385')
print('  -> Copper: k=400, rho=8960, Cp=385')
time.sleep(2)

# ===== Step 3: Physics =====
print('\n[Step 3] Adding Heat Transfer physics...')
try:
    ht = model.component('comp1').physics().create('ht', 'HeatTransfer', 'geom1')
except:
    ht = model.component('comp1').physics('ht')
try:
    ht.feature().create('temp1', 'TemperatureBoundary', 2)
except:
    pass
ht.feature('temp1').selection().set(IntArray([2]))
ht.feature('temp1').set('T0', '373.15')
try:
    ht.feature().create('hs1', 'HeatSource', 3)
except:
    pass
ht.feature('hs1').set('Q0', '1e6')
print('  -> Heat Transfer with BCs')
time.sleep(2)

# ===== Step 4: Mesh =====
print('\n[Step 4] Building mesh...')
try:
    model.component('comp1').mesh().create('mesh1')
except:
    pass
model.component('comp1').mesh('mesh1').run()
print('  -> Mesh built')
time.sleep(3)

# ===== Step 5: Study + Solve =====
print('\n[Step 5] Creating study and solving...')
try:
    model.study().create('std1')
except:
    pass
try:
    model.study('std1').create('stat', 'Stationary')
except:
    pass
model.study('std1').run()
print('  -> Solved!')

# ===== Step 6: Temperature Plot =====
print('\n[Step 6] Adding temperature plot...')
try:
    model.result().create('pg1', 'PlotGroup3D')
except:
    pass
try:
    model.result('pg1').create('surf1', 'Surface')
except:
    pass
model.result('pg1').feature('surf1').set('expr', 'T')
model.result('pg1').feature('surf1').set('unit', 'K')
model.result('pg1').run()
print('  -> Temperature plot created')

print('\n' + '='*50)
print('FULL WORKFLOW ON MODEL1 COMPLETE!')
print('Desktop should NOW show the updated model with:')
print('  1. 3D block geometry')
print('  2. Copper material')
print('  3. Heat Transfer physics')
print('  4. Mesh')
print('  5. Solved temperature results')
print('  6. Temperature surface plot')
print('='*50)
