"""CodeDNA Dark SaaS Design System"""

THEME_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
    --bg: #0B0D17;
    --surface: #111425;
    --border: #1E2140;
    --border-hover: #2A2E50;
    --text-main: #FFFFFF;
    --text-muted: #B0B4D0;
    --text-light: #6B70A0;
    --primary: #7C5CFC;
    --primary-hover: #6A4DE8;
    --primary-light: rgba(124, 92, 252, 0.15);
    --accent: #00D4AA;
    --danger: #EF4444;
    --danger-light: rgba(239, 68, 68, 0.1);
    --success: #10B981;
    --success-light: rgba(16, 185, 129, 0.1);
    --radius: 12px;
    --radius-full: 9999px;
    --shadow-sm: 0 4px 20px rgba(0, 0, 0, 0.3);
    --shadow: 0 8px 30px rgba(0, 0, 0, 0.4);
    --shadow-lg: 0 12px 40px rgba(0, 0, 0, 0.5);
    --shadow-glow: 0 0 24px rgba(124, 92, 252, 0.4);
    --font-heading: 'Plus Jakarta Sans', sans-serif;
    --font-body: 'Plus Jakarta Sans', sans-serif;
}

/* Base App Colors */
.stApp {
    background-color: var(--bg);
}

/* =========================================
   CUSTOM SAAS CLASSES (Safe from Streamlit UI overrides)
   ========================================= */
.c-font { font-family: var(--font-body); }
.c-heading { font-family: var(--font-heading); color: var(--text-main) !important; font-weight: 800; line-height: 1.2; }
.c-text { color: var(--text-muted); line-height: 1.6; }

