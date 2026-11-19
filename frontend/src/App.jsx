import React, { useMemo, useState } from "react";
import {
  Activity, Bell, BookOpen, Check, CheckCircle2, ChevronDown, CircleUserRound,
  Clock3, GitBranch, LayoutDashboard, LogOut, Menu, MoreHorizontal, Plus,
  Search, Settings as SettingsIcon, SlidersHorizontal, Sparkles, Trash2, User,
  X, Zap, Download, Eye, Pencil, Save, ArrowLeft, CalendarDays
} from "lucide-react";
import "./styles.css";

const seedTasks = [
  { id: 1, title: "Finalize Architecture Schema", subject: "Core System", deadline: "2026-11-08", type: "Engineering", priority: "High", status: "In Progress", description: "Complete the system architecture and validate the core modules.", dependsOn: [3] },
  { id: 2, title: "Wireframe Review & Feedback", subject: "TIM UX Flow", deadline: "2026-11-10", type: "Design / Spec", priority: "Medium", status: "Pending", description: "Review the key user journeys and consolidate feedback.", dependsOn: [1] },
  { id: 3, title: "Database Schema Migration", subject: "Infrastructure", deadline: "2026-11-12", type: "Backend", priority: "Low", status: "Backlog", description: "Prepare and migrate the database schema.", dependsOn: [] },
];

const moods = [
  ["Focused / Good", "✦", "mint"], ["High Energy", "☀", "yellow"],
  ["Neutral", "◉", "blue"], ["Fatigued", "☁", "orange"], ["Overwhelmed", "◌", "pink"]
];

const dateLabel = () => new Intl.DateTimeFormat("en-GB", {
  weekday: "short", day: "2-digit", month: "short", year: "numeric"
}).format(new Date());

function load(key, fallback) {
  try { const value = localStorage.getItem(key); return value ? JSON.parse(value) : fallback; }
  catch { return fallback; }
}
function persist(key, value) {
  try { localStorage.setItem(key, JSON.stringify(value)); } catch {}
}

function Brand() {
  return <div className="brand-lockup"><span className="mascot"><i/><i/></span><span>TIM</span></div>;
}

function Sidebar({ page, navigate, user }) {
  const links = [
    ["Dashboard", LayoutDashboard], ["Full Graph", GitBranch], ["Journal", BookOpen],
    ["Settings", SlidersHorizontal], ["Profile", CircleUserRound]
  ];
  return <aside className="sidebar">
    <button className="brand-button" onClick={() => navigate("Dashboard")}><Brand /></button>
    <div className="eyebrow nav-label">Workspace</div>
    <nav className="side-nav">
      {links.map(([label, Icon]) => <button key={label} className={page === label ? "nav-item active" : "nav-item"} onClick={() => navigate(label)}>
        <Icon size={18}/><span>{label}</span>{page === label && <b/>}
      </button>)}
    </nav>
    <div className="side-spacer"/>
    <div className="sidebar-note"><span className="note-spark">✳</span><strong>Make space<br/>for good work.</strong><small>One thing at a time.</small></div>
    <div className="account-block">
      <div className="eyebrow">Account</div>
      <button className="account-card" onClick={() => navigate("Profile")}><span className="avatar">{(user.name || "J").slice(0,1).toUpperCase()}</span><span><strong>{user.name || "Jordan Doe"}</strong><small>Personal workspace</small></span><MoreHorizontal size={18}/></button>
    </div>
  </aside>;
}

function Topbar({ page, navigate, query, setQuery, user }) {
  return <header className="topbar">
    <div><div className="crumb">TIM <span>›</span> Workspace</div><h1>{page}</h1></div>
    <div className="top-actions">
      <label className="search-box"><Search size={16}/><input value={query} onChange={e => setQuery(e.target.value)} placeholder="Search tasks..."/></label>
      <button className="round-icon" aria-label="Notifications"><Bell size={17}/><i/></button>
      <button className="user-chip" onClick={() => navigate("Profile")}><span className="tiny-avatar">{(user.name || "J").slice(0,1).toUpperCase()}</span>{user.name || "Jordan Doe"}<ChevronDown size={14}/></button>
    </div>
  </header>;
}

function SectionHeading({ title, subtitle, action }) {
  return <div className="section-head"><div><h2>{title}</h2>{subtitle && <p>{subtitle}</p>}</div>{action}</div>;
}

