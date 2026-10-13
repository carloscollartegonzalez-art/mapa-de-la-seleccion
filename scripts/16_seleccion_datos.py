"""Cadena de control de la selección y formación de cada cuerpo de funcionarios:
cuerpo → quién convoca (y firma la última convocatoria) → quién preside el tribunal → quién dirige la formación,
y para cada persona: su puesto, cuándo y quién la nombró (BOE), y las marcas del Mapa del Relevo.
Entrada: datos/cuerpos_A1A2.xlsx, datos/tribunales.jsonl, seleccion/tribunales_web.jsonl, seleccion/escuelas.jsonl,
         dashboard/mapa-del-relevo.html (datos del censo con marcas)
Salida: seleccion/seleccion.json
"""
import os, re, json, glob, collections, unicodedata
import openpyxl

B = os.path.join(os.path.dirname(__file__), "..")


def nn(s):
    s = unicodedata.normalize("NFKD", str(s or "")).encode("ascii", "ignore").decode().lower()
    if "," in s and len(s.split(",")) == 2: a, b = s.split(","); s = b + " " + a
    return " ".join(re.sub(r"[^a-z0-9 ]", " ", s).split())


STOP = set("cuerpo cuerpos escala escalas de del la las los el y en sup superior especialidad esp".split())
def toks(s): return {w for w in nn(s).split() if w not in STOP and len(w) > 2}
def jl(p): return [json.loads(l) for l in open(p) if l.strip()] if os.path.exists(p) else []


def gobierno(f):
    if not f: return ""
    if f >= "2018-06-02": return "Sánchez"
    if f >= "2011-12-21": return "Rajoy"
    if f >= "2004-04-17": return "Zapatero"
    return "Anterior a 2004"


# ---------- censo con marcas (desde el dashboard ya generado) ----------
d = open(os.path.join(B, "dashboard/mapa-del-relevo.html")).read()
P = json.loads(re.search(r'<script type="application/json" id="data">(.*?)</script>', d, re.S).group(1).replace("<\\/", "</"))["puestos"]
por_nombre = collections.defaultdict(list)
for p in P:
    if p["t"] and p["t"] not in ("No publicado", "No identificado") and not p["t"].startswith("Vacante"):
        por_nombre[nn(p["t"])].append(p)


def buscar_persona(nombre):
    k = nn(nombre)
    if not k: return []
    if k in por_nombre: return por_nombre[k]
    t = k.split()
    if len(t) >= 3:  # nombre compuesto abreviado
        for kk, L in por_nombre.items():
            u = kk.split()
            if len(u) >= 3 and u[-2:] == t[-2:] and (set(u[:-2]) <= set(t[:-2]) or set(t[:-2]) <= set(u[:-2])): return L
    return []


# ---------- quién nombró: lee el XML del acto ----------
_cache = {}
def nombrado_por(boe):
    m = re.search(r"BOE-A-\d{4}-\d+", boe or "")
    if not m: return ""
    i = m.group(0)
    if i in _cache: return _cache[i]
    f = os.path.join(B, "datos/boe_cache/xml", i + ".xml")
    res = ""
    if os.path.exists(f):
        x = open(f, errors="ignore").read()
        t = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", x.split("<texto>")[-1]))
        rango = re.search(r"<rango[^>]*>([^<]+)", x)
        if rango and "Real Decreto" in rango.group(1):
            pr = re.search(r"(?i)a propuesta (?:del|de la|conjunta de los?|de los) ([^,]{5,140}?)(?:,| y previa)", t)
            res = "Consejo de Ministros" + (f" (propuesta: {pr.group(1).strip()})" if pr else "")
        else:
            fi = re.findall(r"\d{4}\s*\.?\s*[–—-]+\s*(?:El|La)\s+([^.]{5,200})", t)
            if fi: res = fi[-1].strip()
    _cache[i] = res
    return res


ULTIMO = json.load(open(os.path.join(B, "seleccion/nombramientos_personas.json"))) if os.path.exists(os.path.join(B, "seleccion/nombramientos_personas.json")) else {}


def ficha(nombre, rol, organo="", fuente="", extra=None):
    """Nodo de persona con su puesto en el censo (si lo tiene), nombramiento y marcas."""
    hits = buscar_persona(nombre)
    p = hits[0] if hits else None
    n = dict(rol=rol, organo=organo, nombre=nombre, fuente=fuente, en_censo=bool(p))
    if p:
        n.update(puesto=p["p"], ministerio=p["m"], desde=p["d"], gob=gobierno(p["d"]), cese=p["c"], boe=p["boe"],
                 nombrado_por=nombrado_por(p["boe"]), pa=p["pa"], jud=p["jud"], zpa=p["zpa"], zpd=p["zpd"])
    if extra: n.update(extra)
    if not p and not n.get("nombrado_por"):
        u = ULTIMO.get(nn(nombre))
        if u:
            n.update(ultimo_puesto=u["puesto"], desde=u["fecha"], gob=gobierno(u["fecha"]), boe=u["boe"],
                     nombrado_por=nombrado_por(u["boe"]), ultimo=True)
    return n