/* 1. NAVBAR */
.c-navbar {
    display: flex; justify-content: space-between; align-items: center;
    padding: 16px 32px; background: rgba(11, 13, 23, 0.85);
    backdrop-filter: blur(16px); border-bottom: 1px solid var(--border);
    position: sticky; top: 0; z-index: 1000;
    margin: -3rem -3rem 2rem -3rem; /* Offset Streamlit default padding */
    box-shadow: var(--shadow-sm);
}
.c-logo { font-size: 1.25rem; font-weight: 800; color: var(--text-main); display: flex; align-items: center; gap: 8px; }
.c-nav-links { display: flex; gap: 24px; align-items: center; }
.c-nav-link { font-weight: 600; color: var(--text-muted); text-decoration: none; font-size: 0.95rem; transition: color 0.2s; }
.c-nav-link:hover { color: var(--text-main); }
.c-btn { display: inline-block; padding: 12px 24px; border-radius: var(--radius-full); font-weight: 600; text-decoration: none; transition: all 0.2s; cursor: pointer; text-align: center; border: none; font-family: var(--font-body); }
.c-btn-primary { background-color: var(--primary); color: #FFFFFF !important; box-shadow: var(--shadow); }
.c-btn-primary:hover { background-color: var(--primary-hover); transform: translateY(-2px); box-shadow: var(--shadow-glow); }
.c-btn-secondary { background-color: transparent; color: var(--text-muted) !important; border: 2px solid var(--border); }
.c-btn-secondary:hover { border-color: var(--text-main); color: var(--text-main) !important; background-color: rgba(255, 255, 255, 0.03); }

/* 2. HERO */
.c-hero { display: flex; align-items: center; gap: 48px; padding: 60px 0 40px 0; }
.c-hero-left { flex: 1; }
.c-hero-right { flex: 1; display: flex; justify-content: center; }
.c-hero h1 { font-size: 3.5rem; margin-bottom: 24px; letter-spacing: -1px; }
.c-hero p { font-size: 1.25rem; margin-bottom: 32px; }
.c-hero-buttons { display: flex; gap: 16px; }

/* Mockup Container */
.c-mockup {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: var(--radius); box-shadow: var(--shadow-lg);
    width: 100%; aspect-ratio: 16/10; overflow: hidden;
    display: flex; flex-direction: column;
}
.c-mockup-header { height: 32px; background: #0A0C15; border-bottom: 1px solid var(--border); display: flex; align-items: center; padding: 0 16px; gap: 6px; }
.c-mockup-dot { width: 10px; height: 10px; border-radius: 50%; background: #33364D; }
.c-mockup-dot:nth-child(1) { background: #EF4444; }
.c-mockup-dot:nth-child(2) { background: #EAB308; }
.c-mockup-dot:nth-child(3) { background: #10B981; }
.c-mockup-body { flex: 1; background: #000; overflow: hidden; display: flex; align-items: center; justify-content: center; color: var(--text-muted); font-weight: 600; font-family: var(--font-body); }
.c-mockup-body video { width: 100%; height: 100%; object-fit: cover; }

/* 3. SOCIAL PROOF */
.c-social-proof { text-align: center; padding: 40px 0; border-top: 1px solid var(--border); border-bottom: 1px solid var(--border); margin: 40px 0; }
.c-social-proof p { font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px; color: var(--text-light); font-weight: 700; margin-bottom: 24px; }
.c-social-logos { display: flex; justify-content: center; gap: 48px; opacity: 0.6; flex-wrap: wrap; }
.c-logo-placeholder { font-weight: 800; font-size: 1.25rem; color: var(--text-muted); font-family: var(--font-heading); }

/* 4. OLD WAY VS NEW WAY */
.c-section { padding: 60px 0; }
.c-section-title { text-align: center; font-size: 2.5rem; margin-bottom: 48px; color: var(--text-main); font-family: var(--font-heading); font-weight: 800;}
.c-compare { display: grid; grid-template-columns: 1fr 1fr; gap: 32px; }
.c-compare-card { padding: 40px; border-radius: var(--radius); }
.c-card-old { background: var(--danger-light); border: 1px solid rgba(239, 68, 68, 0.3); }
.c-card-old h3 { color: #FCA5A5; margin-bottom: 24px; font-size: 1.5rem; display: flex; align-items: center; gap: 8px; font-family: var(--font-heading); font-weight: 800; }
.c-card-new { background: var(--success-light); border: 1px solid rgba(16, 185, 129, 0.3); box-shadow: var(--shadow); }
.c-card-new h3 { color: #86EFAC; margin-bottom: 24px; font-size: 1.5rem; display: flex; align-items: center; gap: 8px; font-family: var(--font-heading); font-weight: 800; }
.c-compare-list { list-style: none; padding: 0; margin: 0; }
.c-compare-list li { margin-bottom: 16px; display: flex; gap: 12px; align-items: flex-start; color: var(--text-main); font-weight: 500; font-size: 1.1rem; }

/* 5. BENEFITS */
.c-benefits { display: grid; grid-template-columns: repeat(3, 1fr); gap: 24px; }
.c-benefit-card { background: var(--surface); padding: 32px; border-radius: var(--radius); border: 1px solid var(--border); box-shadow: var(--shadow-sm); transition: transform 0.2s; }
.c-benefit-card:hover { transform: translateY(-4px); box-shadow: var(--shadow); border-color: var(--border-hover); }
.c-benefit-icon { width: 56px; height: 56px; background: var(--primary-light); color: var(--primary); border-radius: 16px; display: flex; align-items: center; justify-content: center; font-size: 1.75rem; margin-bottom: 24px; }
.c-benefit-title { font-weight: 700; font-size: 1.25rem; margin-bottom: 12px; color: var(--text-main); }
.c-benefit-desc { color: var(--text-muted); font-size: 1rem; }

/* 6. HOW IT WORKS */
.c-steps { display: grid; grid-template-columns: repeat(3, 1fr); gap: 32px; position: relative; }
.c-step { text-align: center; padding: 24px; }
.c-step-num { width: 56px; height: 56px; background: var(--primary); color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 1.5rem; margin: 0 auto 24px auto; box-shadow: var(--shadow-glow); }
.c-step-title { font-weight: 800; font-size: 1.25rem; margin-bottom: 12px; color: var(--text-main); }
.c-step-desc { color: var(--text-muted); font-size: 1rem; }

/* 10. FINAL CTA */
.c-final-cta { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 80px 32px; text-align: center; color: white; margin: 80px 0 40px 0; box-shadow: var(--shadow-lg); position: relative; overflow: hidden; }
.c-final-cta::before { content:''; position:absolute; top:-50%; left:-50%; width:200%; height:200%; background: linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%); opacity: 0.1; }
.c-final-cta h2 { color: var(--text-main) !important; font-size: 3rem; font-weight: 800; margin-bottom: 24px; letter-spacing: -1px; position:relative; }
.c-final-cta p { font-size: 1.25rem; color: var(--text-muted); margin-bottom: 40px; max-width: 600px; margin-left: auto; margin-right: auto; position:relative; }
.c-btn-white { background: var(--primary); color: #FFF !important; display: inline-block; padding: 16px 40px; border-radius: var(--radius-full); font-weight: 800; font-size: 1.1rem; text-decoration: none; box-shadow: var(--shadow); transition: transform 0.2s; position:relative; z-index:1; }
.c-btn-white:hover { transform: translateY(-4px); box-shadow: var(--shadow-glow); background: var(--primary-hover); }

/* 11. FOOTER */
.c-footer { border-top: 1px solid var(--border); padding: 48px 0; display: flex; justify-content: space-between; align-items: center; color: var(--text-muted); font-size: 0.95rem; margin-top: 40px; }
.c-footer-links { display: flex; gap: 32px; }
.c-footer-links a { color: var(--text-muted); text-decoration: none; font-weight: 500; }
.c-footer-links a:hover { color: var(--text-main); }

/* =========================================
   STREAMLIT WIDGET OVERRIDES (Minimal & Safe)
   ========================================= */
/* Metric overrides */
div[data-testid="stMetricValue"] { color: var(--text-main) !important; font-weight: 800 !important; font-family: var(--font-heading) !important; }
div[data-testid="stMetricLabel"] { color: var(--text-muted) !important; font-weight: 600 !important; }

/* Expander (FAQ) overrides */
div[data-testid="stExpander"] { background: var(--surface) !important; border: 1px solid var(--border) !important; border-radius: var(--radius) !important; margin-bottom: 16px; box-shadow: var(--shadow-sm); }
div[data-testid="stExpander"]:hover { border-color: var(--border-hover) !important; }
div[data-testid="stExpander"] details summary { padding: 16px !important; }
div[data-testid="stExpander"] details summary p { font-family: var(--font-heading) !important; font-weight: 700 !important; color: var(--text-main) !important; font-size: 1.1rem !important; margin: 0 !important; }
div[data-testid="stExpander"] details summary svg { fill: var(--text-main) !important; }

/* Explicit isolation for Streamlit native text */
.stMarkdown { color: var(--text-muted) !important; }
.stMarkdown p { color: var(--text-muted) !important; font-family: var(--font-body); }
h1, h2, h3 { font-family: var(--font-heading) !important; color: var(--text-main) !important; font-weight: 800 !important; }

/* Buttons */
.stButton > button[kind="primary"] { background: var(--primary) !important; color: white !important; border: none !important; border-radius: var(--radius-full) !important; font-weight: 600 !important; padding: 8px 24px !important; font-family: var(--font-body) !important; box-shadow: var(--shadow-glow); transition: all 0.2s !important; }
.stButton > button[kind="primary"]:hover { background: var(--primary-hover) !important; transform: translateY(-2px); box-shadow: var(--shadow-glow); }
.stTextInput > div > div > input { background: var(--surface) !important; color: var(--text-main) !important; border: 1px solid var(--border) !important; border-radius: var(--radius) !important; font-weight: 500;}
.stTextInput > div > div > input:focus { border-color: var(--primary) !important; box-shadow: 0 0 0 2px rgba(124, 92, 252, 0.2) !important;}
</style>
"""
