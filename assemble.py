#!/usr/bin/env python3
"""Assemble the upgraded index.html"""
import os

base = r"C:\Users\sakshxmsingh\Desktop\crixy\client portal\latest portal"

def r(name):
    with open(os.path.join(base, name), 'r', encoding='utf-8') as f:
        return f.read()

logo_const = r('logo_const.txt')
chunk_utils = r('chunk_utils.txt')
chunk_pdf = r('chunk_pdf.txt')
chunk_db = r('chunk_db.txt')
chunk_status = r('chunk_status.txt')
chunk_admin = r('chunk_admin.txt')
chunk_manager = r('chunk_manager.txt')
chunk_portal2 = r('chunk_portal2.txt')
chunk_root = r('chunk_root.txt')

# Read firebase config from original
with open(os.path.join(base, 'index.html'), 'r', encoding='utf-8') as f:
    orig = f.read()

fb_start = orig.find('<script src="https://www.gstatic.com/firebasejs')
fb_end = orig.find('\n</script>', fb_start) + 10
fb_config = orig[fb_start:fb_end].strip()

# New additions
new_components = r"""
/* ═══ NEW COMPONENTS ═══ */

function useTheme() {
  const [theme, setTheme] = useState(() => {
    try { return localStorage.getItem('ut_theme') || 'dark'; } catch { return 'dark'; }
  });
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    try { localStorage.setItem('ut_theme', theme); } catch {}
  }, [theme]);
  const toggle = () => setTheme(t => t === 'dark' ? 'light' : 'dark');
  return { theme, toggle };
}

function useSessionTimer() {
  const [startTime] = useState(Date.now());
  const [elapsed, setElapsed] = useState(0);
  useEffect(() => {
    const interval = setInterval(() => setElapsed(Math.floor((Date.now() - startTime) / 1000)), 1000);
    return () => clearInterval(interval);
  }, [startTime]);
  const h = Math.floor(elapsed / 3600), m = Math.floor((elapsed % 3600) / 60), s = elapsed % 60;
  if (h > 0) return h + 'h ' + m + 'm';
  if (m > 0) return m + 'm ' + s + 's';
  return s + 's';
}

function FirebaseStatus() {
  const online = !!window._db;
  return (
    <div style={{display:'flex',alignItems:'center',gap:6,fontSize:11,color:online?'var(--green)':'var(--amber)'}}>
      <div style={{width:7,height:7,borderRadius:'50%',background:online?'var(--green)':'var(--amber)',boxShadow:`0 0 6px ${online?'var(--green)':'var(--amber)'}`,animation:'pulse 2s infinite'}}/>
      {online?'Live':'Offline'}
    </div>
  );
}

function ShortcutsPanel({onClose}) {
  const shortcuts = [
    { keys: ['Ctrl', 'K'], desc: 'Open command palette' },
    { keys: ['?'], desc: 'Show keyboard shortcuts' },
    { keys: ['Esc'], desc: 'Close modal / panel' },
  ];
  return (
    <div style={{position:'fixed',inset:0,background:'rgba(0,0,0,0.75)',backdropFilter:'blur(8px)',zIndex:1000,display:'flex',alignItems:'center',justifyContent:'center'}} onClick={onClose}>
      <div style={{background:'var(--surface)',border:'1px solid var(--border2)',borderRadius:'var(--radius-lg)',padding:32,minWidth:400,maxWidth:480,boxShadow:'var(--shadow-lg)'}} onClick={e=>e.stopPropagation()}>
        <div style={{fontFamily:'var(--font-display)',fontSize:18,fontWeight:800,marginBottom:24,background:'linear-gradient(135deg,#f1f5f9,#e5e7eb)',WebkitBackgroundClip:'text',WebkitTextFillColor:'transparent'}}>Keyboard Shortcuts</div>
        {shortcuts.map((s,i) => (
          <div key={i} style={{display:'flex',justifyContent:'space-between',alignItems:'center',padding:'10px 0',borderBottom:'1px solid var(--border)'}}>
            <span style={{color:'var(--text2)',fontSize:13}}>{s.desc}</span>
            <div style={{display:'flex',gap:4}}>
              {s.keys.map((k,j) => (
                <kbd key={j} style={{background:'var(--bg3)',border:'1px solid var(--border2)',borderRadius:6,padding:'2px 8px',fontSize:11,fontWeight:600,color:'var(--text)'}}>{k}</kbd>
              ))}
            </div>
          </div>
        ))}
        <button className="btn btn-secondary btn-sm" style={{marginTop:20,width:'100%'}} onClick={onClose}>Close</button>
      </div>
    </div>
  );
}

function calcHealthScore(client) {
  let score = 100;
  const overdueInv = (client.invoices||[]).filter(i => i.status !== 'paid' && isOverdue(i.dueDate));
  score -= overdueInv.length * 10;
  const openTickets = (client.tickets||[]).filter(t => t.status !== 'resolved' && t.status !== 'closed');
  score -= openTickets.length * 5;
  const recentMsgs = (client.messages||[]).filter(m => (Date.now() - new Date(m.ts||m.createdAt||0)) < 7*24*60*60*1000);
  if (recentMsgs.length === 0) score -= 10;
  if ((client.progress||0) < 10 && client.status === 'In Progress') score -= 15;
  return Math.max(0, Math.min(100, score));
}

function HealthScoreBadge({client}) {
  const score = calcHealthScore(client);
  const color = score >= 80 ? 'var(--green)' : score >= 60 ? 'var(--amber)' : 'var(--red)';
  const label = score >= 80 ? 'Healthy' : score >= 60 ? 'Fair' : 'At Risk';
  return (
    <span style={{display:'inline-flex',alignItems:'center',gap:4,padding:'3px 10px',borderRadius:99,background:`${color}20`,color,fontSize:11,fontWeight:700,border:`1px solid ${color}30`}}>
      <span style={{width:5,height:5,borderRadius:'50%',background:color,display:'inline-block'}}/>
      {label} {score}
    </span>
  );
}

function PremiumProgressRing({progress, size=120, stroke=8}) {
  const radius = (size - stroke) / 2;
  const circumference = radius * 2 * Math.PI;
  const offset = circumference - (progress / 100) * circumference;
  const gradId = 'pg' + size;
  return (
    <div style={{position:'relative', width:size, height:size}}>
      <svg width={size} height={size} style={{transform:'rotate(-90deg)'}}>
        <circle cx={size/2} cy={size/2} r={radius} fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth={stroke}/>
        <circle cx={size/2} cy={size/2} r={radius} fill="none"
          stroke={`url(#${gradId})`} strokeWidth={stroke}
          strokeDasharray={circumference} strokeDashoffset={offset}
          strokeLinecap="round" style={{transition:'stroke-dashoffset 1s ease'}}
        />
        <defs>
          <linearGradient id={gradId} x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#f8fafc"/>
            <stop offset="100%" stopColor="#9ca3af"/>
          </linearGradient>
        </defs>
      </svg>
      <div style={{position:'absolute',inset:0,display:'flex',flexDirection:'column',alignItems:'center',justifyContent:'center'}}>
        <span style={{fontSize:Math.max(14,Math.floor(size*0.2)),fontWeight:800,color:'var(--text)',fontFamily:'var(--font-display)'}}>{progress}%</span>
        <span style={{fontSize:Math.max(9,Math.floor(size*0.09)),color:'var(--text2)'}}>Complete</span>
      </div>
    </div>
  );
}

function RevenueChart({clients}) {
  const canvasRef = useRef(null);
  const chartRef = useRef(null);
  useEffect(() => {
    if (!canvasRef.current || typeof Chart === 'undefined') return;
    if (chartRef.current) chartRef.current.destroy();
    const months = [], revenue = [];
    for (let i = 5; i >= 0; i--) {
      const d = new Date(); d.setMonth(d.getMonth() - i);
      months.push(d.toLocaleDateString('en-IN', {month:'short', year:'2-digit'}));
      let total = 0;
      clients.forEach(c => (c.invoices||[]).filter(inv => {
        const invDate = new Date(inv.createdAt||inv.date||'');
        return invDate.getMonth()===d.getMonth()&&invDate.getFullYear()===d.getFullYear()&&inv.status==='paid';
      }).forEach(inv => total += getInvoicePaidAmount(inv)));
      revenue.push(total);
    }
    chartRef.current = new Chart(canvasRef.current, {
      type: 'bar',
      data: { labels: months, datasets: [{ label: 'Revenue', data: revenue, backgroundColor: 'rgba(255,255,255,0.7)', borderColor: '#f8fafc', borderWidth: 2, borderRadius: 8 }] },
      options: { responsive:true, maintainAspectRatio:false, plugins:{legend:{display:false}},
        scales: { y:{grid:{color:'rgba(255,255,255,0.04)'},ticks:{color:'#94a3b8',callback:v=>'\u20B9'+(v/1000).toFixed(0)+'k'}}, x:{grid:{display:false},ticks:{color:'#94a3b8'}} } }
    });
    return () => { if(chartRef.current) chartRef.current.destroy(); };
  }, [clients]);
  return <canvas ref={canvasRef} style={{width:'100%', height:'220px'}}/>;
}

function StatusDonutChart({clients}) {
  const canvasRef = useRef(null);
  const chartRef = useRef(null);
  useEffect(() => {
    if (!canvasRef.current || typeof Chart === 'undefined') return;
    if (chartRef.current) chartRef.current.destroy();
    const statuses = {};
    clients.forEach(c => { statuses[c.status||'Pending'] = (statuses[c.status||'Pending']||0) + 1; });
    chartRef.current = new Chart(canvasRef.current, {
      type: 'doughnut',
      data: { labels: Object.keys(statuses), datasets: [{ data: Object.values(statuses), backgroundColor: ['#f8fafc','#10b981','#f59e0b','#06b6d4','#ec4899','#ef4444'], borderWidth: 0, hoverOffset: 6 }] },
      options: { responsive:true, maintainAspectRatio:false, plugins:{ legend:{position:'bottom',labels:{color:'#94a3b8',padding:14,font:{size:12},boxWidth:12}} }, cutout:'72%' }
    });
    return () => { if(chartRef.current) chartRef.current.destroy(); };
  }, [clients]);
  return <canvas ref={canvasRef} style={{width:'100%', height:'220px'}}/>;
}

function ClientGrowthChart({clients}) {
  const canvasRef = useRef(null);
  const chartRef = useRef(null);
  useEffect(() => {
    if (!canvasRef.current || typeof Chart === 'undefined') return;
    if (chartRef.current) chartRef.current.destroy();
    const months = [], counts = [];
    for (let i = 5; i >= 0; i--) {
      const d = new Date(); d.setMonth(d.getMonth() - i);
      months.push(d.toLocaleDateString('en-IN', {month:'short', year:'2-digit'}));
      counts.push(clients.filter(c => new Date(c.createdAt||'') <= d).length);
    }
    chartRef.current = new Chart(canvasRef.current, {
      type: 'line',
      data: { labels: months, datasets: [{ label: 'Total Clients', data: counts, borderColor: '#9ca3af', backgroundColor: 'rgba(255,255,255,0.08)', borderWidth: 2, pointBackgroundColor: '#9ca3af', pointRadius: 4, fill: true, tension: 0.4 }] },
      options: { responsive:true, maintainAspectRatio:false, plugins:{legend:{display:false}},
        scales: { y:{grid:{color:'rgba(255,255,255,0.04)'},ticks:{color:'#94a3b8',stepSize:1}}, x:{grid:{display:false},ticks:{color:'#94a3b8'}} } }
    });
    return () => { if(chartRef.current) chartRef.current.destroy(); };
  }, [clients]);
  return <canvas ref={canvasRef} style={{width:'100%', height:'200px'}}/>;
}

function AdminAnalytics({clients, settings}) {
  const totalRev = clients.reduce((s,c) => (c.invoices||[]).reduce((a,i) => a+getInvoiceTotal(i),0)+s, 0);
  const paidRev = clients.reduce((s,c) => (c.invoices||[]).reduce((a,i) => a+getInvoicePaidAmount(i),0)+s, 0);
  const totalHrs = clients.reduce((s,c) => (c.timeEntries||[]).reduce((a,e) => a+e.hours,0)+s, 0);
  const totalTasks = clients.reduce((s,c) => (c.tasks||[]).length+s, 0);
  const doneTasks = clients.reduce((s,c) => (c.tasks||[]).filter(t=>t.status==='completed').length+s, 0);
  const avgHealth = clients.length ? Math.round(clients.reduce((s,c) => s+calcHealthScore(c),0)/clients.length) : 0;

  return (
    <div className="space-4 fade-in">
      <div style={{marginBottom:8}}>
        <h1 style={{fontFamily:'var(--font-display)',fontWeight:800,fontSize:26,background:'linear-gradient(135deg,#f1f5f9,#e5e7eb)',WebkitBackgroundClip:'text',WebkitTextFillColor:'transparent'}}>Analytics</h1>
        <p style={{color:'var(--text3)',fontSize:13,marginTop:4}}>Business intelligence and performance overview</p>
      </div>
      <div className="grid-4">
        {[['Total Revenue',curr(totalRev),'💎','c-purple'],['Collected',curr(paidRev),'✅','c-green'],['Total Hours',totalHrs.toFixed(1)+'h','⏱','c-blue'],['Avg Health',avgHealth+'%','❤️','c-amber']].map(([l,v,e,cls])=>
          <div key={l} className={`stat-card ${cls}`}>
            <div className="stat-icon" style={{background:'rgba(255,255,255,.06)',fontSize:22}}>{e}</div>
            <div><div className="stat-label">{l}</div><div className="stat-value">{v}</div></div>
          </div>
        )}
      </div>
      <div className="grid-2">
        <div className="card">
          <h3 style={{fontFamily:'var(--font-display)',fontWeight:700,fontSize:15,marginBottom:4}}>Monthly Revenue</h3>
          <p style={{fontSize:12,color:'var(--text3)',marginBottom:16}}>Paid invoices — last 6 months</p>
          <div style={{height:220}}><RevenueChart clients={clients}/></div>
        </div>
        <div className="card">
          <h3 style={{fontFamily:'var(--font-display)',fontWeight:700,fontSize:15,marginBottom:4}}>Project Status</h3>
          <p style={{fontSize:12,color:'var(--text3)',marginBottom:16}}>Distribution across all clients</p>
          <div style={{height:220}}><StatusDonutChart clients={clients}/></div>
        </div>
      </div>
      <div className="grid-2">
        <div className="card">
          <h3 style={{fontFamily:'var(--font-display)',fontWeight:700,fontSize:15,marginBottom:4}}>Client Growth</h3>
          <p style={{fontSize:12,color:'var(--text3)',marginBottom:16}}>Cumulative clients over time</p>
          <div style={{height:200}}><ClientGrowthChart clients={clients}/></div>
        </div>
        <div className="card">
          <h3 style={{fontFamily:'var(--font-display)',fontWeight:700,fontSize:15,marginBottom:16}}>Revenue by Client</h3>
          {clients.length===0?<div className="empty-state" style={{padding:'30px 0'}}><div className="empty-icon">📊</div><div className="empty-text">No data</div></div>:
            [...clients].sort((a,b)=>(b.invoices||[]).reduce((s,i)=>s+getInvoiceTotal(i),0)-(a.invoices||[]).reduce((s,i)=>s+getInvoiceTotal(i),0)).slice(0,8).map(c=>{
              const r=(c.invoices||[]).reduce((s,i)=>s+getInvoiceTotal(i),0);
              const p=(c.invoices||[]).reduce((s,i)=>s+getInvoicePaidAmount(i),0);
              const pct=totalRev>0?Math.round(r/totalRev*100):0;
              return <div key={c.id} style={{marginBottom:12}}>
                <div style={{display:'flex',justifyContent:'space-between',marginBottom:4}}>
                  <span style={{fontSize:13,fontWeight:600}}>{c.name}</span>
                  <span style={{fontSize:11,color:'var(--text3)'}}>{curr(r)}<span style={{color:'#6ee7b7'}}> ({curr(p)} paid)</span></span>
                </div>
                <div className="progress-bar"><div className="progress-fill" style={{width:pct+'%'}}/></div>
              </div>;
            })
          }
        </div>
      </div>
      <div className="card">
        <h3 style={{fontFamily:'var(--font-display)',fontWeight:700,fontSize:15,marginBottom:16}}>Client Health Overview</h3>
        {clients.length===0?<div className="empty-state" style={{padding:'20px 0'}}><div className="empty-icon">❤️</div><div className="empty-text">No clients yet</div></div>:
          <div style={{display:'grid',gridTemplateColumns:'repeat(auto-fill,minmax(260px,1fr))',gap:12}}>
            {clients.map(c=>{
              const tasks=c.tasks||[];const done=tasks.filter(t=>t.status==='completed').length;
              const overdue=(c.invoices||[]).filter(i=>i.status==='overdue').length;
              return <div key={c.id} style={{padding:'12px 14px',border:'1px solid var(--border)',borderRadius:12,display:'flex',alignItems:'center',gap:12}}>
                <ProgressRing pct={c.progress||0} size={48} stroke={4} color={sc(c.status).dot}/>
                <div style={{flex:1,minWidth:0}}>
                  <div style={{fontWeight:600,fontSize:13,overflow:'hidden',textOverflow:'ellipsis',whiteSpace:'nowrap'}}>{c.name}</div>
                  <div style={{fontSize:11,color:'var(--text3)',marginTop:2}}>{done}/{tasks.length} tasks{overdue>0?' · ⚠️ '+overdue+' overdue':''}</div>
                </div>
                <HealthScoreBadge client={c}/>
              </div>;
            })}
          </div>
        }
      </div>
      <div className="grid-3">
        {[
          {title:'Task Completion',v:totalTasks>0?Math.round(doneTasks/totalTasks*100)+'%':'0%',sub:doneTasks+' of '+totalTasks+' tasks done'},
          {title:'Outstanding',v:curr(totalRev-paidRev),sub:'Unpaid invoice balances'},
          {title:'Billable Value',v:curr(Math.round(totalHrs*(settings.hourlyRate||2000))),sub:totalHrs.toFixed(1)+'h \u00D7 \u20B9'+(settings.hourlyRate||2000).toLocaleString('en-IN')+'/hr'},
        ].map(s=><div key={s.title} className="card">
          <div style={{fontFamily:'var(--font-display)',fontWeight:800,fontSize:24,color:'var(--text)'}}>{s.v}</div>
          <div style={{fontWeight:600,fontSize:13,marginTop:4}}>{s.title}</div>
          <div style={{fontSize:12,color:'var(--text3)',marginTop:4}}>{s.sub}</div>
        </div>)}
      </div>
    </div>
  );
}

function AdminOverview({stats, clients, settings, onSelect}) {
  const recent = [...clients].sort((a,b) => new Date(b.createdAt||0) - new Date(a.createdAt||0)).slice(0,6);
  const overdueInvoices = clients.flatMap(c => (c.invoices||[]).filter(i=>i.status==='overdue').map(i=>({...i,clientName:c.name,clientId:c.id})));
  const statusDist = Object.keys(STATUS).map(s=>({s,n:clients.filter(c=>c.status===s).length})).filter(x=>x.n>0);

  return (
    <div className="space-4 fade-in">
      <div style={{marginBottom:8}}>
        <h1 style={{fontFamily:'var(--font-display)',fontWeight:800,fontSize:28,background:'linear-gradient(135deg,#f1f5f9,#e5e7eb)',WebkitBackgroundClip:'text',WebkitTextFillColor:'transparent'}}>Dashboard</h1>
        <p style={{color:'var(--text3)',fontSize:13,marginTop:4}}>Welcome back — here's what's happening today</p>
      </div>
      <div className="grid-4">
        <div className="stat-card c-blue">
          <div className="stat-icon" style={{background:'rgba(59,130,246,.15)'}}><Icon n="users" s={22} c="#93c5fd"/></div>
          <div><div className="stat-label">Total Clients</div><div className="stat-value">{stats.total}</div><div style={{fontSize:11,color:'var(--text3)',marginTop:4}}>{stats.active} active</div></div>
        </div>
        <div className="stat-card c-green">
          <div className="stat-icon" style={{background:'rgba(16,185,129,.15)'}}><Icon n="dollar" s={22} c="#34d399"/></div>
          <div><div className="stat-label">Revenue Collected</div><div className="stat-value" style={{fontSize:20}}>{curr(stats.revenue)}</div><div style={{fontSize:11,color:'var(--text3)',marginTop:4}}>{curr(stats.due)} outstanding</div></div>
        </div>
        <div className="stat-card c-amber">
          <div className="stat-icon" style={{background:'rgba(245,158,11,.15)'}}><Icon n="project" s={22} c="#fbbf24"/></div>
          <div><div className="stat-label">Task Completion</div><div className="stat-value">{stats.totalTasks>0?Math.round(stats.completedTasks/stats.totalTasks*100):0}%</div><div style={{fontSize:11,color:'var(--text3)',marginTop:4}}>{stats.completedTasks}/{stats.totalTasks} done</div></div>
        </div>
        <div className="stat-card c-purple">
          <div className="stat-icon" style={{background:'rgba(255,255,255,.10)'}}><Icon n="support" s={22} c="#f3f4f6"/></div>
          <div><div className="stat-label">Open Tickets</div><div className="stat-value">{stats.pending}</div><div style={{fontSize:11,color:'var(--text3)',marginTop:4}}>{stats.avgProgress}% avg progress</div></div>
        </div>
      </div>
      {overdueInvoices.length > 0 && (
        <div style={{background:'rgba(239,68,68,.08)',border:'1px solid rgba(239,68,68,.2)',borderRadius:14,padding:'14px 18px',display:'flex',alignItems:'center',gap:14}}>
          <span style={{fontSize:20}}>⚠️</span>
          <div>
            <div style={{fontWeight:700,fontSize:13,color:'#f87171'}}>{overdueInvoices.length} Overdue Invoice{overdueInvoices.length>1?'s':''}</div>
            <div style={{fontSize:12,color:'var(--text3)',marginTop:2}}>{overdueInvoices.map(i=>i.clientName).join(', ')}</div>
          </div>
        </div>
      )}
      <div className="grid-2">
        <div className="card">
          <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',marginBottom:16}}>
            <h3 style={{fontFamily:'var(--font-display)',fontWeight:700,fontSize:15}}>Recent Clients</h3>
            <span style={{fontSize:11,color:'var(--text3)'}}>{recent.length} shown</span>
          </div>
          {recent.length===0?<div className="empty-state" style={{padding:'30px 0'}}><div className="empty-icon">👥</div><div className="empty-text">No clients yet.<br/>Add your first client to get started.</div></div>:
            <div>{recent.map(c=><ClientRowItem key={c.id} c={c} settings={settings} onSelect={()=>onSelect(c.id)}/>)}</div>}
        </div>
        <div className="card">
          <h3 style={{fontFamily:'var(--font-display)',fontWeight:700,fontSize:15,marginBottom:16}}>Project Status</h3>
          {statusDist.length===0?<div className="empty-state" style={{padding:'30px 0'}}><div className="empty-icon">📊</div><div className="empty-text">No data yet</div></div>:
            <div className="space-3">
              {statusDist.map(({s,n})=>{
                const c=sc(s);const pct=Math.round(n/clients.length*100);
                return <div key={s}>
                  <div style={{display:'flex',justifyContent:'space-between',marginBottom:5}}>
                    <span style={{fontSize:12,color:'var(--text2)',display:'flex',alignItems:'center',gap:6}}>
                      <span style={{width:8,height:8,borderRadius:'50%',background:c.dot,display:'inline-block',boxShadow:`0 0 6px ${c.dot}`}}/>{s}
                    </span>
                    <span style={{fontSize:12,fontWeight:700,color:'var(--text)'}}>{n}</span>
                  </div>
                  <div className="progress-bar"><div className="progress-fill" style={{width:pct+'%',background:c.dot}}/></div>
                </div>;
              })}
            </div>
          }
          {stats.pending>0&&<div style={{marginTop:20,padding:'12px 14px',background:'rgba(239,68,68,.08)',border:'1px solid rgba(239,68,68,.15)',borderRadius:12}}>
            <div style={{fontSize:12,color:'#f87171',fontWeight:700}}>🎫 {stats.pending} open support ticket{stats.pending!==1?'s':''}</div>
            <div style={{fontSize:11,color:'var(--text3)',marginTop:2}}>Needs attention</div>
          </div>}
        </div>
      </div>
    </div>
  );
}

function AdminClients({clients,settings,onSelect,onEdit,onDelete,onTogglePin}){
  const [q,setQ]=useState('');
  const [sf,setSf]=useState('All');
  const [selected,setSelected]=useState([]);
  const [pg,setPg]=useState(1);const perPage=20;

  const sorted=useMemo(()=>[...clients.filter(c=>c.pinned),...clients.filter(c=>!c.pinned)],[clients]);
  const filtered=useMemo(()=>sorted.filter(c=>{
    const m=!q||[c.name,c.company,c.projectName,c.email].some(x=>(x||'').toLowerCase().includes(q.toLowerCase()));
    return m&&(sf==='All'||c.status===sf);
  }),[sorted,q,sf]);

  const toggleSelect=id=>setSelected(p=>p.includes(id)?p.filter(x=>x!==id):[...p,id]);
  const clearSel=()=>setSelected([]);
  const bulkExport=()=>{downloadJSON({clients:clients.filter(c=>selected.includes(c.id)),exportedAt:new Date().toISOString()},'selected-clients.json');};
  const bulkDelete=()=>{if(!confirm('Delete '+selected.length+' clients?'))return;selected.forEach(id=>onDelete(id));setSelected([]);};

  return (
    <div className="space-4 fade-in">
      <div style={{marginBottom:8}}>
        <h1 style={{fontFamily:'var(--font-display)',fontWeight:800,fontSize:26,background:'linear-gradient(135deg,#f1f5f9,#e5e7eb)',WebkitBackgroundClip:'text',WebkitTextFillColor:'transparent'}}>Clients</h1>
        <p style={{color:'var(--text3)',fontSize:13,marginTop:4}}>{clients.length} total clients</p>
      </div>
      <div style={{display:'flex',gap:12,flexWrap:'wrap',alignItems:'center'}}>
        <div className="search-bar" style={{flex:1,minWidth:200}}>
          <span className="search-icon"><Icon n="search" s={14}/></span>
          <input className="input" placeholder="Search clients…" value={q} onChange={e=>{setQ(e.target.value);setPg(1);}}/>
        </div>
        <select className="input" style={{width:'auto'}} value={sf} onChange={e=>{setSf(e.target.value);setPg(1);}}>
          <option>All</option>{Object.keys(STATUS).map(s=><option key={s}>{s}</option>)}
        </select>
        {filtered.length>0&&<label style={{display:'flex',alignItems:'center',gap:6,fontSize:12,color:'var(--text2)',cursor:'pointer',whiteSpace:'nowrap'}}>
          <input type="checkbox" checked={selected.length===filtered.length&&filtered.length>0} onChange={e=>e.target.checked?setSelected(filtered.map(c=>c.id)):clearSel()}/>Select all
        </label>}
      </div>
      {selected.length>0&&<div style={{background:'linear-gradient(135deg,rgba(255,255,255,.12),rgba(255,255,255,.08))',border:'1px solid rgba(255,255,255,.20)',borderRadius:10,padding:'10px 16px',display:'flex',alignItems:'center',gap:12,animation:'slideDown .15s ease',backdropFilter:'blur(8px)'}}>
        <span style={{fontSize:13,fontWeight:700,color:'#e5e7eb'}}>{selected.length} selected</span>
        <button className="btn btn-secondary btn-sm" onClick={bulkExport}><Icon n="download" s={12}/> Export</button>
        <button className="btn btn-danger btn-sm" onClick={bulkDelete}><Icon n="trash" s={12}/> Delete</button>
        <button className="btn btn-ghost btn-sm" onClick={clearSel}>✕ Clear</button>
      </div>}
      <div className="card" style={{padding:0,overflow:'hidden'}}>
        {filtered.length===0?<div className="empty-state"><div className="empty-icon">🔍</div><div className="empty-text">No clients match your filter.</div></div>:
          <div>
            <div style={{display:'grid',gridTemplateColumns:'32px 1fr auto auto auto auto',gap:10,padding:'10px 16px',borderBottom:'1px solid var(--border)',background:'rgba(255,255,255,.015)'}}>
              <span/>{['Client','Health','Status','Revenue','Actions'].map(h=><span key={h} style={{fontSize:11,fontWeight:700,color:'var(--text3)',textTransform:'uppercase',letterSpacing:'.04em'}}>{h}</span>)}
            </div>
            {filtered.slice((pg-1)*perPage,pg*perPage).map(c=>(
              <div key={c.id} style={{display:'grid',gridTemplateColumns:'32px 1fr auto auto auto auto',gap:10,padding:'10px 16px',alignItems:'center',borderBottom:'1px solid var(--border)',transition:'background .15s',borderLeft:c.pinned?'2px solid var(--accent)':'2px solid transparent'}}
                onMouseOver={e=>e.currentTarget.style.background='rgba(255,255,255,.025)'}
                onMouseOut={e=>e.currentTarget.style.background='transparent'}>
                <input type="checkbox" checked={selected.includes(c.id)} onChange={()=>toggleSelect(c.id)} onClick={e=>e.stopPropagation()}/>
                <div style={{display:'flex',alignItems:'center',gap:10,cursor:'pointer'}} onClick={()=>onSelect(c.id)}>
                  <Avatar name={c.name} size={36} color={settings.brandColor||'#f8fafc'}/>
                  <div>
                    <div style={{fontWeight:600,fontSize:13,display:'flex',alignItems:'center',gap:6}}>
                      {c.pinned&&<span style={{fontSize:12}}>📌</span>}{c.name}
                    </div>
                    <div style={{fontSize:11,color:'var(--text3)'}}>{c.company||c.projectName||'No project'}</div>
                  </div>
                </div>
                <div style={{cursor:'pointer'}} onClick={()=>onSelect(c.id)}><HealthScoreBadge client={c}/></div>
                <div style={{cursor:'pointer'}} onClick={()=>onSelect(c.id)}><Badge bg={sc(c.status).bg} text={sc(c.status).text}>{c.status||'Pending'}</Badge></div>
                <div style={{fontSize:13,fontWeight:700,cursor:'pointer'}} onClick={()=>onSelect(c.id)}>{curr((c.invoices||[]).reduce((a,i)=>a+getInvoicePaidAmount(i),0))}</div>
                <div style={{display:'flex',gap:3}} onClick={e=>e.stopPropagation()}>
                  <button className="btn btn-ghost btn-icon btn-sm" onClick={()=>onTogglePin&&onTogglePin(c.id)} title={c.pinned?'Unpin':'Pin'} style={{fontSize:13}}>{c.pinned?'📌':'📎'}</button>
                  <button className="btn btn-ghost btn-icon btn-sm" onClick={()=>onEdit(c)}><Icon n="edit" s={13}/></button>
                  <button className="btn btn-danger btn-icon btn-sm" onClick={()=>{if(confirm('Delete client?'))onDelete(c.id);}}><Icon n="trash" s={13}/></button>
                </div>
              </div>
            ))}
          </div>
        }
      </div>
      <Pagination total={filtered.length} page={pg} perPage={perPage} onChange={setPg}/>
    </div>
  );
}
"""

