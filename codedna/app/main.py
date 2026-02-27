"""
CodeDNA — AI-Powered Codebase Genome Analyzer
Direct-Response SaaS Streamlit Frontend
"""
import streamlit as st
import os, sys, shutil, tempfile, hashlib, stat, base64

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config
from app.styles import THEME_CSS

# ═══════════════════════════════════════════════════════════════════
# 1. PAGE CONFIGURATION
# ═══════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="CodeDNA — High-Converting SaaS Landing Page",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed",
)
st.markdown(THEME_CSS, unsafe_allow_html=True)

# ── Session State ──
for k, v in {"done": False, "units": [], "health": None, "evo": None,
             "url": "", "name": "", "emb": None, "sp": None, "idx": None, "srch": None}.items():
    if k not in st.session_state: st.session_state[k] = v


# ═══════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════
def clone_repo(url):
    def rm_ro(fn, p, _): os.chmod(p, stat.S_IWRITE); fn(p)
    h = hashlib.md5(url.encode()).hexdigest()[:10]
    d = os.path.join(tempfile.gettempdir(), f"codedna_{h}")
    if os.path.exists(d): shutil.rmtree(d, onerror=rm_ro)
    os.makedirs(d, exist_ok=True)
    if os.system(f'git clone --depth=1 "{url}" "{d}"') != 0: raise RuntimeError(f"Clone failed: {url}")
    return d

def get_name(u):
    u = u.rstrip("/").rstrip(".git"); p = u.split("/")
    return f"{p[-2]}/{p[-1]}" if len(p) >= 2 else p[-1]

def run_pipeline(url, cb=None):
    from core.parser import CodeParser
    from core.embedder import CodeEmbedder
    from core.sparse import SparseVectorGenerator
    from core.indexer import EndeeIndexer
    from core.searcher import CodeSearcher
    from core.analyzer import CodeHealthAnalyzer
    from core.evolution import EvolutionTracker
    R = {}
    if cb: cb("clone")
    R["path"] = clone_repo(url)
    if cb: cb("parse")
    units = CodeParser().parse_directory(R["path"], recursive=True)
    if not units: raise ValueError("No Python/JS/Java code found.")
    R["units"] = units; st.session_state.units = units
    lc, tc, loc, cx = {}, {}, 0, 0
    for u in units:
        lc[u.language] = lc.get(u.language, 0) + 1
        tc[u.unit_type] = tc.get(u.unit_type, 0) + 1
        loc += u.loc; cx += u.complexity
    R.update(lc=lc, tc=tc, loc=loc, cx=round(cx/len(units), 1))
    if cb: cb("embed")
    emb = CodeEmbedder(); sp = SparseVectorGenerator()
    if len(units) > 5: sp.fit(units)
    st.session_state.emb = emb; st.session_state.sp = sp
    if cb: cb("index")
    idx = EndeeIndexer(embedder=emb, sparse_gen=sp); idx.setup_indexes()
    R["ir"] = idx.index_codebase(units); st.session_state.idx = idx
    if cb: cb("health")
    srch = CodeSearcher(embedder=emb, sparse_gen=sp)
    R["health"] = CodeHealthAnalyzer(searcher=srch).analyze_codebase(units)
    st.session_state.health = R["health"]; st.session_state.srch = srch
    if cb: cb("genome")
    try:
        R["evo"] = EvolutionTracker(embedder=emb).get_embedding_projections(units, method="tsne")
        st.session_state.evo = R["evo"]
    except: R["evo"] = None
    if cb: cb("done")
    return R

# ── Endee status check ──
endee_ok = False
try:
    from endee import Endee
    _c = Endee(); _c.set_base_url(f"http://{config.ENDEE_HOST}:{config.ENDEE_PORT}/api/v1")
    _raw = _c.list_indexes()
    _il = _raw.get("indexes", []) if isinstance(_raw, dict) else _raw
    endee_ok = True
except: _il = []

