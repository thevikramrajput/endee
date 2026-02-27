"""
CodeDNA — AI-Powered Codebase Genome Analyzer
===============================================
One-click codebase analysis. Paste a GitHub repo URL → get instant insights.
"""

import streamlit as st
import os
import sys
import time
import shutil
import tempfile
import hashlib
import stat

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config

# ─── Page Config ─────────────────────────────────────────────────────
st.set_page_config(
    page_title="CodeDNA — Codebase Genome Analyzer",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Design System CSS ──────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap');

    /* ── Reset & Base ── */
    html, body, [class*="css"] { font-family: 'Inter', -apple-system, sans-serif; }
    .main .block-container { padding-top: 1rem; max-width: 1300px; }
    [data-testid="stSidebar"] { background: #0a0a0f; border-right: 1px solid #1a1a2a; }
    .stApp { background: #08080d; }

    /* ── Animated DNA Brand ── */
    @keyframes dna-spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    @keyframes pulse-glow {
        0%, 100% { opacity: 0.6; }
        50% { opacity: 1; }
    }
    @keyframes slide-up {
        from { opacity: 0; transform: translateY(12px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-6px); }
    }
    @keyframes typing {
        from { width: 0; }
        to { width: 100%; }
    }
    @keyframes blink {
        50% { border-color: transparent; }
    }
    @keyframes count-up {
        from { opacity: 0; transform: scale(0.5); }
        to { opacity: 1; transform: scale(1); }
    }
    @keyframes shimmer {
        0% { background-position: -200% 0; }
        100% { background-position: 200% 0; }
    }
    @keyframes border-dance {
        0% { border-color: #2a2a3a; }
        50% { border-color: #7c3aed; }
        100% { border-color: #2a2a3a; }
    }

    /* ── Logo ── */
    .dna-logo {
        display: inline-flex;
        align-items: center;
        gap: 10px;
        animation: slide-up 0.6s ease-out;
    }
    .dna-icon {
        font-size: 1.6rem;
        animation: float 3s ease-in-out infinite;
    }
    .dna-text {
        font-size: 1.1rem;
        font-weight: 700;
        color: #e4e4e7;
        letter-spacing: -0.5px;
    }

    /* ── Hero Section ── */
    .hero {
        animation: slide-up 0.5s ease-out;
        margin-bottom: 1rem;
    }
    .hero-badge {
        display: inline-block;
        background: #18181b;
        color: #a1a1aa;
        font-size: 0.75rem;
        font-weight: 500;
        padding: 4px 12px;
        border-radius: 100px;
        border: 1px solid #27272a;
        margin-bottom: 16px;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }
    .hero h1 {
        font-size: 3rem;
        font-weight: 900;
        color: #fafafa;
        letter-spacing: -2px;
        line-height: 1;
        margin: 0 0 12px 0;
    }
    .hero h1 .accent { color: #7c3aed; }
    .hero p {
        font-size: 1.1rem;
        color: #71717a;
        font-weight: 400;
        line-height: 1.5;
        max-width: 600px;
    }

    /* ── Input Area ── */
    .input-section {
        background: #0f0f14;
        border: 1px solid #1c1c28;
        border-radius: 12px;
        padding: 24px;
        margin: 20px 0;
        animation: slide-up 0.7s ease-out;
        transition: border-color 0.3s ease;
    }
    .input-section:hover { border-color: #7c3aed40; }
    .input-label {
        font-size: 0.8rem;
        color: #71717a;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 600;
        margin-bottom: 10px;
    }

    /* ── Example Chips ── */
    .chip-row { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 14px; }
    .chip {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: #18181b;
        color: #a1a1aa;
        font-size: 0.8rem;
        font-weight: 500;
        padding: 6px 14px;
        border-radius: 8px;
        border: 1px solid #27272a;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    .chip:hover {
        border-color: #7c3aed;
        color: #e4e4e7;
        background: #1a1a24;
    }

    /* ── Feature Tags ── */
    .tags { display: flex; gap: 8px; flex-wrap: wrap; margin: 16px 0; animation: slide-up 0.8s ease-out; }
    .tag {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        font-size: 0.78rem;
        font-weight: 500;
        padding: 5px 12px;
        border-radius: 6px;
        border: 1px solid;
    }
    .tag-violet { color: #a78bfa; border-color: #7c3aed30; background: #7c3aed10; }
    .tag-cyan { color: #67e8f9; border-color: #06b6d430; background: #06b6d410; }
    .tag-emerald { color: #6ee7b7; border-color: #10b98130; background: #10b98110; }
    .tag-amber { color: #fbbf24; border-color: #f59e0b30; background: #f59e0b10; }

    /* ── Stat Cards ── */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
        gap: 12px;
        animation: slide-up 0.6s ease-out;
    }
    .stat-card {
        background: #0f0f14;
        border: 1px solid #1c1c28;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        transition: all 0.25s ease;
        animation: count-up 0.5s ease-out;
    }
    .stat-card:hover {
        border-color: #7c3aed50;
        transform: translateY(-2px);
    }
    .stat-value {
        font-size: 2rem;
        font-weight: 800;
        color: #fafafa;
        letter-spacing: -1px;
        font-family: 'JetBrains Mono', monospace;
    }
    .stat-label {
        font-size: 0.7rem;
        color: #52525b;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        font-weight: 600;
        margin-top: 6px;
    }

    /* ── Grade Circle ── */
    .grade-ring {
        width: 72px;
        height: 72px;
        border-radius: 50%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 2rem;
        font-weight: 900;
        font-family: 'JetBrains Mono', monospace;
        border: 3px solid;
        animation: count-up 0.6s ease-out;
    }
    .grade-A { border-color: #10b981; color: #10b981; background: #10b98110; }
    .grade-B { border-color: #3b82f6; color: #3b82f6; background: #3b82f610; }
    .grade-C { border-color: #f59e0b; color: #f59e0b; background: #f59e0b10; }
    .grade-D { border-color: #ef4444; color: #ef4444; background: #ef444410; }
    .grade-F { border-color: #dc2626; color: #dc2626; background: #dc262610; }

    /* ── Pipeline Steps ── */
    .pipeline-step {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 10px 16px;
        border-radius: 8px;
        font-size: 0.88rem;
        color: #a1a1aa;
        margin-bottom: 4px;
        transition: all 0.3s ease;
    }
    .pipeline-step.active {
        background: #7c3aed10;
        color: #c4b5fd;
        border-left: 2px solid #7c3aed;
    }
    .pipeline-step.done {
        color: #6ee7b7;
    }
    .step-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #3f3f46;
        flex-shrink: 0;
    }
    .step-dot.active { background: #7c3aed; animation: pulse-glow 1.5s infinite; }
    .step-dot.done { background: #10b981; }

    /* ── Sidebar Status ── */
    .status-dot {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        margin-right: 6px;
    }
    .dot-green { background: #10b981; box-shadow: 0 0 6px #10b98180; }
    .dot-red { background: #ef4444; box-shadow: 0 0 6px #ef444480; }

    /* ── Sidebar Nav ── */
    .nav-item {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 8px 12px;
        border-radius: 8px;
        color: #71717a;
        font-weight: 500;
        font-size: 0.88rem;
        margin-bottom: 2px;
        transition: all 0.2s ease;
        cursor: pointer;
    }
    .nav-item:hover { background: #18181b; color: #e4e4e7; }
    .nav-item.active { background: #7c3aed15; color: #c4b5fd; border-left: 2px solid #7c3aed; }

    /* ── Section Headers ── */
    .section-header {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 20px;
        animation: slide-up 0.5s ease-out;
    }
    .section-header h2 {
        font-size: 1.5rem;
        font-weight: 700;
        color: #fafafa;
        letter-spacing: -0.5px;
        margin: 0;
    }
    .section-header .subtitle {
        font-size: 0.9rem;
        color: #52525b;
        margin-top: 4px;
    }

    /* ── Dividers ── */
    .divider {
        height: 1px;
        background: #1c1c28;
        margin: 20px 0;
    }

    /* ── Code Block Style ── */
    .code-block {
        background: #0f0f14;
        border: 1px solid #1c1c28;
        border-radius: 8px;
        padding: 14px 18px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.82rem;
        color: #a1a1aa;
        overflow-x: auto;
    }

    /* ── Violation Card ── */
    .violation-card {
        background: #0f0f14;
        border: 1px solid #1c1c28;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 8px;
        transition: all 0.2s ease;
    }
    .violation-card:hover { border-color: #27272a; }
    .severity-dot {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 8px;
    }
    .sev-critical { background: #ef4444; }
    .sev-high { background: #f97316; }
    .sev-medium { background: #eab308; }
    .sev-low { background: #3b82f6; }

    /* ── Search Bar ── */
    .search-mode-btn {
        padding: 6px 16px;
        border-radius: 6px;
        font-size: 0.82rem;
        font-weight: 500;
        border: 1px solid #27272a;
        color: #71717a;
        background: transparent;
        cursor: pointer;
        transition: all 0.2s;
    }
    .search-mode-btn.active {
        background: #7c3aed;
        color: white;
        border-color: #7c3aed;
    }

    /* ── About Section ── */
    .about-card {
        background: #0f0f14;
        border: 1px solid #1c1c28;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 12px;
    }
    .about-card h3 {
        font-size: 1rem;
        font-weight: 600;
        color: #e4e4e7;
        margin: 0 0 8px 0;
    }
    .about-card p {
        font-size: 0.88rem;
        color: #71717a;
        line-height: 1.6;
    }

    /* ── Streamlit overrides ── */
    .stProgress > div > div > div > div { background: #7c3aed !important; }
    div[data-testid="stMetricValue"] { font-family: 'JetBrains Mono', monospace; }
    .stButton > button[kind="primary"] {
        background: #7c3aed !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.2s !important;
    }
    .stButton > button[kind="primary"]:hover {
        background: #6d28d9 !important;
        transform: translateY(-1px) !important;
    }
    .stButton > button {
        border-radius: 8px !important;
        border: 1px solid #27272a !important;
        background: #18181b !important;
        color: #a1a1aa !important;
        font-weight: 500 !important;
        transition: all 0.2s !important;
    }
    .stButton > button:hover {
        border-color: #7c3aed60 !important;
        color: #e4e4e7 !important;
    }
    .stTextInput > div > div > input {
        background: #18181b !important;
        border: 1px solid #27272a !important;
        border-radius: 8px !important;
        color: #e4e4e7 !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.9rem !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #7c3aed !important;
        box-shadow: 0 0 0 1px #7c3aed40 !important;
    }
    .stTextArea > div > div > textarea {
        background: #18181b !important;
        border: 1px solid #27272a !important;
        border-radius: 8px !important;
        color: #e4e4e7 !important;
        font-family: 'JetBrains Mono', monospace !important;
    }
    .stSelectbox > div > div { background: #18181b !important; }
    div[data-testid="stExpander"] {
        background: #0f0f14;
        border: 1px solid #1c1c28;
        border-radius: 10px;
    }
    div[data-testid="stExpander"]:hover { border-color: #27272a; }
</style>
""", unsafe_allow_html=True)


# ─── Session State ───────────────────────────────────────────────────
defaults = {
    "analysis_complete": False, "parsed_units": [], "health_report": None,
    "evolution_data": None, "repo_url": "", "repo_name": "",
    "embedder": None, "sparse_gen": None, "indexer": None, "searcher": None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ─── Helpers ─────────────────────────────────────────────────────────
def clone_repo(repo_url: str) -> str:
    def remove_readonly(func, path, _):
        os.chmod(path, stat.S_IWRITE)
        func(path)
    repo_hash = hashlib.md5(repo_url.encode()).hexdigest()[:10]
    tmp_dir = os.path.join(tempfile.gettempdir(), f"codedna_{repo_hash}")
    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir, onerror=remove_readonly)
    os.makedirs(tmp_dir, exist_ok=True)
    exit_code = os.system(f'git clone --depth=1 "{repo_url}" "{tmp_dir}"')
    if exit_code != 0:
        raise RuntimeError(f"Failed to clone: {repo_url}")
    return tmp_dir


def get_repo_name(url: str) -> str:
    url = url.rstrip("/").rstrip(".git")
    parts = url.split("/")
    return f"{parts[-2]}/{parts[-1]}" if len(parts) >= 2 else parts[-1]


def run_full_pipeline(repo_url: str, progress_callback=None):
    from core.parser import CodeParser
    from core.embedder import CodeEmbedder
    from core.sparse import SparseVectorGenerator
    from core.indexer import EndeeIndexer
    from core.searcher import CodeSearcher
    from core.analyzer import CodeHealthAnalyzer
    from core.evolution import EvolutionTracker

    results = {}

    if progress_callback: progress_callback("clone", "Cloning repository...")
    results["repo_path"] = clone_repo(repo_url)

    if progress_callback: progress_callback("parse", "Parsing source code...")
    parser = CodeParser()
    units = parser.parse_directory(results["repo_path"], recursive=True)
    if not units:
        raise ValueError("No Python/JS/Java files found in this repo.")
    results["units"] = units
    st.session_state.parsed_units = units

    lang_counts, type_counts, total_loc, total_cx = {}, {}, 0, 0
    for u in units:
        lang_counts[u.language] = lang_counts.get(u.language, 0) + 1
        type_counts[u.unit_type] = type_counts.get(u.unit_type, 0) + 1
        total_loc += u.loc
        total_cx += u.complexity
    results.update({"lang_counts": lang_counts, "type_counts": type_counts,
                     "total_loc": total_loc, "avg_complexity": round(total_cx / len(units), 1)})

    if progress_callback: progress_callback("embed", "Generating AI embeddings...")
    embedder = CodeEmbedder()
    sparse_gen = SparseVectorGenerator()
    if len(units) > 5: sparse_gen.fit(units)
    st.session_state.embedder = embedder
    st.session_state.sparse_gen = sparse_gen

    if progress_callback: progress_callback("index", "Indexing into Endee...")
    indexer = EndeeIndexer(embedder=embedder, sparse_gen=sparse_gen)
    indexer.setup_indexes()
    results["index_results"] = indexer.index_codebase(units)
    st.session_state.indexer = indexer

    if progress_callback: progress_callback("health", "Running health analysis...")
    searcher = CodeSearcher(embedder=embedder, sparse_gen=sparse_gen)
    analyzer = CodeHealthAnalyzer(searcher=searcher)
    results["health_report"] = analyzer.analyze_codebase(units)
    st.session_state.health_report = results["health_report"]
    st.session_state.searcher = searcher

    if progress_callback: progress_callback("evolution", "Generating genome map...")
    try:
        tracker = EvolutionTracker(embedder=embedder)
        results["evolution_data"] = tracker.get_embedding_projections(units, method="tsne")
        st.session_state.evolution_data = results["evolution_data"]
    except Exception:
        results["evolution_data"] = None

    if progress_callback: progress_callback("done", "Complete!")
    return results


# ─── Sidebar ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        '<div class="dna-logo">'
        '<span class="dna-icon">🧬</span>'
        '<span class="dna-text">CodeDNA</span>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.caption("AI-Powered Codebase Genome Analyzer")
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # Connection status
    endee_url = f"http://{config.ENDEE_HOST}:{config.ENDEE_PORT}"
    endee_connected = False
    try:
        from endee import Endee
        client = Endee()
        client.set_base_url(f"{endee_url}/api/v1")
        raw = client.list_indexes()
        idx_list = raw.get("indexes", []) if isinstance(raw, dict) else raw
        endee_connected = True
        st.markdown(
            f'<span class="status-dot dot-green"></span>'
            f'<span style="color:#a1a1aa;font-size:0.85rem">Endee connected · {len(idx_list)} indexes</span>',
            unsafe_allow_html=True,
        )
    except Exception:
        st.markdown(
            '<span class="status-dot dot-red"></span>'
            '<span style="color:#71717a;font-size:0.85rem">Endee offline</span>',
            unsafe_allow_html=True,
        )

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # Navigation
    pages = ["🏠  Analyze", "⚙️  About"]
    if st.session_state.analysis_complete:
        pages = ["🏠  Analyze", "🔍  Search", "🏥  Health", "📈  Genome", "⚙️  About"]
    page = st.radio("nav", pages, label_visibility="collapsed")

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # Tech stack
    st.markdown(
        '<div class="tags">'
        '<span class="tag tag-violet">Endee</span>'
        '<span class="tag tag-cyan">Transformers</span>'
        '<span class="tag tag-emerald">Streamlit</span>'
        '<span class="tag tag-amber">Plotly</span>'
        '</div>',
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════════════════
#  HOME — Analyze Repo
# ═══════════════════════════════════════════════════════════════════
if page == "🏠  Analyze":
    # Hero
    st.markdown(
        '<div class="hero">'
        '<div class="hero-badge">✦ AI-Powered Analysis</div>'
        '<h1>Code<span class="accent">DNA</span></h1>'
        '<p>Paste a public GitHub repo. We\'ll analyze its genome — search, health, evolution — in under a minute.</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    # Tags
    st.markdown(
        '<div class="tags">'
        '<span class="tag tag-violet">🔍 Semantic Search</span>'
        '<span class="tag tag-cyan">🧪 Hybrid Search</span>'
        '<span class="tag tag-emerald">🏥 Health Score</span>'
        '<span class="tag tag-amber">📈 Genome Map</span>'
        '</div>',
        unsafe_allow_html=True,
    )

    # Input
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="input-label">GITHUB REPOSITORY URL</div>', unsafe_allow_html=True)

    col_in, col_btn = st.columns([5, 1])
    with col_in:
        repo_url = st.text_input(
            "repo", placeholder="https://github.com/pallets/flask",
            label_visibility="collapsed", key="repo_url_input",
        )
    with col_btn:
        analyze_clicked = st.button("Analyze →", type="primary", use_container_width=True)

    # Quick picks
    st.markdown('<div class="input-label" style="margin-top:14px">QUICK PICK</div>', unsafe_allow_html=True)
    qc = st.columns(4)
    examples = [
        ("Flask", "https://github.com/pallets/flask"),
        ("FastAPI", "https://github.com/tiangolo/fastapi"),
        ("Requests", "https://github.com/psf/requests"),
        ("Express", "https://github.com/expressjs/express"),
    ]
    for i, (name, url) in enumerate(examples):
        with qc[i]:
            if st.button(f"{name}", key=f"ex_{i}", use_container_width=True):
                st.session_state.repo_url_input = url
                repo_url = url
                analyze_clicked = True

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # ── Run Pipeline ──
    if analyze_clicked and repo_url:
        if not endee_connected:
            st.error("Endee is offline. Run `docker compose up -d` first.")
        elif "github.com" not in repo_url:
            st.error("Enter a valid GitHub URL.")
        else:
            st.session_state.repo_name = get_repo_name(repo_url)
            st.session_state.repo_url = repo_url

            steps_order = ["clone", "parse", "embed", "index", "health", "evolution", "done"]
            steps_label = {
                "clone": "📥  Cloning repository",
                "parse": "🔍  Parsing source code",
                "embed": "🧠  Generating embeddings",
                "index": "📦  Indexing into Endee",
                "health": "🏥  Health analysis",
                "evolution": "📈  Genome mapping",
                "done": "✅  Complete",
            }

            progress = st.progress(0)
            status = st.empty()

            def on_progress(step, msg):
                idx = steps_order.index(step)
                progress.progress(min(idx / (len(steps_order) - 1), 1.0))
                status.markdown(f"**{steps_label.get(step, msg)}**")

            try:
                results = run_full_pipeline(repo_url, on_progress)
                progress.progress(1.0)
                status.empty()
                st.session_state.analysis_complete = True

                # Success banner
                st.markdown(
                    f'<div style="background:#10b98115;border:1px solid #10b98130;border-radius:10px;'
                    f'padding:14px 20px;color:#6ee7b7;font-weight:500;animation:slide-up 0.5s ease-out">'
                    f'✓ Successfully analyzed <strong>{st.session_state.repo_name}</strong></div>',
                    unsafe_allow_html=True,
                )

                # Stats
                report = results["health_report"]
                rd = report.to_dict()
                grade = rd["grade"]

                st.markdown(
                    f'<div class="stats-grid" style="margin-top:20px">'
                    f'<div class="stat-card">'
                    f'  <div class="stat-value">{len(results["units"])}</div>'
                    f'  <div class="stat-label">Code Units</div>'
                    f'</div>'
                    f'<div class="stat-card">'
                    f'  <div class="stat-value">{results["total_loc"]:,}</div>'
                    f'  <div class="stat-label">Lines of Code</div>'
                    f'</div>'
                    f'<div class="stat-card">'
                    f'  <div class="stat-value">{len(results["lang_counts"])}</div>'
                    f'  <div class="stat-label">Languages</div>'
                    f'</div>'
                    f'<div class="stat-card">'
                    f'  <div class="grade-ring grade-{grade}" style="margin:0 auto">{grade}</div>'
                    f'  <div class="stat-label">Health Grade</div>'
                    f'</div>'
                    f'<div class="stat-card">'
                    f'  <div class="stat-value">{rd["overall_score"]}</div>'
                    f'  <div class="stat-label">Score /100</div>'
                    f'</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

                st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
                st.info("👈  Use the sidebar to explore **Search**, **Health**, and **Genome Map**.")

            except Exception as e:
                progress.empty()
                status.empty()
                st.error(f"Analysis failed: {e}")
                st.caption("Make sure the repo URL is valid, public, and Endee is running.")

    elif st.session_state.analysis_complete:
        st.markdown(
            f'<div style="background:#7c3aed10;border:1px solid #7c3aed30;border-radius:10px;'
            f'padding:14px 20px;color:#c4b5fd;font-weight:500">'
            f'✦ Last analyzed: <strong>{st.session_state.repo_name}</strong> — use sidebar to explore results</div>',
            unsafe_allow_html=True,
        )


# ═══════════════════════════════════════════════════════════════════
#  SEARCH
# ═══════════════════════════════════════════════════════════════════
elif page == "🔍  Search":
    st.markdown(
        '<div class="section-header"><h2>🔍 Semantic Search</h2></div>'
        f'<div class="section-header"><span class="subtitle">Search <code>{st.session_state.repo_name}</code> by meaning, not keywords</span></div>',
        unsafe_allow_html=True,
    )

    mode = st.radio("Mode", ["Dense", "Hybrid", "Similar Code"], horizontal=True, label_visibility="collapsed")

    if mode == "Similar Code":
        query = st.text_area("Paste code:", height=150, placeholder="def fibonacci(n):\n    ...")
    else:
        query = st.text_input("Query", placeholder='e.g. "function that validates email"')

    with st.expander("⚙ Filters"):
        fc1, fc2, fc3 = st.columns(3)
        lang_f = fc1.selectbox("Language", [None, "python", "javascript", "java"])
        type_f = fc2.selectbox("Type", [None, "function", "class", "module"])
        top_k = fc3.slider("Results", 1, 30, 10)

    if st.button("Search →", type="primary", use_container_width=True):
        if not query:
            st.warning("Enter a query first.")
        elif not st.session_state.searcher:
            st.error("Analyze a repo first.")
        else:
            with st.spinner("Searching vectors..."):
                try:
                    s = st.session_state.searcher
                    if mode == "Dense":
                        res = s.search_dense(query=query, top_k=top_k, language=lang_f, unit_type=type_f)
                    elif mode == "Hybrid":
                        res = s.search_hybrid(query=query, top_k=top_k, language=lang_f, unit_type=type_f)
                    else:
                        res = s.find_similar_code(code_snippet=query, top_k=top_k)

                    if res:
                        st.markdown(f'<div style="color:#6ee7b7;font-weight:500;margin:12px 0">Found {len(res)} results</div>', unsafe_allow_html=True)
                        for i, r in enumerate(res):
                            m = r.metadata
                            sim_pct = min(r.similarity * 100, 100)
                            with st.expander(
                                f"**{m.get('name', '?')}** · `{m.get('language', '?')}` · {sim_pct:.1f}% match",
                                expanded=(i < 3),
                            ):
                                c1, c2, c3, c4 = st.columns(4)
                                c1.metric("Language", m.get("language", "?"))
                                c2.metric("Type", m.get("unit_type", "?"))
                                c3.metric("LOC", m.get("loc", "?"))
                                c4.metric("Complexity", m.get("complexity", "?"))
                                st.progress(min(r.similarity, 1.0), text=f"Similarity: {r.similarity:.4f}")
                    else:
                        st.info("No results. Try a broader query.")
                except Exception as e:
                    st.error(f"Search error: {e}")


# ═══════════════════════════════════════════════════════════════════
#  HEALTH
# ═══════════════════════════════════════════════════════════════════
elif page == "🏥  Health":
    st.markdown(
        '<div class="section-header"><h2>🏥 Health Report</h2></div>'
        f'<div class="section-header"><span class="subtitle">Anti-pattern matching for <code>{st.session_state.repo_name}</code></span></div>',
        unsafe_allow_html=True,
    )

    report = st.session_state.health_report
    if not report:
        st.warning("Analyze a repo first.")
    else:
        rd = report.to_dict()
        grade = rd["grade"]

        # Top metrics
        g1, g2, g3, g4 = st.columns([1, 1, 1, 1])
        with g1:
            st.markdown(
                f'<div style="text-align:center">'
                f'<div class="grade-ring grade-{grade}">{grade}</div>'
                f'<div class="stat-label" style="margin-top:10px">Grade</div></div>',
                unsafe_allow_html=True,
            )
        g2.metric("Score", f"{rd['overall_score']}/100")
        g3.metric("Violations", rd["total_violations"])
        g4.metric("Units", rd["total_units_analyzed"])

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

        # Metrics
        m = rd["metrics"]
        mc = st.columns(5)
        mc[0].metric("Total LOC", f"{m['total_loc']:,}")
        mc[1].metric("Avg Complexity", m["avg_complexity"])
        mc[2].metric("Doc %", f"{m['documentation_ratio']}%")
        mc[3].metric("Functions", m["function_count"])
        mc[4].metric("Classes", m["class_count"])

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

        # Charts
        if report.violations:
            import plotly.express as px
            import pandas as pd

            ch1, ch2 = st.columns(2)
            with ch1:
                sev = pd.DataFrame({
                    "Severity": ["Critical", "High", "Medium", "Low"],
                    "Count": [rd["critical_violations"], rd["high_violations"],
                              rd["medium_violations"], rd["low_violations"]],
                })
                fig = px.pie(sev, names="Severity", values="Count", hole=0.55,
                             color="Severity",
                             color_discrete_map={"Critical": "#ef4444", "High": "#f97316",
                                                  "Medium": "#eab308", "Low": "#3b82f6"})
                fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                                  font_color="#a1a1aa", height=320, margin=dict(t=30, b=0))
                st.plotly_chart(fig, use_container_width=True)

            with ch2:
                cats = {}
                for v in report.violations:
                    c = getattr(v, "category", "general")
                    cats[c] = cats.get(c, 0) + 1
                if cats:
                    cdf = pd.DataFrame(list(cats.items()), columns=["Category", "Count"])
                    fig2 = px.bar(cdf, x="Category", y="Count", color="Count",
                                  color_continuous_scale=["#7c3aed", "#a78bfa"])
                    fig2.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                                       font_color="#a1a1aa", showlegend=False, height=320,
                                       margin=dict(t=30, b=0))
                    st.plotly_chart(fig2, use_container_width=True)

            # Violation list
            st.markdown("### Violations")
            sev_dots = {"critical": "sev-critical", "high": "sev-high", "medium": "sev-medium", "low": "sev-low"}
            for v in report.violations[:20]:
                dot_cls = sev_dots.get(v.severity, "sev-low")
                with st.expander(f"**{v.pattern_name}** → {v.code_unit_name}"):
                    st.caption(f"Severity: {v.severity.upper()} · File: {v.code_unit_file}")
                    st.write(v.description)
                    st.write(f"**Fix:** {v.suggestion}")
                    if hasattr(v, "similarity") and v.similarity:
                        st.progress(v.similarity)
        else:
            st.markdown(
                '<div style="text-align:center;padding:40px;color:#6ee7b7;font-size:1.1rem">'
                '✦ No violations found. Clean codebase!</div>',
                unsafe_allow_html=True,
            )


# ═══════════════════════════════════════════════════════════════════
#  GENOME MAP
# ═══════════════════════════════════════════════════════════════════
elif page == "📈  Genome":
    st.markdown(
        '<div class="section-header"><h2>📈 Code Genome</h2></div>'
        f'<div class="section-header"><span class="subtitle">t-SNE projection of <code>{st.session_state.repo_name}</code> · each dot = one code unit</span></div>',
        unsafe_allow_html=True,
    )

    proj = st.session_state.evolution_data
    if not proj:
        st.warning("Genome map not available.")
    else:
        import plotly.express as px
        import pandas as pd

        df = pd.DataFrame(proj["points"])

        fig = px.scatter(
            df, x="x", y="y", color="language", symbol="type", size="complexity",
            hover_name="name", hover_data=["file", "loc", "complexity"],
            color_discrete_map={"python": "#7c3aed", "javascript": "#eab308", "java": "#ef4444"},
        )
        fig.update_layout(
            plot_bgcolor="#0a0a0f", paper_bgcolor="rgba(0,0,0,0)", font_color="#a1a1aa",
            height=600, margin=dict(t=10, b=10),
            xaxis=dict(showgrid=False, zeroline=False, title="", showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, title="", showticklabels=False),
        )
        fig.update_traces(marker=dict(line=dict(width=0.5, color="#27272a"), opacity=0.85))
        st.plotly_chart(fig, use_container_width=True)

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

        # Stats
        gs = st.columns(4)
        gs[0].metric("Units", len(df))
        gs[1].metric("Languages", df["language"].nunique())
        gs[2].metric("Avg Complexity", round(df["complexity"].mean(), 1))
        gs[3].metric("Total LOC", int(df["loc"].sum()))

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

        # Distribution
        d1, d2 = st.columns(2)
        with d1:
            fig_l = px.pie(df, names="language", color="language",
                            color_discrete_map={"python": "#7c3aed", "javascript": "#eab308", "java": "#ef4444"})
            fig_l.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                                 font_color="#a1a1aa", height=280, margin=dict(t=10, b=10))
            st.plotly_chart(fig_l, use_container_width=True)
        with d2:
            fig_t = px.histogram(df, x="complexity", nbins=20, color="language",
                                  color_discrete_map={"python": "#7c3aed", "javascript": "#eab308", "java": "#ef4444"})
            fig_t.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                                 font_color="#a1a1aa", height=280, margin=dict(t=10, b=10))
            st.plotly_chart(fig_t, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════
#  ABOUT
# ═══════════════════════════════════════════════════════════════════
elif page == "⚙️  About":
    st.markdown('<div class="section-header"><h2>⚙️ About CodeDNA</h2></div>', unsafe_allow_html=True)

    st.markdown(
        '<div class="about-card">'
        '<h3>What is CodeDNA?</h3>'
        '<p>An AI-powered codebase analyzer built on the Endee vector database. '
        'It treats source code like DNA — parsing it into units, converting to 384-dim vectors, '
        'and using semantic search, health diagnostics, and evolution tracking to give you '
        'deep insights no grep can match.</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    a1, a2 = st.columns(2)
    with a1:
        st.markdown(
            '<div class="about-card">'
            '<h3>🔋 Endee Features Used</h3>'
            '<p>• Dense Index (FLOAT16) — semantic search<br>'
            '• Hybrid Index (FLOAT16) — dense + sparse<br>'
            '• Anti-Pattern Index (FLOAT32) — health<br>'
            '• $eq, $range filters — advanced queries<br>'
            '• Bulk upsert — fast batch indexing<br>'
            '• Python SDK — all core modules</p>'
            '</div>',
            unsafe_allow_html=True,
        )
    with a2:
        st.markdown(
            '<div class="about-card">'
            '<h3>🛠 Tech Stack</h3>'
            '<p>• Endee Vector Database (Docker)<br>'
            '• Python 3.10+ (core engine)<br>'
            '• sentence-transformers (embeddings)<br>'
            '• scikit-learn (TF-IDF sparse vectors)<br>'
            '• Streamlit (dashboard)<br>'
            '• Plotly (interactive charts)</p>'
            '</div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # Active indexes
    st.markdown("### Active Endee Indexes")
    try:
        from endee import Endee
        c = Endee()
        c.set_base_url(f"http://{config.ENDEE_HOST}:{config.ENDEE_PORT}/api/v1")
        raw = c.list_indexes()
        idx_list = raw.get("indexes", []) if isinstance(raw, dict) else raw
        if idx_list:
            import pandas as pd
            st.dataframe(
                pd.DataFrame([{"Name": i.get("name"), "Dim": i.get("dimension"),
                                "Space": i.get("space_type")} for i in idx_list]),
                use_container_width=True, hide_index=True,
            )
        else:
            st.caption("No indexes yet. Analyze a repo to create them.")
    except Exception as e:
        st.caption(f"Cannot connect: {e}")

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown(
        f'<div style="color:#52525b;font-size:0.8rem">'
        f'CodeDNA v{config.APP_VERSION} · Model: {config.EMBEDDING_MODEL} · '
        f'<a href="https://github.com/thevikramrajput/endee" style="color:#7c3aed">GitHub</a>'
        f'</div>',
        unsafe_allow_html=True,
    )