# New AdminApp with all new features
new_admin_app = r"""
/* ═══ ADMIN APP (UPGRADED) ═══ */
function AdminApp({onSwitchPanel}){
  const [settings,setSettings]=useState(DEF_SETTINGS);
  const [clients,setClients]=useState([]);
  const [loading,setLoading]=useState(true);
  const [authed,setAuthed]=useState(()=>{try{return localStorage.getItem('ut_authed')==='true';}catch{return false;}});
  const [page,setPage]=useState('overview');
  const [selId,setSelId]=useState(null);
  const [editClient,setEditClient]=useState(null);
  const [showNotifs,setShowNotifs]=useState(false);
  const [cmdOpen,setCmdOpen]=useState(false);
  const [sideCollapsed,setSideCollapsed]=useState(false);
  const [mobileMenuOpen,setMobileMenuOpen]=useState(false);
  const [showShortcuts,setShowShortcuts]=useState(false);
  const {show,ToastEl}=useToast();
  const {theme,toggle:toggleTheme}=useTheme();
  const sessionTime=useSessionTimer();

  useEffect(()=>{
    Promise.all([getSettings(),getClients()]).then(([s,c])=>{
      setSettings(s);setClients(c.map(normalizeClientData));setLoading(false);
    });
  },[]);

  useEffect(()=>{
    if(!authed||!db())return;
    const unsub=db().collection(FS_COL).onSnapshot(q=>{
      const c=[];q.forEach(d=>c.push(normalizeClientData({id:d.id,...d.data()})));setClients(c);
    },()=>{});
    return ()=>unsub();
  },[authed]);

  useEffect(()=>{
    if(!authed)return;
    const h=e=>{
      if((e.metaKey||e.ctrlKey)&&e.key==='k'){e.preventDefault();setCmdOpen(true);}
      if(e.key==='Escape'){setCmdOpen(false);setShowShortcuts(false);}
      if(e.key==='?'&&!e.ctrlKey&&!e.metaKey&&document.activeElement.tagName!=='INPUT'&&document.activeElement.tagName!=='TEXTAREA')setShowShortcuts(true);
    };
    window.addEventListener('keydown',h);return()=>window.removeEventListener('keydown',h);
  },[authed]);

  const updSettings=s=>{setSettings(s);saveSettings(s);show('Settings saved!');};
  const applyManagerDecision=(req,decision)=>{
    let nextSettings={...settings,managerApprovals:(settings.managerApprovals||[]).map(x=>x.id===req.id?{...x,status:decision,reviewedAt:new Date().toISOString(),reviewedBy:'admin'}:x)};
    if(decision==='approved'&&req.payloadClient){const normalized=normalizeClientData(req.payloadClient);setClients(p=>p.map(c=>c.id===normalized.id?normalized:c));saveClient(normalized);}
    if(decision==='approved'&&req.payloadSettingsPatch)nextSettings={...nextSettings,...req.payloadSettingsPatch};
    nextSettings={...pushManagerAudit(nextSettings,{type:'review',actor:'admin',action:`Manager request ${decision}`,requestId:req.id,clientName:req.clientName||'General'}),
      managerNotifications:[{id:uid(),text:`Admin ${decision} your request${req.clientName?` for ${req.clientName}`:''}`,read:false,ts:new Date().toISOString(),requestId:req.id,status:decision},...(nextSettings.managerNotifications||[])].slice(0,100)};
    setSettings(nextSettings);saveSettings(nextSettings);show(`Manager request ${decision}`);
  };

  const updClient=(id,fn)=>{
    setClients(prev=>{
      const nc=prev.map(c=>c.id===id?normalizeClientData(fn(c)):c);
      const updated=nc.find(c=>c.id===id);
      if(updated)saveClient(updated);
      return nc;
    });
  };

  const delClient=id=>{
    setClients(p=>p.filter(c=>c.id!==id));deleteClient(id);
    if(selId===id){setSelId(null);setPage('clients');}
    show('Client deleted');
  };

  const addOrUpdateClient=c=>{
    const isNew=!clients.find(x=>x.id===c.id);
    if(isNew){
      const nc=normalizeClientData({...c,id:c.id||tok(),createdAt:new Date().toISOString(),pinned:false,activity:[],notifications:[],messages:[],tasks:[],milestones:[],files:[],invoices:[],approvals:[],tickets:[],timeEntries:[],notes:[],contracts:[],feedback:[],expenses:[],meetings:[],links:[],announcements:[],proposals:[],requests:[],followUps:[],reminders:[]});
      setClients(p=>[...p,nc]);saveClient(nc);
    } else {
      const normalized=normalizeClientData(c);
      setClients(p=>p.map(x=>x.id===c.id?normalized:x));saveClient(normalized);
    }
    setPage('clients');show(isNew?'Client added!':'Client updated!');
  };

  const handleCmd=cmd=>{
    if(cmd.action==='addClient'){setEditClient({});setPage('form');}
    if(cmd.action==='overview'){setPage('overview');setSelId(null);}
    if(cmd.action==='analytics'){setPage('analytics');setSelId(null);}
    if(cmd.action==='settings'){setPage('settings');setSelId(null);}
    if(cmd.action==='calendar'){setPage('calendar');setSelId(null);}
    if(cmd.action==='reports'){setPage('reports');setSelId(null);}
    if(cmd.action==='openClient'){setSelId(cmd.data);setPage('client');}
    if(cmd.action==='exportAll'){downloadJSON({settings,clients,exportedAt:new Date().toISOString()},'clientos-backup.json');show('Data exported!');}
  };

  const togglePin=id=>{
    updClient(id,c=>({...c,pinned:!c.pinned}));
    const c=clients.find(x=>x.id===id);
    show(c?.pinned?'Unpinned client':'Pinned client');
  };

  if(loading)return<Loader/>;
  if(!authed)return<AdminLogin settings={settings} onLogin={()=>{setAuthed(true);try{localStorage.setItem('ut_authed','true');}catch{}}} onSwitchPanel={onSwitchPanel}/>;

  const selClient=clients.find(c=>c.id===selId);
  const allNotifs=clients.flatMap(c=>(c.notifications||[]).map(n=>({...n,clientName:c.name,clientId:c.id}))).sort((a,b)=>new Date(b.ts)-new Date(a.ts)).slice(0,30);
  const unreadCount=allNotifs.filter(n=>!n.read).length;
  const pendingManagerApprovals=(settings.managerApprovals||[]).filter(x=>(x.status||'pending')==='pending').length;

  const stats={
    total:clients.length,active:clients.filter(c=>c.status==='In Progress').length,
    revenue:clients.reduce((s,c)=>(c.invoices||[]).reduce((a,i)=>a+getInvoicePaidAmount(i),0)+s,0),
    pending:clients.reduce((s,c)=>(c.tickets||[]).filter(t=>t.status==='open').length+s,0),
    due:clients.reduce((s,c)=>(c.invoices||[]).filter(i=>i.status==='sent'||i.status==='overdue').reduce((a,i)=>a+getInvoiceBalance(i),0)+s,0),
    completed:clients.filter(c=>c.status==='Completed').length,
    totalTasks:clients.reduce((s,c)=>(c.tasks||[]).length+s,0),
    completedTasks:clients.reduce((s,c)=>(c.tasks||[]).filter(t=>t.status==='completed').length+s,0),
    totalHours:clients.reduce((s,c)=>(c.timeEntries||[]).reduce((a,e)=>a+e.hours,0)+s,0),
    avgProgress:clients.length?Math.round(clients.reduce((s,c)=>s+(c.progress||0),0)/clients.length):0,
  };

  const navMain=[
    {id:'overview',label:'Overview',icon:'dashboard'},{id:'clients',label:'Clients',icon:'users'},
    {id:'approvals',label:'Manager Approvals',icon:'check'},{id:'analytics',label:'Analytics',icon:'analytics'},
    {id:'calendar',label:'Calendar',icon:'calendar'},{id:'reports',label:'Reports',icon:'pieChart'},
    {id:'settings',label:'Settings',icon:'settings'},
  ];

  const clearNotifs=()=>{
    clients.forEach(c=>{if((c.notifications||[]).some(n=>!n.read))updClient(c.id,x=>({...x,notifications:(x.notifications||[]).map(n=>({...n,read:true}))}));});
    setShowNotifs(false);
  };

  const pinnedClients=clients.filter(c=>c.pinned);
  const unpinnedClients=clients.filter(c=>!c.pinned);

  return (
    <div className="app-layout">
      <div className="aurora-bg"><div className="aurora-blob"/><div className="aurora-blob"/><div className="aurora-blob"/></div>
      {mobileMenuOpen&&<div className="sidebar-overlay" onClick={()=>setMobileMenuOpen(false)}/>}

      <aside className={`sidebar ${sideCollapsed?'collapsed':''} ${mobileMenuOpen?'mobile-open':''}`}>
        <div className="sidebar-brand">
          <div style={{display:'flex',alignItems:'center',gap:10}}>
            <div className="brand-logo" onClick={()=>setSideCollapsed(!sideCollapsed)} style={{cursor:'pointer',overflow:'hidden'}}>
              <img src={LOGO_B64} alt="Logo" style={{width:'100%',height:'100%',objectFit:'contain'}}/>
            </div>
            <div>
              <div className="brand-name">{settings.businessName}</div>
              <div className="brand-sub">Admin Panel</div>
            </div>
          </div>
        </div>
        <nav style={{flex:1,padding:'8px',overflowY:'auto'}}>
          <div className="nav-section">
            <div className="nav-label">Main</div>
            {navMain.map(n=>(
              <div key={n.id} className={`nav-item ${page===n.id&&!selId?'active':''}`}
                onClick={()=>{setPage(n.id);setSelId(null);setEditClient(null);setMobileMenuOpen(false);}}>
                <Icon n={n.icon} s={16}/><span>{n.label}</span>
                {n.id==='clients'&&clients.length>0&&<span className="nav-badge" style={{marginLeft:'auto'}}>{clients.length}</span>}
                {n.id==='approvals'&&pendingManagerApprovals>0&&<span className="nav-badge" style={{marginLeft:'auto'}}>{pendingManagerApprovals}</span>}
              </div>
            ))}
          </div>
          {pinnedClients.length>0&&<div className="nav-section">
            <div className="nav-label">📌 Pinned</div>
            {pinnedClients.map(c=>(
              <div key={c.id} className={`nav-item ${selId===c.id?'active':''}`}
                onClick={()=>{setSelId(c.id);setPage('client');setEditClient(null);setMobileMenuOpen(false);}}>
                <Avatar name={c.name} size={22} color={settings.brandColor||'#f8fafc'}/>
                <span style={{flex:1,overflow:'hidden',textOverflow:'ellipsis',whiteSpace:'nowrap'}}>{c.name}</span>
              </div>
            ))}
          </div>}
          {unpinnedClients.length>0&&<div className="nav-section">
            <div className="nav-label">Clients</div>
            {unpinnedClients.slice(0,8).map(c=>(
              <div key={c.id} className={`nav-item ${selId===c.id?'active':''}`}
                onClick={()=>{setSelId(c.id);setPage('client');setEditClient(null);setMobileMenuOpen(false);}}>
                <Avatar name={c.name} size={22} color={settings.brandColor||'#f8fafc'}/>
                <span style={{flex:1,overflow:'hidden',textOverflow:'ellipsis',whiteSpace:'nowrap'}}>{c.name}</span>
                {(c.tickets||[]).filter(t=>t.status==='open').length>0&&<span className="nav-badge">{(c.tickets||[]).filter(t=>t.status==='open').length}</span>}
              </div>
            ))}
          </div>}
        </nav>
        <div style={{padding:'8px',borderTop:'1px solid var(--border)'}}>
          <div className="nav-item" style={{opacity:.6,fontSize:12}} onClick={()=>setShowShortcuts(true)}>
            <span style={{fontSize:14}}>⌨️</span><span className="sftext">Shortcuts (?)</span>
          </div>
          <div className="nav-item" onClick={()=>{setAuthed(false);try{localStorage.removeItem('ut_authed');}catch{}}}>
            <Icon n="logout" s={16}/><span>Sign Out</span>
          </div>
        </div>
      </aside>

      <div className="main-area">
        <header className="topbar">
          <button className="btn btn-ghost btn-icon" onClick={()=>{if(window.innerWidth<=768)setMobileMenuOpen(!mobileMenuOpen);else setSideCollapsed(!sideCollapsed);}}><Icon n="menu" s={16}/></button>
          <div className="topbar-title">
            {page==='client'&&selClient?selClient.name:page==='overview'?'Dashboard':page==='analytics'?'Analytics':page==='clients'?'All Clients':page==='approvals'?'Manager Approvals':page==='calendar'?'Calendar':page==='reports'?'Reports':page==='form'?'Client Form':'Settings'}
          </div>
          <div className="topbar-actions">
            <FirebaseStatus/>
            <div style={{fontSize:11,color:'var(--text3)',display:'flex',alignItems:'center',gap:4,padding:'4px 8px',borderRadius:8,background:'rgba(255,255,255,.04)'}}>
              <Icon n="clock" s={12}/><span>{sessionTime}</span>
            </div>
            <button className="btn btn-ghost btn-icon" onClick={toggleTheme} title="Toggle theme" style={{fontSize:15}}>{theme==='dark'?'☀️':'🌙'}</button>
            <div style={{position:'relative'}}>
              <button className="btn btn-ghost btn-icon" onClick={()=>setShowNotifs(!showNotifs)} style={{position:'relative'}}>
                <Icon n="bell" s={16}/>
                {unreadCount>0&&<span style={{position:'absolute',top:2,right:2,width:16,height:16,background:'#ef4444',borderRadius:'50%',fontSize:9,color:'#fff',display:'flex',alignItems:'center',justifyContent:'center',fontWeight:700}}>{unreadCount}</span>}
              </button>
              {showNotifs&&<div className="notif-dropdown" style={{position:'absolute',right:0,top:'calc(100% + 8px)',width:340,background:'var(--bg2)',border:'1px solid var(--border2)',borderRadius:18,boxShadow:'var(--shadow-lg)',zIndex:50,overflow:'hidden',backdropFilter:'blur(12px)'}}>
                <div style={{padding:'14px 16px',borderBottom:'1px solid var(--border)',display:'flex',justifyContent:'space-between',alignItems:'center'}}>
                  <span style={{fontFamily:'var(--font-display)',fontWeight:700,fontSize:14}}>Notifications</span>
                  <button className="btn btn-ghost btn-sm" onClick={clearNotifs} style={{fontSize:11}}>Mark all read</button>
                </div>
                <div style={{maxHeight:340,overflowY:'auto'}}>
                  {allNotifs.length===0?<div className="empty-state" style={{padding:'30px 20px'}}><div className="empty-icon">🔔</div><div className="empty-text">No notifications</div></div>:
                    allNotifs.slice(0,12).map(n=>(
                      <div key={n.id} className={`notif-item ${n.read?'':'unread'}`} onClick={()=>{setSelId(n.clientId);setPage('client');setShowNotifs(false);}}>
                        {!n.read&&<div className="notif-dot"/>}
                        <div style={{flex:1}}>
                          <div style={{fontSize:12,fontWeight:600,color:'var(--text2)',marginBottom:2}}>{n.clientName}</div>
                          <div style={{fontSize:12,color:'var(--text3)'}}>{n.text}</div>
                          <div style={{fontSize:11,color:'var(--text3)',marginTop:2}}>{ago(n.ts)}</div>
                        </div>
                      </div>
                    ))
                  }
                </div>
              </div>}
            </div>
            <button className="btn btn-primary btn-sm" onClick={()=>{setEditClient({});setPage('form');}}>
              <Icon n="plus" s={14}/> <span>Add Client</span>
            </button>
          </div>
        </header>

        <div className="content fade-in">
          {page==='overview'&&<AdminOverview stats={stats} clients={clients} settings={settings} onSelect={id=>{setSelId(id);setPage('client');}}/>}
          {page==='clients'&&<AdminClients clients={clients} settings={settings} onSelect={id=>{setSelId(id);setPage('client');}} onEdit={c=>{setEditClient(c);setPage('form');}} onDelete={delClient} onTogglePin={togglePin}/>}
          {page==='approvals'&&<ManagerApprovalsPanel requests={settings.managerApprovals||[]} onReview={applyManagerDecision}/>}
          {page==='analytics'&&<AdminAnalytics clients={clients} settings={settings}/>}
          {page==='calendar'&&<AdminCalendar clients={clients}/>}
          {page==='reports'&&<AdminReports clients={clients} settings={settings}/>}
          {page==='form'&&<ClientForm client={editClient} onSave={addOrUpdateClient} onCancel={()=>setPage(selId?'client':'clients')}/>}
          {page==='client'&&selClient&&<AdminClientDetail client={selClient} settings={settings} updClient={updClient} show={show} onEdit={()=>{setEditClient(selClient);setPage('form');}} onDelete={delClient}/>}
          {page==='settings'&&<AdminSettings settings={settings} updSettings={updSettings} clients={clients} onReviewManagerRequest={applyManagerDecision}/>}
        </div>
      </div>

      {ToastEl}
      {showNotifs&&<div style={{position:'fixed',inset:0,zIndex:40}} onClick={()=>setShowNotifs(false)}/>}
      {cmdOpen&&<CommandPalette clients={clients} onAction={handleCmd} onClose={()=>setCmdOpen(false)}/>}
      {showShortcuts&&<ShortcutsPanel onClose={()=>setShowShortcuts(false)}/>}
    </div>
  );
}
"""

