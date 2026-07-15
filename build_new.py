#!/usr/bin/env python3
# Build script for upgraded index.html
import os

base = r"C:\Users\sakshxmsingh\Desktop\crixy\client portal\latest portal"

def read_file(name):
    with open(os.path.join(base, name), 'r', encoding='utf-8') as f:
        return f.read()

logo_const = read_file('logo_const.txt')
chunk_utils = read_file('chunk_utils.txt')
chunk_pdf = read_file('chunk_pdf.txt')
chunk_db = read_file('chunk_db.txt')
chunk_status = read_file('chunk_status.txt')
chunk_admin = read_file('chunk_admin.txt')
chunk_manager = read_file('chunk_manager.txt')
chunk_portal2 = read_file('chunk_portal2.txt')
chunk_root = read_file('chunk_root.txt')

print("All chunks loaded")
print("Total chunk size:", sum([len(logo_const), len(chunk_utils), len(chunk_pdf), len(chunk_db), len(chunk_status), len(chunk_admin), len(chunk_manager), len(chunk_portal2)]))

# New additions to inject
NEW_COMPONENTS = r"""
/* ═══ NEW: DARK/LIGHT MODE TOGGLE ═══ */
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

/* ═══ NEW: SESSION TIMER ═══ */
function useSessionTimer() {
  const [startTime] = useState(Date.now());
  const [elapsed, setElapsed] = useState(0);
  useEffect(() => {
    const interval = setInterval(() => {
      setElapsed(Math.floor((Date.now() - startTime) / 1000));
    }, 1000);
    return () => clearInterval(interval);
  }, [startTime]);
  const hours = Math.floor(elapsed / 3600);
  const minutes = Math.floor((elapsed % 3600) / 60);
  const seconds = elapsed % 60;
  if (hours > 0) return `${hours}h ${minutes}m`;
  if (minutes > 0) return `${minutes}m ${seconds}s`;
  return `${seconds}s`;
}

/* ═══ NEW: FIREBASE STATUS ═══ */
function FirebaseStatus() {
  const online = !!window._db;
  return (
    <div style={{display:'flex',alignItems:'center',gap:6,fontSize:11,color:online?'var(--green)':'var(--amber)'}}>
      <div className="firebase-status-dot" style={{background:online?'var(--green)':'var(--amber)',boxShadow:`0 0 6px ${online?'var(--green)':'var(--amber)'}`}}/>
      {online?'Live':'Offline'}
    </div>
  );
}

/* ═══ NEW: SKELETON LOADER ═══ */
function Skeleton({width='100%', height=16, radius=8, style={}}) {
  return (
    <div className="skeleton" style={{width, height, borderRadius:radius, ...style}}/>
  );
}

/* ═══ NEW: KEYBOARD SHORTCUTS PANEL ═══ */
function ShortcutsPanel({onClose}) {
  const shortcuts = [
    { keys: ['Ctrl', 'K'], desc: 'Open command palette' },
    { keys: ['?'], desc: 'Show keyboard shortcuts' },
    { keys: ['Esc'], desc: 'Close modal / panel' },
    { keys: ['Ctrl', 'N'], desc: 'New client' },
    { keys: ['Ctrl', '/'], desc: 'Focus search' },
  ];
  return (
    <div style={{position:'fixed',inset:0,background:'rgba(0,0,0,0.75)',backdropFilter:'blur(8px)',zIndex:1000,display:'flex',alignItems:'center',justifyContent:'center'}} onClick={onClose}>
      <div style={{background:'var(--surface)',border:'1px solid var(--border2)',borderRadius:'var(--radius-lg)',padding:32,minWidth:420,maxWidth:500,boxShadow:'var(--shadow-lg)'}} onClick={e=>e.stopPropagation()}>
        <div style={{fontFamily:'var(--font-display)',fontSize:18,fontWeight:800,marginBottom:24}} className="gradient-text">Keyboard Shortcuts</div>
        {shortcuts.map((s,i) => (
          <div key={i} style={{display:'flex',justifyContent:'space-between',alignItems:'center',padding:'10px 0',borderBottom:'1px solid var(--border)'}}>
            <span style={{color:'var(--text2)',fontSize:13}}>{s.desc}</span>
            <div style={{display:'flex',gap:4}}>
              {s.keys.map((k,j) => (
                <kbd key={j} style={{background:'var(--bg3)',border:'1px solid var(--border2)',borderRadius:6,padding:'2px 8px',fontSize:11,fontWeight:600,color:'var(--text)',fontFamily:'var(--font-body)'}}>{k}</kbd>
              ))}
            </div>
          </div>
        ))}
        <button className="btn btn-secondary btn-sm" style={{marginTop:20,width:'100%'}} onClick={onClose}>Close</button>
      </div>
    </div>
  );
}

/* ═══ NEW: CLIENT HEALTH SCORE ═══ */
function calcHealthScore(client) {
  let score = 100;
  const overdueInv = (client.invoices||[]).filter(i => i.status !== 'paid' && isOverdue(i.dueDate));
  score -= overdueInv.length * 10;
  const openTickets = (client.tickets||[]).filter(t => t.status !== 'resolved' && t.status !== 'closed');
  score -= openTickets.length * 5;
  const recentMsgs = (client.messages||[]).filter(m => {
    const d = new Date(m.ts||m.createdAt||0);
    return (Date.now() - d) < 7*24*60*60*1000;
  });
  if (recentMsgs.length === 0) score -= 10;
  if ((client.progress||0) < 10 && client.status === 'In Progress') score -= 15;
  return Math.max(0, Math.min(100, score));
}

function HealthScoreBadge({client}) {
  const score = calcHealthScore(client);
  const color = score >= 80 ? 'var(--green)' : score >= 60 ? 'var(--amber)' : 'var(--red)';
  const label = score >= 80 ? 'Healthy' : score >= 60 ? 'Fair' : 'At Risk';
  const cls = score >= 80 ? 'health-healthy' : score >= 60 ? 'health-fair' : 'health-atrisk';
  return (
    <span className={`badge ${cls}`} style={{fontWeight:700}}>
      <span style={{width:6,height:6,borderRadius:'50%',background:color,display:'inline-block'}}/>
      {label} {score}
    </span>
  );
}

/* ═══ NEW: PREMIUM PROGRESS RING ═══ */
function PremiumProgressRing({progress, size=120, stroke=8}) {
  const radius = (size - stroke) / 2;
  const circumference = radius * 2 * Math.PI;
  const offset = circumference - (progress / 100) * circumference;
  return (
    <div style={{position:'relative', width:size, height:size}}>
      <svg width={size} height={size} style={{transform:'rotate(-90deg)'}}>
        <circle cx={size/2} cy={size/2} r={radius} fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth={stroke}/>
        <circle cx={size/2} cy={size/2} r={radius} fill="none"
          stroke="url(#progressGrad)" strokeWidth={stroke}
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          style={{transition:'stroke-dashoffset 1s ease'}}
        />
        <defs>
          <linearGradient id="progressGrad" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#f8fafc"/>
            <stop offset="100%" stopColor="#9ca3af"/>
          </linearGradient>
        </defs>
      </svg>
      <div style={{position:'absolute',inset:0,display:'flex',flexDirection:'column',alignItems:'center',justifyContent:'center'}}>
        <span style={{fontSize:Math.floor(size*0.2),fontWeight:800,color:'var(--text)',fontFamily:'var(--font-display)'}}>{progress}%</span>
        <span style={{fontSize:Math.floor(size*0.09),color:'var(--text2)'}}>Complete</span>
      </div>
    </div>
  );
}

/* ═══ NEW: CHART.JS COMPONENTS ═══ */
function RevenueChart({clients}) {
  const canvasRef = useRef(null);
  const chartRef = useRef(null);
  useEffect(() => {
    if (!canvasRef.current || typeof Chart === 'undefined') return;
    if (chartRef.current) chartRef.current.destroy();
    const months = [];
    const revenue = [];
    for (let i = 5; i >= 0; i--) {
      const d = new Date();
      d.setMonth(d.getMonth() - i);
      months.push(d.toLocaleDateString('en-IN', {month:'short', year:'2-digit'}));
      let total = 0;
      clients.forEach(c => {
        (c.invoices||[]).filter(inv => {
          const invDate = new Date(inv.createdAt||inv.date||'');
          return invDate.getMonth() === d.getMonth() && invDate.getFullYear() === d.getFullYear() && inv.status === 'paid';
        }).forEach(inv => total += getInvoicePaidAmount(inv));
      });
      revenue.push(total);
    }
    chartRef.current = new Chart(canvasRef.current, {
      type: 'bar',
      data: {
        labels: months,
        datasets: [{
          label: 'Revenue',
          data: revenue,
          backgroundColor: 'rgba(255,255,255,0.7)',
          borderColor: '#f8fafc',
          borderWidth: 2,
          borderRadius: 8,
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          y: {
            grid: { color: 'rgba(255,255,255,0.04)' },
            ticks: { color: '#94a3b8', callback: v => '₹' + (v/1000).toFixed(0) + 'k' }
          },
          x: { grid: { display: false }, ticks: { color: '#94a3b8' } }
        }
      }
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
      data: {
        labels: Object.keys(statuses),
        datasets: [{
          data: Object.values(statuses),
          backgroundColor: ['#f8fafc','#10b981','#f59e0b','#06b6d4','#ec4899','#ef4444'],
          borderWidth: 0,
          hoverOffset: 6,
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'bottom', labels: { color: '#94a3b8', padding: 14, font: {size:12}, boxWidth: 12 } }
        },
        cutout: '72%'
      }
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
    const months = [];
    const counts = [];
    for (let i = 5; i >= 0; i--) {
      const d = new Date();
      d.setMonth(d.getMonth() - i);
      months.push(d.toLocaleDateString('en-IN', {month:'short', year:'2-digit'}));
      const count = clients.filter(c => {
        const cd = new Date(c.createdAt||'');
        return cd <= d;
      }).length;
      counts.push(count);
    }
    chartRef.current = new Chart(canvasRef.current, {
      type: 'line',
      data: {
        labels: months,
        datasets: [{
          label: 'Total Clients',
          data: counts,
          borderColor: '#9ca3af',
          backgroundColor: 'rgba(255,255,255,0.08)',
          borderWidth: 2,
          pointBackgroundColor: '#9ca3af',
          pointRadius: 4,
          fill: true,
          tension: 0.4
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          y: { grid: { color: 'rgba(255,255,255,0.04)' }, ticks: { color: '#94a3b8', stepSize: 1 } },
          x: { grid: { display: false }, ticks: { color: '#94a3b8' } }
        }
      }
    });
    return () => { if(chartRef.current) chartRef.current.destroy(); };
  }, [clients]);
  return <canvas ref={canvasRef} style={{width:'100%', height:'200px'}}/>;
}

/* ═══ NEW: ANALYTICS PAGE ═══ */
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
        <h1 style={{fontFamily:'var(--font-display)',fontWeight:800,fontSize:26}} className="gradient-text">Analytics</h1>
        <p style={{color:'var(--text3)',fontSize:13,marginTop:4}}>Business intelligence and performance overview</p>
      </div>

      <div className="grid-4">
        {[
          ['Total Revenue', curr(totalRev), '💎', 'c-purple'],
          ['Collected', curr(paidRev), '✅', 'c-green'],
          ['Total Hours', `${totalHrs.toFixed(1)}h`, '⏱', 'c-blue'],
          ['Avg Health', `${avgHealth}%`, '❤️', 'c-amber'],
        ].map(([l,v,e,cls]) =>
          <div key={l} className={`stat-card ${cls}`}>
            <div className="stat-icon" style={{background:'rgba(255,255,255,.06)',fontSize:22}}>{e}</div>
            <div><div className="stat-label">{l}</div><div className="stat-value">{v}</div></div>
          </div>
        )}
      </div>

      <div className="grid-2">
        <div className="card">
          <h3 style={{fontFamily:'var(--font-display)',fontWeight:700,fontSize:15,marginBottom:4}}>Monthly Revenue</h3>
          <p style={{fontSize:12,color:'var(--text3)',marginBottom:16}}>Paid invoices by month (last 6 months)</p>
          <div className="chart-container" style={{height:220}}>
            <RevenueChart clients={clients}/>
          </div>
        </div>
        <div className="card">
          <h3 style={{fontFamily:'var(--font-display)',fontWeight:700,fontSize:15,marginBottom:4}}>Project Status</h3>
          <p style={{fontSize:12,color:'var(--text3)',marginBottom:16}}>Distribution across all clients</p>
          <div className="chart-container" style={{height:220}}>
            <StatusDonutChart clients={clients}/>
          </div>
        </div>
      </div>

      <div className="grid-2">
        <div className="card">
          <h3 style={{fontFamily:'var(--font-display)',fontWeight:700,fontSize:15,marginBottom:4}}>Client Growth</h3>
          <p style={{fontSize:12,color:'var(--text3)',marginBottom:16}}>Cumulative clients over time</p>
          <div className="chart-container" style={{height:200}}>
            <ClientGrowthChart clients={clients}/>
          </div>
        </div>
        <div className="card">
          <h3 style={{fontFamily:'var(--font-display)',fontWeight:700,fontSize:15,marginBottom:16}}>Revenue by Client</h3>
          {clients.length===0 ? <div className="empty-state" style={{padding:'30px 0'}}><div className="empty-icon">📊</div><div className="empty-text">No data yet</div></div> :
            [...clients].sort((a,b) => {
              const ar=(a.invoices||[]).reduce((s,i)=>s+getInvoiceTotal(i),0);
              const br=(b.invoices||[]).reduce((s,i)=>s+getInvoiceTotal(i),0);
              return br-ar;
            }).slice(0,8).map(c => {
              const r=(c.invoices||[]).reduce((s,i)=>s+getInvoiceTotal(i),0);
              const p=(c.invoices||[]).reduce((s,i)=>s+getInvoicePaidAmount(i),0);
              const pct=totalRev>0?Math.round(r/totalRev*100):0;
              return <div key={c.id} style={{marginBottom:12}}>
                <div style={{display:'flex',justifyContent:'space-between',marginBottom:4}}>
                  <span style={{fontSize:13,fontWeight:600}}>{c.name}</span>
                  <span style={{fontSize:12,color:'var(--text3)'}}>{curr(r)} <span style={{color:'#6ee7b7',fontSize:11}}>({curr(p)} paid)</span></span>
                </div>
                <div className="progress-bar"><div className="progress-fill" style={{width:`${pct}%`}}/></div>
              </div>;
            })
          }
        </div>
      </div>

      <div className="card">
        <h3 style={{fontFamily:'var(--font-display)',fontWeight:700,fontSize:15,marginBottom:16}}>Client Health Overview</h3>
        {clients.length === 0 ? <div className="empty-state" style={{padding:'20px 0'}}><div className="empty-icon">❤️</div><div className="empty-text">No clients yet</div></div> :
          <div style={{display:'grid',gridTemplateColumns:'repeat(auto-fill,minmax(280px,1fr))',gap:12}}>
            {clients.map(c => {
              const tasks=c.tasks||[];
              const done=tasks.filter(t=>t.status==='completed').length;
              const overdue=(c.invoices||[]).filter(i=>i.status==='overdue').length;
              return <div key={c.id} style={{padding:'12px 14px',border:'1px solid var(--border)',borderRadius:12,display:'flex',alignItems:'center',gap:12,transition:'all .2s'}}
                onMouseOver={e=>e.currentTarget.style.borderColor='var(--border2)'}
                onMouseOut={e=>e.currentTarget.style.borderColor='var(--border)'}>
                <ProgressRing pct={c.progress||0} size={48} stroke={4} color={sc(c.status).dot}/>
                <div style={{flex:1,minWidth:0}}>
                  <div style={{fontWeight:600,fontSize:13,overflow:'hidden',textOverflow:'ellipsis',whiteSpace:'nowrap'}}>{c.name}</div>
                  <div style={{fontSize:11,color:'var(--text3)',marginTop:2}}>{done}/{tasks.length} tasks{overdue>0?` · ⚠️ ${overdue} overdue`:''}</div>
                </div>
                <HealthScoreBadge client={c}/>
              </div>;
            })}
          </div>
        }
      </div>

      <div className="grid-3">
        {[
          {title:'Task Completion',v:`${totalTasks>0?Math.round(doneTasks/totalTasks*100):0}%`,sub:`${doneTasks} of ${totalTasks} tasks done`},
          {title:'Outstanding',v:curr(totalRev-paidRev),sub:'Unpaid invoice balances'},
          {title:'Billable Value',v:curr(Math.round(totalHrs*(settings.hourlyRate||2000))),sub:`${totalHrs.toFixed(1)}h × ₹${(settings.hourlyRate||2000).toLocaleString('en-IN')}/hr`},
        ].map(s=><div key={s.title} className="card">
          <div style={{fontFamily:'var(--font-display)',fontWeight:800,fontSize:26,color:'var(--text)'}}>{s.v}</div>
          <div style={{fontWeight:600,fontSize:13,marginTop:4}}>{s.title}</div>
          <div style={{fontSize:12,color:'var(--text3)',marginTop:4}}>{s.sub}</div>
        </div>)}
      </div>
    </div>
  );
}
"""