function TaskTable({ tasks, onEdit, onDelete, onStatus, onSelect }) {
  return <section className="panel tasks-panel">
    <SectionHeading title="Tasks" subtitle="Your ordered stack of active tasks" action={<button className="btn btn-primary" onClick={() => onEdit(null)}><Plus size={16}/> Add Task</button>}/>
    <div className="table-wrap"><table><thead><tr><th>Title</th><th>Subject</th><th>Deadline</th><th>Type</th><th>Priority</th><th>Status</th><th/></tr></thead>
      <tbody>{tasks.map(task => <tr key={task.id}>
        <td><button className="task-link" onClick={() => onSelect(task)}>{task.title}</button></td>
        <td><span className="tag">{task.subject}</span></td><td><span className="date-cell"><Clock3 size={13}/>{task.deadline || "Not set"}</span></td>
        <td>{task.type}</td><td><span className={`priority ${task.priority.toLowerCase()}`}>{task.priority}</span></td>
        <td><select className="status-select" value={task.status} onChange={e => onStatus(task.id,e.target.value)}><option>Backlog</option><option>Pending</option><option>In Progress</option><option>Done</option></select></td>
        <td><button className="icon-plain" onClick={() => onEdit(task)} aria-label="Edit task"><Pencil size={15}/></button><button className="icon-plain" onClick={() => onDelete(task.id)} aria-label="Delete task"><Trash2 size={15}/></button></td>
      </tr>)}</tbody></table>{!tasks.length && <div className="empty-state">No tasks yet. Add one to get started.</div>}</div>
  </section>;
}

function MoodLogger({ onLog }) {
  const [mood,setMood] = useState("Focused / Good"); const [note,setNote] = useState("");
  return <section className="panel mood-panel"><div className="mood-title"><div><h2>How are you feeling today?</h2><p>Daily energy &amp; state logging</p></div><span className="mood-icon">☺</span></div>
    <div className="state-row"><span className="eyebrow">State</span>{moods.map(([label,symbol,tone]) => <button key={label} onClick={() => setMood(label)} className={`mood-choice ${tone} ${mood===label?"chosen":""}`}>{symbol} {label}</button>)}</div>
    <form className="mood-entry" onSubmit={e => {e.preventDefault();onLog({id:Date.now(),mood,note,time:new Date().toLocaleTimeString([],{hour:"2-digit",minute:"2-digit"})});setNote("");}}><input value={note} onChange={e=>setNote(e.target.value)} placeholder="How are you feeling? Enter a note or reflection..."/><button className="btn btn-primary"><Check size={16}/> Log Mood</button></form>
  </section>;
}

function GraphCanvas({ tasks, onSelect, fullscreen=false }) {
  const nodes = tasks.slice(0,8);
  const positions = nodes.map((t,i)=>({x: 12 + (i%3)*37, y: 20 + Math.floor(i/3)*30}));
  return <div className={`graph-canvas ${fullscreen?"large":""}`}>
    <svg className="graph-lines" viewBox="0 0 100 100" preserveAspectRatio="none">
      {nodes.map((task,i)=>(task.dependsOn||[]).map(dep=>{const j=nodes.findIndex(n=>n.id===dep);if(j<0)return null;return <line key={`${task.id}-${dep}`} x1={`${positions[j].x+7}%`} y1={`${positions[j].y+4}%`} x2={`${positions[i].x+7}%`} y2={`${positions[i].y+4}%`} stroke="#b66a35" strokeWidth="0.35" strokeDasharray="1.2 1.1"/>;}))}
      {nodes.slice(1).map((t,i)=><line key={`link-${t.id}`} x1={`${positions[i].x+7}%`} y1={`${positions[i].y+4}%`} x2={`${positions[i+1].x+7}%`} y2={`${positions[i+1].y+4}%`} stroke="#d8a06b" strokeWidth=".25"/>)}
    </svg>
    {nodes.map((task,i)=><button key={task.id} className={`graph-node node-${task.status.toLowerCase().replace(" ","-")}`} style={{left:`${positions[i].x}%`,top:`${positions[i].y}%`}} onClick={()=>onSelect(task)}><span className="node-dot"/><strong>{task.title}</strong><small>{task.status}</small></button>)}
    {!nodes.length && <div className="empty-state">Add tasks to build your dependency graph.</div>}
  </div>;
}