# Now patch the admin code to remove old AdminApp, AdminOverview, AdminAnalytics, AdminClients
admin_code = chunk_admin

# Remove old AdminApp
app_start = admin_code.find('/* ═══ ADMIN APP ═══')
app_end = admin_code.find('\n/* ═══ ADMIN OVERVIEW ═══')
admin_code = admin_code[:app_start] + '\n/* ADMIN_APP_REPLACED */\n' + admin_code[app_end:]

# Remove old AdminOverview
ov_start = admin_code.find('/* ═══ ADMIN OVERVIEW ═══')
ov_end = admin_code.find('\nfunction ClientRowItem(')
admin_code = admin_code[:ov_start] + '\n/* OVERVIEW_REPLACED */\n' + admin_code[ov_end:]

# Remove old AdminClients
ac_start = admin_code.find('/* ═══ CLIENTS LIST ═══')
ac_end = admin_code.find('\n/* ═══ CLIENT FORM ═══')
admin_code = admin_code[:ac_start] + '\n/* CLIENTS_REPLACED */\n' + admin_code[ac_end:]

# Remove old AdminAnalytics
an_start = admin_code.find('\nfunction AdminAnalytics(')
an_end = admin_code.find('\n/* ═══ ADMIN SETTINGS ═══')
admin_code = admin_code[:an_start] + '\n/* ANALYTICS_REPLACED */\n' + admin_code[an_end:]