# Modified AdminOverview with better design
NEW_OVERVIEW = r"""
/* ═══ ENHANCED ADMIN OVERVIEW ═══ */
function AdminOverview({stats, clients, settings, onSelect}) {
  const recent = [...clients].sort((a,b) => new Date(b.createdAt||0) - new Date(a.createdAt||0)).slice(0,6);
  const overdueInvoices = clients.flatMap(c => (c.invoices||[]).filter(i=>i.status==='overdue').map(i=>({...i,clientName:c.name,clientId:c.id})));
  const statusDist = Object.keys(STATUS).map(s=>({s,n:clients.filter(c=>c.status===s).length})).filter(x=>x.n>0);

  return (
    <div className="space-4 fade-in">
      <div style={{marginBottom:8}}>
        <h1 style={{fontFamily:'var(--font-display)',fontWeight:800,fontSize:28}} className="gradient-text">Dashboard</h1>
        <p style={{color:'var(--text3)',fontSize:13,marginTop:4}}>Welcome back — here's what's happening today</p>
      </div>

      <div className="grid-4">
        <div className="stat-card c-blue">
          <div className="stat-icon" style={{background:'rgba(59,130,246,.15)'}}><Icon n="users" s={22} c="#93c5fd"/></div>
          <div>
            <div className="stat-label">Total Clients</div>
            <div className="stat-value">{stats.total}</div>
            <div style={{fontSize:11,color:'var(--text3)',marginTop:4}}>{stats.active} active</div>
          </div>
        </div>
        <div className="stat-card c-green">
          <div className="stat-icon" style={{background:'rgba(16,185,129,.15)'}}><Icon n="dollar" s={22} c="#34d399"/></div>
          <div>
            <div className="stat-label">Revenue Collected</div>
            <div className="stat-value" style={{fontSize:20}}>{curr(stats.revenue)}</div>
            <div style={{fontSize:11,color:'var(--text3)',marginTop:4}}>{curr(stats.due)} outstanding</div>
          </div>
        </div>
        <div className="stat-card c-amber">
          <div className="stat-icon" style={{background:'rgba(245,158,11,.15)'}}><Icon n="project" s={22} c="#fbbf24"/></div>
          <div>
            <div className="stat-label">Task Completion</div>
            <div className="stat-value">{stats.totalTasks > 0 ? Math.round(stats.completedTasks/stats.totalTasks*100) : 0}%</div>
            <div style={{fontSize:11,color:'var(--text3)',marginTop:4}}>{stats.completedTasks}/{stats.totalTasks} done</div>
          </div>
        </div>
        <div className="stat-card c-purple">
          <div className="stat-icon" style={{background:'rgba(255,255,255,.10)'}}><Icon n="support" s={22} c="#f3f4f6"/></div>
          <div>
            <div className="stat-label">Open Tickets</div>
            <div className="stat-value">{stats.pending}</div>
            <div style={{fontSize:11,color:'var(--text3)',marginTop:4}}>{stats.avgProgress}% avg progress</div>
          </div>
        </div>
      </div>

      {overdueInvoices.length > 0 && (
        <div style={{background:'rgba(239,68,68,.08)',border:'1px solid rgba(239,68,68,.2)',borderRadius:14,padding:'14px 18px',display:'flex',alignItems:'center',gap:14}}>
          <span style={{fontSize:20}}>⚠️</span>
          <div>
            <div style={{fontWeight:700,fontSize:13,color:'#f87171'}}>{overdueInvoices.length} Overdue Invoice{overdueInvoices.length>1?'s':''}</div>
            <div style={{fontSize:12,color:'var(--text3)',marginTop:2}}>{overdueInvoices.map(i=>i.clientName).join(', ')} — needs immediate attention</div>
          </div>
        </div>
      )}

      <div className="grid-2">
        <div className="card">
          <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',marginBottom:16}}>
            <h3 style={{fontFamily:'var(--font-display)',fontWeight:700,fontSize:15}}>Recent Clients</h3>
            <span style={{fontSize:11,color:'var(--text3)'}}>{recent.length} shown</span>
          </div>
          {recent.length === 0 ? <div className="empty-state" style={{padding:'30px 0'}}><div className="empty-icon">👥</div><div className="empty-text">No clients yet.<br/>Add your first client to get started.</div></div> :
            <div>{recent.map(c => <ClientRowItem key={c.id} c={c} settings={settings} onSelect={() => onSelect(c.id)}/>)}</div>
          }
        </div>

        <div className="card">
          <h3 style={{fontFamily:'var(--font-display)',fontWeight:700,fontSize:15,marginBottom:16}}>Project Status</h3>
          {statusDist.length === 0 ? <div className="empty-state" style={{padding:'30px 0'}}><div className="empty-icon">📊</div><div className="empty-text">No data yet</div></div> :
            <div className="space-3">
              {statusDist.map(({s,n}) => {
                const c = sc(s);
                const pct = Math.round(n/clients.length*100);
                return (
                  <div key={s}>
                    <div style={{display:'flex',justifyContent:'space-between',marginBottom:5}}>
                      <span style={{fontSize:12,color:'var(--text2)',display:'flex',alignItems:'center',gap:6}}>
                        <span style={{width:8,height:8,borderRadius:'50%',background:c.dot,display:'inline-block',boxShadow:`0 0 6px ${c.dot}`}}/>
                        {s}
                      </span>
                      <span style={{fontSize:12,fontWeight:700,color:'var(--text)'}}>{n}</span>
                    </div>
                    <div className="progress-bar"><div className="progress-fill" style={{width:`${pct}%`,background:c.dot}}/></div>
                  </div>
                );
              })}
            </div>
          }
          {stats.pending > 0 && (
            <div style={{marginTop:20,padding:'12px 14px',background:'rgba(239,68,68,.08)',border:'1px solid rgba(239,68,68,.15)',borderRadius:12}}>
              <div style={{fontSize:12,color:'#f87171',fontWeight:700}}>🎫 {stats.pending} open support ticket{stats.pending!==1?'s':''}</div>
              <div style={{fontSize:11,color:'var(--text3)',marginTop:2}}>Needs attention</div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
"""

