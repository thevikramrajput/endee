"""
CodeDNA — AI-Powered Codebase Genome Analyzer
===============================================
One-click codebase analysis. Paste a GitHub repo URL → get instant insights.

Usage:
    streamlit run app/main.py
"""

import streamlit as st
import os
import sys
import time
import shutil
import tempfile
import hashlib

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config


# ─── Page Configuration ─────────────────────────────────────────────
st.set_page_config(
    page_title="CodeDNA — Codebase Genome Analyzer",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ─── Custom CSS ──────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

    :root {
        --primary: #6C5CE7;
        --primary-light: #A29BFE;
        --accent: #00D2D3;
        --accent-green: #00B894;
        --warning: #FDCB6E;
        --danger: #E17055;
        --bg-dark: #0F0F1A;
        --bg-card: #1A1A2E;
    }

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .main .block-container {
        padding-top: 1.5rem;
        max-width: 1400px;
    }

    /* Hero */
    .hero-title {
        font-size: 3.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #6C5CE7, #00D2D3, #A29BFE);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.2rem;
        line-height: 1.1;
        letter-spacing: -1px;
    }

    .hero-subtitle {
        font-size: 1.15rem;
        color: #8B8BA3;
        font-weight: 300;
        margin-bottom: 1.5rem;
    }

    /* Gradient input wrapper */
    .url-input-wrapper {
        background: linear-gradient(145deg, #1A1A2E, #16213E);
        border: 2px solid rgba(108, 92, 231, 0.3);
        border-radius: 16px;
        padding: 2rem;
        margin-bottom: 1.5rem;
        transition: all 0.3s ease;
    }

    .url-input-wrapper:hover {
        border-color: rgba(108, 92, 231, 0.6);
        box-shadow: 0 8px 32px rgba(108, 92, 231, 0.15);
    }

    /* Metric cards */
    .metric-card {
        background: linear-gradient(145deg, #1A1A2E, #16213E);
        border: 1px solid rgba(108, 92, 231, 0.2);
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        transition: all 0.3s ease;
    }

    .metric-card:hover {
        border-color: rgba(108, 92, 231, 0.5);
        transform: translateY(-2px);
        box-shadow: 0 8px 32px rgba(108, 92, 231, 0.15);
    }

    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #6C5CE7;
        line-height: 1;
    }

    .metric-label {
        font-size: 0.85rem;
        color: #8B8BA3;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 0.5rem;
    }

    /* Grade badge */
    .grade-badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 3rem;
        font-weight: 800;
        width: 90px;
        height: 90px;
        border-radius: 50%;
    }
    .grade-A { background: linear-gradient(135deg, #00B894, #55EFC4); color: #1A1A2E; }
    .grade-B { background: linear-gradient(135deg, #0984E3, #74B9FF); color: #1A1A2E; }
    .grade-C { background: linear-gradient(135deg, #FDCB6E, #FFEAA7); color: #1A1A2E; }
    .grade-D { background: linear-gradient(135deg, #E17055, #FAB1A0); color: #1A1A2E; }
    .grade-F { background: linear-gradient(135deg, #D63031, #FF7675); color: white; }

    /* Similarity badge */
    .similarity-badge {
        display: inline-block;
        background: linear-gradient(135deg, #6C5CE7, #A29BFE);
        color: white;
        padding: 3px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }

    /* Feature pill */
    .feature-pill {
        display: inline-block;
        padding: 6px 16px;
        border-radius: 25px;
        font-size: 0.85rem;
        font-weight: 500;
        margin: 4px;
    }
    .pill-purple { background: rgba(108,92,231,0.15); color: #A29BFE; border: 1px solid rgba(108,92,231,0.3); }
    .pill-green { background: rgba(0,184,148,0.15); color: #55EFC4; border: 1px solid rgba(0,184,148,0.3); }
    .pill-blue { background: rgba(9,132,227,0.15); color: #74B9FF; border: 1px solid rgba(9,132,227,0.3); }
    .pill-orange { background: rgba(225,112,85,0.15); color: #FAB1A0; border: 1px solid rgba(225,112,85,0.3); }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0F0F1A 0%, #1A1A2E 100%);
    }

    /* Progress override */
    .stProgress .st-bo {
        background: linear-gradient(90deg, #6C5CE7, #00D2D3);
    }

    /* Gradient divider */
    .gradient-divider {
        height: 2px;
        background: linear-gradient(90deg, transparent, #6C5CE7, #00D2D3, transparent);
        border: none;
        margin: 1.5rem 0;
    }

    /* Pipeline step */
    .pipeline-step {
        background: linear-gradient(145deg, #1A1A2E, #16213E);
        border-left: 4px solid #6C5CE7;
        border-radius: 0 12px 12px 0;
        padding: 1rem 1.2rem;
        margin-bottom: 0.8rem;
    }

    .pipeline-step-active {
        border-left-color: #00D2D3;
        box-shadow: 0 0 20px rgba(0, 210, 211, 0.1);
    }

    .pipeline-step-done {
        border-left-color: #00B894;
    }

    /* Status indicators */
    .status-connected { color: #00B894; font-weight: 600; }
    .status-disconnected { color: #E17055; font-weight: 600; }
</style>
""", unsafe_allow_html=True)


# ─── Session State ───────────────────────────────────────────────────
defaults = {
    "analysis_complete": False,
    "analysis_running": False,
    "parsed_units": [],
    "health_report": None,
    "evolution_data": None,
    "search_results": [],
    "repo_url": "",
    "repo_name": "",
    "embedder": None,
    "sparse_gen": None,
    "indexer": None,
    "searcher": None,
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val


# ─── Helper Functions ────────────────────────────────────────────────
def clone_repo(repo_url: str) -> str:
    """Clone a public GitHub repo to temp directory."""
    import stat

    def remove_readonly(func, path, _):
        """Handle read-only files on Windows (common with .git objects)."""
        os.chmod(path, stat.S_IWRITE)
        func(path)

    repo_hash = hashlib.md5(repo_url.encode()).hexdigest()[:10]
    tmp_dir = os.path.join(tempfile.gettempdir(), f"codedna_{repo_hash}")
    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir, onerror=remove_readonly)
    os.makedirs(tmp_dir, exist_ok=True)
    exit_code = os.system(f'git clone --depth=1 "{repo_url}" "{tmp_dir}"')
    if exit_code != 0:
        raise RuntimeError(f"Failed to clone repository: {repo_url}")
    return tmp_dir


def get_repo_name(url: str) -> str:
    """Extract repo name from GitHub URL."""
    url = url.rstrip("/").rstrip(".git")
    parts = url.split("/")
    if len(parts) >= 2:
        return f"{parts[-2]}/{parts[-1]}"
    return parts[-1] if parts else "unknown"


def run_full_pipeline(repo_url: str, progress_callback=None):
    """Run the complete CodeDNA analysis pipeline."""
    from core.parser import CodeParser
    from core.embedder import CodeEmbedder
    from core.sparse import SparseVectorGenerator
    from core.indexer import EndeeIndexer
    from core.searcher import CodeSearcher
    from core.analyzer import CodeHealthAnalyzer
    from core.evolution import EvolutionTracker

    results = {}

    # Step 1: Clone
    if progress_callback:
        progress_callback("clone", "📥 Cloning repository...")
    repo_path = clone_repo(repo_url)
    results["repo_path"] = repo_path

    # Step 2: Parse
    if progress_callback:
        progress_callback("parse", "🔍 Parsing source code...")
    parser = CodeParser()
    units = parser.parse_directory(repo_path, recursive=True)
    if not units:
        raise ValueError("No code units found in this repository. Make sure it contains Python, JavaScript, or Java files.")
    results["units"] = units
    st.session_state.parsed_units = units

    # Gather stats
    lang_counts = {}
    type_counts = {}
    total_loc = 0
    total_complexity = 0
    for u in units:
        lang_counts[u.language] = lang_counts.get(u.language, 0) + 1
        type_counts[u.unit_type] = type_counts.get(u.unit_type, 0) + 1
        total_loc += u.loc
        total_complexity += u.complexity
    results["lang_counts"] = lang_counts
    results["type_counts"] = type_counts
    results["total_loc"] = total_loc
    results["avg_complexity"] = round(total_complexity / len(units), 1) if units else 0

    # Step 3: Embed
    if progress_callback:
        progress_callback("embed", "🧠 Generating AI embeddings...")
    embedder = CodeEmbedder()
    sparse_gen = SparseVectorGenerator()
    if len(units) > 5:
        sparse_gen.fit(units)
    st.session_state.embedder = embedder
    st.session_state.sparse_gen = sparse_gen

    # Step 4: Index to Endee
    if progress_callback:
        progress_callback("index", "📦 Indexing vectors into Endee...")
    indexer = EndeeIndexer(embedder=embedder, sparse_gen=sparse_gen)
    indexer.setup_indexes()
    index_results = indexer.index_codebase(units)
    results["index_results"] = index_results
    st.session_state.indexer = indexer

    # Step 5: Health Analysis
    if progress_callback:
        progress_callback("health", "🏥 Running health diagnostics...")
    searcher = CodeSearcher(embedder=embedder, sparse_gen=sparse_gen)
    analyzer = CodeHealthAnalyzer(searcher=searcher)
    report = analyzer.analyze_codebase(units)
    results["health_report"] = report
    st.session_state.health_report = report
    st.session_state.searcher = searcher

    # Step 6: Evolution Map
    if progress_callback:
        progress_callback("evolution", "📈 Generating genome map...")
    tracker = EvolutionTracker(embedder=embedder)
    try:
        projection = tracker.get_embedding_projections(units, method="tsne", n_components=2)
        results["evolution_data"] = projection
        st.session_state.evolution_data = projection
    except Exception:
        results["evolution_data"] = None

    # Cleanup
    if progress_callback:
        progress_callback("done", "✅ Analysis complete!")

    return results


# ─── Sidebar ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🧬 CodeDNA")
    st.markdown("*AI-Powered Codebase Genome Analyzer*")
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

    # Endee connection status
    st.markdown("### 🔌 Endee Database")
    endee_url = f"http://{config.ENDEE_HOST}:{config.ENDEE_PORT}"
    endee_connected = False
    try:
        from endee import Endee
        client = Endee()
        client.set_base_url(f"{endee_url}/api/v1")
        raw_indexes = client.list_indexes()
        indexes = raw_indexes.get("indexes", []) if isinstance(raw_indexes, dict) else raw_indexes
        endee_connected = True
        st.markdown(
            f'<span class="status-connected">● Connected</span>',
            unsafe_allow_html=True,
        )
        st.caption(f"{len(indexes)} index(es) active")
    except Exception:
        st.markdown(
            '<span class="status-disconnected">● Disconnected</span>',
            unsafe_allow_html=True,
        )
        st.caption("Start Endee: `docker compose up -d`")

    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

    # Navigation
    st.markdown("### 🧭 Navigation")
    if st.session_state.analysis_complete:
        page = st.radio(
            "Select Page",
            ["🏠 Analyze Repo", "🔍 Semantic Search", "🏥 Health Report", "📈 Code Genome", "⚙️ About"],
            label_visibility="collapsed",
        )
    else:
        page = st.radio(
            "Select Page",
            ["🏠 Analyze Repo", "⚙️ About"],
            label_visibility="collapsed",
        )

    # Powered by
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
    st.markdown("### 🔋 Powered by")
    st.markdown(
        '<span class="feature-pill pill-purple">Endee Vector DB</span>'
        '<span class="feature-pill pill-green">Sentence Transformers</span>'
        '<span class="feature-pill pill-blue">Streamlit</span>'
        '<span class="feature-pill pill-orange">Plotly</span>',
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════════════════
#  PAGE: ANALYZE REPO (Home)
# ═══════════════════════════════════════════════════════════════════
if page == "🏠 Analyze Repo":

    # Hero
    st.markdown(
        '<div class="hero-title">CodeDNA</div>'
        '<div class="hero-subtitle">'
        "Paste a public GitHub repo link → get instant AI-powered code intelligence."
        "</div>",
        unsafe_allow_html=True,
    )

    # Feature pills
    st.markdown(
        '<span class="feature-pill pill-purple">🔍 Semantic Search</span>'
        '<span class="feature-pill pill-green">🧪 Hybrid Search</span>'
        '<span class="feature-pill pill-blue">🏥 Health Analysis</span>'
        '<span class="feature-pill pill-orange">📈 Evolution Tracking</span>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

    # ─── URL Input ───────────────────────────────────────────────
    st.markdown("### 🔗 Enter GitHub Repository URL")

    col_input, col_btn = st.columns([4, 1])
    with col_input:
        repo_url = st.text_input(
            "GitHub URL",
            placeholder="https://github.com/pallets/flask",
            label_visibility="collapsed",
            key="repo_url_input",
        )
    with col_btn:
        analyze_clicked = st.button("🧬 Analyze", type="primary", use_container_width=True)

    # Example repos
    st.markdown("**Try these:**")
    example_cols = st.columns(4)
    examples = [
        ("Flask", "https://github.com/pallets/flask"),
        ("FastAPI", "https://github.com/tiangolo/fastapi"),
        ("Requests", "https://github.com/psf/requests"),
        ("Express.js", "https://github.com/expressjs/express"),
    ]
    for i, (name, url) in enumerate(examples):
        with example_cols[i]:
            if st.button(f"📦 {name}", use_container_width=True, key=f"example_{i}"):
                st.session_state.repo_url_input = url
                repo_url = url
                analyze_clicked = True

    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

    # ─── Analysis Pipeline ───────────────────────────────────────
    if analyze_clicked and repo_url:
        if not endee_connected:
            st.error("⚠️ Endee is not running. Please start it with `docker compose up -d`")
        elif "github.com" not in repo_url:
            st.error("Please enter a valid GitHub repository URL.")
        else:
            st.session_state.repo_name = get_repo_name(repo_url)
            st.session_state.repo_url = repo_url
            st.session_state.analysis_complete = False

            # Pipeline progress display
            st.markdown(f"### 🧬 Analyzing `{st.session_state.repo_name}`")

            pipeline_steps = {
                "clone": "📥 Cloning repository",
                "parse": "🔍 Parsing source code",
                "embed": "🧠 Generating AI embeddings",
                "index": "📦 Indexing to Endee",
                "health": "🏥 Health diagnostics",
                "evolution": "📈 Generating genome map",
                "done": "✅ Complete",
            }

            progress_bar = st.progress(0)
            status_text = st.empty()
            step_count = len(pipeline_steps) - 1  # exclude "done"

            current_step_idx = [0]

            def update_progress(step_key, message):
                step_keys = list(pipeline_steps.keys())
                idx = step_keys.index(step_key)
                progress = min(idx / step_count, 1.0)
                progress_bar.progress(progress)
                status_text.markdown(f"**{message}**")
                current_step_idx[0] = idx

            try:
                results = run_full_pipeline(repo_url, progress_callback=update_progress)

                progress_bar.progress(1.0)
                status_text.markdown("**✅ Analysis complete!**")
                st.session_state.analysis_complete = True

                # Show quick summary
                st.success(f"🎉 Successfully analyzed **{st.session_state.repo_name}**!")

                # Summary metrics
                mcol1, mcol2, mcol3, mcol4, mcol5 = st.columns(5)

                with mcol1:
                    st.markdown(
                        f'<div class="metric-card">'
                        f'<div class="metric-value">{len(results["units"])}</div>'
                        f'<div class="metric-label">Code Units</div>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
                with mcol2:
                    st.markdown(
                        f'<div class="metric-card">'
                        f'<div class="metric-value">{results["total_loc"]:,}</div>'
                        f'<div class="metric-label">Lines of Code</div>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
                with mcol3:
                    st.markdown(
                        f'<div class="metric-card">'
                        f'<div class="metric-value">{len(results["lang_counts"])}</div>'
                        f'<div class="metric-label">Languages</div>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
                with mcol4:
                    report = results["health_report"]
                    report_dict = report.to_dict()
                    grade = report_dict["grade"]
                    grade_class = f"grade-{grade}"
                    st.markdown(
                        f'<div class="metric-card">'
                        f'<div class="grade-badge {grade_class}" style="margin:0 auto">{grade}</div>'
                        f'<div class="metric-label">Health Grade</div>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
                with mcol5:
                    st.markdown(
                        f'<div class="metric-card">'
                        f'<div class="metric-value">{report_dict["overall_score"]}</div>'
                        f'<div class="metric-label">Health Score</div>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )

                st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
                st.info("👈 Use the **sidebar** to explore Semantic Search, Health Report, and Code Genome Map!")

            except Exception as e:
                progress_bar.empty()
                status_text.empty()
                st.error(f"❌ Analysis failed: {str(e)}")
                st.info(
                    "**Troubleshooting:**\n"
                    "- Make sure the repository URL is valid and public\n"
                    "- Make sure Endee is running (`docker compose up -d`)\n"
                    "- Make sure `git` is installed on your system\n"
                )

    # Show previous results if available
    elif st.session_state.analysis_complete:
        st.success(f"✅ Last analysis: **{st.session_state.repo_name}**")
        st.info("👈 Use the sidebar to explore results, or paste a new repo above.")


# ═══════════════════════════════════════════════════════════════════
#  PAGE: SEMANTIC SEARCH
# ═══════════════════════════════════════════════════════════════════
elif page == "🔍 Semantic Search":
    st.markdown(f"## 🔍 Semantic Code Search")
    st.markdown(f"Search `{st.session_state.repo_name}` by **meaning**, not just keywords.")
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

    # Search mode
    search_mode = st.radio(
        "Search Mode",
        ["Dense (Semantic)", "Hybrid (Semantic + Keyword)", "Find Similar Code"],
        horizontal=True,
    )

    # Query
    if search_mode == "Find Similar Code":
        query = st.text_area(
            "Paste code to find similar implementations:",
            height=180,
            placeholder="def calculate_fibonacci(n):\n    if n <= 1:\n        return n\n    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)",
        )
    else:
        query = st.text_input(
            "What are you looking for?",
            placeholder='e.g., "function that handles user authentication" or "error handling middleware"',
        )

    # Filters
    with st.expander("🎛️ Advanced Filters (Endee $eq / $range operators)"):
        fcol1, fcol2, fcol3 = st.columns(3)
        with fcol1:
            language_filter = st.selectbox("Language ($eq)", [None, "python", "javascript", "java"])
        with fcol2:
            unit_type_filter = st.selectbox("Unit Type ($eq)", [None, "function", "class", "module"])
        with fcol3:
            top_k = st.slider("Max Results", 1, 30, 10)

    # Search
    if st.button("🚀 Search Endee", type="primary", use_container_width=True):
        if not query:
            st.warning("Enter a search query first!")
        elif st.session_state.searcher is None:
            st.error("Please analyze a repository first from the home page.")
        else:
            with st.spinner("🔍 Searching Endee vectors..."):
                try:
                    searcher = st.session_state.searcher

                    if search_mode == "Dense (Semantic)":
                        results = searcher.search_dense(
                            query=query, top_k=top_k,
                            language=language_filter, unit_type=unit_type_filter,
                        )
                    elif search_mode == "Hybrid (Semantic + Keyword)":
                        results = searcher.search_hybrid(
                            query=query, top_k=top_k,
                            language=language_filter, unit_type=unit_type_filter,
                        )
                    else:
                        results = searcher.find_similar_code(code_snippet=query, top_k=top_k)

                    if results:
                        st.success(f"Found **{len(results)}** results!")
                        for i, result in enumerate(results):
                            meta = result.metadata
                            with st.expander(
                                f"**{i+1}. {meta.get('name', 'Unknown')}** — "
                                f"`{meta.get('file_path', '')}` "
                                f"(Similarity: {result.similarity:.4f})",
                                expanded=(i < 3),
                            ):
                                ic1, ic2, ic3, ic4 = st.columns(4)
                                ic1.metric("Language", meta.get("language", "?"))
                                ic2.metric("Type", meta.get("unit_type", "?"))
                                ic3.metric("LOC", meta.get("loc", "?"))
                                ic4.metric("Complexity", meta.get("complexity", "?"))

                                st.progress(
                                    min(result.similarity, 1.0),
                                    text=f"Vector Similarity: {result.similarity:.4f}",
                                )
                    else:
                        st.info("No results found. Try a broader query.")

                except Exception as e:
                    st.error(f"Search failed: {e}")


# ═══════════════════════════════════════════════════════════════════
#  PAGE: HEALTH REPORT
# ═══════════════════════════════════════════════════════════════════
elif page == "🏥 Health Report":
    st.markdown(f"## 🏥 Codebase Health Report")
    st.markdown(f"Health diagnostics for `{st.session_state.repo_name}` — powered by Endee anti-pattern matching.")
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

    report = st.session_state.health_report
    if report is None:
        st.warning("Please analyze a repository first from the home page.")
    else:
        report_dict = report.to_dict()

        # Top row: Grade + Score + Violations
        gcol1, gcol2, gcol3, gcol4 = st.columns([1, 1, 1, 1])

        with gcol1:
            grade = report_dict["grade"]
            grade_class = f"grade-{grade}"
            st.markdown(
                f'<div style="text-align:center">'
                f'<div class="grade-badge {grade_class}">{grade}</div>'
                f'<p style="margin-top:10px;color:#8B8BA3;font-size:0.9rem">Overall Grade</p>'
                f'</div>',
                unsafe_allow_html=True,
            )

        with gcol2:
            st.metric("Health Score", f"{report_dict['overall_score']}/100")
        with gcol3:
            st.metric("Total Violations", report_dict["total_violations"])
        with gcol4:
            st.metric("Units Analyzed", report_dict["total_units_analyzed"])

        st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

        # Metrics row
        st.markdown("### 📊 Codebase Metrics")
        mm1, mm2, mm3, mm4, mm5 = st.columns(5)
        metrics = report_dict["metrics"]
        mm1.metric("Total LOC", f"{metrics['total_loc']:,}")
        mm2.metric("Avg Complexity", metrics["avg_complexity"])
        mm3.metric("Documentation %", f"{metrics['documentation_ratio']}%")
        mm4.metric("Functions", metrics["function_count"])
        mm5.metric("Classes", metrics["class_count"])

        st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

        # Violations chart
        if report.violations:
            st.markdown("### ⚠️ Violations Breakdown")

            import plotly.express as px
            import plotly.graph_objects as go
            import pandas as pd

            # Severity donut chart + Category bar chart side by side
            ch1, ch2 = st.columns(2)

            with ch1:
                severity_data = pd.DataFrame({
                    "Severity": ["Critical", "High", "Medium", "Low"],
                    "Count": [
                        report_dict["critical_violations"],
                        report_dict["high_violations"],
                        report_dict["medium_violations"],
                        report_dict["low_violations"],
                    ],
                    "Color": ["#D63031", "#E17055", "#FDCB6E", "#74B9FF"],
                })
                fig = px.pie(
                    severity_data, names="Severity", values="Count",
                    color="Severity",
                    color_discrete_map={"Critical": "#D63031", "High": "#E17055", "Medium": "#FDCB6E", "Low": "#74B9FF"},
                    hole=0.5, title="Violations by Severity",
                )
                fig.update_layout(
                    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                    font_color="#EAEAEA", height=350,
                )
                st.plotly_chart(fig, use_container_width=True)

            with ch2:
                # Category breakdown
                categories = {}
                for v in report.violations:
                    cat = v.category if hasattr(v, "category") else "general"
                    categories[cat] = categories.get(cat, 0) + 1

                if categories:
                    cat_df = pd.DataFrame(list(categories.items()), columns=["Category", "Count"])
                    fig2 = px.bar(
                        cat_df, x="Category", y="Count", color="Count",
                        color_continuous_scale=["#6C5CE7", "#00D2D3"],
                        title="Violations by Category",
                    )
                    fig2.update_layout(
                        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                        font_color="#EAEAEA", showlegend=False, height=350,
                    )
                    st.plotly_chart(fig2, use_container_width=True)

            # Individual violations
            st.markdown("### 📋 Violation Details")
            severity_icons = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🔵"}

            for v in report.violations[:25]:
                icon = severity_icons.get(v.severity, "⚪")
                with st.expander(f"{icon} [{v.severity.upper()}] {v.pattern_name} → {v.code_unit_name}"):
                    st.write(f"**File:** `{v.code_unit_file}`")
                    st.write(f"**Description:** {v.description}")
                    st.write(f"**Suggestion:** {v.suggestion}")
                    if hasattr(v, "similarity") and v.similarity:
                        st.progress(v.similarity, text=f"Similarity: {v.similarity:.2%}")
        else:
            st.success("🎉 No violations found! Your codebase is clean.")


# ═══════════════════════════════════════════════════════════════════
#  PAGE: CODE GENOME MAP
# ═══════════════════════════════════════════════════════════════════
elif page == "📈 Code Genome":
    st.markdown("## 📈 Code Genome Map")
    st.markdown(f"t-SNE projection of `{st.session_state.repo_name}`'s vector genome — each dot is a code unit.")
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

    proj = st.session_state.evolution_data
    if proj is None:
        st.warning("Genome map not available. Please analyze a repository first.")
    else:
        import plotly.express as px
        import pandas as pd

        df = pd.DataFrame(proj["points"])

        # Main scatter plot
        fig = px.scatter(
            df, x="x", y="y",
            color="language", symbol="type",
            size="complexity",
            hover_name="name",
            hover_data=["file", "loc", "complexity"],
            title=f"🧬 Code Genome — {st.session_state.repo_name}",
            color_discrete_map={
                "python": "#6C5CE7", "javascript": "#FDCB6E", "java": "#E17055",
            },
        )
        fig.update_layout(
            plot_bgcolor="rgba(15,15,26,0.9)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#EAEAEA",
            height=650,
            xaxis=dict(showgrid=False, zeroline=False, title="t-SNE Dimension 1"),
            yaxis=dict(showgrid=False, zeroline=False, title="t-SNE Dimension 2"),
        )
        fig.update_traces(marker=dict(line=dict(width=0.5, color="#333"), opacity=0.85))
        st.plotly_chart(fig, use_container_width=True)

        st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

        # Stats
        st.markdown("### 📊 Genome Statistics")
        gs1, gs2, gs3, gs4 = st.columns(4)
        gs1.metric("Total Units", len(df))
        gs2.metric("Languages", df["language"].nunique())
        gs3.metric("Avg Complexity", round(df["complexity"].mean(), 1))
        gs4.metric("Total LOC", int(df["loc"].sum()))

        # Distribution charts
        st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
        dc1, dc2 = st.columns(2)

        with dc1:
            lang_fig = px.pie(
                df, names="language", title="Language Distribution",
                color="language",
                color_discrete_map={"python": "#6C5CE7", "javascript": "#FDCB6E", "java": "#E17055"},
            )
            lang_fig.update_layout(
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                font_color="#EAEAEA",
            )
            st.plotly_chart(lang_fig, use_container_width=True)

        with dc2:
            type_fig = px.histogram(
                df, x="type", color="language", title="Code Unit Types",
                color_discrete_map={"python": "#6C5CE7", "javascript": "#FDCB6E", "java": "#E17055"},
            )
            type_fig.update_layout(
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                font_color="#EAEAEA",
            )
            st.plotly_chart(type_fig, use_container_width=True)

        # Complexity distribution
        st.markdown("### 🔬 Complexity Distribution")
        comp_fig = px.histogram(
            df, x="complexity", nbins=20, color="language",
            title="Complexity Distribution Across Code Units",
            color_discrete_map={"python": "#6C5CE7", "javascript": "#FDCB6E", "java": "#E17055"},
        )
        comp_fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font_color="#EAEAEA",
        )
        st.plotly_chart(comp_fig, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════
#  PAGE: ABOUT
# ═══════════════════════════════════════════════════════════════════
elif page == "⚙️ About":
    st.markdown("## ⚙️ About CodeDNA")
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

    st.markdown(
        """
        ### 🧬 What is CodeDNA?

        **CodeDNA** is an AI-powered codebase genome analyzer built on the
        **[Endee](https://endee.io)** vector database. It treats source code like biological DNA —
        analyzing its genetic structure, diagnosing its health, and tracking its evolution.

        ### 🔋 How It Works

        1. **Parse** — Extracts functions, classes, and modules from Python, JavaScript, and Java files
        2. **Embed** — Converts each code unit into a 384-dimensional vector using AI (sentence-transformers)
        3. **Index** — Stores vectors in 3 Endee indexes (Dense, Hybrid, Anti-Pattern)
        4. **Analyze** — Runs health diagnostics, semantic search, and evolution tracking

        ### 🛠️ Endee Features Used

        | Feature | Usage |
        |---|---|
        | Dense Index (FLOAT16) | Semantic function-level search |
        | Hybrid Index (INT8) | Dense + Sparse combined retrieval |
        | Anti-Pattern Index (FLOAT32) | High-precision health diagnostics |
        | `$eq` filter | Filter by language, unit type |
        | `$range` filter | Filter by complexity, LOC |
        | Bulk upsert | Batch vector indexing |
        | Python SDK | All core engine modules |
        """
    )

    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

    # Endee index info
    st.markdown("### 📦 Active Endee Indexes")
    try:
        from endee import Endee
        client = Endee()
        client.set_base_url(f"http://{config.ENDEE_HOST}:{config.ENDEE_PORT}/api/v1")
        raw_indexes = client.list_indexes()
        indexes = raw_indexes.get("indexes", []) if isinstance(raw_indexes, dict) else raw_indexes
        if indexes:
            import pandas as pd
            idx_data = []
            for idx in indexes:
                idx_data.append({
                    "Name": idx.get("name", ""),
                    "Dimension": idx.get("dimension", ""),
                    "Space": idx.get("space_type", ""),
                })
            st.dataframe(pd.DataFrame(idx_data), use_container_width=True)
        else:
            st.info("No indexes yet. Analyze a repo to create them!")
    except Exception as e:
        st.warning(f"Cannot connect to Endee: {e}")

    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

    st.markdown(
        f"""
        ### 📌 Version Info
        - **CodeDNA** v{config.APP_VERSION}
        - **Embedding Model:** `{config.EMBEDDING_MODEL}`
        - **Endee:** `http://{config.ENDEE_HOST}:{config.ENDEE_PORT}`

        ### 🔗 Links
        - 📖 [Endee Documentation](https://docs.endee.io)
        - 📂 [Endee GitHub](https://github.com/endee-io/endee)
        - 🧬 [CodeDNA GitHub](https://github.com/thevikramrajput/endee)
        """
    )
