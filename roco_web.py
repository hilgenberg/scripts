#!/usr/bin/python
from roco_irregular import *
import re, os, subprocess

class WVerb(DVerb):
	def __init__(self, v:str):
		if v[:2].lower() == "a ": v = v[2:] # "a vorbi" -> "vorbi"
		if not re.match(r'^[a-zA-ZâÂăĂîÎșȘțȚ ]+$', v): raise Exception("Bad verb name!")

		p = os.path.expanduser("~/.cache/roco/")
		f = os.path.join(p, f"{v}.html")
		if os.path.isfile(f):
			# read from cache
			with open(f) as F: s = F.read()
		else:
			# read from web, write to cache
			os.makedirs(p, 0o700, True)
			r = subprocess.run(
				f"chromium --headless --dump-dom https://www.verbix.com/webverbix/go.php?&D1=5&T1={v}".split(),
				capture_output=True, text=True)
			if r.returncode != 0: raise Exception(f"Fetching failed: {str(r)}")
			s = r.stdout
			with open(f, "w") as F:
				F.write(s)

		s = re.sub(r'ş', r'ș', s)
		s = re.sub(r'ţ', r'ț', s)

		s = re.sub(r'^.*<h3>Nominal Forms</h3>', r'', s, flags=re.DOTALL)
		s = re.sub(r'<h3>Synonyms.+$', r'', s, flags=re.DOTALL)
		s = re.sub(r'<a href=[^>]+>([^<]+)</a>', r'\1', s)
		s = re.sub(r'\s*class="normal"', r'', s)
		s = re.sub(r'\s*data-speech="[^"]+"', r'', s)

		h3,h4,key,tr=None,None,None,None
		d = {}
		cases = {'eu':'fs', 'tu':'ss', 'el':'ts', 'ea':'ts', 
			'noi':'fp', 'voi':'sp', 'ei':'tp', 'ele':'tp'}
		keys = {
			'Indicativ|Prezent':'prs',
			'Indicativ|Perfect compus':'cpf',
			'Indicativ|Imperfect':'ipf',
			'Indicativ|Perfect simplu':'pf',

			'Indicativ|Viitor I':'f1',
			'Indicativ|Viitor I (popular)':'f3',
			'Indicativ|Viitor I (popular)':None,
			'Indicativ|Viitor II (popular)':None,
			'Indicativ|Viitor II':None,
			
			'Conditional|Prezent':'op',
			'Conditional|Perfect':'opp',
			'Imperative|None':'imp',
			'Subjonctiv|Prezent':'con',
			'Subjonctiv|Perfect compus':None,
			'Indicativ|Mai mult ca perfect':None,
		}

		for line in s.splitlines():
			if r := re.search(r'<h3>([^<]+)</h3>', line):
				h4 = None
				h3 = r.group(1)
			elif r := re.search(r'<h4>([^<]+)</h4>', line):
				h4 = r.group(1)
			elif h3 is None and h4 is None and (r := re.search(r'<b>(.+?):\s*</b>', line)):
				key = r.group(1)
			elif h3 is None and h4 is None and (r := re.search(r'<span[^>]*>(.+)</span>', line)):
				if key == "Gerunziu":
					d["ge"] = r.group(1)
				elif key == "Participiu":
					d["pp"] = r.group(1)
				elif key == "Infinitiv" or key == "Infinitiv compus":
					pass
				else:
					print(f"Ignoring {key} => {r.group(1)}")
				key = None
			elif h3 is not None and (r := re.search(r'<span class="pronoun">([a-z]+)</span></td><td>((<span[^>]*>[^<]+</span>;?\s*)+)</td></tr>', line)):
				c = r.group(1)
				if not c in cases: raise Exception(f"Garbage case: {c}")
				c = cases[c]

				k = f"{h3}|{h4}"
				if not k in keys: raise Exception(f"Garbage key: {k}")
				k = keys[k]
				if k is None: continue

				if c+k in d:
					print(f"Warning: overwriting {c+k}: {d[c+k]} -> {r.group(2)}")
				
				ss = r.group(2)
				val = []
				while (rr := re.search(r'<span[^>]*>([^<]+)</span>(.*)$', ss)):
					val.append(rr.group(1))
					ss = rr.group(2)
				if len(val) == 0:
					raise Exception(f"Garbage value: {r.group(2)}")
				elif len(val) > 1:
					print(f"Warning: Multivalue {val} for key {c+k}")
				val = val[0]
				d[c+k] = "să " + val if k == "con" else val

			elif (r := re.search(r'<div id="verbixTranslations" sl="ron" tl="eng">(.+)</div>', line)):
				tr = r.group(1)
				tr = re.sub(r'</li>', ', ', tr)
				tr = re.sub(r'<[^>]+>', r'', tr)
				tr = re.sub(r'\s*,?\s*$', r'', tr)
			elif re.match(r'^(\s*<[^>]+>|\s*-)*\s*$', line):
				pass
			elif h3 is not None and re.search(r'Verbs conjugated like', h3):
				pass
			elif h3 == 'Long Infinitive':
				pass
			else:
				print(f"Ignoring line on {h3}|{h4}: {line}")

		if tr == "(none)": tr = None
		super().__init__(v, tr, False, False, None, d)
		P = self.present()
		if self.type == "a":
			if P[0][-2:] == "ez" or P[5][-3:] == "ază":
				self.extend = True
		elif self.type == "i":
			if P[0][-3:] == "esc" or P[5][-3:] == "esc":
				self.extend = True
		elif self.type == "î":
			if P[0][-3:] == "ăsc" or P[5][-3:] == "ăsc":
				self.extend = True
		C = self.conjunctive()
		if C[2] != P[4] and C[2] == P[2]: self.imp_tu = True