# Modified AdminApp with new features
NEW_ADMIN_APP_HEADER = r"""
/* ═══ ADMIN APP ═══ */
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
  const [selectedClients,setSelectedClients]=useState([]);
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
      const c=[];q.forEach(d=>c.push(normalizeClientData({id:d.id,...d.data()})));
      setClients(c);
    },()=>{});
    return ()=>unsub();
  },[authed]);

  useEffect(()=>{
    if(!authed)return;
    const h=e=>{
      if((e.metaKey||e.ctrlKey)&&e.key==='k'){e.preventDefault();setCmdOpen(true);}
      if(e.key==='Escape'){setCmdOpen(false);setShowShortcuts(false);}
      if(e.key==='?'&&!e.ctrlKey&&!e.metaKey&&document.activeElement.tagName!=='INPUT'&&document.activeElement.tagName!=='TEXTAREA'){
        setShowShortcuts(true);
      }
    };
    window.addEventListener('keydown',h);return()=>window.removeEventListener('keydown',h);
  },[authed]);

  const updSettings=s=>{setSettings(s);saveSettings(s);show('Settings saved!');};
  const applyManagerDecision=(req,decision)=>{
    let nextSettings={...settings,managerApprovals:(settings.managerApprovals||[]).map(x=>x.id===req.id?{...x,status:decision,reviewedAt:new Date().toISOString(),reviewedBy:'admin'}:x)};
    if(decision==='approved'&&req.payloadClient){
      const normalized=normalizeClientData(req.payloadClient);
      setClients(p=>p.map(c=>c.id===normalized.id?normalized:c));
      saveClient(normalized);
    }
    if(decision==='approved'&&req.payloadSettingsPatch){
      nextSettings={...nextSettings,...req.payloadSettingsPatch};
    }
    nextSettings={
      ...pushManagerAudit(nextSettings,{type:'review',actor:'admin',action:`Manager request ${decision}`,requestId:req.id,clientName:req.clientName||'General'}),
      managerNotifications:[{id:uid(),text:`Admin ${decision} your request${req.clientName?` for ${req.clientName}`:''}`,read:false,ts:new Date().toISOString(),requestId:req.id,status:decision},...(nextSettings.managerNotifications||[])].slice(0,100),
    };
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
    setClients(p=>p.filter(c=>c.id!==id));
    deleteClient(id);
    if(selId===id){setSelId(null);setPage('clients');}
    show('Client deleted');
  };

  const addOrUpdateClient=c=>{
    const isNew=!clients.find(x=>x.id===c.id);
    if(isNew){
      const nc=normalizeClientData({...c,id:c.id||tok(),createdAt:new Date().toISOString(),activity:[],notifications:[],messages:[],tasks:[],milestones:[],files:[],invoices:[],approvals:[],tickets:[],timeEntries:[],notes:[],contracts:[],feedback:[],expenses:[],meetings:[],links:[],announcements:[],proposals:[],requests:[],followUps:[],reminders:[],pinned:false,clientTags:[]});
      setClients(p=>[...p,nc]);saveClient(nc);
    } else {
      const normalized=normalizeClientData(c);
      setClients(p=>p.map(x=>x.id===c.id?normalized:x));
      saveClient(normalized);
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

  if(loading)return<Loader/>;
  if(!authed)return<AdminLogin settings={settings} onLogin={()=>{setAuthed(true);try{localStorage.setItem('ut_authed','true');}catch{}}} onSwitchPanel={onSwitchPanel}/>;

  const selClient=clients.find(c=>c.id===selId);
  const allNotifs=clients.flatMap(c=>(c.notifications||[]).map(n=>({...n,clientName:c.name,clientId:c.id}))).sort((a,b)=>new Date(b.ts)-new Date(a.ts)).slice(0,30);
  const unreadCount=allNotifs.filter(n=>!n.read).length;
  const pendingManagerApprovals=(settings.managerApprovals||[]).filter(x=>(x.status||'pending')==='pending').length;

  const stats={
    total:clients.length,
    active:clients.filter(c=>c.status==='In Progress').length,
    revenue:clients.reduce((s,c)=>(c.invoices||[]).reduce((a,i)=>a+getInvoicePaidAmount(i),0)+s,0),
    pending:clients.reduce((s,c)=>(c.tickets||[]).filter(t=>t.status==='open').length+s,0),
    due:clients.reduce((s,c)=>(c.invoices||[]).filter(i=>i.status==='sent'||i.status==='overdue').reduce((a,i)=>a+getInvoiceBalance(i),0)+s,0),
    completed:clients.filter(c=>c.status==='Completed').length,
    review:clients.filter(c=>c.status==='Review').length,
    totalTasks:clients.reduce((s,c)=>(c.tasks||[]).length+s,0),
    completedTasks:clients.reduce((s,c)=>(c.tasks||[]).filter(t=>t.status==='completed').length+s,0),
    totalHours:clients.reduce((s,c)=>(c.timeEntries||[]).reduce((a,e)=>a+e.hours,0)+s,0),
    avgProgress:clients.length?Math.round(clients.reduce((s,c)=>s+(c.progress||0),0)/clients.length):0,
  };

  const navMain=[
    {id:'overview',label:'Overview',icon:'dashboard'},
    {id:'clients',label:'Clients',icon:'users'},
    {id:'approvals',label:'Manager Approvals',icon:'check'},
    {id:'analytics',label:'Analytics',icon:'analytics'},
    {id:'calendar',label:'Calendar',icon:'calendar'},
    {id:'reports',label:'Reports',icon:'pieChart'},
    {id:'settings',label:'Settings',icon:'settings'},
  ];

  const clearNotifs=()=>{
    clients.forEach(c=>{
      if((c.notifications||[]).some(n=>!n.read)){
        updClient(c.id,x=>({...x,notifications:(x.notifications||[]).map(n=>({...n,read:true}))}));
      }
    });
    setShowNotifs(false);
  };

  const togglePin=(clientId)=>{
    updClient(clientId, c => ({...c, pinned: !c.pinned}));
    show((clients.find(c=>c.id===clientId)?.pinned ? 'Unpinned' : 'Pinned') + ' client');
  };

  return (
    <div className="app-layout">
      <div className="aurora-bg">
        <div className="aurora-blob"/>
        <div className="aurora-blob"/>
        <div className="aurora-blob"/>
      </div>
      {mobileMenuOpen&&<div className="sidebar-overlay" onClick={()=>setMobileMenuOpen(false)}/>}

      {/* SIDEBAR */}
      <aside className={`sidebar ${sideCollapsed?"collapsed":""} ${mobileMenuOpen?"mobile-open":""}`}>
        <div className="sidebar-brand">
          <div style={{display:'flex',alignItems:'center',gap:10}}>
            <div className="brand-logo" onClick={()=>setSideCollapsed(!sideCollapsed)} style={{cursor:"pointer",overflow:'hidden'}}>
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
                <Icon n={n.icon} s={16}/>
                <span>{n.label}</span>
                {n.id==='clients'&&clients.length>0&&<span className="nav-badge" style={{marginLeft:'auto'}}>{clients.length}</span>}
                {n.id==='approvals'&&pendingManagerApprovals>0&&<span className="nav-badge" style={{marginLeft:'auto'}}>{pendingManagerApprovals}</span>}
              </div>
            ))}
          </div>

          {clients.filter(c=>c.pinned).length > 0 && (
            <div className="nav-section">
              <div className="nav-label">📌 Pinned</div>
              {clients.filter(c=>c.pinned).map(c=>(
                <div key={c.id} className={`nav-item ${selId===c.id?'active':''}`}
                  onClick={()=>{setSelId(c.id);setPage('client');setEditClient(null);setMobileMenuOpen(false);}}>
                  <Avatar name={c.name} size={22} color={settings.brandColor||'#f8fafc'}/>
                  <span style={{flex:1,overflow:'hidden',textOverflow:'ellipsis',whiteSpace:'nowrap'}}>{c.name}</span>
                </div>
              ))}
            </div>
          )}

          {clients.filter(c=>!c.pinned).length > 0 && (
            <div className="nav-section">
              <div className="nav-label">Clients</div>
              {clients.filter(c=>!c.pinned).slice(0,8).map(c=>(
                <div key={c.id} className={`nav-item ${selId===c.id?'active':''}`}
                  onClick={()=>{setSelId(c.id);setPage('client');setEditClient(null);setMobileMenuOpen(false);}}>
                  <Avatar name={c.name} size={22} color={settings.brandColor||'#f8fafc'}/>
                  <span style={{flex:1,overflow:'hidden',textOverflow:'ellipsis',whiteSpace:'nowrap'}}>{c.name}</span>
                  {(c.tickets||[]).filter(t=>t.status==='open').length>0&&<span className="nav-badge">{(c.tickets||[]).filter(t=>t.status==='open').length}</span>}
                </div>
              ))}
            </div>
          )}
        </nav>

        <div style={{padding:'8px',borderTop:'1px solid var(--border)'}}>
          <div className="nav-item" onClick={()=>setShowShortcuts(true)} style={{opacity:.6,fontSize:12}}>
            <span style={{fontSize:14}}>⌨️</span><span className="sftext">Shortcuts</span>
          </div>
          <div className="nav-item" onClick={()=>{setAuthed(false);try{localStorage.removeItem('ut_authed');}catch{}}}>
            <Icon n="logout" s={16}/><span>Sign Out</span>
          </div>
        </div>
      </aside>

      {/* MAIN */}
      <div className="main-area">
        <header className="topbar">
          <button className="btn btn-ghost btn-icon" onClick={()=>{if(window.innerWidth<=768){setMobileMenuOpen(!mobileMenuOpen);}else{setSideCollapsed(!sideCollapsed);}}}><Icon n="menu" s={16}/></button>
          <div className="topbar-title">
            {page==='client'&&selClient?selClient.name:page==='overview'?'Dashboard':page==='analytics'?'Analytics':page==='clients'?'All Clients':page==='approvals'?'Manager Approvals':page==='calendar'?'Calendar':page==='reports'?'Reports':page==='form'?'Client Form':'Settings'}
          </div>
          <div className="topbar-actions">
            <FirebaseStatus/>
            <div style={{fontSize:11,color:'var(--text3)',display:'flex',alignItems:'center',gap:4,padding:'4px 8px',borderRadius:8,background:'rgba(255,255,255,.04)'}}>
              <Icon n="clock" s={12}/>
              <span>{sessionTime}</span>
            </div>
            <button className="btn btn-ghost btn-icon" onClick={toggleTheme} title="Toggle theme" style={{fontSize:16}}>
              {theme==='dark'?'☀️':'🌙'}
            </button>
            <div style={{position:'relative'}}>
              <button className="btn btn-ghost btn-icon" onClick={()=>setShowNotifs(!showNotifs)} style={{position:'relative'}}>
                <Icon n="bell" s={16}/>
                {unreadCount>0&&<span style={{position:'absolute',top:2,right:2,width:16,height:16,background:'#ef4444',borderRadius:'50%',fontSize:9,color:'#fff',display:'flex',alignItems:'center',justifyContent:'center',fontWeight:700}}>{unreadCount}</span>}
              </button>
              {showNotifs&&(
                <div className="notif-dropdown" style={{position:'absolute',right:0,top:'calc(100% + 8px)',width:340,background:'var(--bg2)',border:'1px solid var(--border2)',borderRadius:18,boxShadow:'var(--shadow-lg)',zIndex:50,overflow:'hidden',backdropFilter:'blur(12px)'}}>
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
                </div>
              )}
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

# Enhanced AdminClients with bulk actions and pinning
NEW_ADMIN_CLIENTS = r"""
/* ═══ CLIENTS LIST (ENHANCED) ═══ */
function AdminClients({clients,settings,onSelect,onEdit,onDelete,onTogglePin}){
  const [q,setQ]=useState('');
  const [sf,setSf]=useState('All');
  const [selected,setSelected]=useState([]);
  const [pg,setPg]=useState(1);const perPage=20;

  const sorted=useMemo(()=>{
    const pinned=clients.filter(c=>c.pinned);
    const unpinned=clients.filter(c=>!c.pinned);
    return [...pinned,...unpinned];
  },[clients]);

  const filtered=useMemo(()=>sorted.filter(c=>{
    const m=!q||[c.name,c.company,c.projectName,c.email].some(x=>(x||'').toLowerCase().includes(q.toLowerCase()));
    const s=sf==='All'||c.status===sf;
    return m&&s;
  }),[sorted,q,sf]);

  const toggleSelect=(id)=>{
    setSelected(p=>p.includes(id)?p.filter(x=>x!==id):[...p,id]);
  };
  const selectAll=()=>setSelected(filtered.map(c=>c.id));
  const clearSelection=()=>setSelected([]);
  const bulkDelete=()=>{
    if(!confirm(`Delete ${selected.length} clients? This cannot be undone.`))return;
    selected.forEach(id=>onDelete(id));
    setSelected([]);
  };
  const bulkExport=()=>{
    const data=clients.filter(c=>selected.includes(c.id));
    downloadJSON({clients:data,exportedAt:new Date().toISOString()},'selected-clients.json');
  };

  const paginated=filtered.slice((pg-1)*perPage, pg*perPage);

  return (
    <div className="space-4 fade-in">
      <div style={{marginBottom:8}}>
        <h1 style={{fontFamily:'var(--font-display)',fontWeight:800,fontSize:26}} className="gradient-text">Clients</h1>
        <p style={{color:'var(--text3)',fontSize:13,marginTop:4}}>{clients.length} total clients</p>
      </div>

      <div style={{display:'flex',gap:12,flexWrap:'wrap',alignItems:'center'}}>
        <div className="search-bar" style={{flex:1,minWidth:200}}>
          <span className="search-icon"><Icon n="search" s={14}/></span>
          <input className="input" placeholder="Search clients, company, email…" value={q} onChange={e=>{setQ(e.target.value);setPg(1);}}/>
        </div>
        <select className="input" style={{width:'auto'}} value={sf} onChange={e=>{setSf(e.target.value);setPg(1);}}>
          <option>All</option>
          {Object.keys(STATUS).map(s=><option key={s}>{s}</option>)}
        </select>
        {filtered.length > 0 && (
          <label style={{display:'flex',alignItems:'center',gap:6,fontSize:12,color:'var(--text2)',cursor:'pointer',whiteSpace:'nowrap'}}>
            <input type="checkbox" checked={selected.length===filtered.length&&filtered.length>0} onChange={e=>e.target.checked?selectAll():clearSelection()}/>
            Select all
          </label>
        )}
      </div>

      {selected.length > 0 && (
        <div className="bulk-bar">
          <span style={{fontSize:13,fontWeight:700,color:'#e5e7eb'}}>{selected.length} selected</span>
          <button className="btn btn-secondary btn-sm" onClick={bulkExport}><Icon n="download" s={12}/> Export</button>
          <button className="btn btn-danger btn-sm" onClick={bulkDelete}><Icon n="trash" s={12}/> Delete Selected</button>
          <button className="btn btn-ghost btn-sm" onClick={clearSelection}>✕ Clear</button>
        </div>
      )}

      <div className="card" style={{padding:0,overflow:'hidden'}}>
        {filtered.length===0 ? (
          <div className="empty-state" style={{padding:'60px 20px'}}>
            <div className="empty-icon">🔍</div>
            <div className="empty-text">No clients match your filter.</div>
          </div>
        ) : (
          <div>
            <div style={{display:'grid',gridTemplateColumns:'32px 1fr auto auto auto auto',gap:10,padding:'10px 16px',borderBottom:'1px solid var(--border)',background:'rgba(255,255,255,.02)'}}>
              <span/>
              <span style={{fontSize:11,fontWeight:700,color:'var(--text3)',textTransform:'uppercase',letterSpacing:'.04em'}}>Client</span>
              <span style={{fontSize:11,fontWeight:700,color:'var(--text3)',textTransform:'uppercase',letterSpacing:'.04em',minWidth:80}}>Health</span>
              <span style={{fontSize:11,fontWeight:700,color:'var(--text3)',textTransform:'uppercase',letterSpacing:'.04em',minWidth:90}}>Status</span>
              <span style={{fontSize:11,fontWeight:700,color:'var(--text3)',textTransform:'uppercase',letterSpacing:'.04em',minWidth:80}}>Revenue</span>
              <span style={{fontSize:11,fontWeight:700,color:'var(--text3)',textTransform:'uppercase',letterSpacing:'.04em',minWidth:80}}>Actions</span>
            </div>
            {paginated.map(c=>(
              <div key={c.id} className={c.pinned?'client-pinned':''} style={{display:'grid',gridTemplateColumns:'32px 1fr auto auto auto auto',gap:10,padding:'10px 16px',alignItems:'center',borderBottom:'1px solid var(--border)',transition:'background .15s',cursor:'pointer'}}
                onMouseOver={e=>e.currentTarget.style.background='rgba(255,255,255,.025)'}
                onMouseOut={e=>e.currentTarget.style.background='transparent'}>
                <input type="checkbox" checked={selected.includes(c.id)} onChange={()=>toggleSelect(c.id)} onClick={e=>e.stopPropagation()}/>
                <div style={{display:'flex',alignItems:'center',gap:10}} onClick={()=>onSelect(c.id)}>
                  <Avatar name={c.name} size={36} color={settings.brandColor||'#f8fafc'}/>
                  <div>
                    <div style={{fontWeight:600,fontSize:13,color:'var(--text)',display:'flex',alignItems:'center',gap:6}}>
                      {c.pinned&&<span style={{fontSize:12}}>📌</span>}
                      {c.name}
                    </div>
                    <div style={{fontSize:11,color:'var(--text3)'}}>{c.company||c.projectName||'No project'}</div>
                  </div>
                </div>
                <div onClick={()=>onSelect(c.id)}><HealthScoreBadge client={c}/></div>
                <div onClick={()=>onSelect(c.id)}><Badge bg={sc(c.status).bg} text={sc(c.status).text}>{c.status||'Pending'}</Badge></div>
                <div style={{fontSize:13,fontWeight:700,color:'var(--text)'}} onClick={()=>onSelect(c.id)}>
                  {curr((c.invoices||[]).reduce((a,i)=>a+getInvoicePaidAmount(i),0))}
                </div>
                <div style={{display:'flex',gap:4}} onClick={e=>e.stopPropagation()}>
                  <button className="btn btn-ghost btn-icon btn-sm" onClick={()=>onTogglePin&&onTogglePin(c.id)} title={c.pinned?'Unpin':'Pin'} style={{fontSize:14}}>{c.pinned?'📌':'📎'}</button>
                  <button className="btn btn-ghost btn-icon btn-sm" onClick={()=>onEdit(c)}><Icon n="edit" s={13}/></button>
                  <button className="btn btn-danger btn-icon btn-sm" onClick={()=>{if(confirm('Delete client?'))onDelete(c.id);}}><Icon n="trash" s={13}/></button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
      <Pagination total={filtered.length} page={pg} perPage={perPage} onChange={setPg}/>
    </div>
  );
}
"""

print("Building new file...")

# Now we need to patch the chunk_admin to replace AdminOverview, AdminAnalytics and AdminApp
# We'll remove these from chunk_admin and add our new versions

# Remove the old AdminApp
admin_code = chunk_admin

# Find and remove AdminOverview (old version)
ov_start = admin_code.find('/* ═══ ADMIN OVERVIEW ═══')
ov_end = admin_code.find('\nfunction ClientRowItem(')
old_overview = admin_code[ov_start:ov_end]

# Find and remove AdminClients (old version)
ac_start = admin_code.find('/* ═══ CLIENTS LIST ═══')
ac_end = admin_code.find('\n/* ═══ CLIENT FORM ═══')
old_clients = admin_code[ac_start:ac_end]

# Find and remove AdminAnalytics (old version)
an_start = admin_code.find('\nfunction AdminAnalytics(')
an_end = admin_code.find('\n/* ═══ ADMIN SETTINGS ═══')
old_analytics = admin_code[an_start:an_end]

# Find and remove AdminApp (old version)
app_start = admin_code.find('/* ═══ ADMIN APP ═══')
app_end = admin_code.find('\n/* ═══ ADMIN OVERVIEW ═══')
old_admin_app = admin_code[app_start:app_end]

print(f"Old overview: {len(old_overview)} chars")
print(f"Old clients: {len(old_clients)} chars")
print(f"Old analytics: {len(old_analytics)} chars")
print(f"Old admin app: {len(old_admin_app)} chars")

# Build admin section without these old parts
admin_without_replacements = admin_code.replace(old_overview, '\n/* REPLACED_OVERVIEW */\n')
admin_without_replacements = admin_without_replacements.replace(old_clients, '\n/* REPLACED_CLIENTS */\n')
admin_without_replacements = admin_without_replacements.replace(old_analytics, '\n/* REPLACED_ANALYTICS */\n')
admin_without_replacements = admin_without_replacements.replace(old_admin_app, '\n/* REPLACED_ADMIN_APP */\n')

print("Replacements done, now building file...")

# Read the firebase config from original
with open('index.html', 'r', encoding='utf-8') as f:
    orig = f.read()

fb_config_start = orig.find('<script src="https://www.gstatic.com/firebasejs')
fb_config_end = orig.find('\n</script>', fb_config_start) + 10
fb_config = orig[fb_config_start:fb_config_end].strip()

new_html = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<title>ClientOS — Crixy Ai</title>
<script crossorigin src="https://cdnjs.cloudflare.com/ajax/libs/react/18.2.0/umd/react.production.min.js"></script>
<script crossorigin src="https://cdnjs.cloudflare.com/ajax/libs/react-dom/18.2.0/umd/react-dom.production.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/babel-standalone/7.23.5/babel.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
'''

# Write the CSS
new_html += open('chunk_css.txt', 'r', encoding='utf-8').read() if os.path.exists('chunk_css.txt') else ''

print(f"HTML so far: {len(new_html)} chars")
print("Done - will build full file in next step")
PYEOF
