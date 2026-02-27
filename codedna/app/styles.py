"""CodeDNA Design System — Premium SaaS CSS"""

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap');

/* ═══ RESET & BASE ═══ */
html, body, [class*="css"] { font-family: 'Inter', -apple-system, sans-serif; }
.stApp { background: #09090b; }
.main .block-container { padding: 0 2rem 2rem; max-width: 1200px; }
[data-testid="stSidebar"] { background: #09090b; border-right: 1px solid #18181b; }
header[data-testid="stHeader"] { background: transparent; }

/* ═══ ANIMATIONS ═══ */
@keyframes fadeUp { from { opacity:0; transform:translateY(20px); } to { opacity:1; transform:translateY(0); } }
@keyframes float { 0%,100% { transform:translateY(0); } 50% { transform:translateY(-8px); } }
@keyframes pulse { 0%,100% { opacity:.7; } 50% { opacity:1; } }
@keyframes shimmer { 0% { background-position:-200% 0; } 100% { background-position:200% 0; } }
@keyframes scaleIn { from { opacity:0; transform:scale(.9); } to { opacity:1; transform:scale(1); } }
@keyframes glow { 0%,100% { box-shadow:0 0 5px #7c3aed30; } 50% { box-shadow:0 0 20px #7c3aed50; } }

/* ═══ NAVBAR ═══ */
.navbar {
    display:flex; align-items:center; justify-content:space-between;
    padding:14px 0; margin-bottom:8px;
    border-bottom:1px solid #18181b;
    animation: fadeUp .5s ease;
}
.nav-brand { display:flex; align-items:center; gap:10px; }
.nav-brand .icon { font-size:1.5rem; animation: float 3s ease-in-out infinite; }
.nav-brand .name { font-size:1.15rem; font-weight:800; color:#fafafa; letter-spacing:-.5px; }
.nav-brand .badge {
    font-size:.6rem; font-weight:600; color:#a78bfa;
    background:#7c3aed15; border:1px solid #7c3aed30;
    padding:2px 8px; border-radius:50px; letter-spacing:.5px;
    text-transform:uppercase;
}
.nav-links { display:flex; gap:6px; }
.nav-link {
    color:#71717a; font-size:.82rem; font-weight:500;
    padding:6px 14px; border-radius:6px;
    text-decoration:none; transition:all .2s;
}
.nav-link:hover { color:#e4e4e7; background:#18181b; }

/* ═══ HERO ═══ */
.hero { text-align:center; padding:60px 0 40px; animation:fadeUp .6s ease; }
.hero-eyebrow {
    display:inline-block; font-size:.72rem; font-weight:600;
    color:#a78bfa; letter-spacing:1.5px; text-transform:uppercase;
    margin-bottom:16px; padding:5px 16px;
    background:#7c3aed10; border:1px solid #7c3aed25;
    border-radius:50px;
}
.hero h1 {
    font-size:3.5rem; font-weight:900; color:#fafafa;
    letter-spacing:-2.5px; line-height:1.05; margin:0 0 16px;
}
.hero h1 .accent {
    background:linear-gradient(135deg,#7c3aed,#a78bfa,#c084fc);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
}
.hero .sub {
    font-size:1.15rem; color:#71717a; font-weight:400;
    line-height:1.6; max-width:560px; margin:0 auto 28px;
}

/* ═══ GLASS CARD ═══ */
.glass {
    background:#0f0f12; border:1px solid #1c1c24;
    border-radius:14px; padding:24px;
    backdrop-filter:blur(12px);
    transition:all .25s ease;
}
.glass:hover { border-color:#27272a; transform:translateY(-2px); box-shadow:0 8px 30px #00000040; }
.glass-sm { padding:16px; border-radius:10px; }
.glass-highlight { border-color:#7c3aed30; }
.glass-highlight:hover { border-color:#7c3aed60; }

/* ═══ STAT CARDS ═══ */
.stats-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(130px,1fr)); gap:12px; }
.stat-card {
    background:#0f0f12; border:1px solid #1c1c24;
    border-radius:12px; padding:20px 16px; text-align:center;
    transition:all .25s ease; animation:scaleIn .5s ease;
}
.stat-card:hover { border-color:#7c3aed40; transform:translateY(-3px); box-shadow:0 8px 24px #00000030; }
.stat-val {
    font-size:2rem; font-weight:800; color:#fafafa;
    letter-spacing:-1px; font-family:'JetBrains Mono',monospace;
}
.stat-lbl {
    font-size:.68rem; color:#52525b; text-transform:uppercase;
    letter-spacing:1.5px; font-weight:600; margin-top:6px;
}

/* ═══ GRADE ═══ */
.grade-ring {
    width:68px; height:68px; border-radius:50%;
    display:inline-flex; align-items:center; justify-content:center;
    font-size:1.8rem; font-weight:900; border:3px solid;
    font-family:'JetBrains Mono',monospace;
    animation:scaleIn .6s ease;
}
.grade-A { border-color:#10b981; color:#10b981; background:#10b98110; }
.grade-B { border-color:#3b82f6; color:#3b82f6; background:#3b82f610; }
.grade-C { border-color:#f59e0b; color:#f59e0b; background:#f59e0b10; }
.grade-D { border-color:#ef4444; color:#ef4444; background:#ef444410; }
.grade-F { border-color:#dc2626; color:#dc2626; background:#dc262610; }

/* ═══ FEATURE CARDS ═══ */
.feat-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:16px; }
.feat-card {
    background:#0f0f12; border:1px solid #1c1c24;
    border-radius:14px; padding:28px 24px;
    transition:all .3s ease; cursor:default;
}
.feat-card:hover { border-color:#7c3aed40; transform:translateY(-4px); box-shadow:0 12px 40px #00000030; }
.feat-icon { font-size:2rem; margin-bottom:14px; display:block; }
.feat-title { font-size:1rem; font-weight:700; color:#e4e4e7; margin-bottom:8px; }
.feat-desc { font-size:.85rem; color:#71717a; line-height:1.55; }

/* ═══ HOW IT WORKS ═══ */
.steps-row { display:grid; grid-template-columns:repeat(4,1fr); gap:16px; position:relative; }
.step-card { text-align:center; padding:24px 16px; position:relative; }
.step-num {
    width:36px; height:36px; border-radius:50%;
    background:#7c3aed; color:white;
    display:inline-flex; align-items:center; justify-content:center;
    font-weight:700; font-size:.9rem; margin-bottom:12px;
}
.step-title { font-size:.9rem; font-weight:600; color:#e4e4e7; margin-bottom:6px; }
.step-desc { font-size:.8rem; color:#52525b; line-height:1.5; }

/* ═══ FAQ ═══ */
div[data-testid="stExpander"] {
    background:#0f0f12 !important; border:1px solid #1c1c24 !important;
    border-radius:10px !important; margin-bottom:6px;
}
div[data-testid="stExpander"]:hover { border-color:#27272a !important; }

/* ═══ SECTION HEADERS ═══ */
.sec-header { text-align:center; margin:48px 0 28px; animation:fadeUp .5s ease; }
.sec-header h2 { font-size:1.8rem; font-weight:800; color:#fafafa; letter-spacing:-1px; margin:0 0 8px; }
.sec-header p { font-size:.95rem; color:#52525b; }
.sec-left { text-align:left; margin:20px 0 16px; }

/* ═══ INPUT ═══ */
.input-label {
    font-size:.72rem; color:#52525b; text-transform:uppercase;
    letter-spacing:1.5px; font-weight:700; margin-bottom:8px;
}

/* ═══ TAGS ═══ */
.tags { display:flex; gap:8px; flex-wrap:wrap; justify-content:center; }
.tag {
    display:inline-flex; align-items:center; gap:5px;
    font-size:.76rem; font-weight:500; padding:5px 13px;
    border-radius:6px; border:1px solid;
}
.tag-v { color:#a78bfa; border-color:#7c3aed25; background:#7c3aed08; }
.tag-c { color:#67e8f9; border-color:#06b6d425; background:#06b6d408; }
.tag-e { color:#6ee7b7; border-color:#10b98125; background:#10b98108; }
.tag-a { color:#fbbf24; border-color:#f59e0b25; background:#f59e0b08; }

/* ═══ DIVIDER ═══ */
.div { height:1px; background:#18181b; margin:24px 0; }
.div-accent {
    height:2px; margin:32px 0;
    background:linear-gradient(90deg,transparent,#7c3aed40,transparent);
}

/* ═══ FOOTER ═══ */
.footer {
    text-align:center; padding:32px 0 16px;
    border-top:1px solid #18181b; margin-top:48px;
    color:#3f3f46; font-size:.8rem;
}
.footer a { color:#7c3aed; text-decoration:none; }
.footer a:hover { color:#a78bfa; }

/* ═══ CTA BANNER ═══ */
.cta-banner {
    text-align:center; padding:48px 32px;
    background:#0f0f12; border:1px solid #7c3aed20;
    border-radius:16px; margin:40px 0;
}
.cta-banner h2 { font-size:1.6rem; font-weight:800; color:#fafafa; margin:0 0 10px; letter-spacing:-1px; }
.cta-banner p { color:#71717a; font-size:.95rem; margin-bottom:20px; }

/* ═══ STATUS ═══ */
.dot { display:inline-block; width:7px; height:7px; border-radius:50%; margin-right:6px; }
.dot-g { background:#10b981; box-shadow:0 0 6px #10b98180; }
.dot-r { background:#ef4444; box-shadow:0 0 6px #ef444480; }

/* ═══ STREAMLIT OVERRIDES ═══ */
.stProgress > div > div > div > div { background:#7c3aed !important; border-radius:10px; }
div[data-testid="stMetricValue"] { font-family:'JetBrains Mono',monospace; }
.stButton > button[kind="primary"] {
    background:#7c3aed !important; border:none !important;
    border-radius:8px !important; font-weight:600 !important;
    letter-spacing:-.2px; transition:all .2s !important;
}
.stButton > button[kind="primary"]:hover {
    background:#6d28d9 !important; transform:translateY(-1px) !important;
    box-shadow:0 4px 16px #7c3aed40 !important;
}
.stButton > button {
    border-radius:8px !important; border:1px solid #27272a !important;
    background:#18181b !important; color:#a1a1aa !important;
    font-weight:500 !important; transition:all .2s !important;
}
.stButton > button:hover {
    border-color:#7c3aed50 !important; color:#e4e4e7 !important;
    background:#1c1c24 !important;
}
.stTextInput > div > div > input {
    background:#18181b !important; border:1px solid #27272a !important;
    border-radius:8px !important; color:#e4e4e7 !important;
    font-family:'JetBrains Mono',monospace !important; font-size:.88rem !important;
    padding:10px 14px !important;
}
.stTextInput > div > div > input:focus { border-color:#7c3aed !important; box-shadow:0 0 0 2px #7c3aed20 !important; }
.stTextArea > div > div > textarea {
    background:#18181b !important; border:1px solid #27272a !important;
    border-radius:8px !important; color:#e4e4e7 !important;
    font-family:'JetBrains Mono',monospace !important;
}
.stSelectbox > div > div { background:#18181b !important; border-radius:8px !important; }
</style>
"""
