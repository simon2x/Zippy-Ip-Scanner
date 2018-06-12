# Generate python modules from UI forms
import os
import os.path


os.chdir(os.path.split(__file__)[0])

files = [f for f in os.listdir('.') if os.path.isfile(f)]
for f in files:
    if not f.endswith('.ui'):
        continue
    os.system('pyuic5 -o ui{0}.py {1}'.format(f[:-3], f))
    
print('Done!')