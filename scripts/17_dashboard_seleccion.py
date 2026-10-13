"""Genera el dashboard «Mapa de la Selección» (Extramuros) a partir de seleccion/seleccion.json.
Reutiliza los estilos de dashboard/plantilla.html. Salida: dashboard/mapa-de-la-seleccion.html"""
import os, re, json, base64

B = os.path.join(os.path.dirname(__file__), "..")
base = open(os.path.join(B, "dashboard/plantilla.html")).read()
estilos = re.search(r"<style>(.*?)</style>", base, re.S).group(1)
logo = "data:image/png;base64," + base64.b64encode(open(os.path.join(B, "dashboard/logo_em.png"), "rb").read()).decode()
data = json.load(open(os.path.join(B, "seleccion/seleccion.json")))
_h = os.path.join(B, "seleccion/historico.json")
if os.path.exists(_h):
    H = json.load(open(_h))
    for c in data["cuerpos"]:
        h = H["cuerpos"].get(c["cuerpo"])
        if h: c["hist"] = dict(serie=[dict(f=x["fecha"], g=x["gob"], p=x["presidente"]) for x in h["serie"]], cambios=h.get("cambios", {}), rep=h["repetidores"][:3])
    data["hist_resumen"] = H.get("resumen", {}); data["hist_top"] = H.get("top", [])[:20]

extra = """
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(360px,1fr));gap:14px;margin-bottom:24px}
.card{background:var(--surface);border:1px solid var(--line);border-radius:8px;display:flex;flex-direction:column}
.card > header{padding:12px 14px;border-bottom:1px solid var(--line);display:flex;gap:8px;align-items:baseline;flex-wrap:wrap}
.card h3{font-family:var(--serif);font-weight:600;color:var(--ink);font-size:17px;margin:0;flex:1 1 200px;text-wrap:balance}
.card .meta{font-size:12px;color:var(--muted);width:100%}
.gr{font-size:11.5px;font-weight:600;border-radius:4px;padding:1px 6px;background:var(--zp-bg);color:var(--zp)}
.chain{padding:6px 14px 10px;display:flex;flex-direction:column}
.step{display:grid;grid-template-columns:118px 1fr;gap:4px 12px;padding:9px 0;border-bottom:1px dashed var(--line)}
.step:last-child{border-bottom:0}
.step .r{font-size:11px;letter-spacing:.05em;text-transform:uppercase;color:var(--muted);padding-top:2px}
.step .who{font-weight:600;color:var(--ink)}
.step .pos{color:var(--text);font-size:13px}
.step .by{color:var(--muted);font-size:12.5px}
.step .by b{color:var(--text);font-weight:600}
.step .fl{margin-top:4px;display:flex;gap:5px;flex-wrap:wrap}
.step.vacio .who{color:var(--muted);font-weight:400;font-style:italic}
.ind{display:flex;gap:6px;flex-wrap:wrap;padding:0 14px 10px}
.bd.ia{color:var(--jud);background:var(--jud-bg)} .bd.ic{color:var(--discr);background:var(--discr-bg)} .bd.ir{color:var(--mand);background:var(--mand-bg)}
.bd.ip{color:var(--par);background:var(--par-bg)} .bd.ig{color:var(--zp);background:var(--zp-bg)}
.c-ia{color:var(--jud)} .c-ic{color:var(--discr)} .c-ir{color:var(--mand)} .c-ip{color:var(--par)} .c-ig{color:var(--zp)}
.chip[aria-pressed="true"].c-ia{background:var(--jud-bg)} .chip[aria-pressed="true"].c-ic{background:var(--discr-bg)} .chip[aria-pressed="true"].c-ir{background:var(--mand-bg)}
.chip[aria-pressed="true"].c-ip{background:var(--par-bg)} .chip[aria-pressed="true"].c-ig{background:var(--zp-bg)}
.card details{border-top:1px solid var(--line);padding:8px 14px;font-size:12.5px;color:var(--muted)}
.card details summary{cursor:pointer;color:var(--ink);font-weight:600}
.card details p{margin:6px 0}
.llave{background:var(--surface);border:1px solid var(--line);border-radius:8px;margin:14px 0 18px}
.llave > summary{padding:12px 16px;cursor:pointer;list-style:none;display:flex;align-items:baseline;gap:10px}
.llave > summary::-webkit-details-marker{display:none}
.llave > summary h2{font-family:var(--serif);font-weight:600;color:var(--ink);font-size:20px;margin:0}
.llave > summary::after{content:"▾";margin-left:auto;color:var(--muted)}
.llave:not([open]) > summary::after{transform:rotate(-90deg)}
.lrow{display:grid;grid-template-columns:44px minmax(0,1.6fr) minmax(0,1.8fr) minmax(0,1.4fr);gap:10px;align-items:center;padding:8px 16px;border-top:1px solid var(--line);cursor:pointer}
.lrow:hover{background:var(--sunk)}
.lrow .num{font-family:var(--serif);font-size:22px;color:var(--ink);font-variant-numeric:tabular-nums;text-align:right}
.lrow .nm{font-weight:600;color:var(--ink)} .lrow .ps{font-size:12.5px;color:var(--muted)}
.lrow .rl{font-size:12px;color:var(--text)}
.lrow .bar2{height:6px;background:var(--gold);border-radius:3px;margin-top:4px}
@media (max-width:760px){ .cards{grid-template-columns:1fr} .step{grid-template-columns:1fr} .lrow{grid-template-columns:40px 1fr} .lrow .rl,.lrow .mk{grid-column:2} }
"""

