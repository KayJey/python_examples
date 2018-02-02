import os
import sys

class Spec(object):
	def __init__(self, name, loader, file=None, path=None, cached=None, parent=None, has_location=False):
		self.name = name
		self.loader = loader
		self.origin = file
		self.submodule_search_location = path
		self.cached = cached
		self.has_location = has_location

class Finder(object):
	def __init__(self, path):
		self.path = path

	def find_spec(self, name, path, target):
		print('find spec name:%s path:%s target:%s' % (name,path,target))
		return Spec(name,self,path)

	def load_module(self, fullname):
		print('loading module',fullname)
		if fullname+'.py' in os.listdir(self.path):
			import builtins
			mod = type(os)
			modobject = mod(fullname)
			modobject.__builtins__ = builtins
			def foo():
				print('hi, i am foo')
			modobject.__dict__['too'] = foo
			sys.modules[fullname] = modobject
			modobject.__spec__ = 'asdfasdfasdf'
			modobject.__name__ = fullname
			modobject.__file__ = 'yannicks file'
			return modobject

sys.meta_path.append(Finder(r'tmp'))
import notes
notes.too()