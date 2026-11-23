/* Автор и разработчик: Postautov_K_V */
/* Расчетное ядро модели интеграции (порт model.py). Суммы в млн руб., время в годах от t=0. */
const TRL_NAMES = ["TRL1→2","TRL2→3","TRL3→4","TRL4→5","TRL5→6","TRL6→7","TRL7→8","TRL8→9"];
const STAGE_NAMES = ["Исходные данные и общие решения","Проектная документация, экспертиза и корректировка","Рабочая документация","Поставка МТР","Строительно-монтажные работы","ПНР без нагрузки","ПНР под нагрузкой","Комплексное опробование"];
const SCENARIOS = ["BASE","TRL7","TRL6","TRL5"];
const INTEG = ["TRL7","TRL6","TRL5"];
const SCN_TITLE = {BASE:"Базовый",TRL7:"Интеграция TRL7",TRL6:"Интеграция TRL6",TRL5:"Интеграция TRL5"};
const LVL = {TRL5:5,TRL6:6,TRL7:7};
const EV_COST0 = [2.0,5.0,10.0,20.0,30.0];
const EV_DELAY0 = [30,30,30,60,90];

const DEFAULTS = {
  budget:1000.0, share_inn:0.35, rate:0.12, t_dev:3.0, t_inv:5.0,
  w_time:[5,7,10,13,15,15,15,20], w_tax:[5,7,10,13,15,15,15,20],
  stage_share:[3,8,9,8,42,12,15,3], smr_lead:2/3,
  op_years:30, load:[0.2,0.6], revenue:350.0, staff:11, salary_k:100.0, markup:0.35, admin:0.10,
  to_rate:0.0012, tr_rate:0.0025, tr_years:[3,6,9,12,15,18,21,24,27,30], kr_rate:0.005, kr_years:[5,10,15,20,25,30],
  tax:0.25, amort_years:20, loss_limit:0.5, loss_limit_end:2030, first_tax_year:2026,
  pilot_all:false, pilot_share:0.10,
  p_ev:[0.09,0.06,0.04,0.03,0.02], ev_cost:[2.0,5.0,10.0,20.0,30.0], ev_delay_d:[30,30,30,60,90], days:365.0,
  phi_s:[0.40,0.20,0.10], mfix:false, sigma:0.60, pir_share:0.07, pd_part:0.40, exp_share:0.05, exp_days:30.0,
  ev6_cost_abs:null, ev6_delay_abs:null, ev6_p_abs:null,
  t7_store:0.015, t7_remount:0.06, t7_warr_p:0.25, t7_warr_cost:0.05,
  criterion:"reserve", crit_w:[30,15,15,15,10,15], q_evid:[3,5,4,3], q_load:[5,2,3,3], n_years:40
};

function P(ov){
  const p = Object.assign({}, DEFAULTS, ov||{});
  p.b_inn = p.budget*p.share_inn;
  p.b_inv = p.budget - p.b_inn;
  p.opex  = p.staff*p.salary_k*12/1000.0*(1+p.markup+p.admin);
  p.to    = p.budget*p.to_rate;
  p.tr    = p.budget*p.tr_rate;
  p.kr    = p.budget*p.kr_rate;
  p.pilot = p.pilot_share*p.b_inn;
  return p;
}
const load_j = (p,j) => (j <= p.load.length ? p.load[j-1] : 1.0);
const r9 = x => Math.round(x*1e9)/1e9;
const overlap = (a,b,n) => Math.max(0.0, Math.min(b,n) - Math.max(a,n-1));
function spread(a,b,amount,n){
  if (b-a <= 1e-12) return (n-1 < a && a <= n+1e-12) ? amount : 0.0;
  return amount*overlap(a,b,n)/(b-a);
}
const year_of = t => Math.ceil(r9(t));