@st.cache_data
def get_video_html(filepath):
    try:
        with open(filepath, "rb") as f:
            data = f.read()
        b64 = base64.b64encode(data).decode()
        return f'<video autoplay loop muted playsinline style="width:100%;height:100%;object-fit:cover;"><source src="data:video/mp4;base64,{b64}" type="video/mp4"></video>'
    except Exception as e:
        return f'<div style="color:red">🎬 Video Error: {e}</div>'

# ═══════════════════════════════════════════════════════════════════
# 1. NAVBAR (Minimal & Sticky)
# ═══════════════════════════════════════════════════════════════════
st.markdown('''<div class="c-navbar">
    <div class="c-logo">
        <span style="font-size:2rem;line-height:1">🧬</span>
        <span>CodeDNA</span>
    </div>
    <div class="c-nav-links">
        <a href="#" class="c-nav-link">Features</a>
        <a href="#" class="c-nav-link">How It Works</a>
        <a href="#" class="c-nav-link">FAQ</a>
    </div>
    <a href="#" class="c-btn c-btn-primary" style="padding:10px 20px">Get Started</a>
</div>''', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# 2. HERO SECTION & 7. DEMO
# ═══════════════════════════════════════════════════════════════════
hc1, hc2 = st.columns([1.1, 1], gap="large")

with hc1:
    st.markdown('''
    <div style="padding: 60px 0 40px 0;">
        <h1 class="c-heading" style="font-size:3.5rem;letter-spacing:-1px;">Understand Any Codebase Without Reading Files</h1>
        <p class="c-text" style="font-size:1.25rem;margin-top:-8px;margin-bottom:32px;">
            Paste a public GitHub repo URL and get instant semantic search, health diagnostics, and a visual 2D codebase genome map.
        </p>
    </div>
    ''', unsafe_allow_html=True)
    
    st.markdown('<p class="c-heading" style="margin-bottom:8px">Try it free right now</p>', unsafe_allow_html=True)
    ri, bi = st.columns([3, 1])
    with ri: repo = st.text_input("repo_input", placeholder="https://github.com/pallets/flask", label_visibility="collapsed")
    with bi: btn = st.button("Analyze Repo", type="primary", use_container_width=True)

with hc2:
    vid_path = os.path.join(os.path.dirname(__file__), "..", "Animation.mp4")
    vid_html = get_video_html(vid_path)
    
    st.markdown(f'''
    <div style="padding: 60px 0 20px 0;">
        <div class="c-mockup">
            <div class="c-mockup-header">
                <div class="c-mockup-dot"></div><div class="c-mockup-dot"></div><div class="c-mockup-dot"></div>
            </div>
            <div class="c-mockup-body">
                {vid_html}
            </div>
        </div>
    </div>
    ''', unsafe_allow_html=True)

# ── Pipeline execution (The Actual Demo Output) ──
if btn and repo:
    st.markdown("---")
    if not endee_ok: st.error("⚡ Endee is offline. Start it: `docker compose up -d`")
    elif "github.com" not in repo: st.error("Please enter a valid GitHub URL.")
    else:
        st.session_state.name = get_name(repo)
        steps = {"clone":"📥 Cloning repository...","parse":"🔍 Parsing source files...",
                    "embed":"🧠 Generating AI embeddings...","index":"📦 Indexing to Endee...",
                    "health":"🏥 Running health diagnostics...","genome":"📈 Building genome map...",
                    "done":"✅ Analysis complete!"}
        keys = list(steps.keys())
        
        with st.status("Initializing CodeDNA Analysis...", expanded=True) as status_box:
            def on_step(s): 
                pct = int(min(keys.index(s)/(len(keys)-1), 1.0) * 100)
                status_box.update(label=f"[{pct}%] {steps[s]}", state="running")
            
            try:
                R = run_pipeline(repo, on_step)
                status_box.update(label="✅ Analysis Complete!", state="complete", expanded=False)
                st.session_state.done = True
                st.success(f"✓ Successfully analyzed **{st.session_state.name}**")
                
                # Show Metrics
                rd = R["health"].to_dict()
                col1, col2, col3, col4, col5 = st.columns(5)
                col1.metric("Code Units", len(R["units"]))
                col2.metric("Lines of Code", f"{R['loc']:,}")
                col3.metric("Languages", len(R["lc"]))
                col4.metric("Health Grade", rd["grade"])
                col5.metric("Health Score", f"{rd['overall_score']}/100")
                
                st.markdown("<br/>", unsafe_allow_html=True)
                t1, t2, t3 = st.tabs(["🔍 Semantic Search Demo", "🏥 Health Diagnostics", "📈 Architecture Map"])
                
                with t1:
                    st.markdown("### Ask questions about the codebase")
                    sq = st.text_input("Search query", placeholder="e.g. How is data saved?", key="sq_hero")
                    if sq:
                        res = st.session_state.srch.hybrid_search(sq, R["units"], top_k=3)
                        for idx_r, r in enumerate(res):
                            with st.expander(f"`{r.unit.name}` (Score: {r.score:.2f})"):
                                st.code(r.unit.content, language=r.unit.language)
                
                with t2:
                    st.markdown("### Anti-Pattern Detections")
                    violations = getattr(R["health"], "violations", [])
                    if not violations:
                        st.success("No major issues detected!")
                    else:
                        for issue in violations:
                            st.warning(f"**{issue.pattern_name}** ({issue.severity}): {issue.description} in `{issue.code_unit_name}`")
                            
                with t3:
                    st.markdown("### Codebase Vector Projection (t-SNE)")
                    st.markdown("Visualising dense AI representations of the repository structurally.")
                    if R.get("evo") and R["evo"].get("points"):
                        import pandas as pd
                        import plotly.express as px
                        df = pd.DataFrame(R["evo"]["points"])
                        fig = px.scatter(
                            df, x="x", y="y", color="type",
                            hover_name="name", hover_data=["file", "complexity"],
                            title="2D Semantic Mapping of Functions/Classes"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No genome map data generated for this repository.")
                
            except Exception as e:
                status_box.update(label=f"❌ Analysis failed: {e}", state="error")
                st.error(f"Analysis failed: {e}")


# ═══════════════════════════════════════════════════════════════════
# 3. SOCIAL PROOF
# ═══════════════════════════════════════════════════════════════════
st.markdown('''
<div class="c-social-proof">
    <p>TRUSTED BY ENGINEERS AT TOP COMPANIES</p>
    <div class="c-social-logos">
        <span class="c-logo-placeholder">ACME CORP</span>
        <span class="c-logo-placeholder">GLOBEX</span>
        <span class="c-logo-placeholder">SOYLENT</span>
        <span class="c-logo-placeholder">VNTR</span>
        <span class="c-logo-placeholder">INITECH</span>
    </div>
</div>
''', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# 4. OLD WAY VS NEW WAY
# ═══════════════════════════════════════════════════════════════════
st.markdown('''
<div class="c-section">
    <div class="c-section-title c-heading">There's a Better Way to Read Code</div>
    <div class="c-compare">
        <div class="c-compare-card c-card-old">
            <h3 class="c-heading">❌ The Old Way</h3>
            <ul class="c-compare-list">
                <li>Endless grep and Ctrl+F manual searching</li>
                <li>Staring at undocumented spaghetti legacy code</li>
                <li>Guessing architectural impacts of changes</li>
                <li>Spending hours onboarding to new repositories</li>
            </ul>
        </div>
        <div class="c-compare-card c-card-new">
            <h3 class="c-heading">✅ CodeDNA</h3>
            <ul class="c-compare-list">
                <li>Search codebase by semantic meaning instantly</li>
                <li>Automated anti-pattern and health diagnostics</li>
                <li>Visual vector projection of the entire architecture</li>
                <li>Understand massive repos in under 60 seconds</li>
            </ul>
        </div>
    </div>
</div>
''', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# 5. BENEFITS SECTION
# ═══════════════════════════════════════════════════════════════════
st.markdown('''
<div class="c-section" style="background:var(--bg); margin:0 -2.5rem; padding:80px 2.5rem;">
    <div class="c-section-title c-heading">Why You'll Love CodeDNA</div>
    <div class="c-benefits">
        <div class="c-benefit-card">
            <div class="c-benefit-icon">🧠</div>
            <div class="c-benefit-title">Semantic Retrieval</div>
            <div class="c-benefit-desc">No more regex. Ask "where is authentication handled?" and get exact matches using advanced sentence-transformer vectors.</div>
        </div>
        <div class="c-benefit-card">
            <div class="c-benefit-icon">🏥</div>
            <div class="c-benefit-title">Instant Health Grading</div>
            <div class="c-benefit-desc">Detect code smells, monolithic functions, and poor documentation instantly through vector similarity anti-patterns.</div>
        </div>
        <div class="c-benefit-card">
            <div class="c-benefit-icon">🌐</div>
            <div class="c-benefit-title">Cross-Language Support</div>
            <div class="c-benefit-desc">Write in Python, JS/TS, or Java? Our AST engine normalizes logic across languages natively.</div>
        </div>
    </div>
</div>
''', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# 6. HOW IT WORKS
# ═══════════════════════════════════════════════════════════════════
st.markdown('''
<div class="c-section">
    <div class="c-section-title c-heading">How It Works</div>
    <div class="c-steps">
        <div class="c-step">
            <div class="c-step-num c-heading">1</div>
            <div class="c-step-title">Clone & Parse</div>
            <div class="c-step-desc">Provide a GitHub URL. We clone it locally and extract functions and classes via Tree-Sitter AST.</div>
        </div>
        <div class="c-step">
            <div class="c-step-num c-heading">2</div>
            <div class="c-step-title">Embed & Index</div>
            <div class="c-step-desc">AI generates 384-dimensional dense vectors and TF-IDF spare vectors, indexing them directly into Endee DB.</div>
        </div>
        <div class="c-step">
            <div class="c-step-num c-heading">3</div>
            <div class="c-step-title">Query & Visualize</div>
            <div class="c-step-desc">Instantly query the DB for meaning, generate health reports, and explore 2D t-SNE visual projections.</div>
        </div>
    </div>
</div>
''', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# 9. FAQ SECTION
# ═══════════════════════════════════════════════════════════════════
st.markdown('<div class="c-section"><div class="c-section-title c-heading">Frequently Asked Questions</div>', unsafe_allow_html=True)
for q, a in [
    ("Is this right for me?", "If you regularly join new projects or deal with large undocumented codebases, CodeDNA will save you hours of tracing function calls."),
    ("How long does it take?", "Parsing and embedding takes about 30 seconds for a small repo (under 100 files) and a few minutes for massive codebases."),
    ("Do I need experience?", "No experience needed! Paste a URL, and we abstract away the embeddings, vector database, and search mechanics."),
    ("Is my code stored on your servers?", "No. CodeDNA clones locally and uses a local Endee Vector DB. Your proprietary code never leaves your infrastructure."),
    ("Can I integrate it?", "Absolutely. CodeDNA is completely open-source and built on Endee, making it easy to fork and integrate into CI/CD pipelines."),
]:
    with st.expander(q): st.write(a)
st.markdown('</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# 10. FINAL CTA SECTION
# ═══════════════════════════════════════════════════════════════════
st.markdown('''
<div class="c-final-cta">
    <h2 class="c-heading">Ready to Master Your Codebase?</h2>
    <p class="c-font">Stop guessing. Start analyzing. Paste your first repository below and see the magic in 60 seconds.</p>
    <a href="#" class="c-btn c-btn-white">Start Your Free Trial</a>
</div>
''', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# 11. FOOTER
# ═══════════════════════════════════════════════════════════════════
st.markdown(f'''
<div class="c-footer">
    <div>
        <span class="c-heading" style="font-size:1.2rem;color:var(--text-main);margin-right:8px;">🧬 CodeDNA</span>
        <span>© 2026. All rights reserved.</span>
    </div>
    <div class="c-footer-links">
        <a href="#">Privacy Policy</a>
        <a href="#">Terms of Service</a>
        <a href="https://github.com/thevikramrajput/endee">GitHub</a>
        <a href="#">Contact</a>
    </div>
</div>
''', unsafe_allow_html=True)
