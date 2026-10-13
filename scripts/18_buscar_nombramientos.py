"""Para las personas de la cadena de selección sin 'quién le nombró', busca su último nombramiento o adjudicación
en los eventos del BOE (II.A, 2004-2011 y 2018-2026) y guarda puesto, fecha, acto y mecanismo.
Salida: seleccion/nombramientos_personas.json  {nombre_normalizado: {...}}"""
import os, re, json, unicodedata
B = os.path.join(os.path.dirname(__file__), "..")
def nn(s):
    s = unicodedata.normalize("NFKD", str(s or "")).encode("ascii", "ignore").decode().lower()
    if "," in s and len(s.split(",")) == 2: a, b = s.split(","); s = b + " " + a
    s = re.sub(r"\b(m|ma)\b", "maria", s)
    return " ".join(re.sub(r"[^a-z ]", " ", s).split())
D = json.load(open(os.path.join(B, "seleccion/seleccion.json")))["cuerpos"]
objetivo = {nn(n["nombre"]): n["nombre"] for c in D for n in c["nodos"] if not n.get("nombrado_por")}
# índice por apellidos para tolerar nombres compuestos abreviados
por_ap = {}
for k in objetivo:
    t = k.split()
    if len(t) >= 3: por_ap.setdefault(" ".join(t[-2:]), []).append(k)
res = {}
with open(os.path.join(B, "datos/eventos.jsonl")) as fh:
    for l in fh:
        if '"nombre": ""' in l: continue
        e = json.loads(l)
        if e["acto"] not in ("nombramiento", "adjudicacion_LD") or not e["nombre"] or e["nombre"] == "DESIERTO": continue
        k = nn(e["nombre"])
        dest = k if k in objetivo else None
        if not dest:
            t = k.split()
            for kk in por_ap.get(" ".join(t[-2:]), []) if len(t) >= 3 else []:
                a, b = set(t[:-2]), set(kk.split()[:-2])
                if a and b and (a <= b or b <= a): dest = kk; break
        if not dest: continue
        if re.search(r"(?i)nombran? funcionari|personal estatutario|en pr[aá]cticas|proceso selectivo|aspirantes", e["titulo"]): continue
        f = e["fecha_disp"] or e["fecha_pub"]
        if dest not in res or f > res[dest]["fecha"]:
            res[dest] = dict(puesto=(e.get("puesto_completo") or e["puesto"])[:200], fecha=f, boe=e["id"], rango=e.get("rango", ""),
                             mecanismo=e.get("mecanismo_literal", ""), condicion=e.get("condicion_literal", ""), departamento=e["departamento"])
json.dump(res, open(os.path.join(B, "seleccion/nombramientos_personas.json"), "w"), ensure_ascii=False, indent=1)
print("buscadas", len(objetivo), "| encontradas", len(res))

# ---------- Segunda pasada: buscador del BOE (todos los años) para las no encontradas ----------
import time, urllib.parse, html as H, importlib.util, requests, warnings
warnings.filterwarnings("ignore")
spec = importlib.util.spec_from_file_location("ext", os.path.join(B, "scripts/03_extraer.py")); ext = importlib.util.module_from_spec(spec); spec.loader.exec_module(ext)
S = requests.Session(); S.headers["User-Agent"] = "Mozilla/5.0"
def buscar(frase):
    q = {"campo[0]": "ORIS", "dato[0][2]": "2", "operador[0]": "and", "campo[1]": "TITULOS", "dato[1]": "", "operador[1]": "and",
         "campo[2]": "DEM", "dato[2]": "", "operador[2]": "and", "campo[3]": "DOC", "dato[3]": f'"{frase}"', "operador[3]": "and",
         "campo[4]": "NBOS", "dato[4]": "", "operador[4]": "and", "campo[5]": "NOF", "dato[5]": "", "operador[5]": "and",
         "campo[6]": "FPU", "dato[6][0]": "", "dato[6][1]": "", "operador[6]": "and", "page_hits": "50",
         "sort_field[0]": "FPU", "sort_order[0]": "desc", "sort_field[1]": "ORI", "sort_order[1]": "asc", "sort_field[2]": "REF", "sort_order[2]": "asc", "accion": "Buscar"}
    try: t = S.get("https://www.boe.es/buscar/boe.php?" + urllib.parse.urlencode(q), timeout=30).text
    except Exception: return []
    out = []
    for it in re.findall(r'(?s)<li class="resultado-busqueda">(.*?)</li>', t):
        ids = re.findall(r"BOE-A-\d{4}-\d+", it)
        if ids: out.append((ids[0], " ".join(H.unescape(re.sub(r"<[^>]+>", " ", it)).split())))
    return out
pend = [k for k in objetivo if k not in res]
for k in pend:
    nombre = objetivo[k]; t = nn(nombre).split()
    frase = " ".join(nombre.split()[-2:]) if len(t) >= 3 else nombre
    for bid, titulo in buscar(frase):
        if re.search(r"(?i)convoca|aprobad|admitid|excluid|aspirantes|tribunal|ascensos|jubila|cese|corrige|correcci", titulo): continue
        if not re.search(r"(?i)nombra|libre designaci|adjudica|destino|designa", titulo): continue
        f = os.path.join(B, "datos/boe_cache/xml", bid + ".xml")
        if not os.path.exists(f):
            r = S.get(f"https://www.boe.es/diario_boe/xml.php?id={bid}", timeout=30); time.sleep(0.5)
            if r.status_code != 200: continue
            open(f, "wb").write(r.content)
        evs = ext.procesar({"id": bid, "fecha_pub": "", "departamento": "", "titulo": ""})
        hit = next((e for e in evs if nn(e["nombre"]) == k or (len(t) >= 3 and nn(e["nombre"]).split()[-2:] == t[-2:])), None)
        if hit:
            res[k] = dict(puesto=(hit.get("puesto_completo") or hit["puesto"])[:200], fecha=hit["fecha_disp"], boe=bid, rango=hit.get("rango", ""),
                          mecanismo=hit.get("mecanismo_literal", ""), condicion=hit.get("condicion_literal", ""), departamento="", origen="buscador BOE")
            break
    time.sleep(1)
json.dump(res, open(os.path.join(B, "seleccion/nombramientos_personas.json"), "w"), ensure_ascii=False, indent=1)
print("tras buscador BOE: encontradas", len(res), "de", len(objetivo))