function schedule(scn,p){
  const d_trl = p.w_time.map(w => w/100.0*p.t_dev);
  const conf = []; let t = 0.0;
  for (const d of d_trl){ t += d; conf.push(t); }
  const d_st = p.stage_share.map(w => w/100.0*p.t_inv);
  let f;
  if (scn === "BASE") f = conf[conf.length-1];
  else f = conf[LVL[scn]-2] - d_st[0];
  const st = [], en = []; t = f;
  for (const d of d_st){ st.push(t); t += d; en.push(t); }
  const tv = en[en.length-1];
  const conf_s = conf.slice(), start_s = [0.0].concat(conf.slice(0,-1));
  if (scn !== "BASE"){
    const k = LVL[scn];
    if (k < 6){ conf_s[4] = en[2]; start_s[4] = st[1]; }
    if (k < 7){ conf_s[5] = en[4]; start_s[5] = st[4]; }
    conf_s[6] = en[5]; start_s[6] = st[5];
    conf_s[7] = en[7]; start_s[7] = st[6];
  }
  const d_s = conf_s.map((c,j) => c - start_s[j]);
  return {d_trl:d_s, d_plan:d_trl, conf:conf_s, trl_start:start_s, conf_plan:conf, d_st:d_st, st:st, en:en, f:f, tv:tv, scn:scn};
}
/* Число переходов, затраты которых признаются расходами по статье 262 */
const N_EXP = {BASE:3, TRL5:4, TRL6:5, TRL7:6};
const pilot_window = sch => [sch.trl_start[4], sch.conf[4]];

