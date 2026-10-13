"""Para cada persona de la cadena de selección: nombramientos publicados en el BOE en la etapa Zapatero (2004-04-17→2011-12-20)
y en la etapa Sánchez (2018-06-02→), desde los eventos extraídos (sección II.A). Coincidencia por nombre: es una pista;
para los titulares del censo se usa además la revisión Zapatero–Sánchez. Salida: seleccion/etapas_personas.json"""
import os, re, json, unicodedata
B = os.path.join(os.path.dirname(__file__), "..")
def nn(s):
    s = unicodedata.normalize("NFKD", str(s or "")).encode("ascii", "ignore").decode().lower()
    if "," in s and len(s.split(",")) == 2: a, b = s.split(","); s = b + " " + a
    s = re.sub(r"\b(m|ma)\b", "maria", s)
    return " ".join(re.sub(r"[^a-z ]", " ", s).split())
D = json.load(open(os.path.join(B, "seleccion/seleccion.json")))["cuerpos"]
obj = {}
for c in D:
    for n in c["nodos"]:
        k = nn(re.sub(r"(?i)^(coronel|teniente coronel|general)\s+(don|doña)?\s*", "", n["nombre"]))
        if len(k.split()) >= 3: obj[k] = n["nombre"]
res = {k: dict(zp=[], sanchez=[]) for k in obj}
SKIP = re.compile(r"(?i)nombran? funcionari|personal estatutario|en pr[aá]cticas|proceso selectivo|aspirantes|tribunal")
with open(os.path.join(B, "datos/eventos.jsonl")) as fh:
    for l in fh:
        e = json.loads(l)
        if e["acto"] not in ("nombramiento", "adjudicacion_LD") or not e["nombre"]: continue
        k = nn(e["nombre"])
        if k not in res or SKIP.search(e["titulo"]): continue
        f = e["fecha_disp"] or e["fecha_pub"]
        x = dict(fecha=f, puesto=(e.get("puesto_completo") or e["puesto"])[:140], boe=e["id"])
        if "2004-04-17" <= e["fecha_pub"] <= "2011-12-20": res[k]["zp"].append(x)
        elif e["fecha_pub"] >= "2018-06-02": res[k]["sanchez"].append(x)
for k in res:
    for et in ("zp", "sanchez"):
        res[k][et] = sorted(res[k][et], key=lambda x: x["fecha"])[-3:]
json.dump(res, open(os.path.join(B, "seleccion/etapas_personas.json"), "w"), ensure_ascii=False, indent=1)
print("personas", len(res), "| con cargos ZP", sum(1 for v in res.values() if v["zp"]), "| con Sánchez", sum(1 for v in res.values() if v["sanchez"]),
      "| ambas", sum(1 for v in res.values() if v["zp"] and v["sanchez"]))
