#!/usr/bin/python
import sys

def deaccent(s:str) -> str:
	return s.translate(str.maketrans("âăî","aai"))

def eprint(*args, **kwargs):
	print(*args, file=sys.stderr, **kwargs)

verbs = {} # will hold all verbs, indexed by infinitive

class Verb:
	def __init__(self, s:str, tr:str=None, ext_present:bool=False, imp_tu:bool=False):
		if s[:2].lower() == "a ": s = s[2:] # "a vorbi" -> "vorbi"
		self.full = s
		self.trans = tr
		if s[:-2].lower() == "ea": # todo: some of them can be -a
			self.stem = s[:-2].lower()
			self.type = "ea"
		else:
			self.stem = s[:-1].lower()
			self.type = s[-1:].lower()
			if not self.type in {"a","e","i","î"}:
				raise Exception("Unknown verb type!")
		self.extend = ext_present
		if self.extend and self.type in {"e","ea"}:
			raise Exception("Cannot extend -e or -ea verbs!")
		self.imp_tu = imp_tu

	def __eq__(self, other):
		return other is not None and self.full == other.full

	def __str__(self):
		return self.full

	##########################################################################
	# Conjugations
	##########################################################################

	def order() -> list:
		return ["eu", "noi", "tu", "voi", "el/ea", "ele/ei"]
	def add_units(E:list) -> list:
		O = Verb.order()
		assert len(E) == len(O)
		return list(O[i] + " " + E[i] for i in range(0,len(E)))

	def present(self) -> list:
		b = self.type[0] # ea -> e
		if b == "î": b = "â" # îm -> âm
		if not self.extend:
			a = (b in {"a","â"})
			E = ("", "ăm" if self.type == "a" else b+"m", "i", b+"ți", "ă" if a else "e", "ă" if a else "")
		elif self.type == "a":
			e = ("i" if self.stem[-1] == "i" else "e")
			E = ("ez", "ăm", "ezi", b+"ți", e+"ază", e+"ază")
		elif self.type == "i":
			i = "i" if self.stem[-1] == "u" else ""
			E = (i+"esc", "im", i+"ești", b+"ți", i+"ește", i+"esc")
		elif self.type == "î":
			E = ("ăsc", b+"m", "ăști", b+"ți", "ăște", "ăsc")
		assert(len(E) == 6)
		return list(self.stem + e for e in E)

	def conjunctive(self) -> list:
		E = self.present()
		e = E[4]
		if e[-4:] == "ează":
			e = e[:-4] + "eze"
		elif e[-4:] == "ește":
			e = e[:-4] + "ească"
		elif e[-1] == "e":
			e = e[:-1] + "ă"
		elif e[-1] == "ă":
			e = e[:-1] + "e"
		E[4:5] = e,e
		return list("să " + e for e in E)

	def participle_perfect(self) -> str:
		return self.stem + self.type + "t" # todo...

	def compound_perfect(self) -> list:
		hv = ["am", "am", "ai", "ați", "a", "au"]
		pp = self.participle_perfect()
		return list(h + " " + pp for h in hv)

	def imperfect(self) -> list:
		E = ["m", "m", "i", "ți", "", "u"]
		if self.type == "i" and self.stem[-1] in {"a","e","i","o","u","ă","î","â"}:
			m = "ia"
		elif self.type in {"a","î"} or self.full == "scrie":
			m = "a"
		else:
			m = "ea"
		return list(self.stem + m + e for e in E)

	def perfect(self) -> list:
		pp = self.participle_perfect()
		if pp[-1] == "t": pp = pp[:-1]
		elif pp[-1] == "s": pp = pp + "e"
		E = ["i", "răm", "și", "răți", "", "ră"]
		if self.type == "a":
			E[4] = "e" if self.stem[-1] == "i" else "ă"
		return list(pp + e for e in E)

	def future1(self) -> list:
		hv = ["voi", "vom", "vei", "veți", "va", "vor"]
		return list(h + " " + self.full for h in hv)

	def future2(self) -> list:
		hv = ["am", "am", "ai", "aveți", "are", "au"]
		c = self.conjunctive()
		return list(hv[i] + " " + c[i] for i in range(0,len(hv)))

	def future3(self) -> list:
		C = self.conjunctive()
		return list("o " + c for c in C)

	def optative(self) -> list:
		hv = ["aș", "am", "ai", "ați", "ar", "ar"]
		return list(h + " " + self.full for h in hv)

	def optative_perfect(self) -> list:
		hv = ["aș", "am", "ai", "ați", "ar", "ar"]
		pp = self.participle_perfect()
		return list(h + " fi " + pp for h in hv)

	def gerund(self) -> str:
		return self.stem + ("ind" if self.type == "i" else "ând")

	def imperative(self) -> list:
		C = self.conjunctive()
		P = self.present()
		C[2] = P[4] if not self.imp_tu else P[2] # tu = present.el or present.tu
		C[3] = P[3] # voi = present.voi
		return C

	def neg_imperative(self) -> list:
		C = self.conjunctive()
		P = self.present()
		C[2] = self.full
		C[3] = P[3] # voi = present.voi
		return ["nu " + c for c in C]

	##########################################################################
	# Regularity
	##########################################################################
	
	def regular(self) -> bool:
		if type(self) == Verb: return True
		v = Verb(self.full)
		def c(A,B) -> bool:
			if len(A) != len(B): return False
			for i in range(0, len(A)):
				if A[i].lower() != B[i].lower(): return False
			return True
		if v.gerund().lower() != self.gerund().lower(): return False
		if v.participle_perfect().lower() != self.participle_perfect().lower(): return False
		if not c(v.present(), self.present()): return False
		if not c(v.conjunctive(), self.conjunctive()): return False
		if not c(v.compound_perfect(), self.compound_perfect()): return False
		if not c(v.imperfect(), self.imperfect()): return False
		if not c(v.perfect(), self.perfect()): return False
		if not c(v.future1(), self.future1()): return False
		if not c(v.future2(), self.future2()): return False
		if not c(v.future3(), self.future3()): return False
		if not c(v.optative(), self.optative()): return False
		if not c(v.optative_perfect(), self.optative_perfect()): return False
		if not c(v.imperative(), self.imperative()): return False
		if not c(v.neg_imperative(), self.neg_imperative()): return False
		return True

	def irregularities(self) -> dict:
		if type(self) == Verb: return {}
		d = {}
		v = Verb(self.full)
		def f(a,b,k):
			if a.lower() != b.lower(): d[k] = b
		def c(A,B,k) -> bool:
			assert(len(A) == len(B))
			for i in range(0, len(A)):
				f(A[i], B[i], k+str(i))
		f(v.gerund(), self.gerund(), "ge")
		f(v.participle_perfect(), self.participle_perfect(), "pp")
		c(v.present(), self.present(), "prs")
		c(v.conjunctive(), self.conjunctive(), "con")
		c(v.compound_perfect(), self.compound_perfect(), "cpf")
		c(v.imperfect(), self.imperfect(), "ipf")
		c(v.perfect(), self.perfect(), "pf")
		c(v.future1(), self.future1(), "f1")
		c(v.future2(), self.future2(), "f2")
		c(v.future3(), self.future3(), "f3")
		c(v.optative(), self.optative(), "op")
		c(v.optative_perfect(), self.optative_perfect(), "opp")
		c(v.imperative(), self.imperative(), "imp")
		c(v.neg_imperative(), self.neg_imperative(), "nimp")
		return d


if __name__ == "__main__":
	v = Verb("a vorbi")
	v.table()
	print("\n")
	v = Verb("comer")
	v.table()
	print("\n")
	v = Verb("morir")
	v.table()