function Dashboard({tasks,setTasks,moodsLog,onMoodLog,onEdit,onDelete,onSelect,onStatus,notify}) {
  const active=tasks.filter(t=>t.status!=="Done").length, high=tasks.filter(t=>t.priority==="High"&&t.status!=="Done").length, done=tasks.filter(t=>t.status==="Done").length;
  return <div className="page-content">
    <div className="welcome-row"><div><h2>A LITTLE CLARITY GOES A LONG WAY <span>✳</span></h2><p>Here’s your overview. Start with what matters most.</p></div><div className="date-pill"><i/> {dateLabel()}</div></div>
    <div className="stats-grid"><article className="stat-card peach"><Activity/><span>Active tasks</span><strong>{String(active).padStart(2,"0")}</strong><small>Keep the next step small</small></article><article className="stat-card lilac"><Zap/><span>High priority</span><strong>{String(high).padStart(2,"0")}</strong><small>Tasks that need attention</small></article><article className="stat-card lime"><CheckCircle2/><span>Completed</span><strong>{String(done).padStart(2,"0")}</strong><small>Progress, not perfection</small></article></div>
    <MoodLogger onLog={onMoodLog}/>
    {moodsLog.length>0&&<section className="panel recent-panel"><SectionHeading title="Recent check-ins" subtitle="Your latest mood logs"/>{moodsLog.slice(-3).reverse().map(log=><div className="recent-row" key={log.id}><i/><strong>{log.mood}</strong><span>{log.note}</span><time>{log.time}</time></div>)}</section>}
    <TaskTable tasks={tasks} onEdit={onEdit} onDelete={onDelete} onStatus={onStatus} onSelect={onSelect}/>
    <section className="panel graph-preview"><SectionHeading title="Dependency Graph" subtitle="See how your tasks connect" action={<button className="btn btn-secondary" onClick={()=>notify("Open Full Graph from the sidebar to explore the complete graph.")}>View full graph <GitBranch size={15}/></button>}/><GraphCanvas tasks={tasks} onSelect={onSelect}/></section>
  </div>;
}

function Journal({moodsLog}) {
  const [mood,setMood]=useState(4),[stress,setStress]=useState(2),[energy,setEnergy]=useState(5),[quick,setQuick]=useState(""),[title,setTitle]=useState(""),[reflection,setReflection]=useState("");
  const [entries,setEntries]=useState(load("tim_entries",[]));
  const save=()=>{if(!title.trim()&&!reflection.trim()&&!quick.trim())return;const next=[{id:Date.now(),title:title||"Daily reflection",reflection:reflection||quick,date:dateLabel()},...entries];setEntries(next);persist("tim_entries",next);setTitle("");setReflection("");setQuick("");};
  const rating=(label,value,setValue,low,high)=><div className="rating-row"><div><strong>{label}</strong><small>{low}, 5={high}</small></div><div className="rating-buttons">{[1,2,3,4,5].map(n=><button key={n} className={value===n?"selected":""} onClick={()=>setValue(n)}>{n}</button>)}</div><span className="selected-label">Selected: {value}</span></div>;
  return <div className="page-content journal-screen"><section className="panel checkin-panel"><SectionHeading title="Daily Check-In" subtitle="Daily state & reflection logging"/><div className="checkin-ratings">{rating("MOOD",mood,setMood,"1=Low","5=High")}{rating("STRESS",stress,setStress,"1=Calm","5=High")}{rating("ENERGY",energy,setEnergy,"1=Low","5=Vitality")}</div><div className="quick-row"><input value={quick} onChange={e=>setQuick(e.target.value)} placeholder="Quick notes or reflection context..."/><button className="btn btn-primary" onClick={()=>{setTitle("Daily check-in");setReflection(`Mood ${mood}/5 · Stress ${stress}/5 · Energy ${energy}/5. ${quick}`);}}>Use in diary</button></div></section>
    <section className="panel diary-panel"><SectionHeading title="Diary & Reflection" subtitle="Freeform entry, personal notes and thoughts"/><label className="field-label">Title<input value={title} onChange={e=>setTitle(e.target.value)} placeholder="Title of today's entry..."/></label><label className="field-label">Reflection<textarea value={reflection} onChange={e=>setReflection(e.target.value)} placeholder="Write about your day, thoughts, or reflections..."/></label><div className="form-footer"><span>Drafts are stored in this browser.</span><button className="btn btn-primary" onClick={save}><Save size={15}/> Save Entry</button></div></section>
    <section className="panel saved-entries"><SectionHeading title="Previous reflections" subtitle="Your saved journal entries"/>{entries.length?entries.map(e=><article key={e.id} className="entry-card"><time>{e.date}</time><h3>{e.title}</h3><p>{e.reflection}</p></article>):<div className="empty-state">Your saved reflections will appear here.</div>}</section>
    <section className="panel recent-panel"><SectionHeading title="Recent mood check-ins" subtitle="A simple record of how you have been feeling"/>{moodsLog.map(m=><div className="recent-row" key={m.id}><i/><strong>{m.mood}</strong><span>{m.note}</span><time>{m.time}</time></div>)}</section>
  </div>;
}

