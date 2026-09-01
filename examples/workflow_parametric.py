"""
Parametric sweep model - multiple solutions for visible computation.
Sweeps through different heat flux values, shows progress.
"""
import mph
import time

client = mph.Client(port=2036, host='localhost')
from jpype import JArray, JString, JInt
StringArray = JArray(JString)
IntArray = JArray(JInt)

java = client.java
model = java.model('Model1')
print('Connected to Model1')

# ===== Step 1: Add parameter =====
print('\n[Step 1] Adding parameter for sweep...')
try:
    model.param().remove('q_flux')
except:
    pass
model.param().set('q_flux', '1000')
print('  -> Parameter q_flux = 1000 W/m2')
time.sleep(1)

# ===== Step 2: Update Heat Flux to use parameter =====
print('\n[Step 2] Linking Heat Flux to parameter...')
ht = model.component('comp1').physics('ht')
ht.feature('hf1').set('q0', 'q_flux')
print('  -> Heat Flux = q_flux')
time.sleep(1)

# ===== Step 3: Create Parametric Study =====
print('\n[Step 3] Creating Parametric Study...')
try:
    model.study().remove('std2')
except:
    pass
model.study().create('std2')
model.study('std2').create('stat', 'Stationary')

# Add parameter sweep
try:
    model.study('std2').create('param', 'Parametric')
except:
    pass

# Sweep through 5 different heat flux values
model.study('std2').feature('param').set('pname', 'q_flux')
model.study('std2').feature('param').set('plist', '1000 2000 3000 4000 5000')
print('  -> Sweeping q_flux: 1000, 2000, 3000, 4000, 5000 W/m2')
time.sleep(2)

# ===== Step 4: Run Parametric Study =====
print('\n[Step 4] Running Parametric Study (5 solutions)...')
start = time.time()
model.study('std2').run()
elapsed = time.time() - start
print(f'  -> Parametric study completed in {elapsed:.1f} seconds')
print(f'  -> Average time per solution: {elapsed/5:.1f} seconds')
time.sleep(2)

# ===== Step 5: Create Multiple Plots =====
print('\n[Step 5] Creating temperature plots for each solution...')
for i in range(1, 6):
    try:
        model.result().create(f'pg{i}', 'PlotGroup3D')
    except:
        pass
    model.result(f'pg{i}').create('surf1', 'Surface')
    model.result(f'pg{i}').feature('surf1').set('expr', 'T')
    model.result(f'pg{i}').feature('surf1').set('unit', 'K')
    model.result(f'pg{i}').run()
    print(f'  -> Plot {i} created')
time.sleep(2)

print('\n' + '='*50)
print('PARAMETRIC SWEEP COMPLETE!')
print(f'Total time: {elapsed:.1f} seconds')
print(f'Average per solution: {elapsed/5:.1f} seconds')
print('Desktop should show:')
print('  1. 5m x 5m x 0.5m plate geometry')
print('  2. Steel material')
print('  3. Parametric study with 5 solutions')
print('  4. Temperature plots for each solution')
print('='*50)
