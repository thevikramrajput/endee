"""
CodeDNA — AI-Powered Codebase Genome Analyzer
Premium SaaS Frontend
"""
import streamlit as st
import os, sys, time, shutil, tempfile, hashlib, stat

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config
from app.styles import CSS

# ── Page Config ──
st.set_page_config(page_title="CodeDNA — Codebase Genome Analyzer", page_icon="🧬",
                   layout="wide", initial_sidebar_state="collapsed")
st.markdown(CSS, unsafe_allow_html=True)

# ── Session State ──
for k, v in {"done": False, "units": [], "health": None, "evo": None,
             "url": "", "name": "", "emb": None, "sp": None, "idx": None, "srch": None}.items():
    if k not in st.session_state: st.session_state[k] = v


# ═══════════════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════════════
def clone_repo(url):
    def rm_ro(fn, p, _): os.chmod(p, stat.S_IWRITE); fn(p)
    h = hashlib.md5(url.encode()).hexdigest()[:10]
    d = os.path.join(tempfile.gettempdir(), f"codedna_{h}")
    if os.path.exists(d): shutil.rmtree(d, onerror=rm_ro)
    os.makedirs(d, exist_ok=True)
    if os.system(f'git clone --depth=1 "{url}" "{d}"') != 0:
        raise RuntimeError(f"Clone failed: {url}")
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
    from core.analyzer import CodeHealthAnalyzer
    R["health"] = CodeHealthAnalyzer(searcher=srch).analyze_codebase(units)
    st.session_state.health = R["health"]; st.session_state.srch = srch
    if cb: cb("genome")
    try:
        R["evo"] = EvolutionTracker(embedder=emb).get_embedding_projections(units, method="tsne")
        st.session_state.evo = R["evo"]
    except: R["evo"] = None
    if cb: cb("done")
    return R


