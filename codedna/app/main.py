"""
CodeDNA — Streamlit Dashboard
==============================
Main entry point for the CodeDNA web application.
Provides semantic code search, health analysis, and evolution visualization.

Usage:
    streamlit run app/main.py
"""

import streamlit as st
import os
import sys

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
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    /* Root variables */
    :root {
        --primary: #6C5CE7;
        --primary-light: #A29BFE;
        --accent: #00D2D3;
        --accent-green: #00B894;
        --warning: #FDCB6E;
        --danger: #E17055;
        --bg-dark: #0F0F1A;
        --bg-card: #1A1A2E;
        --text-primary: #EAEAEA;
        --text-secondary: #8B8BA3;
    }

    /* Global font */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Main container */
    .main .block-container {
        padding-top: 2rem;
        max-width: 1400px;
    }

    /* Hero section */
    .hero-title {
        font-size: 2.8rem;
        font-weight: 700;
        background: linear-gradient(135deg, #6C5CE7, #00D2D3, #A29BFE);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.3rem;
        line-height: 1.2;
    }

    .hero-subtitle {
        font-size: 1.15rem;
        color: #8B8BA3;
        font-weight: 300;
        margin-bottom: 2rem;
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
        display: inline-block;
        font-size: 3rem;
        font-weight: 800;
        width: 80px;
        height: 80px;
        line-height: 80px;
        text-align: center;
        border-radius: 50%;
        margin: 0 auto;
    }

    .grade-A { background: linear-gradient(135deg, #00B894, #55EFC4); color: #1A1A2E; }
    .grade-B { background: linear-gradient(135deg, #0984E3, #74B9FF); color: #1A1A2E; }
    .grade-C { background: linear-gradient(135deg, #FDCB6E, #FFEAA7); color: #1A1A2E; }
    .grade-D { background: linear-gradient(135deg, #E17055, #FAB1A0); color: #1A1A2E; }
    .grade-F { background: linear-gradient(135deg, #D63031, #FF7675); color: white; }

    /* Code block styling */
    .code-result {
        background: #0D1117;
        border: 1px solid #30363D;
        border-radius: 12px;
        padding: 1rem;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.85rem;
        overflow-x: auto;
    }

    /* Search result card */
    .result-card {
        background: linear-gradient(145deg, #1A1A2E, #16213E);
        border: 1px solid rgba(108, 92, 231, 0.15);
        border-radius: 12px;
        padding: 1.2rem;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }

    .result-card:hover {
        border-color: #6C5CE7;
        box-shadow: 0 4px 20px rgba(108, 92, 231, 0.2);
    }

    .similarity-badge {
        display: inline-block;
        background: linear-gradient(135deg, #6C5CE7, #A29BFE);
        color: white;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0F0F1A 0%, #1A1A2E 100%);
    }

    /* Status indicators */
    .status-connected {
        color: #00B894;
        font-weight: 600;
    }
    .status-disconnected {
        color: #E17055;
        font-weight: 600;
    }

    /* Navigation pills */
    .nav-pill {
        display: inline-block;
        padding: 8px 20px;
        border-radius: 25px;
        background: rgba(108, 92, 231, 0.1);
        border: 1px solid rgba(108, 92, 231, 0.3);
        color: #A29BFE;
        font-size: 0.9rem;
        margin: 4px;
        transition: all 0.3s ease;
    }

    /* Progress bar override */
    .stProgress .st-bo {
        background: linear-gradient(90deg, #6C5CE7, #00D2D3);
    }

    /* Divider */
    .gradient-divider {
        height: 2px;
        background: linear-gradient(90deg, transparent, #6C5CE7, #00D2D3, transparent);
        border: none;
        margin: 2rem 0;
    }
</style>
""", unsafe_allow_html=True)


# ─── Session State ───────────────────────────────────────────────────
if "embedder" not in st.session_state:
    st.session_state.embedder = None
if "searcher" not in st.session_state:
    st.session_state.searcher = None
if "indexer" not in st.session_state:
    st.session_state.indexer = None
if "parsed_units" not in st.session_state:
    st.session_state.parsed_units = []
if "health_report" not in st.session_state:
    st.session_state.health_report = None
if "evolution_data" not in st.session_state:
    st.session_state.evolution_data = None


# ─── Sidebar ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🧬 CodeDNA")
    st.markdown("*AI-Powered Codebase Genome Analyzer*")
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

    # Endee connection status
    st.markdown("### 🔌 Endee Connection")
    endee_url = f"http://{config.ENDEE_HOST}:{config.ENDEE_PORT}"
    try:
        from endee import Endee
        client = Endee()
        client.set_base_url(f"{endee_url}/api/v1")
        indexes = client.list_indexes()
        st.markdown(
            f'<span class="status-connected">● Connected</span> to {endee_url}',
            unsafe_allow_html=True,
        )
        st.caption(f"{len(indexes)} indexes found")
    except Exception:
        st.markdown(
            '<span class="status-disconnected">● Disconnected</span>',
            unsafe_allow_html=True,
        )
        st.caption("Start Endee: `docker compose up -d`")

    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

    # Navigation
    st.markdown("### 🧭 Navigation")
    page = st.radio(
        "Select Page",
        ["🏠 Home", "🔍 Semantic Search", "🏥 Health Analysis", "📈 Evolution", "⚙️ Settings"],
        label_visibility="collapsed",
    )


# ─── Home Page ───────────────────────────────────────────────────────
if page == "🏠 Home":
    st.markdown(
        '<div class="hero-title">CodeDNA</div>'
        '<div class="hero-subtitle">'
        "Treat your codebase like DNA — analyze its genome, track its evolution, "
        "and diagnose its health using AI-powered vector intelligence."
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

    # Feature cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(
            '<div class="metric-card">'
            '<div class="metric-value">🔍</div>'
            '<div class="metric-label">Semantic Search</div>'
            "</div>",
            unsafe_allow_html=True,
        )
        st.caption("Find code by meaning, not keywords")

    with col2:
        st.markdown(
            '<div class="metric-card">'
            '<div class="metric-value">🧪</div>'
            '<div class="metric-label">Hybrid Search</div>'
            "</div>",
            unsafe_allow_html=True,
        )
        st.caption("Dense + Sparse for best results")

    with col3:
        st.markdown(
            '<div class="metric-card">'
            '<div class="metric-value">🏥</div>'
            '<div class="metric-label">Health Analysis</div>'
            "</div>",
            unsafe_allow_html=True,
        )
        st.caption("Detect anti-patterns & code smells")

    with col4:
        st.markdown(
            '<div class="metric-card">'
            '<div class="metric-value">📈</div>'
            '<div class="metric-label">Evolution</div>'
            "</div>",
            unsafe_allow_html=True,
        )
        st.caption("Track architecture drift over time")

    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

    # Quick start
    st.markdown("### 🚀 Quick Start")
    st.code(
        "# 1. Start Endee\n"
        "docker compose up -d\n\n"
        "# 2. Ingest a repository\n"
        "python scripts/ingest_repo.py --repo https://github.com/pallets/flask\n\n"
        "# 3. Launch this dashboard\n"
        "streamlit run app/main.py",
        language="bash",
    )

    # Powered by Endee
    st.markdown("### 🔋 Powered by Endee Vector Database")
    st.markdown(
        """
        CodeDNA leverages **Endee's** advanced capabilities:
        - **Dense Indexes** — FLOAT16 precision for semantic code embeddings
        - **Hybrid Indexes** — INT8 precision combining dense + sparse vectors
        - **Advanced Filtering** — `$eq`, `$in`, `$range` operators for metadata
        - **Multiple Precisions** — BINARY, INT8, INT16, FLOAT16, FLOAT32
        - **HNSW Algorithm** — Fast approximate nearest neighbor search
        """
    )


# ─── Semantic Search Page ────────────────────────────────────────────
elif page == "🔍 Semantic Search":
    st.markdown("## 🔍 Semantic Code Search")
    st.markdown("Search for code by **meaning** using Endee's vector search.")
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

    # Search mode selection
    search_mode = st.radio(
        "Search Mode",
        ["Dense (Semantic)", "Hybrid (Semantic + Keyword)", "Find Similar Code"],
        horizontal=True,
    )

    # Query input
    if search_mode == "Find Similar Code":
        query = st.text_area(
            "Paste code to find similar implementations:",
            height=200,
            placeholder="def calculate_fibonacci(n):\n    if n <= 1:\n        return n\n    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)",
        )
    else:
        query = st.text_input(
            "Enter your search query:",
            placeholder="e.g., 'function that handles user authentication and session management'",
        )

    # Filters
    with st.expander("🎛️ Advanced Filters (Endee $eq/$in/$range)"):
        fcol1, fcol2, fcol3 = st.columns(3)
        with fcol1:
            language_filter = st.selectbox(
                "Language ($eq filter)",
                [None, "python", "javascript", "java"],
            )
        with fcol2:
            unit_type_filter = st.selectbox(
                "Unit Type ($eq filter)",
                [None, "function", "class", "module"],
            )
        with fcol3:
            top_k = st.slider("Results (top_k)", 1, 50, 10)

        rcol1, rcol2 = st.columns(2)
        with rcol1:
            complexity_range = st.slider(
                "Complexity Range ($range filter)", 1, 30, (1, 30)
            )
        with rcol2:
            loc_range = st.slider(
                "Lines of Code Range ($range filter)", 3, 500, (3, 500)
            )

    # Search execution
    if st.button("🚀 Search", type="primary", use_container_width=True):
        if not query:
            st.warning("Please enter a search query.")
        else:
            with st.spinner("Searching Endee..."):
                try:
                    from core.embedder import CodeEmbedder
                    from core.sparse import SparseVectorGenerator
                    from core.searcher import CodeSearcher

                    if st.session_state.embedder is None:
                        st.session_state.embedder = CodeEmbedder()

                    sparse_gen = SparseVectorGenerator()
                    searcher = CodeSearcher(
                        embedder=st.session_state.embedder,
                        sparse_gen=sparse_gen,
                    )

                    if search_mode == "Dense (Semantic)":
                        results = searcher.search_dense(
                            query=query,
                            top_k=top_k,
                            language=language_filter,
                            unit_type=unit_type_filter,
                            min_complexity=complexity_range[0],
                            max_complexity=complexity_range[1],
                            min_loc=loc_range[0],
                            max_loc=loc_range[1],
                        )
                    elif search_mode == "Hybrid (Semantic + Keyword)":
                        results = searcher.search_hybrid(
                            query=query,
                            top_k=top_k,
                            language=language_filter,
                            unit_type=unit_type_filter,
                        )
                    else:
                        results = searcher.find_similar_code(
                            code_snippet=query, top_k=top_k
                        )

                    if results:
                        st.success(f"Found {len(results)} results!")
                        for i, result in enumerate(results):
                            with st.container():
                                col1, col2 = st.columns([3, 1])
                                with col1:
                                    st.markdown(
                                        f"**{i+1}. {result.metadata.get('name', 'Unknown')}** "
                                        f"— `{result.metadata.get('file_path', '')}`"
                                    )
                                with col2:
                                    st.markdown(
                                        f'<span class="similarity-badge">'
                                        f"Similarity: {result.similarity:.4f}</span>",
                                        unsafe_allow_html=True,
                                    )
                                meta = result.metadata
                                st.caption(
                                    f"📝 {meta.get('unit_type', '?')} | "
                                    f"🌐 {meta.get('language', '?')} | "
                                    f"📏 {meta.get('loc', '?')} LOC | "
                                    f"🔄 Complexity: {meta.get('complexity', '?')}"
                                )
                                st.divider()
                    else:
                        st.info("No results found. Try a different query or check if data has been ingested.")

                except Exception as e:
                    st.error(f"Search failed: {e}")
                    st.info("Make sure Endee is running and data has been indexed.")


# ─── Health Analysis Page ────────────────────────────────────────────
elif page == "🏥 Health Analysis":
    st.markdown("## 🏥 Codebase Health Analysis")
    st.markdown("Diagnose your codebase by comparing against known anti-patterns in Endee.")
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

    repo_path = st.text_input(
        "📁 Repository Path:",
        placeholder="/path/to/your/repository",
    )

    if st.button("🔬 Analyze Codebase", type="primary", use_container_width=True):
        if not repo_path:
            st.warning("Please provide a repository path.")
        else:
            with st.spinner("Analyzing codebase health..."):
                try:
                    from core.parser import CodeParser
                    from core.embedder import CodeEmbedder
                    from core.searcher import CodeSearcher
                    from core.analyzer import CodeHealthAnalyzer

                    parser = CodeParser()
                    units = parser.parse_directory(repo_path)

                    if not units:
                        st.error("No code units found in the specified path.")
                    else:
                        if st.session_state.embedder is None:
                            st.session_state.embedder = CodeEmbedder()

                        searcher = CodeSearcher(embedder=st.session_state.embedder)
                        analyzer = CodeHealthAnalyzer(searcher=searcher)
                        report = analyzer.analyze_codebase(units)
                        st.session_state.health_report = report
                        st.session_state.parsed_units = units

                except Exception as e:
                    st.error(f"Analysis failed: {e}")

    # Display health report
    if st.session_state.health_report:
        report = st.session_state.health_report
        report_dict = report.to_dict()

        # Grade display
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            grade_class = f"grade-{report_dict['grade']}"
            st.markdown(
                f'<div style="text-align:center">'
                f'<div class="grade-badge {grade_class}">{report_dict["grade"]}</div>'
                f'<p style="margin-top:8px;color:#8B8BA3">Overall Grade</p>'
                f"</div>",
                unsafe_allow_html=True,
            )

        with col2:
            st.metric("Health Score", f"{report_dict['overall_score']}/100")

        with col3:
            st.metric("Total Violations", report_dict["total_violations"])

        with col4:
            st.metric("Units Analyzed", report_dict["total_units_analyzed"])

        st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

        # Metrics
        st.markdown("### 📊 Codebase Metrics")
        mcol1, mcol2, mcol3, mcol4 = st.columns(4)
        metrics = report_dict["metrics"]
        with mcol1:
            st.metric("Total LOC", f"{metrics['total_loc']:,}")
        with mcol2:
            st.metric("Avg Complexity", metrics["avg_complexity"])
        with mcol3:
            st.metric("Documentation", f"{metrics['documentation_ratio']}%")
        with mcol4:
            st.metric("Functions", metrics["function_count"])

        # Violations breakdown
        if report.violations:
            st.markdown("### ⚠️ Violations")

            import plotly.express as px
            import pandas as pd

            # Severity chart
            severity_data = {
                "Severity": ["Critical", "High", "Medium", "Low"],
                "Count": [
                    report_dict["critical_violations"],
                    report_dict["high_violations"],
                    report_dict["medium_violations"],
                    report_dict["low_violations"],
                ],
            }
            df = pd.DataFrame(severity_data)
            fig = px.bar(
                df,
                x="Severity",
                y="Count",
                color="Severity",
                color_discrete_map={
                    "Critical": "#D63031",
                    "High": "#E17055",
                    "Medium": "#FDCB6E",
                    "Low": "#74B9FF",
                },
            )
            fig.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                showlegend=False,
            )
            st.plotly_chart(fig, use_container_width=True)

            # Violation details
            for v in report.violations[:20]:
                severity_colors = {
                    "critical": "🔴",
                    "high": "🟠",
                    "medium": "🟡",
                    "low": "🔵",
                }
                icon = severity_colors.get(v.severity, "⚪")
                with st.expander(
                    f"{icon} [{v.severity.upper()}] {v.pattern_name} — {v.code_unit_name}"
                ):
                    st.write(f"**File:** `{v.code_unit_file}`")
                    st.write(f"**Description:** {v.description}")
                    st.write(f"**Suggestion:** {v.suggestion}")
                    st.progress(v.similarity, text=f"Similarity: {v.similarity:.2%}")


# ─── Evolution Page ──────────────────────────────────────────────────
elif page == "📈 Evolution":
    st.markdown("## 📈 Architecture Evolution Tracker")
    st.markdown("Visualize how your codebase's vector genome evolves over time.")
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

    repo_path = st.text_input(
        "📁 Repository Path for Evolution Analysis:",
        placeholder="/path/to/your/repository",
    )

    if st.button("🧬 Generate Evolution Map", type="primary", use_container_width=True):
        if not repo_path:
            st.warning("Please provide a repository path.")
        else:
            with st.spinner("Generating code genome map..."):
                try:
                    from core.parser import CodeParser
                    from core.embedder import CodeEmbedder
                    from core.evolution import EvolutionTracker

                    parser = CodeParser()
                    units = parser.parse_directory(repo_path)

                    if not units:
                        st.error("No code units found.")
                    else:
                        if st.session_state.embedder is None:
                            st.session_state.embedder = CodeEmbedder()

                        tracker = EvolutionTracker(embedder=st.session_state.embedder)

                        # Generate 2D projection
                        projection = tracker.get_embedding_projections(
                            units, method="tsne", n_components=2
                        )

                        st.session_state.evolution_data = projection
                        st.session_state.parsed_units = units

                except Exception as e:
                    st.error(f"Evolution analysis failed: {e}")

    if st.session_state.evolution_data:
        import plotly.express as px
        import pandas as pd

        proj = st.session_state.evolution_data
        df = pd.DataFrame(proj["points"])

        # 2D scatter plot of code genome
        fig = px.scatter(
            df,
            x="x",
            y="y",
            color="language",
            symbol="type",
            size="complexity",
            hover_name="name",
            hover_data=["file", "loc", "complexity"],
            title="🧬 Code Genome Map (t-SNE Projection)",
            color_discrete_map={
                "python": "#6C5CE7",
                "javascript": "#FDCB6E",
                "java": "#E17055",
            },
        )
        fig.update_layout(
            plot_bgcolor="rgba(15,15,26,0.8)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#EAEAEA",
            height=600,
        )
        fig.update_traces(marker=dict(line=dict(width=0.5, color="#333")))
        st.plotly_chart(fig, use_container_width=True)

        # Genome statistics
        st.markdown("### 📊 Genome Statistics")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Code Units", len(df))
        with col2:
            st.metric("Languages", df["language"].nunique())
        with col3:
            st.metric("Avg Complexity", round(df["complexity"].mean(), 1))
        with col4:
            st.metric("Total LOC", df["loc"].sum())

        # Language distribution
        lang_fig = px.pie(
            df,
            names="language",
            title="Language Distribution",
            color="language",
            color_discrete_map={
                "python": "#6C5CE7",
                "javascript": "#FDCB6E",
                "java": "#E17055",
            },
        )
        lang_fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#EAEAEA",
        )

        type_fig = px.histogram(
            df,
            x="type",
            color="language",
            title="Code Unit Types by Language",
            color_discrete_map={
                "python": "#6C5CE7",
                "javascript": "#FDCB6E",
                "java": "#E17055",
            },
        )
        type_fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#EAEAEA",
        )

        tcol1, tcol2 = st.columns(2)
        with tcol1:
            st.plotly_chart(lang_fig, use_container_width=True)
        with tcol2:
            st.plotly_chart(type_fig, use_container_width=True)


# ─── Settings Page ───────────────────────────────────────────────────
elif page == "⚙️ Settings":
    st.markdown("## ⚙️ Settings & Configuration")
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

    # Endee Configuration
    st.markdown("### 🔌 Endee Configuration")
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("Host", value=config.ENDEE_HOST, disabled=True)
    with col2:
        st.text_input("Port", value=str(config.ENDEE_PORT), disabled=True)

    # Index Management
    st.markdown("### 📦 Index Management")
    try:
        from endee import Endee
        client = Endee()
        client.set_base_url(f"http://{config.ENDEE_HOST}:{config.ENDEE_PORT}/api/v1")
        indexes = client.list_indexes()

        if indexes:
            import pandas as pd
            idx_data = []
            for idx in indexes:
                idx_data.append({
                    "Name": idx.get("name", ""),
                    "Dimension": idx.get("dimension", ""),
                    "Space Type": idx.get("space_type", ""),
                })
            st.dataframe(pd.DataFrame(idx_data), use_container_width=True)
        else:
            st.info("No indexes found. Run the ingestion script first.")
    except Exception as e:
        st.warning(f"Cannot connect to Endee: {e}")

    # Model info
    st.markdown("### 🤖 Embedding Model")
    st.code(f"Model: {config.EMBEDDING_MODEL}\nDimension: {config.DENSE_DIMENSION}")

    # About
    st.markdown("### ℹ️ About CodeDNA")
    st.markdown(
        f"""
        **CodeDNA** v{config.APP_VERSION}

        An AI-powered codebase genome analyzer built on the **Endee** vector database.
        Uses dense + hybrid vector search to provide semantic code intelligence.

        📖 [Endee Documentation](https://docs.endee.io)
        📂 [Endee GitHub](https://github.com/endee-io/endee)
        """
    )
