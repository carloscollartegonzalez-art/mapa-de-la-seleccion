# Cadena de control de la selección de un cuerpo — instrucciones comunes (13-oct-2026)

Para cada cuerpo del lote, documenta con fuentes oficiales quién controla su acceso y su formación, y quién nombró a cada responsable.

## Qué buscar por cuerpo
1. **Convoca y aprueba el temario**: órgano (p. ej. Comisión de Selección, Subsecretaría, Dirección General de Función Pública de la comunidad) y su titular actual (13-oct-2026).
2. **Tribunal**: el de la convocatoria más reciente (2023-2026): presidente/a y secretario/a con su cuerpo o cargo literal, quién lo nombra (órgano y firmante) y fuente.
3. **Formación previa al ejercicio**: escuela u órgano (Escuela Judicial, Centro de Estudios Jurídicos, INAP, escuela autonómica de administración pública…) y su director/a actual.
4. **Dirige el cuerpo**, si hay un órgano propio (p. ej. CGPJ, Fiscalía General, Abogacía General).
Para cada persona: cargo, fecha de nombramiento, acto (BOE o boletín autonómico, con id o URL), mecanismo literal y **quién la nombró** (firmante, o «Consejo de Gobierno / Consejo de Ministros a propuesta de…», o «Pleno del CGPJ»). Si el nombramiento lo hace un gobierno autonómico, anota el presidente de ese gobierno en esa fecha (dato público), sin atribuir partido a la persona nombrada.

## Reglas
- Nada sin fuente. Vacío = no localizado; explícalo en notas.
- Solo hechos publicados. No etiquetes la ideología ni la afinidad de nadie. No anotes afiliación de funcionarios, jueces, fiscales ni miembros de tribunal.
- No afirmes que exista selección de afines: el objetivo es documentar la cadena.
- Fuentes: BOE (XML https://www.boe.es/diario_boe/xml.php?id=..., buscador https://www.boe.es/buscar/boe.php — campos `campo[3]=DOC` para texto completo), boletines autonómicos (BOJA, DOGC, DOG, BOCM, DOGV, BOPV, BON, BOA, BOC, BOCYL, DOE, BORM, BOPA, BOIB, BOR, BOCCE, BOME), CGPJ (poderjudicial.es), Fiscalía (fiscal.es), webs oficiales. curl -m 30 con User-Agent de navegador. WebSearch está agotado: no lo uses. No lances subagentes.

## Salida
JSON Lines en `seleccion/cadena_<lote>.jsonl`, una línea por cuerpo del lote, escribiendo cada 3 cuerpos. Claves exactas:
cuerpo, ambito, comunidad, convoca, tribunal, formacion, dirige_cuerpo, notas
- `convoca`, `formacion`, `dirige_cuerpo`: objeto {organo, titular, cargo, desde, acto, mecanismo, nombrado_por, gobierno_que_nombra, fuente} (vacío {} si no aplica).
- `tribunal`: objeto {fecha, acto, presidente, cuerpo_presidente, secretario, cuerpo_secretario, organo_que_nombra, firmante, fuente}.
- `comunidad`: solo en autonómicos.
Valida al final (JSON válido, una línea por cuerpo). Respuesta final: resumen breve (cobertura por eslabón y problemas).