function flows(scn,p,delay_days,extra,sch,taxmode){
  delay_days = delay_days||0.0; extra = extra||[];
  sch = sch || schedule(scn,p);
  const N = p.n_years;
  const tv = sch.tv + delay_days/p.days;
  const m = Math.floor(r9(tv));
  const phi = r9(tv - m);
  const b_inn = p.b_inn;
  const inn_cash = [];
  for (let n=1;n<=N;n++){
    let s = 0.0;
    for (let k=0;k<p.w_tax.length;k++) s += spread(sch.trl_start[k], sch.conf[k], p.w_tax[k]/100.0*b_inn, n);
    inn_cash.push(s);
  }
  /* Расходами по статье 262 признаются затраты переходов, завершенных до вовлечения
     разработки в инвестиционный проект. Затраты последующих переходов формируют
     первоначальную стоимость объекта и переносятся через амортизацию. */
  const ne = N_EXP[scn];
  const rec = new Array(N).fill(0.0);
  let cap_inn = 0.0;
  for (let k=0;k<p.w_tax.length;k++){
    const amt = p.w_tax[k]/100.0*b_inn;
    if (k < ne){ const y = year_of(sch.conf[k]); if (y <= N) rec[y-1] += amt; }
    else cap_inn += amt;
  }
  const pilot = new Array(N).fill(0.0);
  if (scn === "BASE" || scn === "TRL7"){
    const [a,b] = pilot_window(sch);
    for (let n=1;n<=N;n++) pilot[n-1] = spread(a,b,p.pilot,n);
  }
  const inv = [];
  for (let n=1;n<=N;n++) inv.push(spread(sch.f, sch.tv, p.b_inv, n));
  const exc = new Array(N).fill(0.0);
  for (const [t,c] of extra) exc[year_of(t)-1] += c;
  const t7x = new Array(N).fill(0.0);
  // Затраты ожидания определяются по календарному плану. Окно простоя оборудования
  // возникает, если изделие готово раньше начала монтажа. Окно ожидания разработчика
  // возникает, если подтверждение уровня готовности привязано к стадии строительства
  // и наступает позже планового окончания перехода. Если окна нет, затрат нет.
  if (scn !== "BASE"){
    const a7 = sch.conf[5], b7 = sch.st[4];               // простой оборудования до монтажа
    if (b7 - a7 > 1e-9){
      for (let n=1;n<=N;n++) t7x[n-1] += spread(a7,b7,p.t7_store*p.b_inn*(b7-a7),n);
      t7x[year_of(b7)-1] += p.t7_remount*p.b_inn;
    }
    for (let j=0;j<8;j++){                                // ожидание разработчика на переходах
      const lag = sch.d_trl[j] - sch.d_plan[j];
      if (lag > 1e-9){
        const a = sch.conf[j] - lag, b = sch.conf[j];
        for (let n=1;n<=N;n++) t7x[n-1] += spread(a,b,p.t7_store*p.b_inn*lag,n);
      }
    }
    t7x[year_of(sch.tv)-1] += p.t7_warr_p*p.t7_warr_cost*p.b_inn;
  }
  /* Первоначальная стоимость объекта: инвестиционная часть, капитализированные инновационные
     затраты, затраты подтверждения уровней на объекте и прямые затраты доработок. Затраты
     на опытную инфраструктуру в стоимость объекта не входят, она демонтируется. */
  const sumArr = a => a.reduce((x,y)=>x+y,0.0);
  const am_base = (taxmode === "amort")
    ? (p.b_inv + b_inn + sumArr(t7x) + sumArr(exc))
    : (p.b_inv + cap_inn + sumArr(t7x) + sumArr(exc));

  function opj(j,kind){
    if (j < 1 || j > p.op_years) return 0.0;
    if (kind === "rev")  return p.revenue*load_j(p,j);
    if (kind === "opex") return p.opex;
    if (kind === "to")   return p.to;
    if (kind === "tr")   return p.tr_years.indexOf(j) >= 0 ? p.tr : 0.0;
    if (kind === "kr")   return p.kr_years.indexOf(j) >= 0 ? p.kr : 0.0;
    if (kind === "am"){
      return j <= p.amort_years ? am_base/p.amort_years : 0.0;
    }
    return 0.0;
  }
  const cal = (n,kind) => { const j = n-m; return (1-phi)*opj(j,kind) + phi*opj(j-1,kind); };
  let loss = 0.0, cum = 0.0, cumd = 0.0;
  const out = [];
  for (let n=1;n<=N;n++){
    const r = {n:n, year:p.first_tax_year+n-1};
    r.inn = inn_cash[n-1]; r.pilot = pilot[n-1]; r.inv = inv[n-1]; r.rework = exc[n-1]; r.t7x = t7x[n-1];
    r.capex = r.inn + r.pilot + r.inv + r.rework + r.t7x;
    r.rev = cal(n,"rev"); r.opex = cal(n,"opex");
    r.to = cal(n,"to"); r.tr = cal(n,"tr"); r.kr = cal(n,"kr");
    r.toir = r.to + r.tr + r.kr;
    r.am = cal(n,"am"); r.rnd = ((taxmode === "amort") ? 0.0 : rec[n-1]) + r.pilot;
    r.ebitda = r.rev - r.opex - r.toir;
    r.base = r.ebitda - r.am - r.rnd;
    const lim = r.year <= p.loss_limit_end ? p.loss_limit : 1.0;
    r.loss_open = loss;
    if (r.base < 0){ r.loss_add = -r.base; r.loss_use = 0.0; }
    else { r.loss_add = 0.0; r.loss_use = Math.min(loss, lim*r.base); }
    loss = loss + r.loss_add - r.loss_use;
    r.loss_close = loss; r.limit = lim;
    r.taxable = Math.max(r.base,0.0) - r.loss_use;
    r.tax = p.tax*r.taxable;
    r.cf_op = r.ebitda - r.tax;
    r.cf = r.cf_op - r.capex;
    r.df = Math.pow(1+p.rate,-n);
    r.pv = r.cf*r.df; r.pv_op = r.cf_op*r.df; r.pv_capex = r.capex*r.df;
    cum += r.cf; cumd += r.pv; r.cum = cum; r.cumd = cumd;
    out.push(r);
  }
  return out;
}
const npv = rows => rows.reduce((a,r)=>a+r.pv,0);
const npv_at = (rows,rate) => rows.reduce((a,r)=>a+r.cf*Math.pow(1+rate,-r.n),0);
function irr(rows,lo,hi){
  lo = lo===undefined?-0.5:lo; hi = hi===undefined?2.0:hi;
  if (!rows.some(r=>r.cf>0) || !rows.some(r=>r.cf<0)) return null;
  const f = x => npv_at(rows,x);
  let flo = f(lo), fhi = f(hi);
  if (flo*fhi > 0) return null;
  for (let i=0;i<200;i++){
    const mid = (lo+hi)/2, fm = f(mid);
    if (flo*fm <= 0){ hi = mid; fhi = fm; } else { lo = mid; flo = fm; }
  }
  return (lo+hi)/2;
}
function payback(rows,key){
  let prev_c = 0.0, c = 0.0, seen = false;
  for (const r of rows){
    c += r[key];
    if (c < 0) seen = true;
    if (seen && c >= 0){
      const frac = (c !== prev_c) ? (0-prev_c)/(c-prev_c) : 0;
      return (r.n-1)+frac;
    }
    prev_c = c;
  }
  return null;
}
function indicators(rows,rate){
  const pv_ic = rows.reduce((a,r)=>a+r.pv_capex,0);
  const pv_cf = rows.reduce((a,r)=>a+r.pv_op,0);
  return {npv:pv_cf-pv_ic, pi:pv_cf/pv_ic, pv_ic:pv_ic, pv_cf:pv_cf,
          pp:payback(rows,"cf"), dpp:payback(rows,"pv"), irr:irr(rows),
          sum_capex:rows.reduce((a,r)=>a+r.capex,0)};
}
function event_scope(scn,sch,k,p){
  const t = sch.conf[k-2];
  if (scn === "BASE") return [false,t,"нет (изолированный анализ)"];
  const st = sch.st, en = sch.en, eps = 1e-9;
  const started = st.map(s => s < t-eps);
  if (k === 5){ const aff = started[1]; return [aff,t, aff?"ПД и экспертиза":"нет: уровень подтвержден до начала ПД"]; }
  if (k === 6){ const aff = (en[1] <= t+eps) || started[1]; return [aff,t, aff?"ПД, РД и выполненные работы":"нет: уровень подтвержден до начала ПД"]; }
  const aff = started.slice(1).some(x=>x);
  return [aff,t, aff?"документация, конструкция, инфраструктура, испытания":"нет: уровень подтвержден до начала ПД"];
}
function ev_params(p,scn,k,sch){
  const i = k-5;
  const LV = {TRL5:0,TRL6:1,TRL7:2};
  const phi = (scn in LV) ? p.phi_s[LV[scn]] : p.phi_s[1];
  const m = p.mfix ? 1.0 : phi/p.phi_s[1];
  let pr = Math.min(1.0, p.p_ev[i]*m);
  let cost = p.ev_cost[i], dd = p.ev_delay_d[i];
  if (k === 6 && scn === "TRL5"){
    const ch = phi*p.sigma;
    const cpir = p.pir_share*p.b_inv;
    sch = sch || schedule(scn,p);
    const days = (sch.d_st[1]+sch.d_st[2])*p.days;
    cost = (ch*cpir + p.exp_share*p.pd_part*cpir)*(p.ev_cost[1]/EV_COST0[1]);
    dd = (ch*days + p.exp_days)*(p.ev_delay_d[1]/EV_DELAY0[1]);
    if (p.ev6_cost_abs !== null && p.ev6_cost_abs !== undefined) cost = p.ev6_cost_abs;
    if (p.ev6_delay_abs !== null && p.ev6_delay_abs !== undefined) dd = p.ev6_delay_abs;
    if (p.ev6_p_abs !== null && p.ev6_p_abs !== undefined) pr = p.ev6_p_abs;
  }
  return [pr,cost,dd];
}
function outcomes(scn,p,sch){
  sch = sch || schedule(scn,p);
  const base_rows = flows(scn,p,0,[],sch);
  const n0 = npv(base_rows);
  const active = [];
  for (let k=5;k<=9;k++){
    const [aff,t,desc] = event_scope(scn,sch,k,p);
    const [pr,c,d] = ev_params(p,scn,k,sch);
    active.push({k:k,aff:aff,t:t,desc:desc,p:pr,cost:c,dd:d});
  }
  const ev = active.filter(a=>a.aff);
  const res = [];
  const total = 1 << ev.length;
  for (let mask=0;mask<total;mask++){
    const combo = ev.map((_,i) => (mask >> (ev.length-1-i)) & 1);
    let prob = 1.0, cost = 0.0, dd = 0.0; const extra = [], names = [];
    ev.forEach((a,i) => {
      const c = combo[i];
      prob *= c ? a.p : (1-a.p);
      if (c){ cost += a.cost; dd += a.dd; extra.push([a.t,a.cost]); names.push("TRL"+a.k); }
    });
    const rows = flows(scn,p,dd,extra,sch);
    res.push({combo:combo,names:names,prob:prob,cost:cost,delay:dd,npv:npv(rows),loss:n0-npv(rows)});
  }
  const E = res.reduce((a,i)=>a+i.prob*i.npv,0);
  return {events:active, items:res, npv0:n0, E_npv:E, E_loss:n0-E};
}

