"""CodeDNA Light SaaS Design System"""

THEME_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
    --bg: #FAFAFA;
    --surface: #FFFFFF;
    --border: #E5E7EB;
    --text-main: #111827;
    --text-muted: #4B5563;
    --text-light: #9CA3AF;
    --primary: #4F46E5;
    --primary-hover: #4338CA;
    --primary-light: #EEF2FF;
    --accent: #0D9488;
    --danger: #EF4444;
    --danger-light: #FEF2F2;
    --success: #10B981;
    --success-light: #F0FDF4;
    --radius: 12px;
    --radius-full: 9999px;
    --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
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
.c-heading { font-family: var(--font-heading); color: var(--text-main); font-weight: 800; line-height: 1.2; }
.c-text { color: var(--text-muted); line-height: 1.6; }

/* 1. NAVBAR */
.c-navbar {
    display: flex; justify-content: space-between; align-items: center;
    padding: 16px 32px; background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px); border-bottom: 1px solid var(--border);
    position: sticky; top: 0; z-index: 1000;
    margin: -3rem -3rem 2rem -3rem; /* Offset Streamlit default padding */
    box-shadow: var(--shadow-sm);
}
.c-logo { font-size: 1.25rem; font-weight: 800; color: var(--text-main); display: flex; align-items: center; gap: 8px; }
.c-nav-links { display: flex; gap: 24px; align-items: center; }
.c-nav-link { font-weight: 600; color: var(--text-muted); text-decoration: none; font-size: 0.95rem; transition: color 0.2s; }
.c-nav-link:hover { color: var(--primary); }
.c-btn { display: inline-block; padding: 12px 24px; border-radius: var(--radius-full); font-weight: 600; text-decoration: none; transition: all 0.2s; cursor: pointer; text-align: center; border: none; font-family: var(--font-body); }
.c-btn-primary { background-color: var(--primary); color: #FFFFFF !important; box-shadow: var(--shadow); }
.c-btn-primary:hover { background-color: var(--primary-hover); transform: translateY(-2px); box-shadow: var(--shadow-lg); }
.c-btn-secondary { background-color: transparent; color: var(--text-main) !important; border: 2px solid var(--border); }
.c-btn-secondary:hover { border-color: var(--text-muted); background-color: #F9FAFB; }

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
.c-mockup-header { height: 32px; background: #F3F4F6; border-bottom: 1px solid var(--border); display: flex; align-items: center; padding: 0 16px; gap: 6px; }
.c-mockup-dot { width: 10px; height: 10px; border-radius: 50%; background: #D1D5DB; }
.c-mockup-dot:nth-child(1) { background: #FECACA; }
.c-mockup-dot:nth-child(2) { background: #FEF08A; }
.c-mockup-dot:nth-child(3) { background: #BBF7D0; }
.c-mockup-body { flex: 1; background: repeating-linear-gradient(45deg, #F9FAFB, #F9FAFB 10px, #F3F4F6 10px, #F3F4F6 20px); display: flex; align-items: center; justify-content: center; color: var(--text-muted); font-weight: 600; font-family: var(--font-body); }

/* 3. SOCIAL PROOF */
.c-social-proof { text-align: center; padding: 40px 0; border-top: 1px solid var(--border); border-bottom: 1px solid var(--border); margin: 40px 0; }
.c-social-proof p { font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px; color: var(--text-light); font-weight: 700; margin-bottom: 24px; }
.c-social-logos { display: flex; justify-content: center; gap: 48px; opacity: 0.5; flex-wrap: wrap; }
.c-logo-placeholder { font-weight: 800; font-size: 1.25rem; color: var(--text-muted); font-family: var(--font-heading); }

/* 4. OLD WAY VS NEW WAY */
.c-section { padding: 60px 0; }
.c-section-title { text-align: center; font-size: 2.5rem; margin-bottom: 48px; }
.c-compare { display: grid; grid-template-columns: 1fr 1fr; gap: 32px; }
.c-compare-card { padding: 40px; border-radius: var(--radius); }
.c-card-old { background: var(--danger-light); border: 1px solid #FCA5A5; }
.c-card-old h3 { color: var(--danger); margin-bottom: 24px; font-size: 1.5rem; display: flex; align-items: center; gap: 8px; }
.c-card-new { background: var(--success-light); border: 1px solid #86EFAC; box-shadow: var(--shadow); }
.c-card-new h3 { color: var(--success); margin-bottom: 24px; font-size: 1.5rem; display: flex; align-items: center; gap: 8px; }
.c-compare-list { list-style: none; padding: 0; margin: 0; }
.c-compare-list li { margin-bottom: 16px; display: flex; gap: 12px; align-items: flex-start; color: var(--text-main); font-weight: 500; font-size: 1.1rem; }

/* 5. BENEFITS */
.c-benefits { display: grid; grid-template-columns: repeat(3, 1fr); gap: 24px; }
.c-benefit-card { background: var(--surface); padding: 32px; border-radius: var(--radius); border: 1px solid var(--border); box-shadow: var(--shadow-sm); transition: transform 0.2s; }
.c-benefit-card:hover { transform: translateY(-4px); box-shadow: var(--shadow); }
.c-benefit-icon { width: 56px; height: 56px; background: var(--primary-light); color: var(--primary); border-radius: 16px; display: flex; align-items: center; justify-content: center; font-size: 1.75rem; margin-bottom: 24px; }
.c-benefit-title { font-weight: 700; font-size: 1.25rem; margin-bottom: 12px; color: var(--text-main); }
.c-benefit-desc { color: var(--text-muted); font-size: 1rem; }

/* 6. HOW IT WORKS */
.c-steps { display: grid; grid-template-columns: repeat(3, 1fr); gap: 32px; position: relative; }
.c-step { text-align: center; padding: 24px; }
.c-step-num { width: 56px; height: 56px; background: var(--primary); color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 1.5rem; margin: 0 auto 24px auto; box-shadow: var(--shadow); }
.c-step-title { font-weight: 800; font-size: 1.25rem; margin-bottom: 12px; color: var(--text-main); }
.c-step-desc { color: var(--text-muted); font-size: 1rem; }

/* 8. PRICING */
.c-pricing { display: grid; grid-template-columns: repeat(3, 1fr); gap: 24px; align-items: center; margin-top: 48px; }
.c-price-card { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 40px 32px; text-align: center; }
.c-price-card.c-popular { border: 2px solid var(--primary); transform: scale(1.05); box-shadow: var(--shadow-lg); position: relative; }
.c-popular-badge { position: absolute; top: -14px; left: 50%; transform: translateX(-50%); background: var(--primary); color: white; padding: 6px 16px; border-radius: var(--radius-full); font-size: 0.75rem; font-weight: 800; text-transform: uppercase; letter-spacing: 1px; }
.c-price-name { font-weight: 700; color: var(--text-muted); margin-bottom: 16px; text-transform: uppercase; letter-spacing: 1px; font-family: var(--font-heading); }
.c-price-val { font-size: 3.5rem; font-weight: 800; color: var(--text-main); margin-bottom: 8px; font-family: var(--font-heading); }
.c-price-features { list-style: none; padding: 0; margin: 32px 0; text-align: left; }
.c-price-features li { padding: 12px 0; color: var(--text-muted); border-bottom: 1px solid var(--border); font-size: 1rem; display: flex; gap: 12px; align-items: center;}

/* 10. FINAL CTA */
.c-final-cta { background: var(--primary); border-radius: var(--radius); padding: 80px 32px; text-align: center; color: white; margin: 80px 0 40px 0; box-shadow: var(--shadow-lg); }
.c-final-cta h2 { color: white !important; font-size: 3rem; font-weight: 800; margin-bottom: 24px; letter-spacing: -1px; }
.c-final-cta p { font-size: 1.25rem; opacity: 0.9; margin-bottom: 40px; max-width: 600px; margin-left: auto; margin-right: auto; }
.c-btn-white { background: white; color: var(--primary) !important; display: inline-block; padding: 16px 40px; border-radius: var(--radius-full); font-weight: 800; font-size: 1.1rem; text-decoration: none; box-shadow: var(--shadow); transition: transform 0.2s; }
.c-btn-white:hover { transform: translateY(-4px); box-shadow: var(--shadow-lg); }

/* 11. FOOTER */
.c-footer { border-top: 1px solid var(--border); padding: 48px 0; display: flex; justify-content: space-between; align-items: center; color: var(--text-muted); font-size: 0.95rem; }
.c-footer-links { display: flex; gap: 32px; }
.c-footer-links a { color: var(--text-muted); text-decoration: none; font-weight: 500; }
.c-footer-links a:hover { color: var(--primary); }

/* =========================================
   STREAMLIT WIDGET OVERRIDES (Minimal & Safe)
   ========================================= */
/* Metric overrides */
div[data-testid="stMetricValue"] { color: var(--text-main) !important; font-weight: 800 !important; font-family: var(--font-heading) !important; }
div[data-testid="stMetricLabel"] { color: var(--text-muted) !important; font-weight: 600 !important; }

/* Expander (FAQ) overrides */
div[data-testid="stExpander"] { background: var(--surface) !important; border: 1px solid var(--border) !important; border-radius: var(--radius) !important; margin-bottom: 16px; box-shadow: var(--shadow-sm); }
div[data-testid="stExpander"] details summary { padding: 16px !important; }
div[data-testid="stExpander"] details summary p { font-family: var(--font-heading) !important; font-weight: 700 !important; color: var(--text-main) !important; font-size: 1.1rem !important; margin: 0 !important; }

/* Explicit isolation for Streamlit native text */
.stMarkdown { color: var(--text-main) !important; }
h1, h2, h3 { font-family: var(--font-heading) !important; color: var(--text-main) !important; font-weight: 800 !important; }

/* Buttons */
.stButton > button[kind="primary"] { background: var(--primary) !important; color: white !important; border: none !important; border-radius: var(--radius-full) !important; font-weight: 600 !important; padding: 8px 24px !important; font-family: var(--font-body) !important; box-shadow: var(--shadow); transition: all 0.2s !important; }
.stButton > button[kind="primary"]:hover { background: var(--primary-hover) !important; transform: translateY(-2px); box-shadow: var(--shadow-lg); }
</style>
"""