function TaskModal({task,onClose,onSave}) {
  const [form,setForm]=useState(task?{...task}:{title:"",subject:"",deadline:"",type:"Design / Spec",priority:"Medium",status:"Backlog",description:"",dependsOn:[]});
  const update=(k,v)=>setForm(f=>({...f,[k]:v}));
  return <div className="modal-backdrop" onMouseDown={e=>e.target===e.currentTarget&&onClose()}><form className="modal-card" onSubmit={e=>{e.preventDefault();onSave({...form,id:task?.id||Date.now()});}}>
    <div className="modal-head"><div><span className="eyebrow">Workspace / Tasks</span><h2>{task?"Edit task":"Add a task"}</h2></div><button type="button" className="icon-plain" onClick={onClose}><X/></button></div>
    <label className="field-label">Task title<input required value={form.title} onChange={e=>update("title",e.target.value)} placeholder="e.g. Review the onboarding flow"/></label>
    <label className="field-label">Subject<input value={form.subject} onChange={e=>update("subject",e.target.value)} placeholder="e.g. Product design"/></label>
    <div className="form-grid"><label className="field-label">Deadline<input type="date" value={form.deadline} onChange={e=>update("deadline",e.target.value)}/></label><label className="field-label">Task type<select value={form.type} onChange={e=>update("type",e.target.value)}><option>Design / Spec</option><option>Engineering</option><option>Backend</option><option>Research</option><option>Personal</option></select></label><label className="field-label">Priority<select value={form.priority} onChange={e=>update("priority",e.target.value)}><option>High</option><option>Medium</option><option>Low</option></select></label><label className="field-label">Status<select value={form.status} onChange={e=>update("status",e.target.value)}><option>Backlog</option><option>Pending</option><option>In Progress</option><option>Done</option></select></label></div>
    <label className="field-label">Description<textarea value={form.description} onChange={e=>update("description",e.target.value)} placeholder="Add context, next steps, or notes..."/></label>
    <div className="modal-actions"><button type="button" className="btn btn-secondary" onClick={onClose}>Cancel</button><button className="btn btn-primary"><Check size={15}/>{task?"Save changes":"Create task"}</button></div>
  </form></div>;
}

function TaskDetail({task,onClose,onEdit,onStatus}) {
  if(!task)return null;
  return <div className="modal-backdrop" onMouseDown={e=>e.target===e.currentTarget&&onClose()}><section className="detail-card"><div className="modal-head"><div><span className="eyebrow">Task detail & inspection</span><h2>{task.title}</h2></div><button className="icon-plain" onClick={onClose}><X/></button></div><div className="detail-grid"><div><small>Subject</small><strong>{task.subject}</strong></div><div><small>Deadline</small><strong>{task.deadline||"Not set"}</strong></div><div><small>Task type</small><strong>{task.type}</strong></div><div><small>Priority</small><strong>{task.priority}</strong></div><div><small>Status</small><select value={task.status} onChange={e=>onStatus(task.id,e.target.value)}><option>Backlog</option><option>Pending</option><option>In Progress</option><option>Done</option></select></div></div><div className="detail-description"><small>Description</small><p>{task.description||"No description has been added yet."}</p></div><div className="modal-actions"><button className="btn btn-secondary" onClick={onClose}>Close</button><button className="btn btn-primary" onClick={()=>onEdit(task)}><Pencil size={15}/> Edit task</button></div></section></div>;
}

