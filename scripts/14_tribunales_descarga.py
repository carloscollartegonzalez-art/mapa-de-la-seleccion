"""Selecciona en los sumarios (sección II.B, órganos del Estado, desde 2023-11-20) convocatorias de procesos selectivos
y nombramientos de tribunales, y descarga su XML. Salida: datos/seleccion_2B.jsonl + datos/boe_cache/xml/<id>.xml"""
import os, re, json, glob, sys
sys.argv = ["x"]
B = os.path.join(os.path.dirname(__file__), "..")
ns = {"__file__": os.path.join(B, "scripts/02_seleccion_xml.py")}
exec(open(os.path.join(B, "scripts/02_seleccion_xml.py")).read().split("sel = list(items())")[0], ns)
TRIB = re.compile(r"(?i)tribunal(es)? calificador|nombra(n)? (a )?(los )?(miembros del )?tribunal|composici[oó]n del tribunal|[oó]rgano de selecci|designan? (los )?tribunal")
CONV = re.compile(r"(?i)convoca(n)? (el )?proceso selectivo|convoca(n)? (las )?pruebas selectivas|convoca(n)? procesos selectivos")
sel = []
for f in sorted(glob.glob(os.path.join(B, "datos/boe_cache/sumarios/202[3-6]*.json"))):
    fecha = os.path.basename(f)[:8]
    if fecha < "20231120": continue
    d = json.load(open(f))["data"]["sumario"].get("diario", [])
    for ctx, it in ns["_walk"](d, {}):
        if ctx.get("seccion") != "2B": continue
        dep = ctx.get("departamento", "")
        # aquí sí entran Cortes, CGPJ, Tribunal Constitucional y Ministerio Fiscal (órganos que seleccionan cuerpos propios)
        if re.search(r"UNIVERSIDAD|COMUNIDAD|COMUNITAT|ADMINISTRACI[ÓO]N LOCAL|CIUDAD DE|JUNTA ELECTORAL", dep): continue
        t = it["titulo"]
        tipo = "tribunal" if TRIB.search(t) else "convocatoria" if CONV.search(t) else ""
        if not tipo: continue
        sel.append(dict(id=it["identificador"], fecha_pub=f"{fecha[:4]}-{fecha[4:6]}-{fecha[6:]}", departamento=dep, tipo=tipo, titulo=t))
with open(os.path.join(B, "datos/seleccion_2B.jsonl"), "w") as fh:
    for s in sel: fh.write(json.dumps(s, ensure_ascii=False) + "\n")
print("seleccionadas", len(sel), flush=True)
from concurrent.futures import ThreadPoolExecutor
st = {}
with ThreadPoolExecutor(3) as ex:
    for r in ex.map(ns["fetch"], sel): st[r] = st.get(r, 0) + 1
print("FIN", st, flush=True)
