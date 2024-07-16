
from numba import jit 
from numba import types
from numba.typed import Dict

@jit(nopython=True)
def createDict(keys, values):
	d = Dict.empty(
		key_type=types.unicode_type,
		value_type=types.float64
	)
	for i in range(len(keys)):
		d[keys[i]] = float(values[i])
	return d

class Base:

	def __init__(self, x):
		self.x = x

class Test(Base):

	def __init__(self, var1, var2, x):
		super().__init__(x)
		self.p = {
			'var1': var1,
			'var2': var2
		}
		self.fnc = [ self.calc1, self.calc2 ]

	@staticmethod
	@jit(nopython=True)
	def calc1(p):
		r1 = p['var1'] * p['var2']
		r2 = p['var1'] + p['var2']
		a = 0
		if a:
			return createDict(['r1', 'r2', 'a'], [r1, r2, a])
		else:
			return createDict(['r1', 'r2'], [r1, r2])


	@staticmethod
	@jit(nopython=True)
	def calc2(p):
		r1 = p['var1'] * p['var2']
		r2 = p['var1'] + p['var2']
		return createDict(['r1', 'r2'], [r1, r2])


t = Test(2.0, 3.0, 4.0)

p = createDict(list(t.p.keys()), list(t.p.values()))
r = t.fnc[0](p)
print(r)
print(type(r))