function FullGraph({tasks,onSelect,navigate}) {
  return <div className="page-content"><div className="welcome-row"><div><h2>Task dependency map <span>✳</span></h2><p>Explore the relationships that shape your workload.</p></div><button className="btn btn-secondary" onClick={()=>navigate("Profile")}>Saved snapshots</button></div><section className="panel full-graph-panel"><div className="graph-toolbar"><div><strong>Dynamic Cognitive Dependency Graph</strong><small>Click any node to inspect its task</small></div><div><button className="btn btn-secondary" onClick={()=>window.print()}>Export / Print <Download size={15}/></button></div></div><GraphCanvas tasks={tasks} onSelect={onSelect} fullscreen/><div className="graph-legend"><span><i className="legend-dot active-dot"/> In progress</span><span><i className="legend-dot pending-dot"/> Pending</span><span><i className="legend-dot done-dot"/> Completed</span></div></section></div>;
}

function SettingsScreen({user,setUser,notify,onLogout}) {
  const [notifications,setNotifications]=useState(true),[reminder,setReminder]=useState(true),[summary,setSummary]=useState(false),[sound,setSound]=useState(true);
  return <div className="page-content"><div className="settings-intro panel"><div><span className="eyebrow">Workspace / Settings</span><h2>System preferences &amp; account settings</h2><p>Configure personal identification details, communication preferences, and active sessions.</p></div><span className="version-tag">CONFIG // V1.0</span></div><div className="settings-grid"><section className="panel setting-card"><div className="setting-heading"><div><h2>[ 01 ] Profile Information</h2><p>Manage personal details and credentials</p></div><User/></div><div className="setting-body"><div className="profile-mini"><span className="avatar large">{(user.name||"J").slice(0,1)}</span><div><strong>{user.name}</strong><small>Active Member // Primary</small></div></div><label className="field-label">Full name<input value={user.name} onChange={e=>setUser({...user,name:e.target.value})}/></label><label className="field-label">Email address<input value={user.email} onChange={e=>setUser({...user,email:e.target.value})}/></label><label className="field-label">Workspace handle<input value={user.handle||"tim_member"} onChange={e=>setUser({...user,handle:e.target.value})}/></label><button className="btn btn-primary align-right" onClick={()=>notify("Profile settings saved locally.")}>Save changes</button></div></section>
    <section className="panel setting-card"><div className="setting-heading"><div><h2>[ 02 ] Preferences</h2><p>Configure notifications and system alert settings</p></div><SlidersHorizontal/></div><div className="setting-body">{[[notifications,setNotifications,"Notifications","Global toggle for push and dispatch triggers"],[reminder,setReminder,"Daily journal reminder","Scheduled prompt alert at 18:00 daily"],[summary,setSummary,"Email summaries","Weekly digest of logged entries and reflections"],[sound,setSound,"Sound feedback","Auditory click cues during keystroke input"]].map(([v,set,label,desc])=><div className="toggle-row" key={label}><div><strong>{label}</strong><small>{desc}</small></div><button className={v?"toggle on":"toggle"} onClick={()=>set(!v)}>{v?"ON":"OFF"}</button></div>)}<div className="sync-note">↻ Settings cached to local storage. Auto-synced.</div></div></section></div><section className="session-panel"><div className="session-icon"><LogOut/></div><div><h2>Active session management</h2><p>End active session on this device. Your workspace status and saved journal drafts remain stored in this browser.</p></div><button className="btn btn-secondary" onClick={onLogout}>Log out</button></section></div>;
}