/* ---------- запас устойчивости и шестикритериальная оценка (раздел 3.3) ---------- */
/* Наихудший исход наступает, когда происходят все возможные события доработки,
   поэтому перебор сочетаний не нужен. Множитель m масштабирует затраты и задержки. */
function worstNpv(scn,p,sch,m){
  sch = sch || schedule(scn,p);
  let dd = 0.0; const extra = [];
  for (let k=5;k<=9;k++){
    const sc = event_scope(scn,sch,k,p);
    if (!sc[0]) continue;
    const ep = ev_params(p,scn,k,sch);
    dd += ep[2]*m; extra.push([sc[1], ep[1]*m]);
  }
  return npv(flows(scn,p,dd,extra,sch));
}
/* Критический множитель: во сколько раз должны вырасти затраты и задержки доработок,
   чтобы преимущество к базовому сценарию в наихудшем исходе обратилось в ноль. */
function criticalM(scn,p,baseNpv,sch){
  sch = sch || schedule(scn,p);
  const q = m => worstNpv(scn,p,sch,m) - baseNpv;
  if (!(q(1) > 0)) return null;
  let lo = 1.0, hi = 1.5;
  for (let i=0;i<40 && q(hi) > 0;i++){ lo = hi; hi *= 1.5; if (hi > 1e6) return null; }
  for (let i=0;i<80;i++){ const mid = (lo+hi)/2; if (q(mid) > 0) lo = mid; else hi = mid; }
  return (lo+hi)/2;
}
const CRIT_NAMES = ["ЧДД","Срок ввода","Остаток в наихудшем исходе",
                    "Доказательность TRL","Ресурсная нагрузка","Устойчивость (m*)"];