# ---------- órgano convocante → titular del censo ----------
SUBSE = {}
for p in P:
    if p["n"] == "Subsecretaría" and re.match(r"(?i)subsecretari", p["p"]):
        SUBSE.setdefault(p["m"], p)


def convocante(texto):
    t = texto or ""
    m = re.search(r"Ministerio (?:de |del |de la |para la )?([^;,.()]+)", t)
    if re.search(r"(?i)subsecretar", t) and m:
        k = toks(m.group(1))
        best = max(SUBSE.items(), key=lambda kv: len(k & toks(kv[0])), default=None)
        if best and len(k & toks(best[0])) >= 1:
            p = best[1]
            return dict(organo=f"Subsecretaría ({best[0].replace('Ministerio de ', '').replace('Ministerio del ', '')})", persona=p["t"], p=p)
    for pat, clave in [(r"(?i)guardia civil", "Directora General de la Guardia Civil"), (r"(?i)polic[ií]a", "Director General de la Policía"),
                       (r"(?i)funci[oó]n p[uú]blica", "Secretari"), (r"(?i)agencia estatal de administraci[oó]n tributaria|AEAT", "Agencia Estatal de Administración Tributaria"),
                       (r"(?i)instituciones penitenciarias", "Secretario General de Instituciones Penitenciarias"), (r"(?i)subsecretar[ií]a de defensa", "Subsecretari")]:
        if re.search(pat, t):
            cand = [p for p in P if clave.lower() in p["p"].lower() and p["t"] not in ("No publicado", "No identificado")]
            if pat.endswith("p[uú]blica"): cand = [p for p in P if re.search(r"(?i)secretari[oa] de estado de funci[oó]n p[uú]blica", p["p"])]
            if "defensa" in pat: cand = [p for p in P if p["n"] == "Subsecretaría" and "Defensa" in p["m"]]
            if cand: return dict(organo=cand[0]["p"], persona=cand[0]["t"], p=cand[0])
    return dict(organo=t[:160], persona="", p=None)


# ---------- tribunales ----------
T = [t for t in jl(os.path.join(B, "datos/tribunales.jsonl")) if t["cuerpo"] and any(m["rol"] == "Presidencia" for m in t["miembros"])]
TW = {nn(t["cuerpo"]): t for t in jl(os.path.join(B, "seleccion/tribunales_web.jsonl"))}
pres_count = collections.Counter()
for t in T:
    for m in t["miembros"]:
        if m["rol"] == "Presidencia" and m["bloque"] == "titular": pres_count[nn(m["nombre"])] += 1


def tribunal(cuerpo):
    a = toks(cuerpo)
    cands = sorted(T, key=lambda t: (len(a & toks(t["cuerpo"])) / max(1, len(a)), t["fecha_pub"]), reverse=True)
    if cands and len(a & toks(cands[0]["cuerpo"])) / max(1, len(a)) >= 0.75:
        t = cands[0]
        pres = next((m for m in t["miembros"] if m["rol"] == "Presidencia" and m["bloque"] == "titular"), None) or next((m for m in t["miembros"] if m["rol"] == "Presidencia"), None)
        sec = next((m for m in t["miembros"] if m["rol"] == "Secretaría" and m["bloque"] == "titular"), None)
        return dict(fecha=t["fecha_pub"], acto=t["id"], url=t["url"], firma=t["cargo_firmante"], firmante=t["firmante"],
                    presidente=pres["nombre"] if pres else "", cuerpo_pres=pres["cuerpo"] if pres else "",
                    secretario=sec["nombre"] if sec else "", origen="BOE")
    w = TW.get(nn(cuerpo))
    if w and w.get("presidente"):
        return dict(fecha=w.get("fecha", ""), acto=w.get("convocatoria", ""), url=w.get("fuente", ""), firma=w.get("organo_que_nombra", ""),
                    firmante=w.get("firmante", ""), presidente=w["presidente"], cuerpo_pres=w.get("cuerpo_presidente", ""),
                    secretario=w.get("secretario", ""), origen="Web oficial")
    return None