function ProfileScreen({user,tasks,snapshots,setSnapshots,onView,onToast}) {
  const createSnapshot=()=>{const snap={id:Date.now(),name:`Graph snapshot — ${dateLabel()}`,date:dateLabel(),tasks:JSON.parse(JSON.stringify(tasks))};setSnapshots(s=>[snap,...s]);onToast("Graph snapshot saved.");};
  return <div className="page-content"><div className="profile-banner"><div><span className="eyebrow">Workspace &gt; Profile</span><h2>User Profile</h2></div><span className="version-tag">SYS_STATUS: [OK]</span></div><section className="panel profile-summary"><SectionHeading title="[ 01 ] Account Summary" subtitle="Your workspace identity and usage"/><div className="summary-layout"><div className="avatar-frame"><span className="avatar huge">{(user.name||"J").slice(0,1)}</span></div><div className="summary-fields"><div><small>User name</small><strong>{user.name}</strong></div><div><small>Email identifier</small><strong>{user.email}</strong></div><div><small>Workspace role</small><strong>Member / Researcher</strong></div><div><small>Join date</small><strong>Workspace member</strong></div></div></div><div className="summary-footer"><span>STORAGE_QUOTA: <b>Local browser storage</b></span><button className="btn btn-secondary" onClick={()=>onToast("Edit your details in Settings.")}>Edit profile</button></div></section>
    <section className="panel snapshots-panel"><SectionHeading title="[ 02 ] Saved Dependency Graphs" subtitle="Historical snapshots" action={<button className="btn btn-primary" onClick={createSnapshot}><Save size={15}/> Save current graph</button>}/>{snapshots.length?snapshots.map((s,i)=><div className="snapshot-row" key={s.id}><div className="snapshot-thumb"><GitBranch/></div><div className="snapshot-info"><strong>{s.name}</strong><small>{s.tasks.length} nodes · Archived snapshot · {s.date}</small></div><button className="btn btn-secondary" onClick={()=>onView(s)}><Eye size={15}/> View</button></div>):<div className="empty-state">No saved snapshots yet. Save your current dependency graph to keep a historical version.</div>}</section></div>;
}

function SnapshotViewer({snapshot,onBack,onSelect}) {
  return <div className="page-content"><button className="back-link" onClick={onBack}><ArrowLeft size={16}/> Back to profile</button><div className="welcome-row"><div><h2>{snapshot.name}</h2><p>Read-only historical dependency graph · {snapshot.date}</p></div><button className="btn btn-secondary" onClick={()=>window.print()}><Download size={15}/> Export</button></div><section className="panel full-graph-panel"><div className="graph-toolbar"><div><strong>Archived graph snapshot</strong><small>{snapshot.tasks.length} task nodes · Historical view</small></div><span className="version-tag">READ ONLY</span></div><GraphCanvas tasks={snapshot.tasks} onSelect={onSelect} fullscreen/></section><div className="notice">This is a historical snapshot. Changes made to current tasks will not affect this saved graph.</div></div>;
}

function AuthScreen({onLogin}) {
  const [mode,setMode]=useState("login"),[name,setName]=useState(""),[email,setEmail]=useState(""),[password,setPassword]=useState("");
  return <div className="auth-screen"><div className="auth-left"><Brand/><div className="auth-copy"><span className="eyebrow">A clearer way to work</span><h1>Let TIM plan your day.</h1><p>Bring your tasks, priorities, and next steps into one clear view.</p><ul><li><CheckCircle2/> See what needs your attention</li><li><GitBranch/> Understand how tasks connect</li><li><Sparkles/> Make progress one step at a time</li></ul></div><div className="auth-foot">TIM · Task Interdependency Mapper</div></div><div className="auth-right"><form className="auth-card" onSubmit={e=>{e.preventDefault();onLogin({name:name||email.split("@")[0]||"Jordan Doe",email:email||"user@tim.app"});}}><span className="eyebrow">{mode==="login"?"Welcome back":"Create your workspace"}</span><h2>{mode==="login"?"Sign in to TIM":"Create an account"}</h2><p>{mode==="login"?"Pick up where you left off.":"Set up your personal planning space."}</p>{mode==="signup"&&<label className="field-label">Full name<input required value={name} onChange={e=>setName(e.target.value)} placeholder="Your name"/></label>}<label className="field-label">Email address<input required type="email" value={email} onChange={e=>setEmail(e.target.value)} placeholder="you@example.com"/></label><label className="field-label">Password<input required type="password" minLength="4" value={password} onChange={e=>setPassword(e.target.value)} placeholder="Enter your password"/></label><button className="btn btn-primary auth-submit">{mode==="login"?"Sign in":"Create account"} <ArrowLeft className="arrow-right" size={16}/></button><div className="auth-switch">{mode==="login"?"New to TIM?":"Already have an account?"} <button type="button" onClick={()=>setMode(mode==="login"?"signup":"login")}>{mode==="login"?"Create account":"Sign in"}</button></div><small className="auth-disclaimer">Prototype sign-in only. Connect an authentication service before production use.</small></form></div></div>;
}