# ═══════════════════════════════════════════════════════════════════
#  SIDEBAR
# ═══════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown('<div class="nav-brand"><span class="icon">🧬</span>'
                '<span class="name">CodeDNA</span>'
                '<span class="badge">v1.0</span></div>', unsafe_allow_html=True)
    st.caption("AI-Powered Codebase Analyzer")
    st.markdown('<div class="div"></div>', unsafe_allow_html=True)
    endee_ok = False
    try:
        from endee import Endee
        c = Endee(); c.set_base_url(f"http://{config.ENDEE_HOST}:{config.ENDEE_PORT}/api/v1")
        raw = c.list_indexes()
        il = raw.get("indexes", []) if isinstance(raw, dict) else raw
        endee_ok = True
        st.markdown(f'<span class="dot dot-g"></span>'
                    f'<span style="color:#a1a1aa;font-size:.84rem">Endee online · {len(il)} indexes</span>',
                    unsafe_allow_html=True)
    except:
        st.markdown('<span class="dot dot-r"></span>'
                    '<span style="color:#52525b;font-size:.84rem">Endee offline</span>',
                    unsafe_allow_html=True)
    st.markdown('<div class="div"></div>', unsafe_allow_html=True)
    pages = ["🏠 Home", "⚙️ About"]
    if st.session_state.done:
        pages = ["🏠 Home", "🔍 Search", "🏥 Health", "📈 Genome", "⚙️ About"]
    page = st.radio("", pages, label_visibility="collapsed")
    st.markdown('<div class="div"></div>', unsafe_allow_html=True)
    st.markdown('<div class="tags">'
                '<span class="tag tag-v">Endee</span>'
                '<span class="tag tag-c">AI</span>'
                '<span class="tag tag-e">Streamlit</span>'
                '<span class="tag tag-a">Plotly</span></div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
#  HOME
# ═══════════════════════════════════════════════════════════════════
if page == "🏠 Home":
    # ── Navbar ──
    st.markdown(
        '<div class="navbar">'
        '<div class="nav-brand"><span class="icon">🧬</span><span class="name">CodeDNA</span></div>'
        '<div class="nav-links">'
        '<span class="nav-link">Features</span>'
        '<span class="nav-link">How It Works</span>'
        '<span class="nav-link">FAQ</span>'
        '</div></div>', unsafe_allow_html=True)

    # ── Hero ──
    st.markdown(
        '<div class="hero">'
        '<div class="hero-eyebrow">✦ Open Source · Powered by Endee Vector DB</div>'
        '<h1>Understand Your<br>Codebase <span class="accent">DNA</span></h1>'
        '<p>Paste a public GitHub repo — get instant semantic search, health diagnostics, '
        'and genome visualization. No setup required.</p>'
        '</div>', unsafe_allow_html=True)

    st.markdown('<div class="tags">'
                '<span class="tag tag-v">🔍 Semantic Search</span>'
                '<span class="tag tag-c">🧪 Hybrid Search</span>'
                '<span class="tag tag-e">🏥 Health Score</span>'
                '<span class="tag tag-a">📈 Genome Map</span></div>', unsafe_allow_html=True)

    # ── Try It Live ──
    st.markdown('<div class="sec-header"><h2>Try It Live</h2>'
                '<p>Paste any public repo URL and hit Analyze</p></div>', unsafe_allow_html=True)

    st.markdown('<div class="input-label">REPOSITORY URL</div>', unsafe_allow_html=True)
    ci, cb = st.columns([5, 1])
    with ci:
        repo = st.text_input("r", placeholder="https://github.com/pallets/flask",
                             label_visibility="collapsed", key="repo_input")
    with cb:
        go = st.button("Analyze →", type="primary", use_container_width=True)

    st.markdown('<div class="input-label" style="margin-top:12px">QUICK START</div>', unsafe_allow_html=True)
    qc = st.columns(4)
    for i, (n, u) in enumerate([("Flask", "https://github.com/pallets/flask"),
                                 ("FastAPI", "https://github.com/tiangolo/fastapi"),
                                 ("Requests", "https://github.com/psf/requests"),
                                 ("Express", "https://github.com/expressjs/express")]):
        with qc[i]:
            if st.button(n, key=f"q{i}", use_container_width=True):
                st.session_state.repo_input = u; repo = u; go = True

    st.markdown('<div class="div-accent"></div>', unsafe_allow_html=True)

    # ── Run Pipeline ──
    if go and repo:
        if not endee_ok:
            st.error("⚡ Endee is offline. Run `docker compose up -d`")
        elif "github.com" not in repo:
            st.error("Please enter a valid GitHub URL.")
        else:
            st.session_state.name = get_name(repo); st.session_state.url = repo
            steps = {"clone": "📥 Cloning repo", "parse": "🔍 Parsing code", "embed": "🧠 Generating embeddings",
                     "index": "📦 Indexing to Endee", "health": "🏥 Health analysis",
                     "genome": "📈 Genome map", "done": "✅ Done"}
            keys = list(steps.keys())
            bar = st.progress(0); status = st.empty()
            def on(s):
                bar.progress(min(keys.index(s) / (len(keys)-1), 1.0))
                status.markdown(f"**{steps[s]}**")
            try:
                R = run_pipeline(repo, on)
                bar.progress(1.0); status.empty(); st.session_state.done = True
                rd = R["health"].to_dict(); g = rd["grade"]
                st.markdown(f'<div style="background:#10b98108;border:1px solid #10b98125;border-radius:10px;'
                            f'padding:14px 20px;color:#6ee7b7;font-weight:500;animation:fadeUp .5s">'
                            f'✓ Analyzed <strong>{st.session_state.name}</strong></div>', unsafe_allow_html=True)
                st.markdown(f'<div class="stats-grid" style="margin-top:16px">'
                    f'<div class="stat-card"><div class="stat-val">{len(R["units"])}</div><div class="stat-lbl">Units</div></div>'
                    f'<div class="stat-card"><div class="stat-val">{R["loc"]:,}</div><div class="stat-lbl">LOC</div></div>'
                    f'<div class="stat-card"><div class="stat-val">{len(R["lc"])}</div><div class="stat-lbl">Languages</div></div>'
                    f'<div class="stat-card"><div class="grade-ring grade-{g}" style="margin:0 auto">{g}</div><div class="stat-lbl">Grade</div></div>'
                    f'<div class="stat-card"><div class="stat-val">{rd["overall_score"]}</div><div class="stat-lbl">Score</div></div>'
                    f'</div>', unsafe_allow_html=True)
                st.info("👈 Open sidebar → explore **Search**, **Health**, and **Genome Map**")
            except Exception as e:
                bar.empty(); status.empty()
                st.error(f"Failed: {e}")
                st.caption("Check: valid public repo? Endee running? Git installed?")

    elif st.session_state.done:
        st.markdown(f'<div style="background:#7c3aed08;border:1px solid #7c3aed20;border-radius:10px;'
                    f'padding:14px 20px;color:#c4b5fd;font-weight:500">'
                    f'✦ Last: <strong>{st.session_state.name}</strong> — open sidebar for results</div>',
                    unsafe_allow_html=True)

    # ── Features ──
    st.markdown('<div class="sec-header"><h2>Why CodeDNA?</h2>'
                '<p>Everything you need to understand a codebase at the vector level</p></div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="feat-grid">'
        '<div class="feat-card"><span class="feat-icon">🔍</span>'
        '<div class="feat-title">Semantic Search</div>'
        '<div class="feat-desc">Find code by meaning. Ask "error handling middleware" and get exact matches — no regex needed.</div></div>'
        '<div class="feat-card"><span class="feat-icon">🧪</span>'
        '<div class="feat-title">Hybrid Search</div>'
        '<div class="feat-desc">Combines dense vectors + TF-IDF sparse vectors for precision meets recall. Best of both worlds.</div></div>'
        '<div class="feat-card"><span class="feat-icon">🏥</span>'
        '<div class="feat-title">Health Diagnostics</div>'
        '<div class="feat-desc">Anti-pattern detection powered by vector similarity. Get grades, violations, and fix suggestions.</div></div>'
        '<div class="feat-card"><span class="feat-icon">📈</span>'
        '<div class="feat-title">Genome Visualization</div>'
        '<div class="feat-desc">t-SNE projection of your entire codebase. See clusters, outliers, and architecture patterns.</div></div>'
        '<div class="feat-card"><span class="feat-icon">⚡</span>'
        '<div class="feat-title">Endee Vector DB</div>'
        '<div class="feat-desc">Built on Endee with 3 index types, multi-precision storage, and blazing fast similarity queries.</div></div>'
        '<div class="feat-card"><span class="feat-icon">🌐</span>'
        '<div class="feat-title">Multi-Language</div>'
        '<div class="feat-desc">Parse Python, JavaScript, and Java. Cross-language search finds similar logic across all three.</div></div>'
        '</div>', unsafe_allow_html=True)

    # ── How It Works ──
    st.markdown('<div class="sec-header"><h2>How It Works</h2>'
                '<p>Four steps from URL to insights</p></div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="steps-row">'
        '<div class="step-card"><div class="step-num">1</div>'
        '<div class="step-title">Clone</div>'
        '<div class="step-desc">We clone the public repo to a temp directory</div></div>'
        '<div class="step-card"><div class="step-num">2</div>'
        '<div class="step-title">Parse & Embed</div>'
        '<div class="step-desc">AST parsing → 384-dim vectors via sentence-transformers</div></div>'
        '<div class="step-card"><div class="step-num">3</div>'
        '<div class="step-title">Index</div>'
        '<div class="step-desc">Vectors stored in Endee with dense, hybrid & pattern indexes</div></div>'
        '<div class="step-card"><div class="step-num">4</div>'
        '<div class="step-title">Analyze</div>'
        '<div class="step-desc">Health scoring, genome mapping, and search — all instant</div></div>'
        '</div>', unsafe_allow_html=True)

    # ── FAQ ──
    st.markdown('<div class="sec-header"><h2>FAQ</h2></div>', unsafe_allow_html=True)
    faq = [("Is this beginner friendly?", "Yes! Just paste a GitHub URL and click Analyze."),
           ("How accurate is the health scoring?", "It uses vector similarity against 10 curated anti-patterns plus heuristic rules for complexity, documentation, and function length."),
           ("What languages are supported?", "Python, JavaScript, and Java. We use AST parsing for accurate code unit extraction."),
           ("Is my code stored anywhere?", "No. Repos are cloned to a temp directory and vectors are stored locally in your Endee instance."),
           ("How fast is the analysis?", "Small repos (<100 files): ~30 seconds. Larger repos may take 1-2 minutes for embedding generation.")]
    for q, a in faq:
        with st.expander(q): st.write(a)

    # ── CTA ──
    st.markdown(
        '<div class="cta-banner">'
        '<h2>Ready to decode your codebase?</h2>'
        '<p>Scroll up, paste a repo, and let CodeDNA do the rest.</p>'
        '</div>', unsafe_allow_html=True)

    # ── Footer ──
    st.markdown(
        f'<div class="footer">'
        f'<strong>CodeDNA</strong> v{config.APP_VERSION} · Built with '
        f'<a href="https://github.com/endee-ai/endee">Endee Vector DB</a><br>'
        f'<a href="https://github.com/thevikramrajput/endee">GitHub</a> · '
        f'© 2026 CodeDNA. Open Source.'
        f'</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
#  SEARCH
# ═══════════════════════════════════════════════════════════════════
elif page == "🔍 Search":
    st.markdown(f'<div class="sec-left"><h2>🔍 Semantic Search</h2>'
                f'<span class="subtitle">Search <code>{st.session_state.name}</code> by meaning</span></div>',
                unsafe_allow_html=True)
    mode = st.radio("", ["Dense", "Hybrid", "Similar Code"], horizontal=True, label_visibility="collapsed")
    if mode == "Similar Code":
        q = st.text_area("Code:", height=140, placeholder="def fibonacci(n):\n    ...")
    else:
        q = st.text_input("Query", placeholder='"function that validates email"')
    with st.expander("⚙ Filters"):
        f1, f2, f3 = st.columns(3)
        lf = f1.selectbox("Language", [None, "python", "javascript", "java"])
        tf = f2.selectbox("Type", [None, "function", "class", "module"])
        tk = f3.slider("Results", 1, 30, 10)
    if st.button("Search →", type="primary", use_container_width=True):
        if not q: st.warning("Enter a query.")
        elif not st.session_state.srch: st.error("Analyze a repo first.")
        else:
            with st.spinner("Searching..."):
                try:
                    s = st.session_state.srch
                    r = (s.search_dense(q, tk, lf, tf) if mode == "Dense" else
                         s.search_hybrid(q, tk, lf, tf) if mode == "Hybrid" else
                         s.find_similar_code(q, tk))
                    if r:
                        st.markdown(f'<div style="color:#6ee7b7;font-weight:500;margin:12px 0">{len(r)} results</div>',
                                    unsafe_allow_html=True)
                        for i, x in enumerate(r):
                            m = x.metadata; sp = min(x.similarity * 100, 100)
                            with st.expander(f"**{m.get('name','?')}** · `{m.get('language','?')}` · {sp:.0f}%", expanded=i < 3):
                                c1, c2, c3, c4 = st.columns(4)
                                c1.metric("Lang", m.get("language", "?")); c2.metric("Type", m.get("unit_type", "?"))
                                c3.metric("LOC", m.get("loc", "?")); c4.metric("Complexity", m.get("complexity", "?"))
                                st.progress(min(x.similarity, 1.0))
                    else: st.info("No results.")
                except Exception as e: st.error(f"Error: {e}")


# ═══════════════════════════════════════════════════════════════════
#  HEALTH
# ═══════════════════════════════════════════════════════════════════
elif page == "🏥 Health":
    st.markdown(f'<div class="sec-left"><h2>🏥 Health Report</h2>'
                f'<span class="subtitle">Anti-pattern analysis for <code>{st.session_state.name}</code></span></div>',
                unsafe_allow_html=True)
    rp = st.session_state.health
    if not rp: st.warning("Analyze a repo first.")
    else:
        rd = rp.to_dict(); g = rd["grade"]
        g1, g2, g3, g4 = st.columns(4)
        with g1:
            st.markdown(f'<div style="text-align:center"><div class="grade-ring grade-{g}">{g}</div>'
                        f'<div class="stat-lbl" style="margin-top:10px">Grade</div></div>', unsafe_allow_html=True)
        g2.metric("Score", f"{rd['overall_score']}/100")
        g3.metric("Violations", rd["total_violations"])
        g4.metric("Units", rd["total_units_analyzed"])
        st.markdown('<div class="div"></div>', unsafe_allow_html=True)
        m = rd["metrics"]; mc = st.columns(5)
        mc[0].metric("LOC", f"{m['total_loc']:,}"); mc[1].metric("Avg Cx", m["avg_complexity"])
        mc[2].metric("Doc%", f"{m['documentation_ratio']}%"); mc[3].metric("Funcs", m["function_count"])
        mc[4].metric("Classes", m["class_count"])
        st.markdown('<div class="div"></div>', unsafe_allow_html=True)
        if rp.violations:
            import plotly.express as px, pandas as pd
            ch1, ch2 = st.columns(2)
            with ch1:
                sv = pd.DataFrame({"Sev": ["Critical","High","Medium","Low"],
                    "N": [rd["critical_violations"],rd["high_violations"],rd["medium_violations"],rd["low_violations"]]})
                fig = px.pie(sv, names="Sev", values="N", hole=.55, color="Sev",
                    color_discrete_map={"Critical":"#ef4444","High":"#f97316","Medium":"#eab308","Low":"#3b82f6"})
                fig.update_layout(plot_bgcolor="rgba(0,0,0,0)",paper_bgcolor="rgba(0,0,0,0)",
                    font_color="#a1a1aa",height=300,margin=dict(t=20,b=0))
                st.plotly_chart(fig, use_container_width=True)
            with ch2:
                cats = {}
                for v in rp.violations:
                    ct = getattr(v, "category", "general"); cats[ct] = cats.get(ct, 0) + 1
                if cats:
                    cdf = pd.DataFrame(list(cats.items()), columns=["Cat","N"])
                    f2 = px.bar(cdf, x="Cat", y="N", color="N", color_continuous_scale=["#7c3aed","#a78bfa"])
                    f2.update_layout(plot_bgcolor="rgba(0,0,0,0)",paper_bgcolor="rgba(0,0,0,0)",
                        font_color="#a1a1aa",showlegend=False,height=300,margin=dict(t=20,b=0))
                    st.plotly_chart(f2, use_container_width=True)
            st.markdown("### Violations")
            for v in rp.violations[:20]:
                with st.expander(f"**{v.pattern_name}** → {v.code_unit_name}"):
                    st.caption(f"{v.severity.upper()} · {v.code_unit_file}")
                    st.write(v.description); st.write(f"**Fix:** {v.suggestion}")
        else:
            st.markdown('<div style="text-align:center;padding:40px;color:#6ee7b7">✦ Clean codebase!</div>',
                        unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
#  GENOME
# ═══════════════════════════════════════════════════════════════════
elif page == "📈 Genome":
    st.markdown(f'<div class="sec-left"><h2>📈 Code Genome</h2>'
                f'<span class="subtitle">t-SNE projection of <code>{st.session_state.name}</code></span></div>',
                unsafe_allow_html=True)
    pr = st.session_state.evo
    if not pr: st.warning("Not available.")
    else:
        import plotly.express as px, pandas as pd
        df = pd.DataFrame(pr["points"])
        fig = px.scatter(df, x="x", y="y", color="language", symbol="type", size="complexity",
            hover_name="name", hover_data=["file","loc"],
            color_discrete_map={"python":"#7c3aed","javascript":"#eab308","java":"#ef4444"})
        fig.update_layout(plot_bgcolor="#0a0a0f",paper_bgcolor="rgba(0,0,0,0)",font_color="#a1a1aa",
            height=550,margin=dict(t=10,b=10),
            xaxis=dict(showgrid=False,zeroline=False,title="",showticklabels=False),
            yaxis=dict(showgrid=False,zeroline=False,title="",showticklabels=False))
        fig.update_traces(marker=dict(line=dict(width=.5,color="#27272a"),opacity=.85))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('<div class="div"></div>', unsafe_allow_html=True)
        gs = st.columns(4)
        gs[0].metric("Units", len(df)); gs[1].metric("Languages", df["language"].nunique())
        gs[2].metric("Avg Cx", round(df["complexity"].mean(), 1)); gs[3].metric("LOC", int(df["loc"].sum()))


# ═══════════════════════════════════════════════════════════════════
#  ABOUT
# ═══════════════════════════════════════════════════════════════════
elif page == "⚙️ About":
    st.markdown('<div class="sec-left"><h2>⚙️ About CodeDNA</h2></div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="glass" style="margin-bottom:16px">'
        '<h3 style="color:#e4e4e7;margin:0 0 8px">What is CodeDNA?</h3>'
        '<p style="color:#71717a;line-height:1.6;margin:0">An AI-powered codebase genome analyzer built on Endee. '
        'Parses code into units, converts to 384-dim vectors, and uses semantic search + health diagnostics '
        'to give you deep insights no grep can match.</p></div>', unsafe_allow_html=True)
    a1, a2 = st.columns(2)
    with a1:
        st.markdown(
            '<div class="glass"><h3 style="color:#e4e4e7;margin:0 0 8px">🔋 Endee Features</h3>'
            '<p style="color:#71717a;line-height:1.7;margin:0">'
            '• Dense Index (FLOAT16)<br>• Hybrid Index (dense+sparse)<br>'
            '• Anti-Pattern Index (FLOAT32)<br>• $eq, $range filters<br>'
            '• Bulk upsert · Python SDK</p></div>', unsafe_allow_html=True)
    with a2:
        st.markdown(
            '<div class="glass"><h3 style="color:#e4e4e7;margin:0 0 8px">🛠 Stack</h3>'
            '<p style="color:#71717a;line-height:1.7;margin:0">'
            '• Endee Vector DB (Docker)<br>• Python 3.10+<br>'
            '• sentence-transformers<br>• scikit-learn (TF-IDF)<br>'
            '• Streamlit · Plotly</p></div>', unsafe_allow_html=True)
    st.markdown('<div class="div"></div>', unsafe_allow_html=True)
    st.markdown("### Active Indexes")
    try:
        from endee import Endee; c = Endee()
        c.set_base_url(f"http://{config.ENDEE_HOST}:{config.ENDEE_PORT}/api/v1")
        raw = c.list_indexes(); il = raw.get("indexes", []) if isinstance(raw, dict) else raw
        if il:
            import pandas as pd
            st.dataframe(pd.DataFrame([{"Name":i.get("name"),"Dim":i.get("dimension"),"Space":i.get("space_type")} for i in il]),
                         use_container_width=True, hide_index=True)
        else: st.caption("No indexes yet.")
    except Exception as e: st.caption(f"Offline: {e}")
    st.markdown(f'<div class="footer"><strong>CodeDNA</strong> v{config.APP_VERSION} · '
                f'<a href="https://github.com/thevikramrajput/endee">GitHub</a> · © 2026</div>',
                unsafe_allow_html=True)
