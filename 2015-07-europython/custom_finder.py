import sys
from importlib.machinery import ModuleSpec
import importlib.abc

class CustomModule:
    pass

class CustomFinder:
    def find_spec(self, name, path=None, target=None):
        print('Finding', name, path, target)
        if name == 'mymod':
            return ModuleSpec(name, CustomLoader())

class CustomLoader:
    def create_module(self, name):
        print('Creating', name)
        return CustomModule()

    def exec_module(self, mod):
        print(vars(mod))
        print('Executing', mod)

sys.meta_path.insert(0, CustomFinder())

import mymod

print(mymod)



class CustomImporter(importlib.abc.InspectLoader):
    def find_spec(self, name, path=None, target=None):
        print('Finding', name, path, target)
        if name == 'zzmod':
            return ModuleSpec(name, self)

    def get_source(self, name):
        return 'p = 3'

sys.meta_path.insert(0, CustomImporter())

import zzmod

print(zzmod)
print(zzmod.p)