/* Линейная нормировка по наилучшему и наихудшему значению среди вариантов. */
function critNorm(v,lo,hi,inv){ const x = hi > lo ? (v-lo)/(hi-lo) : 0.0; return (inv ? 1-x : x)*100; }
/* opts: [{key,label,npv,tv,worst,m,qe,qr}], w — шесть весов в долях единицы. */
function scoreOptions(opts,w){
  const col = f => opts.map(f);
  const lo = a => Math.min(...a), hi = a => Math.max(...a);
  const nv = col(d=>d.npv), tv = col(d=>d.tv), wo = col(d=>d.worst), ms = col(d=>d.m);
  opts.forEach(d => {
    d.score = [critNorm(d.npv,lo(nv),hi(nv),false), critNorm(d.tv,lo(tv),hi(tv),true),
               critNorm(d.worst,lo(wo),hi(wo),false), (d.qe-1)/4*100, (d.qr-1)/4*100,
               critNorm(d.m,lo(ms),hi(ms),false)];
    d.total = d.score.reduce((a,x,i)=>a+x*w[i],0.0);
  });
  return opts;
}

/* ---------- имитационное моделирование (метод Монте-Карло) ---------- */
/* Генератор mulberry32 с фиксированным начальным значением, расчет воспроизводим. */
function rngMake(seed){
  let a = (seed >>> 0) || 1;
  const u = () => { a = (a + 0x6D2B79F5) >>> 0; let t = a; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
  let spare = null;
  const gauss = (mu,sd) => {
    if (spare !== null){ const v = spare; spare = null; return mu + sd*v; }
    let s = 0, x = 0, y = 0;
    do { x = 2*u()-1; y = 2*u()-1; s = x*x + y*y; } while (s >= 1 || s === 0);
    const f = Math.sqrt(-2*Math.log(s)/s);
    spare = y*f; return mu + sd*x*f;
  };
  return {u:u, gauss:gauss};
}
/* Отклонения параметров одного прогона. Логнормальные множители имеют среднее 1. */
function mcDraw(rnd){
  const ln = s => Math.exp(rnd.gauss(-s*s/2, s));
  return {td:ln(0.15), ti:ln(0.15), pe:ln(0.5), ce:ln(0.4),
          rate:0.10 + 0.06*rnd.u(), rev:Math.max(0.3, rnd.gauss(1,0.15)),
          u:[rnd.u(),rnd.u(),rnd.u(),rnd.u(),rnd.u()]};
}
/* Один прогон. Все сценарии считаются на одном наборе отклонений. */
function mcOne(p,d){
  const pp = P(Object.assign({}, p, {t_dev:p.t_dev*d.td, t_inv:p.t_inv*d.ti, rate:d.rate, revenue:p.revenue*d.rev}));
  const out = {};
  for (const s of SCENARIOS){
    const sch = schedule(s,pp);
    checkCalendar(s,sch);
    let delay = 0.0; const extra = [];
    for (let i=0;i<5;i++){
      const k = 5+i;
      const sc = event_scope(s,sch,k,pp);
      if (!sc[0]) continue;
      const ep = ev_params(pp,s,k,sch);
      if (d.u[i] < Math.min(1.0, ep[0]*d.pe)){ delay += ep[2]*d.ce; extra.push([sc[1], ep[1]*d.ce]); }
    }
    const horizon = Math.max(pp.n_years, year_of(sch.tv+delay/pp.days)+pp.op_years);
    if (!Number.isFinite(horizon) || horizon>500) throw Error("Случайный горизонт превышает 500 лет");
    out[s] = npv(flows(s,{...pp,n_years:horizon},delay,extra,sch));
  }
  return out;
}
const mcQ = (a,x) => { const b = a.slice().sort((i,j)=>i-j); return b[Math.floor(x*(b.length-1))]; };
function monteCarlo(p,N,seed){
  N = N || 5000; seed = (seed === undefined || seed === null) ? 20261107 : seed;
  const rnd = rngMake(seed);
  const res = {}; SCENARIOS.forEach(s => res[s] = []);
  const rates = [];
  for (let i=0;i<N;i++){
    const d = mcDraw(rnd), o = mcOne(p, d);
    SCENARIOS.forEach(s => res[s].push(o[s]));
    rates.push(d.rate);
  }
  const mc = {N:N, seed:seed, scn:{}};
  const best = {}, best_int = {};
  SCENARIOS.forEach(s => best[s] = 0); INTEG.forEach(s => best_int[s] = 0);
  for (let i=0;i<N;i++){
    let bs = SCENARIOS[0], bi = INTEG[0];
    SCENARIOS.forEach(s => { if (res[s][i] > res[bs][i]) bs = s; });
    INTEG.forEach(s => { if (res[s][i] > res[bi][i]) bi = s; });
    best[bs] += 1; best_int[bi] += 1;
  }
  SCENARIOS.forEach(s => {
    const a = res[s], adv = a.map((v,i) => v - res.BASE[i]);
    mc.scn[s] = {p10:mcQ(a,0.1), p50:mcQ(a,0.5), p90:mcQ(a,0.9),
      mean:a.reduce((x,y)=>x+y,0)/N,
      neg:a.filter(v => v < 0).length/N,
      adv_p10:mcQ(adv,0.1), adv_p50:mcQ(adv,0.5), adv_p90:mcQ(adv,0.9),
      beat_base:adv.filter((v,i) => res[s][i] > res.BASE[i]).length/N,
      best:best[s]/N};
  });
  mc.best_int = {}; INTEG.forEach(s => mc.best_int[s] = best_int[s]/N);
  const dif = res.TRL5.map((v,i) => v - res.TRL6[i]);
  mc.d56 = {p10:mcQ(dif,0.1), p50:mcQ(dif,0.5), p90:mcQ(dif,0.9), pos:dif.filter(v => v > 0).length/N};
  mc.series = res;
  mc.rates = rates;
  return mc;
}

if (typeof module !== "undefined") module.exports = {N_EXP,worstNpv,criticalM,scoreOptions,CRIT_NAMES,P,schedule,flows,npv,npv_at,irr,payback,indicators,outcomes,ev_params,event_scope,pilot_window,monteCarlo,rngMake,mcDraw,mcOne,SCENARIOS,INTEG,SCN_TITLE,TRL_NAMES,STAGE_NAMES,DEFAULTS};
