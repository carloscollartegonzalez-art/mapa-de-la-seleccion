"""Extrae de las convocatorias y resoluciones de tribunales (sección II.B) quién preside cada tribunal calificador,
quién es el secretario, de qué cuerpo trata y quién firma el acto (el órgano que nombra el tribunal).
Entrada: datos/seleccion_2B.jsonl + XML. Salida: datos/tribunales.jsonl (una línea por acto con tribunal o firma).
Solo hechos publicados: nombre, cargo en el tribunal y cuerpo literal. Sin valoraciones."""
import os, re, json
from lxml import etree

B = os.path.join(os.path.dirname(__file__), "..")
TRAT = r"(?:D\.ª|D\.|Dña\.|don|doña)\s+"
NOM = r"([A-ZÁÉÍÓÚÑÜ][\wÁÉÍÓÚÑÜáéíóúñüçàèòï'’\-]+(?:\s+(?:de|del|de la|de los|y|i)?\s*[A-ZÁÉÍÓÚÑÜ][\wÁÉÍÓÚÑÜáéíóúñüçàèòï'’\-]+){1,5})"


def txt(el): return re.sub(r"\s+", " ", "".join(el.itertext())).strip()


def cuerpo_titulo(t):
    for pat in (r"(?i)\b(?:en|a)\s+(?:el|la|los|las)\s+((?:Cuerpo|Escala|Carrera|Escalas|Cuerpos)\b[^,;:(]*?)(?=,| por | mediante | del sistema| de acceso| y se | correspondiente|\.|$)",
                r"(?i)\b((?:Cuerpo|Escala|Carrera)\s+(?:de|del|Superior|General|T[eé]cnic|Facultativ|Ejecutiv|Especial)[^,;:(]*?)(?=,| por | mediante | del sistema| de acceso| y se |\.|$)"):
        m = re.search(pat, t)
        if m and len(m.group(1)) > 8: return m.group(1).strip()
    return ""


def firmante(paras):
    CARGO = r"(?:Subsecretari[oa]|Secretari[oa] de Estado|Secretari[oa] General|Director[a]? General|Director[a]?|President[ea]|Ministr[oa]|Delegad[oa]|Gerente|Rector[a]?)[^,]*"
    for t in reversed(paras):
        if not re.search(r"\d{4}\s*\.?\s*[–—-]", t): continue
        cola = re.split(r"\d{4}\s*\.?\s*[–—-]+\s*", t)[-1].strip().rstrip(".")
        ms = list(re.finditer(r"(?:El|La|el|la)\s+(" + CARGO + r"),\s*([A-ZÁÉÍÓÚÑ][^,]{3,80})$", cola))
        if ms:
            m = ms[-1]
            return dict(firma=cola, firmante=m.group(2).strip(), cargo_firmante=m.group(1).strip())
        if cola: return dict(firma=cola, firmante=cola.split(",")[-1].strip(), cargo_firmante="")
    return dict(firma="", firmante="", cargo_firmante="")


def miembros_parrafo(texto):
    """Busca bloques 'Tribunal titular/suplente' y dentro 'Presidente: Nombre, Cuerpo.' / 'Secretaria: ...'"""
    out = []
    # trocear por encabezados titular/suplente para saber a qué bloque pertenece cada cargo
    marcas = [(m.start(), "suplente" if "suplente" in m.group(0).lower() else "titular")
              for m in re.finditer(r"(?i)tribunal(?: calificador)?(?: n\.?º ?\d+)?\s*(titular|suplente)|(?:miembros|vocales) (titulares|suplentes)", texto)]
    for m in re.finditer(r"(?i)\b(President[ea]|Secretari[oa])\s*(?:titular|suplente)?\s*:\s*(?:" + TRAT + r")?" + NOM + r"\s*[,.(]\s*([^.;]{0,160})", texto):
        pos = m.start()
        bloque = "titular"
        for p, b in marcas:
            if p <= pos: bloque = b
        cargo = "Presidencia" if m.group(1).lower().startswith("president") else "Secretaría"
        cuerpo = m.group(3).strip()
        if not re.search(r"(?i)cuerpo|escala|carrera|catedr|profesor|magistrad|fiscal|letrad|abogad|general|coronel|comisari|inspector|personal|funcionari", cuerpo): cuerpo = ""
        out.append(dict(rol=cargo, bloque=bloque, nombre=m.group(2).strip(), cuerpo=cuerpo))
    return out


def miembros_tabla(root):
    out = []
    for tab in root.iter("table"):
        bloque = "titular"
        for tr in tab.iter("tr"):
            celdas = [txt(td) for td in tr.findall("td")]
            linea = " ".join(celdas)
            if re.search(r"(?i)suplente", linea) and len(celdas) <= 2: bloque = "suplente"
            if re.search(r"(?i)titular", linea) and len(celdas) <= 2: bloque = "titular"
            for i, c in enumerate(celdas):
                if re.fullmatch(r"(?i)(president[ea]|secretari[oa])(\s*(titular|suplente))?:?", c.strip()) and i + 1 < len(celdas):
                    nombre = celdas[i + 1]; cuerpo = celdas[i + 2] if i + 2 < len(celdas) else ""
                    if re.search(r"(?i)suplente", c): bloque_c = "suplente"
                    else: bloque_c = bloque
                    out.append(dict(rol="Presidencia" if c.lower().startswith("president") else "Secretaría", bloque=bloque_c,
                                    nombre=re.sub(r"^(?i:D\.ª|D\.|Dña\.|don|doña)\s+", "", nombre).strip(), cuerpo=cuerpo.strip()))
    return out


import sys
ENTRADA = sys.argv[1] if len(sys.argv) > 1 else "datos/seleccion_2B.jsonl"
SALIDA = sys.argv[2] if len(sys.argv) > 2 else "datos/tribunales.jsonl"
sel = [json.loads(l) for l in open(os.path.join(B, ENTRADA))]
n = 0
with open(os.path.join(B, SALIDA), "w") as fh:
    for s in sel:
        f = os.path.join(B, "datos/boe_cache/xml", s["id"] + ".xml")
        if not os.path.exists(f): continue
        try: root = etree.parse(f).getroot()
        except Exception: continue
        tx = root.find("texto")
        if tx is None: continue
        paras = [txt(p) for p in tx.iter("p")]
        texto = " ".join(paras)
        md = root.find("metadatos")
        fd = md.findtext("fecha_disposicion") or ""
        miembros = miembros_tabla(tx) or miembros_parrafo(texto)
        # quitar duplicados
        vistos, mm = set(), []
        for x in miembros:
            k = (x["rol"], x["bloque"], x["nombre"])
            if k not in vistos and len(x["nombre"].split()) >= 2: vistos.add(k); mm.append(x)
        fi = firmante(paras)
        rec = dict(id=s["id"], fecha_pub=s["fecha_pub"], fecha_disp=f"{fd[:4]}-{fd[4:6]}-{fd[6:]}" if fd else "", departamento=s["departamento"],
                   tipo=s["tipo"], titulo=s["titulo"], cuerpo=cuerpo_titulo(s["titulo"]) or cuerpo_titulo(texto[:1500]),
                   numero_tribunales=len({x["bloque"] for x in mm}), miembros=mm, **fi,
                   url=f"https://www.boe.es/diario_boe/txt.php?id={s['id']}")
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n"); n += 1
print("actos", n)
