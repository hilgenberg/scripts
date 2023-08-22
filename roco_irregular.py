#!/usr/bin/python
from roco_regular import *
import re, os

class DVerb(Verb):
	def __init__(self, v:str, tr:str, ext_present:bool, imp_tu:bool, p:str, D):
		super().__init__(v, tr, ext_present, imp_tu)
		if p is not None:
			n = 0
			while n < len(v) and n < len(p) and v[-1-n] == p[-1-n]:
				n += 1
			self.parent = (p, p[:len(p)-n], v[:len(v)-n])
		else:
			self.parent = None

		if type(D) is str:
			self.d = {}
			while True:
				#m = re.search(r'^([a-z]+):([^ ]+) ?(.*)$', D)
				# allow for spaces in the values:
				m = re.search(r'^([a-z]+):((?:[^: ]+\s+)*(?:[^: ]+))(?:\s+|$)(.*)$', D)
				if m is None:
					assert(re.match(r'^\s*$', D))
					break
				self.d[m.group(1)] = m.group(2)
				D = m.group(3)
		else:
			self.d = D

	##########################################################################
	# Helper stuff
	##########################################################################

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

	def conj(self, code:str, d:list) -> list:
		T = ["fs","fp","ss","sp","ts","tp"]
		return [self.find(T[i]+code) or d[i] for i in range(0, len(T))]

	##########################################################################
	# Simple overrides by dict (i.e. self.d)
	##########################################################################

	def gerund(self) -> str:
		return self.find("ge") or super().gerund()

	def participle_perfect(self) -> str:
		return self.find("pp") or super().participle_perfect()

	def present(self) -> list:
		return self.conj("prs", super().present())

	def conjunctive(self) -> list:
		return self.conj("con", super().conjunctive())

	def compound_perfect(self) -> list:
		return self.conj("cpf", super().compound_perfect())

	def imperfect(self) -> list:
		return self.conj("ipf", super().imperfect())

	def perfect(self) -> list:
		return self.conj("pf", super().perfect())

	def future1(self) -> list:
		return self.conj("f1", super().future1())

	def future2(self) -> list:
		return self.conj("f2", super().future2())

	def future3(self) -> list:
		return self.conj("f3", super().future3())

	def optative(self) -> list:
		return self.conj("op", super().optative())

	def optative_perfect(self) -> list:
		return self.conj("opp", super().optative_perfect())

	def imperative(self) -> list:
		return self.conj("imp", super().imperative())

	def neg_imperative(self) -> list:
		return self.conj("nimp", super().neg_imperative())

	##########################################################################
	# Optimizer
	##########################################################################

	def recipe(self) -> str:
		tr = '' if self.trans is None else self.trans
		if len(self.d) == 0 and self.parent is None:
			return f"'{self.full}': ({repr(tr)}, {self.extend}, {self.imp_tu})"
		else:
			D = " ".join([k+':'+v for k,v in self.d.items()])
			P = None if self.parent is None else self.parent[0]
			return f"'{self.full}': ({repr(tr)}, {self.extend}, {self.imp_tu}, {repr(P)}, {repr(D)})"


	def optimize(self, reparent:bool=True) -> bool:
		eprint(f"optimizing {self.full}")
		n0 = len(self.d)
		DD = {}
		if (v := self.d.pop("ge", None)) is not None:
			if self.gerund() != v: self.d["ge"] = v
		if (v := self.d.pop("pp", None)) is not None:
			if self.participle_perfect() != v: self.d["pp"] = v

		T = ["fs","fp","ss","sp","ts","tp"]
		M = [
			("prs",  DVerb.present),
			("con",  DVerb.conjunctive),
			("cpf",  DVerb.compound_perfect),
			("ipf",  DVerb.imperfect),
			("pf",   DVerb.perfect),
			("f1",   DVerb.future1),
			("f2",   DVerb.future2),
			("f3",   DVerb.future3),
			("op",   DVerb.optative),
			("opp",  DVerb.optative_perfect),
			("imp",  DVerb.imperative),
			("nimp", DVerb.neg_imperative)]

		DD["ge"] = self.gerund()
		DD["pp"] = self.participle_perfect()

		for code,f in M:
			P = f(self)
			for i,t in enumerate(T):
				DD[t+code] = P[i]
				if (v := self.d.pop(t+code, None)) is None: continue
				if f(self)[i] != v: self.d[t+code] = v

		n = len(self.d)
		if n != n0:
			eprint(f"removed {n0-n} items")

		if not reparent: return n < n0

		min = n

		global verbs
		V = []
		for s,v in verbs.items():
			if s == self.full: continue
			if type(v) == Verb: continue
			if self.parent is not None and self.parent[0] == s: continue
			if v.extend != self.extend: continue
			s0 = self.full
			# find common suffix
			m = 0
			while m < len(s) and m < len(s0) and s[-1-m] == s0[-1-m]:
				m += 1
			if m <= len(self.type): continue

			vv = DVerb(s0, self.trans, self.extend, self.imp_tu, s, DD)
			vv.optimize(False)
			nn = len(vv.d)
			if nn < min: min = nn
			if nn < n and nn == min:
				V.append(vv)

		p = os.path.expanduser("~/bin/roco_verbs_new.py")
		with open(p, "a") as F:
			if n == min:
				print(self.recipe())
				F.write(self.recipe()+",\n")
			else:
				for v in V:
					if len(v.d) > min: continue
					print(v.recipe())
					F.write(self.recipe()+",\n")

		return min < n0



