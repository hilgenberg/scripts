#!/usr/bin/python

def accented(s:str) -> str:
	if s == 'a': return "á"
	if s == 'e': return "é"
	if s == 'i': return "í"
	if s == 'o': return "ó"
	if s == 'u': return "ú"
	return s

def deaccent(s:str) -> str:
	return s.translate(str.maketrans("áéíóú","aeiou"))

verbs = {} # will hold all verbs, indexed by infinitivo

class Verb:
	def __init__(self, s:str, tr:str=None):
		self.full = s
		self.trans = tr
		self.stem = s[:-2].lower()
		self.type = deaccent(s[-2:].lower())
		if not self.type in {"ar","er","ir"}:
			raise Exception("Unknown verb type!")
		self.ar = self.type == "ar"
		self.er = self.type == "er"
		self.ir = self.type == "ir"

	def __eq__(self, other):
		return other is not None and self.s == other.s

	def __str__(self):
		return self.full

	##########################################################################
	# Helper stuff
	##########################################################################

	# lists with length 7 have "vos", those with length 6 have "vos" == "tú"
	# order: (yo, nosotros, tú, (vos), vosotros, él/..., ellos/...)
	def pad(E:list) -> list:
		if len(E) == 7: return E
		return E[:3]+E[2:3]+E[3:]

	def order() -> list:
		return ["yo", "nosotros", "tú", "vos", "vosotros",
			"él/ella/usted/se", "ellos/ellas/ustedes"]

	def add_units(E:list) -> list:
		O = Verb.order()
		assert len(E) == len(O)
		return list(O[i] + " " + E[i] for i in range(0,len(E)))

	def standard(self, base:str, nos_accent:str=None, vos_accent:str=None) -> list:
		a = base
		b = (base if nos_accent is None else nos_accent)
		c = (base if vos_accent is None else vos_accent)
		E = (a, b+"mos", a+"s", c+"is", a, a+"n")
		return Verb.pad(list(self.stem + e for e in E))


	##########################################################################
	# Conjugations
	##########################################################################
	
	def gerund(self) -> str:
		return self.stem + ("ando" if self.ar else "iendo")

	def perfect(self) -> str:
		return self.stem + ("ado" if self.ar else "ido")

	def present(self) -> list:
		b = self.type[0]
		bb = accented(b)
		be = b.replace("i", "e") # abrir => tú abres (and not abris)
		E = ("o", b+"mos", be+"s", bb+"s", (bb+"is").replace("íi","í"), be, be+"n")
		return list(self.stem + e for e in E)

		#if   self.ar: E = ("o", "amos", "as", "ás", "áis", "a", "an")
		#elif self.er: E = ("o", "emos", "es", "és", "éis", "e", "en")
		#elif self.ir: E = ("o", "imos", "es", "ís",  "ís", "e", "en")
		#return list(self.stem + e for e in E)

	def imperativ(self) -> list:
		b = self.type[0] # for vosotros and tú (except -ir)
		bb = accented(b) # vos gets an accent: ¡vos abrí!
		be = b.replace("i", "e") # abrir => ¡tú abre! (and not abri)
		if self.ar: x = "e"
		else:       x = "a"
		E = (x,      x+"mos", 
		     be,bb,  b+"d", 
		     x,      x+"n")
		return list(self.stem + e for e in E)

		#if   self.ar: E = ("e", "emos", "a", "á", "ad", "e", "en")
		#elif self.er: E = ("a", "amos", "e", "é", "ed", "a", "an")
		#elif self.ir: E = ("a", "amos", "e", "í", "id", "a", "an")
		#return list(self.stem + e for e in E)

	##########################################################################
	# Futures
	##########################################################################
	
	def futur(self) -> list:
		E = ("é", "emos", "ás", "éis", "á", "án")
		return Verb.pad(list(self.stem + self.type + e for e in E))

	##########################################################################
	# Pasts
	##########################################################################
	
	def indefinido(self) -> list:
		if self.ar: E = ("é", "amos", "aste", "asteis",  "ó",  "aron")
		else:       E = ("í", "imos", "iste", "isteis", "ió", "ieron")
		return Verb.pad(list(self.stem + e for e in E))

	def imperfekt(self) -> list:
		if self.ar: return self.standard("aba", "ába")
		else:       return self.standard("ía")

	##########################################################################
	# Conditionals
	##########################################################################
	
	def konditional(self) -> list:
		return self.standard(self.type + "ía")

	def subjunktiv(self) -> list:
		if self.ar: return self.standard("e", None, "é")
		else:       return self.standard("a", None, "á")

	def subjunktiv_I(self, alt:bool=False) -> list:
		ra = "ra" if not alt else "se"
		if self.ar: return self.standard( "a"+ra,  "á"+ra)
		else:       return self.standard("ie"+ra, "ié"+ra)

	def subjunktiv_F(self) -> list:
		if self.ar: return self.standard( "are",  "áre")
		else:       return self.standard("iere", "iére")

	##########################################################################
	# Regularity
	##########################################################################
	
	def regular(self) -> bool:
		if type(self) == Verb: return True
		v = Verb(self.full)
		if v.gerund().lower() != self.gerund().lower(): return False
		if v.perfect().lower() != self.perfect().lower(): return False
		def c(A,B) -> bool:
			if len(A) != len(B): return False
			for i in range(0, len(A)):
				if A[i].lower() != B[i].lower(): return False
			return True
		if not c(v.present(), self.present()): return False
		if not c(v.indefinido(), self.indefinido()): return False
		if not c(v.imperfekt(), self.imperfekt()): return False
		if not c(v.futur(), self.futur()): return False
		if not c(v.imperativ(), self.imperativ()): return False
		if not c(v.konditional(), self.konditional()): return False
		if not c(v.subjunktiv(), self.subjunktiv()): return False
		if not c(v.subjunktiv_I(), self.subjunktiv_I()): return False
		if not c(v.subjunktiv_I(True), self.subjunktiv_I(True)): return False
		if not c(v.subjunktiv_F(), self.subjunktiv_F()): return False
		return True

	def irregularities(self) -> dict:
		if type(self) == Verb: return {}
		d = {}
		v = Verb(self.full)
		def f(a,b,k):
			if a.lower() != b.lower(): d[k] = b
			
		f(v.gerund(), self.gerund(), "g")
		f(v.perfect(), self.perfect(), "p")
		def c(A,B,k) -> bool:
			assert(len(A) == len(B))
			for i in range(0, len(A)):
				f(A[i], B[i], k+str(i))
		c(v.present(), self.present(), "prs")
		c(v.indefinido(), self.indefinido(), "ind")
		c(v.imperfekt(), self.imperfekt(), "imp")
		c(v.futur(), self.futur(), "ftr")
		c(v.imperativ(), self.imperativ(), "imv")
		c(v.konditional(), self.konditional(), "con")
		c(v.subjunktiv(), self.subjunktiv(), "sub")
		c(v.subjunktiv_I(), self.subjunktiv_I(), "si1")
		c(v.subjunktiv_I(True), self.subjunktiv_I(True), "si2")
		c(v.subjunktiv_F(), self.subjunktiv_F(), "sf")
		return d

	##########################################################################
	# Compound tenses
	##########################################################################

	def neg_imperative(self) -> list:
		return ["no " + x for x in self.subjunktiv()]

	def present_progressive(self) -> list:
		global verbs
		g = self.gerund()
		assert("estar" in verbs)
		e = verbs["estar"]
		return [x + " " + g for x in e.present()]

	def present_perfect(self) -> list:
		global verbs
		p = self.perfect()
		assert("haber" in verbs)
		h = verbs["haber"]
		return [x + " " + p for x in h.present()]

if __name__ == "__main__":
	v = Verb("comprar")
	v.table()
	print("\n")
	v = Verb("comer")
	v.table()
	print("\n")
	v = Verb("morir")
	v.table()