# ---------- escuelas ----------
ESC = jl(os.path.join(B, "seleccion/escuelas.jsonl"))
def escuela(texto):
    if not texto or texto == "None": return None
    for e in ESC:
        if any(texto[:120] == (o or "")[:120] for o in e.get("textos_origen", [])): return e
    k = toks(texto)
    best = max(ESC, key=lambda e: len(k & toks(e.get("escuela", ""))), default=None)
    return best if best and len(k & toks(best.get("escuela", ""))) >= 2 else None


# ---------- cuerpos ----------
rows = list(openpyxl.load_workbook(os.path.join(B, "datos/cuerpos_A1A2.xlsx"), read_only=True).worksheets[0].iter_rows(values_only=True))
data = [r for r in rows[12:] if any(r)]
def ambito(r):
    a = str(r[2] or ""); c = str(r[0] or "")
    if re.search("Guardia Civil", a + c): return "Guardia Civil"
    if re.search(r"(?i)polic", a) or re.search(r"(?i)polic[ií]a nacional", c): return "Policía Nacional"
    if a.startswith("Armed"): return "Fuerzas Armadas"
    if a == "AGE": return "Administración General del Estado"
    return None
out = []
for r in data:
    amb = ambito(r)
    if not amb: continue
    s = lambda i: ("" if r[i] in (None, "None") else str(r[i]))
    conv = convocante(s(6))
    nodos = []
    if conv["persona"]:
        nodos.append(ficha(conv["persona"], "Convoca y aprueba el temario", conv["organo"], fuente=s(17)))
    tri = tribunal(s(0))
    if tri and tri["presidente"]:
        nodos.append(ficha(tri["presidente"], "Preside el tribunal", f"Tribunal calificador ({tri['origen']}, {tri['fecha']})", fuente=tri["url"],
                           extra=dict(cuerpo_literal=tri["cuerpo_pres"], nombrado_tribunal_por=(tri["firma"] + (", " + tri["firmante"] if tri["firmante"] else "")).strip(", "),
                                      presidencias=pres_count.get(nn(tri["presidente"]), 1))))
    esc = escuela(s(13) or s(14))
    if esc and esc.get("titular"):
        n = ficha(esc["titular"], "Dirige la formación", esc.get("escuela", ""), fuente=esc.get("fuente_titular", ""))
        if not n.get("en_censo"):
            n.update(puesto=esc.get("cargo", ""), desde=esc.get("desde", ""), gob=gobierno(esc.get("desde", "")), boe=esc.get("boe_nombramiento", ""),
                     nombrado_por=esc.get("nombrado_por", ""), cese=esc.get("mecanismo", ""))
        nodos.append(n)
    lider = s(5)
    if lider and not any(nn(lider.split(",")[0]) == nn(n["nombre"]) for n in nodos):
        nombre_l = lider.split(",")[0].strip()
        if len(nombre_l.split()) >= 2:
            nodos.append(ficha(nombre_l, "Dirige el cuerpo u órgano gestor", lider[len(nombre_l):].strip(" ,")[:160], fuente=s(18)))
    ind = []
    if any(n.get("cese") == "Libre" and n["rol"] == "Preside el tribunal" for n in nodos): ind.append("trib_alto")
    if any(n.get("en_censo") and n["rol"] == "Preside el tribunal" for n in nodos): ind.append("trib_cargo")
    if any(n.get("pa") for n in nodos): ind.append("partido")
    if any(n.get("gob") == "Sánchez" for n in nodos): ind.append("nombr_actual")
    if any(n.get("presidencias", 1) > 1 for n in nodos if n["rol"] == "Preside el tribunal"): ind.append("repite")
    out.append(dict(cuerpo=s(0), grupo=s(1), ambito=amb, codigo=s(3), gestiona=s(4), convoca=s(6), temario=s(7), nombra_tribunal=s(9),
                    examen=s(10)[:400], formacion=s(12), imparte=s(13), dirige_formacion=s(14), aviso=s(15), fuente=s(17),
                    caveat=s(20)[:300], ministerio=(conv["p"]["m"] if conv["p"] else ""), tribunal=tri, nodos=nodos, ind=ind))

json.dump(dict(generado="13 oct 2026", cuerpos=out), open(os.path.join(B, "seleccion/seleccion.json"), "w"), ensure_ascii=False)
c = collections.Counter()
for o in out:
    c["cuerpos"] += 1; c["con convocante identificado"] += any(n["rol"].startswith("Convoca") for n in o["nodos"])
    c["con presidente de tribunal"] += any(n["rol"] == "Preside el tribunal" for n in o["nodos"])
    c["con director de formación"] += any(n["rol"] == "Dirige la formación" for n in o["nodos"])
    for i in o["ind"]: c["ind:" + i] += 1
print(dict(c)); print(collections.Counter(o["ambito"] for o in out))