export default function App() {
  const [authenticated,setAuthenticated]=useState(load("tim_auth",true));
  const [user,setUser]=useState(load("tim_user",{name:"Jordan Doe",email:"jordan@domain.com",handle:"jordan_doe"}));
  const [page,setPage]=useState("Dashboard");
  const [tasks,setTasks]=useState(load("tim_tasks",seedTasks));
  const [moodsLog,setMoodsLog]=useState(load("tim_moods",[]));
  const [snapshots,setSnapshots]=useState(load("tim_snapshots",[]));
  const [query,setQuery]=useState("");
  const [editing,setEditing]=useState(undefined);
  const [selected,setSelected]=useState(null);
  const [snapshot,setSnapshot]=useState(null);
  const [toast,setToast]=useState("");
  const notify=message=>{setToast(message);window.clearTimeout(window.__timToast);window.__timToast=window.setTimeout(()=>setToast(""),2600);};
  const filtered=useMemo(()=>tasks.filter(t=>`${t.title} ${t.subject} ${t.type}`.toLowerCase().includes(query.toLowerCase())),[tasks,query]);
  const saveTasks=next=>{setTasks(next);persist("tim_tasks",next);};
  const navigate=p=>{setPage(p);setSnapshot(null);};
  const saveTask=task=>{const next=task.id&&tasks.some(t=>t.id===task.id)?tasks.map(t=>t.id===task.id?task:t):[...tasks,task];saveTasks(next);setEditing(undefined);notify(task.id&&tasks.some(t=>t.id===task.id)?"Task updated.":"Task created.");};
  const status=(id,value)=>saveTasks(tasks.map(t=>t.id===id?{...t,status:value}:t));
  const remove=id=>{if(window.confirm("Delete this task?")){saveTasks(tasks.filter(t=>t.id!==id));notify("Task deleted.");}};
  const logMood=log=>{const next=[...moodsLog,log];setMoodsLog(next);persist("tim_moods",next);notify("Mood logged.");};
  const updateUser=next=>{setUser(next);persist("tim_user",next);};
  const updateSnapshots=fn=>setSnapshots(current=>{const next=typeof fn==="function"?fn(current):fn;persist("tim_snapshots",next);return next;});
  const login=profile=>{updateUser({...user,...profile});setAuthenticated(true);persist("tim_auth",true);};
  if(!authenticated)return <AuthScreen onLogin={login}/>;
  return <div className="app-shell"><Sidebar page={snapshot?"Profile":page} navigate={navigate} user={user}/><main className="main-content"><Topbar page={snapshot?"Snapshot Viewer":page} navigate={navigate} query={query} setQuery={setQuery} user={user}/>
    {page==="Dashboard"&&<Dashboard tasks={filtered} moodsLog={moodsLog} onMoodLog={logMood} onEdit={setEditing} onDelete={remove} onSelect={setSelected} onStatus={status} notify={notify}/>}
    {page==="Journal"&&<Journal moodsLog={moodsLog}/>}
    {page==="Full Graph"&&<FullGraph tasks={filtered} onSelect={setSelected} navigate={navigate}/>}
    {page==="Settings"&&<SettingsScreen user={user} setUser={updateUser} notify={notify} onLogout={()=>{setAuthenticated(false);persist("tim_auth",false);}}/>}
    {page==="Profile"&&!snapshot&&<ProfileScreen user={user} tasks={tasks} snapshots={snapshots} setSnapshots={updateSnapshots} onView={setSnapshot} onToast={notify}/>}
    {snapshot&&<SnapshotViewer snapshot={snapshot} onBack={()=>setSnapshot(null)} onSelect={setSelected}/>}
    </main>
    {toast&&<div className="toast"><CheckCircle2 size={17}/>{toast}</div>}
    {editing!==undefined&&<TaskModal task={editing} onClose={()=>setEditing(undefined)} onSave={saveTask}/>}
    {selected&&<TaskDetail task={tasks.find(t=>t.id===selected.id)||selected} onClose={()=>setSelected(null)} onEdit={task=>{setSelected(null);setEditing(task);}} onStatus={status}/>}
  </div>;
}