# Now remove normalizeClientData pinned (it will be added in new_components)
# Actually normalizeClientData is in chunk_db, let's patch it to add pinned
chunk_db_patched = chunk_db.replace(
    'websiteChangeRequestEnabled: client.websiteChangeRequestEnabled||false,',
    'websiteChangeRequestEnabled: client.websiteChangeRequestEnabled||false,\n    pinned: client.pinned||false,'
)

# CSS for the new design
new_css = r"""<style>
:root {
  --bg: #060711;
  --bg2: #0b0d1a;
  --bg3: #10122a;
  --surface: #141728;
  --surface2: #1c1f38;
  --surface3: #242848;
  --border: rgba(255,255,255,0.06);
  --border2: rgba(255,255,255,0.1);
  --border3: rgba(255,255,255,0.15);
  --accent: #f8fafc;
  --accent2: #9ca3af;
  --accent3: #d1d5db;
  --accent-glow: rgba(255,255,255,0.24);
  --accent-glow2: rgba(255,255,255,0.12);
  --green: #10b981;
  --green-glow: rgba(16,185,129,0.2);
  --amber: #f59e0b;
  --red: #ef4444;
  --blue: #3b82f6;
  --cyan: #06b6d4;
  --pink: #ec4899;
  --orange: #f97316;
  --teal: #14b8a6;
  --text: #f1f5f9;
  --text2: #94a3b8;
  --text3: #4a5568;
  --font-display: 'Plus Jakarta Sans', sans-serif;
  --font-body: 'Inter', sans-serif;
  --radius: 16px;
  --radius-sm: 10px;
  --radius-xs: 6px;
  --radius-lg: 24px;
  --shadow: 0 4px 24px rgba(0,0,0,0.4);
  --shadow-lg: 0 8px 48px rgba(0,0,0,0.6);
  --shadow-accent: 0 8px 32px rgba(255,255,255,0.24);
}
[data-theme="light"] {
  --bg: #f8fafc; --bg2: #f1f5f9; --bg3: #e8eef5;
  --surface: #ffffff; --surface2: #f8fafc; --surface3: #f1f5f9;
  --border: rgba(0,0,0,0.08); --border2: rgba(0,0,0,0.12); --border3: rgba(0,0,0,0.18);
  --text: #0f172a; --text2: #475569; --text3: #94a3b8;
  --shadow: 0 4px 24px rgba(0,0,0,0.08); --shadow-lg: 0 8px 48px rgba(0,0,0,0.15);
}
*{margin:0;padding:0;box-sizing:border-box}
html,body{height:100%;-webkit-text-size-adjust:100%;background:var(--bg);color:var(--text);font-family:var(--font-body);font-size:14px;line-height:1.6}
::-webkit-scrollbar{width:4px;height:4px}
::-webkit-scrollbar-track{background:transparent}
::-webkit-scrollbar-thumb{background:var(--border2);border-radius:99px}
.aurora-bg{position:fixed;inset:0;pointer-events:none;z-index:0;overflow:hidden}
.aurora-blob{position:absolute;border-radius:50%;filter:blur(80px);opacity:0.07;animation:aurora-float 20s ease-in-out infinite}
.aurora-blob:nth-child(1){width:600px;height:600px;background:radial-gradient(circle,#f8fafc,transparent);top:-200px;left:-100px}
.aurora-blob:nth-child(2){width:500px;height:500px;background:radial-gradient(circle,#9ca3af,transparent);top:40%;right:-150px;animation-delay:-7s}
.aurora-blob:nth-child(3){width:400px;height:400px;background:radial-gradient(circle,#d1d5db,transparent);bottom:-100px;left:30%;animation-delay:-14s}
@keyframes aurora-float{0%,100%{transform:translate(0,0) scale(1)}33%{transform:translate(30px,-30px) scale(1.05)}66%{transform:translate(-20px,20px) scale(0.95)}}
body::before{content:'';position:fixed;inset:0;pointer-events:none;z-index:0;background-image:url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.03'/%3E%3C/svg%3E");opacity:.35}
#root{position:relative;z-index:1}
.app-layout{display:flex;height:100vh;overflow:hidden}
.sidebar{width:260px;flex-shrink:0;display:flex;flex-direction:column;background:rgba(11,13,26,0.97);backdrop-filter:blur(20px);border-right:1px solid var(--border);transition:width .3s cubic-bezier(.4,0,.2,1);z-index:50}
.sidebar.collapsed{width:64px}
.sidebar.collapsed .brand-name,.sidebar.collapsed .brand-sub,.sidebar.collapsed .nav-item span,.sidebar.collapsed .nav-label,.sidebar.collapsed .nav-badge,.sidebar.collapsed .sftext{display:none}
.sidebar.collapsed .nav-item{justify-content:center;padding:10px 0}
.sidebar-brand{padding:20px 16px 16px;border-bottom:1px solid var(--border)}
.brand-logo{width:38px;height:38px;border-radius:12px;display:flex;align-items:center;justify-content:center;background:linear-gradient(135deg,var(--accent),var(--accent2));box-shadow:0 0 24px var(--accent-glow);flex-shrink:0}
.brand-name{font-family:var(--font-display);font-weight:700;font-size:14px;color:var(--text);line-height:1.2}
.brand-sub{font-size:11px;color:var(--text3)}
.nav-section{padding:8px 8px 4px}
.nav-label{font-size:10px;font-weight:700;color:var(--text3);letter-spacing:.1em;text-transform:uppercase;padding:4px 8px 6px}
.nav-item{display:flex;align-items:center;gap:10px;padding:9px 12px;border-radius:var(--radius-sm);cursor:pointer;transition:all .2s cubic-bezier(.4,0,.2,1);font-size:13px;font-weight:500;color:var(--text2);position:relative;white-space:nowrap;overflow:hidden;border:1px solid transparent}
.nav-item:hover{background:rgba(255,255,255,.05);color:var(--text)}
.nav-item.active{background:linear-gradient(135deg,rgba(255,255,255,0.14),rgba(255,255,255,0.08));border:1px solid rgba(255,255,255,0.24);color:#e5e7eb}
.nav-item.active::before{content:'';position:absolute;left:0;top:20%;bottom:20%;width:3px;border-radius:0 3px 3px 0;background:linear-gradient(to bottom,var(--accent),var(--accent2))}
.nav-badge{margin-left:auto;min-width:20px;height:20px;border-radius:99px;padding:0 6px;background:linear-gradient(135deg,var(--accent),var(--accent2));color:#fff;font-size:10px;font-weight:700;display:flex;align-items:center;justify-content:center;box-shadow:0 2px 8px var(--accent-glow)}
.main-area{flex:1;display:flex;flex-direction:column;overflow:hidden}
.topbar{height:58px;flex-shrink:0;background:rgba(11,13,26,0.9);backdrop-filter:blur(20px);border-bottom:1px solid var(--border);display:flex;align-items:center;padding:0 24px;gap:16px}
.topbar-title{font-family:var(--font-display);font-size:16px;font-weight:700;flex:1;background:linear-gradient(135deg,var(--text),var(--text2));-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.topbar-actions{display:flex;align-items:center;gap:8px}
.content{flex:1;overflow:auto;padding:24px}
.card{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:20px;transition:all .2s ease}
.card-sm{padding:14px 16px}
.card-hover:hover{border-color:var(--border2);transform:translateY(-2px);box-shadow:var(--shadow)}
.card-glass{background:rgba(20,23,40,0.6);backdrop-filter:blur(20px);border:1px solid var(--border);border-radius:var(--radius)}
.stat-card{background:linear-gradient(135deg,var(--surface),var(--surface2));border:1px solid var(--border);border-radius:var(--radius);padding:20px;display:flex;align-items:center;gap:16px;position:relative;overflow:hidden;transition:all .3s ease}
.stat-card:hover{transform:translateY(-2px);box-shadow:0 8px 32px rgba(0,0,0,0.4);border-color:var(--border2)}
.stat-card::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;background:linear-gradient(90deg,var(--accent),var(--accent2))}
.stat-card::after{content:'';position:absolute;right:-20px;top:-20px;width:100px;height:100px;border-radius:50%;opacity:.06}
.stat-card.c-blue::after{background:var(--blue)}
.stat-card.c-green::after{background:var(--green)}
.stat-card.c-amber::after{background:var(--amber)}
.stat-card.c-purple::after{background:var(--accent2)}
.stat-icon{width:48px;height:48px;border-radius:14px;display:flex;align-items:center;justify-content:center;font-size:22px;flex-shrink:0}
.stat-label{font-size:12px;color:var(--text2);font-weight:500}
.stat-value{font-family:var(--font-display);font-size:28px;font-weight:800;color:var(--text);line-height:1;margin-top:2px}
.btn{display:inline-flex;align-items:center;gap:6px;padding:8px 16px;border-radius:var(--radius-sm);font-size:13px;font-weight:600;cursor:pointer;border:none;transition:all .2s ease;font-family:var(--font-body);white-space:nowrap}
.btn-primary{background:linear-gradient(135deg,var(--accent),var(--accent2));color:#fff;box-shadow:0 4px 15px var(--accent-glow)}
.btn-primary:hover{transform:translateY(-1px);box-shadow:0 8px 25px var(--accent-glow)}
.btn-secondary{background:rgba(255,255,255,.07);color:var(--text);border:1px solid var(--border2)}
.btn-secondary:hover{background:rgba(255,255,255,.11);border-color:var(--border3)}
.btn-ghost{background:transparent;color:var(--text2)}
.btn-ghost:hover{background:rgba(255,255,255,.05);color:var(--text)}
.btn-danger{background:rgba(239,68,68,.15);color:#f87171;border:1px solid rgba(239,68,68,.2)}
.btn-danger:hover{background:rgba(239,68,68,.25)}
.btn-success{background:rgba(16,185,129,.15);color:#34d399;border:1px solid rgba(16,185,129,.2)}
.btn-success:hover{background:rgba(16,185,129,.25)}
.btn-warning{background:rgba(245,158,11,.15);color:#fbbf24;border:1px solid rgba(245,158,11,.2)}
.btn-info{background:rgba(6,182,212,.15);color:#22d3ee;border:1px solid rgba(6,182,212,.2)}
.btn-sm{padding:5px 12px;font-size:12px;border-radius:8px}
.btn-icon{padding:7px;border-radius:8px}
.btn-xs{padding:3px 8px;font-size:11px;border-radius:6px}
.btn-lg{padding:12px 28px;font-size:15px;border-radius:14px}
.btn-group{display:flex;gap:0}
.btn-group .btn{border-radius:0}
.btn-group .btn:first-child{border-radius:8px 0 0 8px}
.btn-group .btn:last-child{border-radius:0 8px 8px 0}
.input{width:100%;padding:9px 12px;border:1.5px solid var(--border2);border-radius:10px;font-size:13px;outline:none;transition:all .2s;background:rgba(255,255,255,.04);color:var(--text);font-family:var(--font-body)}
.input:focus{border-color:var(--accent);box-shadow:0 0 0 3px var(--accent-glow)}
.input::placeholder{color:var(--text3)}
.input option{background:var(--surface)}
textarea.input{resize:vertical;min-height:80px}
.badge{display:inline-flex;align-items:center;padding:3px 10px;border-radius:99px;font-size:11px;font-weight:700;gap:4px}
.badge-dot{width:6px;height:6px;border-radius:50%;flex-shrink:0}
.table-wrap{overflow-x:auto;-webkit-overflow-scrolling:touch}
.table{width:100%;border-collapse:collapse}
.table th{font-size:11px;font-weight:700;color:var(--text3);text-align:left;padding:10px 14px;text-transform:uppercase;letter-spacing:.05em;border-bottom:1px solid var(--border)}
.table td{padding:12px 14px;border-bottom:1px solid rgba(255,255,255,.03);font-size:13px}
.table tr:hover td{background:rgba(255,255,255,.02)}
.table tr:last-child td{border-bottom:none}
.progress-bar{height:6px;background:rgba(255,255,255,.06);border-radius:99px;overflow:hidden}
.progress-fill{height:100%;border-radius:99px;transition:width .6s cubic-bezier(.4,0,.2,1);background:linear-gradient(90deg,var(--accent),var(--accent2))}
.tabs{display:flex;gap:0;border-bottom:1px solid var(--border);overflow-x:auto;overflow-y:hidden;-webkit-overflow-scrolling:touch;scrollbar-width:thin}
.tabs::-webkit-scrollbar{height:4px}
.tabs::-webkit-scrollbar-thumb{background:var(--border2);border-radius:99px}
.tab-item{padding:10px 16px;font-size:13px;font-weight:500;color:var(--text2);cursor:pointer;border-bottom:2px solid transparent;transition:all .15s;white-space:nowrap;flex-shrink:0}
.tab-item:hover{color:var(--text)}
.tab-item.active{color:#e5e7eb;border-bottom-color:var(--accent)}
.modal-overlay{position:fixed;inset:0;z-index:100;background:rgba(0,0,0,.75);backdrop-filter:blur(8px);display:flex;align-items:center;justify-content:center;padding:16px;animation:fadeIn .15s ease}
.modal-box{background:var(--bg2);border:1px solid var(--border2);border-radius:var(--radius-lg);box-shadow:var(--shadow-lg);width:100%;max-height:90vh;overflow-y:auto;animation:slideUp .25s cubic-bezier(.4,0,.2,1)}
.modal-box.wide{max-width:720px}
.modal-box.medium{max-width:520px}
.modal-box.small{max-width:400px}
.modal-box.xl{max-width:900px}
.modal-footer{padding:16px 24px;border-top:1px solid var(--border);display:flex;gap:8px;justify-content:flex-end}
.modal-header{display:flex;align-items:center;justify-content:space-between;padding:20px 24px 16px;border-bottom:1px solid var(--border)}
.modal-title{font-family:var(--font-display);font-size:16px;font-weight:700}
.modal-body{padding:20px 24px}
.avatar{border-radius:50%;display:flex;align-items:center;justify-content:center;font-family:var(--font-display);font-weight:800;color:#fff;flex-shrink:0;font-size:12px}
.kanban-board{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}
.kanban-col{background:rgba(255,255,255,.025);border:1px solid var(--border);border-radius:14px;padding:12px;min-height:180px}
.kanban-col-header{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:var(--text3);margin-bottom:10px;display:flex;align-items:center;gap:6px}
.task-card{background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:12px;margin-bottom:8px;cursor:pointer;transition:all .2s ease}
.task-card:hover{border-color:var(--border2);transform:translateY(-1px);box-shadow:0 4px 16px rgba(0,0,0,.3)}
.chat-bubble{max-width:75%;border-radius:16px;padding:10px 14px;font-size:13px;line-height:1.5}
.chat-bubble.sent{background:linear-gradient(135deg,var(--accent),var(--accent2));color:#fff;border-bottom-right-radius:4px}
.chat-bubble.recv{background:var(--surface);border:1px solid var(--border2);color:var(--text);border-bottom-left-radius:4px}
.toast{position:fixed;bottom:24px;right:24px;z-index:200;padding:12px 20px;border-radius:14px;font-size:13px;font-weight:600;box-shadow:var(--shadow-lg);animation:slideUp .2s ease;display:flex;align-items:center;gap:10px;backdrop-filter:blur(12px)}
.toast.success{background:rgba(16,185,129,.2);border:1px solid rgba(16,185,129,.35);color:#34d399}
.toast.error{background:rgba(239,68,68,.2);border:1px solid rgba(239,68,68,.35);color:#f87171}
.toast.warning{background:rgba(245,158,11,.2);border:1px solid rgba(245,158,11,.35);color:#fbbf24}
.toast.info{background:rgba(59,130,246,.2);border:1px solid rgba(59,130,246,.35);color:#93c5fd}
.login-page{min-height:100vh;display:flex;align-items:center;justify-content:center;background:radial-gradient(ellipse 80% 60% at 50% -10%,rgba(255,255,255,.16),transparent),radial-gradient(ellipse 50% 40% at 90% 90%,rgba(255,255,255,.10),transparent),var(--bg)}
.login-card{background:rgba(20,23,40,0.9);backdrop-filter:blur(20px);border:1px solid var(--border2);border-radius:var(--radius-lg);padding:44px;width:100%;max-width:400px;box-shadow:var(--shadow-lg)}
.timeline{position:relative;padding-left:28px}
.timeline::before{content:'';position:absolute;left:8px;top:0;bottom:0;width:1px;background:var(--border)}
.timeline-item{position:relative;margin-bottom:20px}
.timeline-dot{position:absolute;left:-24px;width:12px;height:12px;border-radius:50%;border:2px solid var(--bg2);background:var(--text3);top:4px}
.timeline-dot.active{background:var(--accent);box-shadow:0 0 10px var(--accent-glow)}
.notif-item{display:flex;gap:10px;padding:10px 12px;border-radius:10px;cursor:pointer;transition:.15s}
.notif-item:hover{background:rgba(255,255,255,.04)}
.notif-item.unread{background:rgba(255,255,255,.06)}
.notif-dot{width:8px;height:8px;border-radius:50%;background:var(--accent);margin-top:5px;flex-shrink:0;box-shadow:0 0 6px var(--accent-glow)}
.search-bar{position:relative}
.search-bar input{padding-left:36px}
.search-bar .search-icon{position:absolute;left:10px;top:50%;transform:translateY(-50%);color:var(--text3);pointer-events:none}
.portal-page{min-height:100vh;background:radial-gradient(ellipse 80% 50% at 50% -5%,rgba(255,255,255,.14),transparent),var(--bg)}
.portal-header{background:rgba(11,13,26,0.95);backdrop-filter:blur(20px);border-bottom:1px solid var(--border);padding:0 24px;height:60px;display:flex;align-items:center;justify-content:space-between;position:sticky;top:0;z-index:10}
.ring-container{position:relative}
.ring-container svg{transform:rotate(-90deg)}
.ring-container .ring-text{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-family:var(--font-display);font-weight:700;font-size:16px}
@keyframes skeleton-wave{0%{background-position:200% 0}100%{background-position:-200% 0}}
.skeleton{background:linear-gradient(90deg,var(--surface) 25%,var(--surface2) 50%,var(--surface) 75%);background-size:200% 100%;animation:skeleton-wave 1.5s ease-in-out infinite;border-radius:8px}
@keyframes fadeIn{from{opacity:0}to{opacity:1}}
@keyframes slideUp{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:translateY(0)}}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.5}}
@keyframes spin{to{transform:rotate(360deg)}}
@keyframes slideDown{from{opacity:0;transform:translateY(-12px)}to{opacity:1;transform:translateY(0)}}
.fade-in{animation:fadeIn .2s ease}
.slide-up{animation:slideUp .25s ease}
.animate-pulse{animation:pulse 2s infinite}
.spin{animation:spin 1s linear infinite}
.approval-card{border:1px solid var(--border);border-radius:14px;padding:16px;transition:.15s}
.approval-card:hover{border-color:var(--border2)}
.approval-pending{border-left:3px solid var(--amber)}
.approval-approved{border-left:3px solid var(--green)}
.approval-changes{border-left:3px solid var(--red)}
@media print{.no-print{display:none !important}body{background:#fff;color:#000}.card{border:1px solid #ddd}}
@media(max-width:1024px){.grid-4,.grid-5,.grid-6{grid-template-columns:repeat(2,1fr) !important}.kanban-board{grid-template-columns:repeat(2,1fr) !important}}
@media(max-width:768px){
  .sidebar{position:fixed !important;top:0;bottom:0;left:0;width:260px !important;z-index:200;transform:translateX(-100%);transition:transform .25s ease}
  .sidebar.mobile-open{transform:translateX(0) !important}
  .sidebar.collapsed{width:260px !important;transform:translateX(-100%)}
  .sidebar.collapsed.mobile-open{transform:translateX(0) !important}
  .sidebar.collapsed .brand-name,.sidebar.collapsed .brand-sub,.sidebar.collapsed .nav-item span,.sidebar.collapsed .nav-label,.sidebar.collapsed .nav-badge,.sidebar.collapsed .sftext{display:flex !important}
  .sidebar.collapsed .nav-item{justify-content:flex-start !important;padding:9px 12px !important}
  .sidebar-overlay{position:fixed;inset:0;background:rgba(0,0,0,.6);z-index:199;backdrop-filter:blur(2px)}
  .app-layout{flex-direction:row !important}
  .main-area{width:100% !important;min-width:0}
  .topbar{padding:0 10px;gap:6px;height:50px}
  .topbar-title{font-size:14px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
  .topbar-actions .btn>span{display:none}
  .topbar-actions{gap:4px}
  .content{padding:12px !important;overflow-x:hidden}
  .grid-2{grid-template-columns:1fr !important;gap:10px !important}
  .grid-3{grid-template-columns:1fr !important;gap:10px !important}
  .grid-4{grid-template-columns:1fr 1fr !important;gap:8px !important}
  .grid-5,.grid-6{grid-template-columns:1fr 1fr !important;gap:8px !important}
  .stat-card{padding:12px;gap:8px}
  .stat-value{font-size:18px}
  .stat-label{font-size:10px}
  .stat-icon{width:36px;height:36px;font-size:16px}
  .card{padding:12px;border-radius:12px}
  .table-wrap{overflow-x:auto;margin:0 -12px;padding:0 12px}
  .table{min-width:500px}
  .table th,.table td{padding:8px 10px;font-size:11px}
  .kanban-board{grid-template-columns:1fr !important;gap:8px}
  .tabs::-webkit-scrollbar{display:none}
  .tab-item{padding:8px 10px;font-size:11px;flex-shrink:0}
  .modal-overlay{padding:0;align-items:flex-end}
  .modal-box,.modal-box.wide,.modal-box.medium,.modal-box.small,.modal-box.xl{max-width:100% !important;width:100%;border-radius:20px 20px 0 0;max-height:90vh}
  .modal-header{padding:14px 16px}
  .modal-body{padding:14px 16px}
  .input{font-size:16px !important}
  select.input{font-size:16px !important}
  .chat-bubble{max-width:85%}
  .btn{padding:7px 10px;font-size:12px}
  .btn-sm{padding:5px 8px;font-size:11px}
  h1{font-size:20px !important}
  h2{font-size:17px !important}
  .notif-dropdown{position:fixed !important;top:54px !important;left:8px !important;right:8px !important;width:auto !important;max-height:70vh;border-radius:14px}
  .cmd-overlay{padding:12px;padding-top:10vh}
  .cmd-box{max-width:100%;border-radius:14px}
  .cmd-input{font-size:16px;padding:14px}
  .login-page{padding:16px}
  .login-card{padding:24px 20px;margin:0;max-width:100%}
  .toast{left:10px;right:10px;bottom:16px}
  .timeline{padding-left:20px}
  .timeline-dot{left:-16px}
  .empty-state{padding:32px 12px}
  .search-bar{min-width:100% !important}
  .portal-header{padding:0 10px;height:50px}
  .portal-content{padding:12px !important;padding-bottom:88px !important}
  body,#root,.app-layout,.main-area,.content,.portal-page{max-width:100vw;overflow-x:hidden}
}
@media(max-width:400px){
  .grid-2{grid-template-columns:1fr !important}
  .grid-4,.grid-5,.grid-6{grid-template-columns:1fr !important}
  .topbar-title{max-width:100px;font-size:13px}
  .tab-item{padding:6px 8px;font-size:10px}
  h1{font-size:18px !important}
  .btn{font-size:11px;padding:5px 8px}
}
.portal-content{flex:1;overflow:auto;padding:24px;padding-bottom:88px}
.portal-bottom-nav{position:fixed;bottom:0;left:0;right:0;height:64px;background:rgba(11,13,26,0.97);border-top:1px solid var(--border2);display:flex;align-items:stretch;justify-content:space-around;z-index:20;padding-bottom:env(safe-area-inset-bottom,0px);backdrop-filter:blur(20px)}
.portal-bnav-item{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:3px;cursor:pointer;flex:1;padding:4px 4px 6px;transition:all .15s;position:relative}
.portal-bnav-item:hover{background:rgba(255,255,255,.04)}
.portal-bnav-item .bnav-label{font-size:10px;font-weight:600;color:var(--text3);transition:color .15s}
.portal-bnav-item.active .bnav-label{color:var(--accent)}
.portal-bnav-item.active::before{content:'';position:absolute;top:0;left:20%;right:20%;height:2px;background:linear-gradient(90deg,var(--accent),var(--accent2));border-radius:0 0 3px 3px}
.empty-state{text-align:center;padding:60px 20px}
.empty-icon{font-size:44px;margin-bottom:14px;opacity:.6}
.empty-text{color:var(--text3);font-size:14px;line-height:1.6}
.divider{height:1px;background:var(--border);margin:16px 0}
.grid-2{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.grid-3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px}
.grid-4{display:grid;grid-template-columns:repeat(4,1fr);gap:16px}
.grid-5{display:grid;grid-template-columns:repeat(5,1fr);gap:16px}
.grid-6{display:grid;grid-template-columns:repeat(6,1fr);gap:16px}
.form-label{font-size:11px;font-weight:600;color:var(--text2);margin-bottom:5px;display:block;text-transform:uppercase;letter-spacing:.04em}
.space-2>*+*{margin-top:8px}
.space-3>*+*{margin-top:12px}
.space-4>*+*{margin-top:16px}
.space-6>*+*{margin-top:24px}
.cmd-overlay{position:fixed;inset:0;z-index:150;background:rgba(0,0,0,.7);backdrop-filter:blur(8px);display:flex;align-items:flex-start;justify-content:center;padding-top:20vh}
.cmd-box{background:var(--bg2);border:1px solid var(--border2);border-radius:20px;width:100%;max-width:540px;box-shadow:var(--shadow-lg);overflow:hidden}
.cmd-input{width:100%;padding:18px 20px;background:transparent;border:none;border-bottom:1px solid var(--border);color:var(--text);font-size:16px;outline:none;font-family:var(--font-body)}
.cmd-results{max-height:320px;overflow-y:auto;padding:8px}
.cmd-item{display:flex;align-items:center;gap:12px;padding:10px 12px;border-radius:10px;cursor:pointer;transition:.1s}
.cmd-item:hover,.cmd-item.selected{background:rgba(255,255,255,.12)}
.tag{display:inline-flex;align-items:center;gap:4px;padding:2px 8px;border-radius:6px;font-size:11px;font-weight:600;background:rgba(255,255,255,.10);color:#e5e7eb}
.toggle{position:relative;width:40px;height:22px;background:rgba(255,255,255,.1);border-radius:99px;cursor:pointer;transition:.2s;border:none}
.toggle.on{background:linear-gradient(135deg,var(--accent),var(--accent2));box-shadow:0 2px 8px var(--accent-glow)}
.toggle::after{content:'';position:absolute;left:3px;top:3px;width:16px;height:16px;border-radius:50%;background:#fff;transition:.2s}
.toggle.on::after{left:21px}
.dropdown{position:absolute;top:calc(100% + 4px);right:0;background:var(--bg2);border:1px solid var(--border2);border-radius:14px;box-shadow:var(--shadow-lg);min-width:180px;z-index:30;padding:4px;animation:slideDown .15s ease;backdrop-filter:blur(12px)}
.dropdown-item{padding:8px 12px;font-size:13px;border-radius:10px;cursor:pointer;display:flex;align-items:center;gap:8px;color:var(--text2);transition:.1s}
.dropdown-item:hover{background:rgba(255,255,255,.06);color:var(--text)}
</style>
"""