html = """<meta charset="utf-8">
<title>Mapa de la Selección</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=EB+Garamond:wght@500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>""" + estilos + extra + """</style>

<header class="top">
  <div class="wrap">
    <div class="logo"><img src="__LOGO__" alt="Extramuros"></div>
    <div>
      <h1>Mapa de la Selección</h1>
      <div class="sub">Quién controla el acceso y la formación de cada cuerpo de funcionarios (Estado, Justicia, órganos constitucionales, entidades locales, universidades y comunidades autónomas), y quién nombró a cada responsable.</div>
    </div>
    <div class="meta"><span>Foto a <b>13 oct 2026</b></span><span>Fuentes: BOE, webs oficiales y el censo del Mapa del Relevo</span></div>
  </div>
  <div class="rule"></div>
</header>

<main class="wrap">
  <details class="aviso" id="aviso" open>
    <summary>Nota de uso y límites</summary>
    <ul>
      <li>Muestra la cadena de control de cada cuerpo: quién convoca y aprueba el temario, quién preside el tribunal, quién dirige la formación previa al ejercicio y quién nombró a cada uno. Son hechos publicados en el BOE o en webs oficiales.</li>
      <li>No prueba que se seleccione o se promocione a personas afines. Para afirmarlo harían falta otros datos (resultados, composición de tribunales a lo largo del tiempo, valoración de ejercicios). Los indicadores señalan dónde mirar, no conclusiones.</li>
      <li>Los miembros de tribunal son en su mayoría funcionarios de carrera. No se etiqueta su ideología. «Partido» solo aparece cuando la persona ocupa un cargo del censo y lo ha hecho público (candidatura, cargo electo o de partido).</li>
      <li>Historia de tribunales: convocatorias y nombramientos de tribunal del BOE (sección II.B) desde 2004; los formatos antiguos y los anexos en imagen reducen la cobertura de algunos años (2012 especialmente). Un mismo nombre en años distintos se trata como la misma persona.</li>
      <li>Cobertura: tribunales identificados solo cuando se publican en el BOE o en webs oficiales; muchas convocatorias recientes los publican fuera del BOE. «No publicado» significa pendiente.</li>
      <li>Uso restringido a las personas destinatarias: no publicar ni reenviar.</li>
    </ul>
  </details>

  <details class="legend" id="legend" open>
    <summary><h2>Cómo leer el mapa</h2><span class="hint lg-hint">indicadores</span></summary>
    <div class="lg-grid">
      <div class="lg-col">
        <h3>Indicadores del cuerpo</h3>
        <p><span class="bd ia">Tribunal: alto cargo</span> Quien preside el tribunal ocupa un alto cargo de libre nombramiento.</p>
        <p><span class="bd ic">Tribunal: cargo directivo</span> Quien preside el tribunal ocupa un puesto directivo del censo (subdirección, gabinete, división…).</p>
        <p><span class="bd ir">Repite presidencia</span> La misma persona preside más de un tribunal en las convocatorias publicadas.</p>
      </div>
      <div class="lg-col">
        <h3>&nbsp;</h3>
        <p><span class="bd ip">Partido en la cadena</span> Alguien de la cadena tiene un vínculo de partido público y con fuente.</p>
        <p><span class="bd ig">Nombrado con Sánchez</span> Alguien de la cadena tiene nombramientos publicados en el BOE desde junio de 2018.</p>
        <p><span class="bd zpd">Nombrado con ZP</span> Alguien de la cadena tuvo nombramientos publicados con Zapatero (2004-2011).</p>
        <p><span class="bd zpa">Con ZP y con Sánchez</span> La misma persona tiene nombramientos en las dos etapas. Coincidencia por nombre en el BOE: para quien no está en el censo es una pista, no una identidad confirmada. Una misma persona puede marcar muchos cuerpos (por ejemplo, la Subsecretaría de Defensa convoca los 30 cuerpos militares).</p>
        <p><span class="pill Sin">No publicado</span> El dato no aparece en el BOE ni en la web oficial consultada.</p>
      </div>
    </div>
  </details>

  <details class="llave" id="llave" open>
    <summary><h2>Quién tiene la llave</h2><span class="hint">personas que controlan 3 o más cuerpos (convocan, presiden el tribunal o dirigen la formación) · pulsa para ver sus cuerpos</span></summary>
    <div id="llaveList"></div>
  </details>

  <details class="llave" id="histPanel">
    <summary><h2>Tribunales 2004-2026</h2><span class="hint">quién ha presidido los tribunales a lo largo del tiempo, según el BOE</span></summary>
    <div id="histBody" style="padding:4px 16px 14px"></div>
  </details>

  <section class="filters" aria-label="Filtros">
    <button type="button" class="btn ftoggle" id="ftoggle" aria-expanded="false" aria-controls="fbody">Filtros <span class="tabn" id="fcount"></span></button>
    <div id="fbody">
    <div class="frow">
      <div class="field"><label for="q">Buscar</label><input type="search" id="q" placeholder="Cuerpo o persona"></div>
      <div class="field"><label for="fAmb">Ámbito</label><select id="fAmb"></select></div>
      <div class="field"><label for="fGr">Grupo</label><select id="fGr"></select></div>
      <div class="field"><label for="fMin">Ministerio que convoca</label><select id="fMin"></select></div>
      <div class="field"><label for="fCom">Comunidad autónoma</label><select id="fCom"></select></div>
    </div>
    <div class="frow">
      <div class="chips" id="cInd" role="group" aria-label="Indicadores"></div>
      <button class="btn reset" id="reset" type="button">Quitar filtros</button>
    </div>
    </div>
  </section>

  <div class="sum" id="sum" aria-live="polite"></div>
  <section class="cards" id="cards"></section>

  <footer class="notes">
    <p>Fuentes: documento «Spain: A1/A2 and justice - bodies, selection and training governance» (13 oct 2026), BOE (convocatorias y tribunales, sección II.B, nov-2023 a oct-2026; nombramientos, sección II.A), webs oficiales y censo del Mapa del Relevo. Elaborado por Extramuros.</p>
  </footer>
</main>

<script type="application/json" id="data">/*__DATA__*/</script>
<script>
(function(){
  const D = JSON.parse(document.getElementById('data').textContent).cuerpos;
  const $ = s => document.querySelector(s);
  const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
  const norm = s => String(s||'').normalize('NFD').replace(/[\\u0300-\\u036f]/g,'').toLowerCase();
  const fmt = d => d ? d.split('-').reverse().join('/') : '';
  const shortMin = m => (m||'').replace(/^Ministerio (de la |del |de |para la )?/,'');
  const IND = [['trib_alto','Tribunal: alto cargo','ia'],['trib_cargo','Tribunal: cargo directivo','ic'],['repite','Repite presidencia','ir'],['partido','Partido en la cadena','ip'],['nombr_actual','Nombrado con Sánchez','ig'],['con_zp','Nombrado con ZP','ig'],['zp_y_s','Con ZP y con Sánchez','ip']];
  const st = {q:'', amb:'', gr:'', min:'', com:'', ind:new Set()};
  const opts = (sel, vals, all) => { sel.innerHTML = `<option value="">${all}</option>` + vals.map(v=>`<option value="${esc(v)}">${esc(v)}</option>`).join(''); };
  opts($('#fAmb'), [...new Set(D.map(c=>c.ambito))], 'Todos');
  opts($('#fGr'), [...new Set(D.map(c=>c.grupo).filter(Boolean))].sort(), 'Todos');
  const mins = [...new Set(D.map(c=>c.ministerio).filter(Boolean))].sort((a,b)=>a.localeCompare(b,'es'));
  $('#fMin').innerHTML = '<option value="">Todos</option>' + mins.map(m=>`<option value="${esc(m)}">${esc(shortMin(m))}</option>`).join('');
  opts($('#fCom'), [...new Set(D.map(c=>c.comunidad).filter(Boolean))].sort((a,b)=>a.localeCompare(b,'es')), 'Todas');
  $('#cInd').innerHTML = IND.map(([k,t,c])=>`<button type="button" class="chip c-${c}" data-k="${k}" aria-pressed="false"><span class="dot"></span>${t}</button>`).join('');

  function match(c){
    if (st.amb && c.ambito!==st.amb) return false;
    if (st.gr && c.grupo!==st.gr) return false;
    if (st.min && c.ministerio!==st.min) return false;
    if (st.com && c.comunidad!==st.com) return false;
    for (const k of st.ind) if (!c.ind.includes(k)) return false;
    if (st.q){ const t=norm(st.q); if (!norm(c.cuerpo+' '+c.nodos.map(n=>n.nombre+' '+(n.puesto||'')).join(' ')+' '+(c.hist?c.hist.serie.map(x=>x.p).join(' '):'')).includes(t)) return false; }
    return true;
  }
  function marcas(n){
    const b=[];
    if (n.pa) b.push(`<span class="bd par" title="${esc(n.pa)}">Partido</span>`);
    if (n.jud) b.push(`<span class="bd jud">Judicial${n.jud==='prensa'?' <span class="ded">· prensa</span>':''}</span>`);
    const lista = L => (L||[]).map(x=>`${fmt(x.fecha)} ${x.puesto}`).join(' · ');
    if (n.con_zp && n.con_s) b.push(`<span class="bd zpa" title="${esc(lista(n.cargos_zp))}">Con ZP y con Sánchez</span>`);
    else if (n.con_zp) b.push(`<span class="bd zpd" title="${esc(lista(n.cargos_zp))}">Nombrado con ZP</span>`);
    else if (n.con_s) b.push(`<span class="bd ig" title="${esc(lista(n.cargos_s))}">Nombrado con Sánchez</span>`);
    if (n.cese==='Libre') b.push('<span class="pill Libre">Cese libre</span>');
    if (n.presidencias>1) b.push(`<span class="bd ir">Preside ${n.presidencias} tribunales</span>`);
    return b.join(' ');
  }
  const link = (u,t) => u && /^https?:/.test(u) ? `<a href="${esc(u.split(/[\\s;]+/)[0])}" target="_blank" rel="noopener">${esc(t)}</a>` : '';
  function paso(rol, n, vacio){
    if (!n) return `<div class="step vacio"><div class="r">${rol}</div><div><div class="who">${vacio}</div></div></div>`;
    const boe = (n.boe||'').match(/BOE-A-\\d{4}-\\d+/);
    const por = n.nombrado_por ? `nombrado por <b>${esc(n.nombrado_por)}</b>` : '';
    const cuando = n.desde ? `el ${fmt(n.desde)}${n.gob?` (${esc(n.gob)})`:''}${n.gobierno_que_nombra?` (gobierno de ${esc(n.gobierno_que_nombra)})`:''}` : '';
    const trib = n.nombrado_tribunal_por ? `<div class="by">Designado para el tribunal por <b>${esc(n.nombrado_tribunal_por)}</b></div>` : '';
    return `<div class="step"><div class="r">${rol}</div><div>
      <div class="who">${esc(n.nombre)}</div>
      <div class="pos">${esc(n.puesto || n.cuerpo_literal || n.organo || '')}</div>
      ${n.ultimo?`<div class="by">${n.ultimo_puesto?`Último nombramiento publicado en el BOE: <b>${esc(n.ultimo_puesto)}</b>`:'Último acto de nombramiento publicado en el BOE'}</div>`:''}
      ${(por||cuando)?`<div class="by">${[por,cuando].filter(Boolean).join(' ')}${boe?` · <a class="mono" href="https://www.boe.es/diario_boe/txt.php?id=${boe[0]}" target="_blank" rel="noopener">${boe[0]}</a>`:''}</div>`:''}
      ${trib}
      ${(n.cargos_zp&&n.cargos_zp.length)?`<div class="by">Con ZP: ${esc(n.cargos_zp.map(x=>x.puesto+' ('+x.fecha.slice(0,4)+')').join(' · '))}</div>`:''}
      <div class="fl">${marcas(n)} ${link(n.fuente,'fuente')}</div></div></div>`;
  }
  function render(){
    const R = D.filter(match);
    const cnt = k => R.filter(c=>c.ind.includes(k)).length;
    $('#sum').innerHTML = [[R.length,'cuerpos'],[R.filter(c=>c.nodos.some(n=>n.rol==='Preside el tribunal')).length,'con presidente de tribunal identificado'],[cnt('trib_alto')+cnt('trib_cargo')-R.filter(c=>c.ind.includes('trib_alto')&&c.ind.includes('trib_cargo')).length,'tribunales presididos por un cargo del censo'],[cnt('repite'),'con presidencia repetida'],[cnt('partido'),'con partido en la cadena'],[new Set(R.flatMap(c=>c.nodos.filter(n=>n.con_zp&&n.con_s).map(n=>n.nombre))).size,'personas con ZP y con Sánchez']].map(([v,t])=>`<span><b>${v}</b>${t}</span>`).join('');
    $('#cards').innerHTML = R.length ? R.map(c=>{
      const by = r => c.nodos.find(n=>n.rol===r);
      const ind = c.ind.filter(k=>k!=='nombr_actual').map(k=>{ const i=IND.find(x=>x[0]===k); return `<span class="bd ${i[2]}">${i[1]}</span>`; }).join(' ');
      return `<article class="card"><header><h3>${esc(c.cuerpo)}</h3>${c.grupo?`<span class="gr">${esc(c.grupo)}</span>`:''}<div class="meta">${esc(c.ambito)}${c.comunidad?' · '+esc(c.comunidad):''}${c.ministerio?' · '+esc(shortMin(c.ministerio)):''}</div></header>
        ${ind?`<div class="ind" style="padding-top:10px">${ind}</div>`:''}
        <div class="chain">
          ${paso('Convoca', by('Convoca y aprueba el temario'), 'Órgano convocante sin titular identificado')}
          ${paso('Preside el tribunal', by('Preside el tribunal'), 'Tribunal no publicado en el BOE ni en la web consultada')}
          ${paso('Dirige la formación', by('Dirige la formación'), c.imparte?esc(c.imparte):'Sin formación posterior específica')}
          ${by('Dirige el cuerpo u órgano gestor')?paso('Dirige el cuerpo', by('Dirige el cuerpo u órgano gestor'),''):''}
        </div>
        ${c.hist?`<details><summary>Historia del tribunal (${c.hist.serie.length} convocatorias, ${c.hist.serie[0].f.slice(0,4)}-${c.hist.serie[c.hist.serie.length-1].f.slice(0,4)})</summary>
          ${Object.entries(c.hist.cambios||{}).map(([g,x])=>`<p><b>Al llegar ${esc(g)}:</b> ${x.mismo?'siguió el mismo presidente':'cambió el presidente'} (${esc(x.antes)}, ${x.fecha_antes.slice(0,4)} → ${esc(x.despues)}, ${x.fecha_despues.slice(0,4)})</p>`).join('')}
          ${c.hist.serie.map(x=>`<p style="margin:2px 0"><span class="mono">${x.f.slice(0,4)}</span> · ${esc(x.g)} · ${esc(x.p)}</p>`).join('')}
        </details>`:''}
        <details><summary>Cómo se selecciona y se forma</summary>
          ${c.temario?`<p><b>Temario:</b> ${esc(c.temario)}</p>`:''}
          ${c.nombra_tribunal?`<p><b>Tribunal:</b> ${esc(c.nombra_tribunal).slice(0,400)}</p>`:''}
          ${c.examen?`<p><b>Examen:</b> ${esc(c.examen)}</p>`:''}
          ${c.formacion?`<p><b>Formación:</b> ${esc(c.formacion)}${c.dirige_formacion?' · '+esc(c.dirige_formacion):''}</p>`:''}
          ${c.notas?`<p><b>Notas:</b> ${esc(c.notas)}</p>`:''}
          <p>${link(c.fuente,'Convocatoria')}${c.tribunal&&c.tribunal.url?' · '+link(c.tribunal.url,'Tribunal'):''}</p>
        </details></article>`;
    }).join('') : '<div class="empty">Ningún cuerpo con estos filtros.</div>';
    const n=(st.q?1:0)+(st.amb?1:0)+(st.gr?1:0)+(st.min?1:0)+(st.com?1:0)+st.ind.size; $('#fcount').textContent = n? n+' activos':'';
    document.querySelectorAll('#cInd .chip').forEach(b=>b.setAttribute('aria-pressed', st.ind.has(b.dataset.k)));
  }
  $('#q').addEventListener('input', e=>{ st.q=e.target.value; render(); });
  $('#fAmb').addEventListener('change', e=>{ st.amb=e.target.value; render(); });
  $('#fGr').addEventListener('change', e=>{ st.gr=e.target.value; render(); });
  $('#fMin').addEventListener('change', e=>{ st.min=e.target.value; render(); });
  $('#fCom').addEventListener('change', e=>{ st.com=e.target.value; render(); });
  $('#cInd').addEventListener('click', e=>{ const b=e.target.closest('.chip'); if(!b) return; const k=b.dataset.k; st.ind.has(k)?st.ind.delete(k):st.ind.add(k); render(); });
  $('#reset').addEventListener('click', ()=>{ Object.assign(st,{q:'',amb:'',gr:'',min:'',com:''}); st.ind.clear(); ['#q','#fAmb','#fGr','#fMin','#fCom'].forEach(s=>$(s).value=''); render(); });
  $('#ftoggle').addEventListener('click', ()=>{ const f=$('.filters'); const ab=!f.classList.contains('abierto'); f.classList.toggle('abierto', ab); $('#ftoggle').setAttribute('aria-expanded', ab); });
  const L = JSON.parse(document.getElementById('data').textContent).llave || [];
  const maxN = L.length ? L[0].n : 1;
  const ROLES = {'Convoca y aprueba el temario':'convoca','Preside el tribunal':'preside tribunal','Dirige la formación':'dirige formación'};
  $('#llaveList').innerHTML = L.slice(0,25).map(x=>{
    const roles = Object.entries(x.roles).map(([r,v])=>`${ROLES[r]||r} ${v}`).join(' · ');
    const nomb = x.nombrado_por ? `Nombrado por ${esc(x.nombrado_por)}${x.desde?' el '+fmt(x.desde):''}${x.gob?' ('+esc(x.gob)+')':''}${x.gobierno_que_nombra?' (gobierno de '+esc(x.gobierno_que_nombra)+')':''}` : '';
    const mk = [x.pa?`<span class="bd par" title="${esc(x.pa)}">Partido</span>`:'', (x.con_zp&&x.con_s)?'<span class="bd zpa">Con ZP y con Sánchez</span>':x.con_zp?'<span class="bd zpd">Nombrado con ZP</span>':x.con_s?'<span class="bd ig">Nombrado con Sánchez</span>':'', x.jud?'<span class="bd jud">Judicial</span>':''].join(' ');
    return `<div class="lrow" data-n="${esc(x.nombre)}" tabindex="0" role="button" aria-label="Ver los cuerpos de ${esc(x.nombre)}">
      <div class="num">${x.n}</div>
      <div><div class="nm">${esc(x.nombre)}</div><div class="ps">${esc(x.puesto)}</div><div class="bar2" style="width:${Math.max(6,100*x.n/maxN)}%"></div></div>
      <div class="rl">${roles}<div class="ps">${nomb}</div></div>
      <div class="mk">${mk} <span class="ps">${esc(x.ambitos.join(', '))}</span></div></div>`;
  }).join('');
  $('#llaveList').addEventListener('click', e=>{ const r=e.target.closest('.lrow'); if(!r) return; st.q=r.dataset.n; $('#q').value=st.q; render(); $('.filters').scrollIntoView({behavior:'smooth'}); });
  $('#llaveList').addEventListener('keydown', e=>{ if(e.key==='Enter'){ const r=e.target.closest('.lrow'); if(r){ st.q=r.dataset.n; $('#q').value=st.q; render(); } } });
  const HR = JSON.parse(document.getElementById('data').textContent).hist_resumen || {};
  const HT = JSON.parse(document.getElementById('data').textContent).hist_top || [];
  const pct = (a,b) => b ? Math.round(100*a/b)+' %' : '–';
  $('#histBody').innerHTML = `
    <p class="hint" style="max-width:95ch">Primera convocatoria de cada cuerpo tras un cambio de Gobierno, comparada con la última anterior. Es una foto de continuidad o relevo en la presidencia del tribunal; el tiempo entre una y otra varía y la rotación también ocurre por causas ordinarias.</p>
    <div class="sum" style="padding-block:6px">
      ${HR['Rajoy']?`<span><b>${pct(HR['Rajoy'].cambia,HR['Rajoy'].cuerpos)}</b>cambió el presidente al llegar Rajoy (${HR['Rajoy'].cambia} de ${HR['Rajoy'].cuerpos} cuerpos)</span>`:''}
      ${HR['Sánchez']?`<span><b>${pct(HR['Sánchez'].cambia,HR['Sánchez'].cuerpos)}</b>cambió el presidente al llegar Sánchez (${HR['Sánchez'].cambia} de ${HR['Sánchez'].cuerpos}; siguió el mismo en ${HR['Sánchez'].sigue})</span>`:''}
    </div>
    <h3 style="font-size:11px;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);margin:10px 0 4px">Quienes más tribunales han presidido</h3>
    ${HT.map(x=>`<div class="lrow" data-n="${esc(x.nombre)}" tabindex="0" role="button"><div class="num">${x.veces}</div>
      <div><div class="nm">${esc(x.nombre)}</div><div class="ps">${esc(x.cuerpo_pres)}</div></div>
      <div class="rl">${esc(x.cuerpos.slice(0,4).join(' · '))}${x.cuerpos.length>4?' …':''}</div>
      <div class="mk"><span class="ps">Etapas: ${esc(x.etapas.join(', '))}</span></div></div>`).join('')}`;
  $('#histBody').addEventListener('click', e=>{ const r=e.target.closest('.lrow'); if(!r) return; st.q=r.dataset.n; $('#q').value=st.q; render(); $('.filters').scrollIntoView({behavior:'smooth'}); });
  if (window.matchMedia('(max-width:760px)').matches){ $('#llave').open=false; $('#legend').open=false; $('#aviso').open=false; }
  render();
})();
</script>
"""
out = html.replace("__LOGO__", logo).replace("/*__DATA__*/", json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/"))
open(os.path.join(B, "dashboard/mapa-de-la-seleccion.html"), "w").write(out)
print("cuerpos", len(data["cuerpos"]), "| tamaño", round(len(out) / 1024), "KB")
