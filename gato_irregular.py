#!/usr/bin/python
from gato_regular import *
import re
import sys

class DVerb(Verb):
	def __init__(self, v:str, tr:str, p:str, D:str):
		super().__init__(v, tr)
		if p is not None:
			n = 0
			while n < len(v) and n < len(p) and v[-1-n] == p[-1-n]:
				n += 1
			self.parent = (p, p[:len(p)-n], v[:len(v)-n])
		else:
			self.parent = None
		self.d = {}
		while True:
			m = re.search(r'^([a-z]+):([^ ]+) ?(.*)$', D)
			if m is None:
				assert(re.match(r'^\s*$', D))
				break
			self.d[m.group(1)] = m.group(2)
			D = m.group(3)

	##########################################################################
	# Helper stuff
	##########################################################################

	def mod_standard(self, stem:str, base:str, nos:str=None, vos:str=None) -> list:
		a = base
		b = (base if nos is None else nos)
		c = (base if vos is None else vos)
		E = (a, b+"mos", a+"s", c+"is", a, a+"n")
		return Verb.pad(list(stem + e for e in E))
	
	def find(self, key:str):
		global verbs
		x = self
		mod = []
		val = None
		while True:
			if key in x.d:
				val = x.d[key]
				break
			if x.parent is None: return None
			f,r,a = x.parent
			assert(f in verbs)
			x = verbs[f]
			mod.append((r,a))
		for r,a in reversed(mod):
			assert(val.startswith(r))
			val = a + val[len(r):]
		return val.lower()

	def fix(self, T:list, d:list) -> list:
		return [T[i] or d[i] for i in range(0, len(T))]

	def conj(self, code:str, has_vos:bool, d:list) -> list:
		T = ["fs","fp","ss","sv" if has_vos else "ss","sp","ts","tp"]
		return [self.find(T[i]+code) or d[i] for i in range(0, len(T))]

	##########################################################################
	# Simple overrides by dict (i.e. self.d)
	##########################################################################

	def gerund(self) -> str:
		return self.find("ge") or super().gerund()

	def perfect(self) -> str:
		return self.find("po") or super().perfect()

	def present(self) -> list:
		return self.conj("pr", True, super().present())
	
	def imperfekt(self) -> list:
		return self.conj("ii", False, super().imperfekt())

	def indefinido(self) -> list:
		return self.conj("pt", False, super().indefinido())

	def subjunktiv(self) -> list:
		return self.conj("pb", False, super().subjunktiv())

	##########################################################################
	# Imperative
	##########################################################################

	def imperativ(self) -> list:
		# take all from dict
		I = self.conj("io", True, [None]*7)
		# add vosotros (hablad f.e.)
		if I[4] is None: I[4] = self.full[:-1] + "d"
		# take 1. and 3. person from subjunctive
		E = self.subjunktiv()
		for i in [0,1,5,6]:
			if I[i] is None: I[i] = E[i]
		# use él as yo (could also set to None)
		I[0] = I[5]
		# fill 2. person from parent if needed
		return self.fix(I, super().imperativ())

	##########################################################################
	# Root-based overrides
	##########################################################################

	def futur(self) -> list:
		rf = self.find("rf")
		if rf is None: return super().futur()
		E = ("é", "emos", "ás", "éis", "á", "án")
		return Verb.pad(list(rf + e for e in E))

	def konditional(self) -> list:
		rf = self.find("rf")
		if rf is None: rf = self.stem + self.type
		T = self.mod_standard(rf, "ía")
		return self.fix(T, super().konditional())

	def subjunktiv_I(self, alt:bool=False) -> list:
		# root is indefinido for ellos without "ron"
		s = self.indefinido()[-1]
		assert(s[-3:].lower() == "ron")
		s = s[:-3]
		ra = "ra" if not alt else "se"
		# nosotros needs an accent
		acc = "á" if s[-1].lower() == "a" else "é"
		T = self.mod_standard(s[:-1], s[-1]+ra, acc+ra)
		return self.fix(T, super().subjunktiv_I(alt))

	def subjunktiv_F(self) -> list:
		# same as sub_I, but with "re" instead of "ra"
		s = self.indefinido()[-1]
		assert(s[-3:].lower() == "ron")
		s = s[:-3]
		acc = "á" if s[-1].lower() == "a" else "é"
		T = self.mod_standard(s[:-1], s[-1]+"re", acc+"re")
		return self.fix(T, super().subjunktiv_F())