# Build the full HTML
output = '<!DOCTYPE html>\n<html lang="en">\n<head>\n'
output += '<meta charset="UTF-8">\n'
output += '<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">\n'
output += '<title>ClientOS — Crixy Ai</title>\n'
output += '<script crossorigin src="https://cdnjs.cloudflare.com/ajax/libs/react/18.2.0/umd/react.production.min.js"></script>\n'
output += '<script crossorigin src="https://cdnjs.cloudflare.com/ajax/libs/react-dom/18.2.0/umd/react-dom.production.min.js"></script>\n'
output += '<script src="https://cdnjs.cloudflare.com/ajax/libs/babel-standalone/7.23.5/babel.min.js"></script>\n'
output += '<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>\n'
output += '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">\n'
output += new_css
output += '\n</head>\n<body>\n\n'
output += fb_config + '\n\n'
output += '<div id="root"></div>\n'
output += '<script type="text/babel">\n'
output += chunk_utils + '\n\n'
output += chunk_pdf + '\n\n'
output += chunk_db_patched + '\n\n'
output += chunk_status + '\n\n'
output += new_components + '\n\n'
output += new_admin_app + '\n\n'
output += admin_code + '\n\n'
output += chunk_manager + '\n\n'
output += chunk_portal2 + '\n\n'
output += chunk_root + '\n'
output += '</script>\n</body>\n</html>'

out_path = os.path.join(base, 'index.html')
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(output)

print(f"Written: {len(output)} bytes ({len(output)//1024} KB)")
print("Done!")
