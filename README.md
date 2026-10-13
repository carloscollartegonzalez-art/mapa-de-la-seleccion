# Mapa de la Selección

Trabajo de Extramuros: para cada cuerpo de funcionarios del Estado (Administración General del Estado, Fuerzas Armadas, Guardia Civil y Policía Nacional), la cadena de control de su acceso y formación: quién convoca y aprueba el temario, quién preside el tribunal, quién dirige la formación previa al ejercicio y quién nombró a cada una de esas personas (acto del BOE, fecha y Gobierno).

> **Repositorio privado.** Contiene nombres de personas. Ver «Límites».

## Contenido

| Ruta | Qué es |
|---|---|
| `dashboard/mapa-de-la-seleccion.html` | Dashboard autocontenido (publicado como artifact privado) |
| `seleccion/seleccion.json` | Datos del dashboard: 142 cuerpos con su cadena de control |
| `seleccion/tribunales_web.jsonl` | Tribunales localizados fuera de la extracción automática |
| `seleccion/escuelas.jsonl` | Escuelas y órganos de formación con su titular y nombramiento |
| `seleccion/nombramientos_personas.json` | Último nombramiento publicado de presidentes de tribunal y otros responsables |
| `datos/cuerpos_A1A2.xlsx` | Documento de origen de los cuerpos (Google Sheet «Spain: A1/A2 and justice - bodies, selection and training governance», 13 oct 2026) |
| `datos/seleccion_2B.jsonl`, `datos/tribunales.jsonl` | Convocatorias y tribunales del BOE (sección II.B, nov-2023 a oct-2026) y su extracción |
| `scripts/14…18` | Descarga y extracción de tribunales, construcción de la cadena, búsqueda de nombramientos, dashboard |

## Dependencias

Se genera desde el proyecto del **Mapa del Relevo** (repositorio `mapa-del-relevo`), porque reutiliza su caché del BOE, su extractor (`scripts/02_seleccion_xml.py`, `scripts/03_extraer.py`), el censo de titulares y el estilo de su dashboard (`dashboard/plantilla.html`, `dashboard/mapa-del-relevo.html`). Para regenerarlo, colocar estos scripts en ese proyecto y ejecutar en orden 14, 15, 18, 16 y 17.

## Límites

- Muestra quién controla cada eslabón y quién le nombró, con hechos publicados. No prueba que se seleccione o promocione a personas afines.
- No se etiqueta la ideología de funcionarios ni de miembros de tribunal. «Partido» solo aparece para quien ocupa un cargo del censo y lo ha hecho público.
- «Último nombramiento publicado» no siempre es el puesto actual. Los destinos militares y de la Guardia Civil se publican en boletines propios (BOD, BOGC) y pueden faltar.
- Uso interno. No publicar ni difundir sin revisión legal.
