"""Tribunales a lo largo del tiempo (2004-2026) por cuerpo: quién preside cada convocatoria, repeticiones
y renovación tras cada cambio de Gobierno. Solo nombres y cargos publicados en el BOE; sin valoraciones.
Entrada: datos/tribunales_hist.jsonl (de 15_tribunales.py sobre datos/seleccion_2B_hist.jsonl), seleccion/seleccion.json
Salida: seleccion/historico.json"""
import os, re, json, collections, unicodedata
B = os.path.join(os.path.dirname(__file__), "..")
def nn(s):
    s = unicodedata.normalize("NFKD", str(s or "")).encode("ascii", "ignore").decode().lower()
    if "," in s and len(s.split(",")) == 2: a, b = s.split(","); s = b + " " + a
    return " ".join(re.sub(r"[^a-z ]", " ", s).split())
STOP = set("cuerpo cuerpos escala escalas de del la las los el y en sup superior especialidad esp".split())
def toks(s): return {w for w in nn(s).split() if w not in STOP and len(w) > 2}
def gobierno(f):
    if f >= "2018-06-02": return "Sánchez"
    if f >= "2011-12-21": return "Rajoy"
    if f >= "2004-04-17": return "Zapatero"
    return "Anterior"
T = [json.loads(l) for l in open(os.path.join(B, "datos/tribunales_hist.jsonl"))]
T = [t for t in T if t["cuerpo"] and any(m["rol"] == "Presidencia" for m in t["miembros"])]
cuerpos = json.load(open(os.path.join(B, "seleccion/seleccion.json")))["cuerpos"]
hist = {}
for c in cuerpos:
    a = toks(c["cuerpo"])
    if len(a) < 1: continue
    filas = []
    for t in T:
        if not a <= toks(t["cuerpo"]): continue  # todas las palabras distintivas del cuerpo deben estar
        p = next((m for m in t["miembros"] if m["rol"] == "Presidencia" and m["bloque"] == "titular"), None) or next((m for m in t["miembros"] if m["rol"] == "Presidencia"), None)
        if not p: continue
        filas.append(dict(fecha=t["fecha_pub"], gob=gobierno(t["fecha_pub"]), presidente=p["nombre"], cuerpo_pres=p["cuerpo"][:90], acto=t["id"],
                          firma=(t["cargo_firmante"] + (", " + t["firmante"] if t["firmante"] else "")).strip(", ")))
    # una fila por año y presidente (las modificaciones del mismo tribunal repiten)
    vistos, uni = set(), []
    for f in sorted(filas, key=lambda x: x["fecha"]):
        k = (f["fecha"][:4], nn(f["presidente"]))
        if k in vistos: continue
        vistos.add(k); uni.append(f)
    if not uni: continue
    cnt = collections.Counter(nn(f["presidente"]) for f in uni)
    por_gob = collections.defaultdict(set)
    for f in uni: por_gob[f["gob"]].add(nn(f["presidente"]))
    # renovación: presidentes de cada etapa que no presidieron en la etapa anterior
    reno = {}
    for prev, cur in (("Zapatero", "Rajoy"), ("Rajoy", "Sánchez")):
        if por_gob[cur] and por_gob[prev]:
            reno[cur] = round(100 * len(por_gob[cur] - por_gob[prev]) / len(por_gob[cur]))
    # primer tribunal tras cada cambio de Gobierno frente al último anterior
    cambios = {}
    for fecha_cambio, nuevo in (("2011-12-21", "Rajoy"), ("2018-06-02", "Sánchez")):
        antes = [f for f in uni if f["fecha"] < fecha_cambio]; despues = [f for f in uni if f["fecha"] >= fecha_cambio and f["gob"] == nuevo]
        if antes and despues:
            a_, d_ = antes[-1], despues[0]
            cambios[nuevo] = dict(antes=a_["presidente"], fecha_antes=a_["fecha"], despues=d_["presidente"], fecha_despues=d_["fecha"],
                                  mismo=nn(a_["presidente"]) == nn(d_["presidente"]))
    hist[c["cuerpo"]] = dict(serie=uni, cambios=cambios, n_convocatorias=len(uni), n_presidentes=len(cnt),
                             repetidores=[dict(nombre=next(f["presidente"] for f in uni if nn(f["presidente"]) == k), veces=v) for k, v in cnt.most_common() if v > 1],
                             por_gobierno={g: len(s) for g, s in por_gob.items()}, renovacion=reno)
# personas que más tribunales han presidido (todos los cuerpos y años)
glob_cnt = collections.Counter(); ejemplo = {}
for c, h in hist.items():
    for f in h["serie"]:
        k = nn(f["presidente"]); glob_cnt[k] += 1; ejemplo.setdefault(k, dict(nombre=f["presidente"], cuerpos=set(), gobs=set(), cuerpo_pres=f["cuerpo_pres"]))
        ejemplo[k]["cuerpos"].add(c); ejemplo[k]["gobs"].add(f["gob"])
top = [dict(nombre=ejemplo[k]["nombre"], veces=v, cuerpos=sorted(ejemplo[k]["cuerpos"]), etapas=sorted(ejemplo[k]["gobs"]), cuerpo_pres=ejemplo[k]["cuerpo_pres"])
       for k, v in glob_cnt.most_common(40) if v > 2]
resumen = {}
for nuevo in ("Rajoy", "Sánchez"):
    L = [h["cambios"][nuevo] for h in hist.values() if nuevo in h["cambios"]]
    resumen[nuevo] = dict(cuerpos=len(L), cambia=sum(1 for x in L if not x["mismo"]), sigue=sum(1 for x in L if x["mismo"]))
cruzan = [x for x in top if len(x["etapas"]) > 1]
json.dump(dict(cuerpos=hist, top=top, resumen=resumen), open(os.path.join(B, "seleccion/historico.json"), "w"), ensure_ascii=False)
print("primer tribunal tras cambio de Gobierno:", resumen)
print("cuerpos con serie", len(hist), "| convocatorias", sum(h["n_convocatorias"] for h in hist.values()),
      "| con serie desde Zapatero", sum(1 for h in hist.values() if h["por_gobierno"].get("Zapatero")),
      "| personas que presiden >2 veces", len(top))
