import streamlit as st
import pdfplumber
import requests
import json
import re
import os
import time
from datetime import datetime
import html

# ============================================
# CONFIGURATION
# ============================================
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"
TAVILY_API_URL = "https://api.tavily.com/search"

# ============================================
# PAGE CONFIGURATION
# ============================================
st.set_page_config(
    page_title="FactCheck AI — Truth Layer",
    page_icon="✅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CSS STYLING — Premium Professional Redesign
# ============================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&display=swap');

:root {
    --bg-primary: #080c14;
    --bg-secondary: #0d1321;
    --bg-card: #111827;
    --bg-card-hover: #141e2e;
    --border-subtle: rgba(255,255,255,0.06);
    --border-accent: rgba(56,189,248,0.25);
    --accent-cyan: #38bdf8;
    --accent-cyan-dim: rgba(56,189,248,0.12);
    --accent-emerald: #10b981;
    --accent-amber: #f59e0b;
    --accent-red: #f43f5e;
    --accent-violet: #8b5cf6;
    --text-primary: #f1f5f9;
    --text-secondary: #94a3b8;
    --text-muted: #475569;
    --font-display: 'Playfair Display', Georgia, serif;
    --font-body: 'DM Sans', system-ui, sans-serif;
}

* { font-family: var(--font-body) !important; }

.stApp {
    background: var(--bg-primary) !important;
    background-image:
        radial-gradient(ellipse 80% 50% at 50% -10%, rgba(56,189,248,0.08) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 90% 80%, rgba(139,92,246,0.05) 0%, transparent 50%),
        linear-gradient(180deg, #080c14 0%, #060a11 100%) !important;
}

#MainMenu, footer, header { visibility: hidden; }

/* ─── SIDEBAR ─── */
[data-testid="stSidebar"] {
    background: #09111f !important;
    border-right: 1px solid var(--border-subtle) !important;
}
[data-testid="stSidebar"] * { color: var(--text-secondary) !important; }
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] strong {
    color: var(--text-primary) !important;
    font-family: var(--font-body) !important;
}
[data-testid="stSidebar"] .stSuccess {
    background: rgba(16,185,129,0.08) !important;
    border: 1px solid rgba(16,185,129,0.2) !important;
    border-radius: 10px !important;
}
[data-testid="stSidebar"] .stError {
    background: rgba(244,63,94,0.08) !important;
    border: 1px solid rgba(244,63,94,0.2) !important;
    border-radius: 10px !important;
}

/* ─── HERO ─── */
.hero {
    position: relative;
    padding: 3.5rem 3rem;
    margin-bottom: 2rem;
    text-align: center;
    border-radius: 20px;
    background: linear-gradient(135deg, rgba(13,19,33,0.9), rgba(9,17,31,0.9));
    border: 1px solid var(--border-subtle);
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute;
    inset: 0;
    background: radial-gradient(ellipse 70% 60% at 50% 0%, rgba(56,189,248,0.06) 0%, transparent 70%);
    pointer-events: none;
}
.hero-eyebrow {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: rgba(56,189,248,0.08);
    border: 1px solid rgba(56,189,248,0.2);
    border-radius: 100px;
    padding: 0.3rem 1rem;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--accent-cyan);
    margin-bottom: 1.2rem;
}
.hero h1 {
    font-family: var(--font-display) !important;
    font-size: 3.6rem;
    font-weight: 800;
    letter-spacing: -0.02em;
    line-height: 1.1;
    color: var(--text-primary);
    margin: 0 0 0.5rem 0;
}
.hero h1 span {
    background: linear-gradient(135deg, var(--accent-cyan), #67e8f9, var(--accent-violet));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.hero-sub {
    color: var(--text-secondary);
    font-size: 1rem;
    font-weight: 400;
    margin: 0 auto 1.8rem;
    max-width: 480px;
    line-height: 1.6;
}
.pill-row {
    display: flex;
    gap: 0.5rem;
    justify-content: center;
    flex-wrap: wrap;
}
.pill {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 100px;
    padding: 0.3rem 0.9rem;
    font-size: 0.75rem;
    font-weight: 500;
    color: var(--text-secondary);
    letter-spacing: 0.01em;
}

/* ─── PROCESS STEPS ─── */
.steps {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1px;
    background: var(--border-subtle);
    border: 1px solid var(--border-subtle);
    border-radius: 16px;
    overflow: hidden;
    margin: 1.5rem 0 2rem;
}
.step-card {
    background: var(--bg-card);
    padding: 1.4rem 1.2rem;
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: 0.8rem;
    transition: background 0.2s;
}
.step-card:hover { background: var(--bg-card-hover); }
.step-num {
    font-family: var(--font-display) !important;
    font-size: 2rem;
    font-weight: 800;
    color: var(--accent-cyan);
    opacity: 0.35;
    line-height: 1;
}
.step-title {
    font-weight: 600;
    color: var(--text-primary);
    font-size: 0.9rem;
}
.step-desc {
    font-size: 0.78rem;
    color: var(--text-muted);
    line-height: 1.5;
}

/* ─── UPLOAD AREA ─── */
[data-testid="stFileUploader"] {
    background: var(--bg-card) !important;
    border: 1.5px dashed rgba(56,189,248,0.2) !important;
    border-radius: 14px !important;
    padding: 1rem !important;
    transition: border-color 0.2s !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: rgba(56,189,248,0.4) !important;
}
[data-testid="stFileUploader"] label {
    color: var(--text-secondary) !important;
    font-size: 0.9rem !important;
}

/* ─── BUTTON ─── */
.stButton > button {
    background: var(--accent-cyan) !important;
    color: #000 !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
    letter-spacing: 0.02em !important;
    padding: 0.75rem 2rem !important;
    width: 100% !important;
    transition: opacity 0.2s, transform 0.15s !important;
}
.stButton > button:hover {
    opacity: 0.88 !important;
    transform: translateY(-1px) !important;
}

/* ─── STAT CARDS ─── */
.stat-card {
    background: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-radius: 14px;
    padding: 1.2rem 1rem;
    text-align: center;
    position: relative;
    overflow: hidden;
}
.stat-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: currentColor;
    opacity: 0.4;
}
.stat-number {
    font-family: var(--font-display) !important;
    font-size: 2.4rem;
    font-weight: 800;
    line-height: 1;
    margin-bottom: 0.3rem;
}
.stat-label {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--text-muted);
}

/* ─── CLAIM CARDS ─── */
.claim-card {
    background: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-left: 3px solid;
    border-radius: 12px;
    padding: 1.3rem 1.4rem;
    margin-bottom: 0.85rem;
    transition: background 0.18s, transform 0.18s;
    position: relative;
}
.claim-card:hover {
    background: var(--bg-card-hover);
    transform: translateX(3px);
}
.verified   { border-left-color: var(--accent-emerald); }
.inaccurate { border-left-color: var(--accent-amber); }
.false      { border-left-color: var(--accent-red); }
.unverified { border-left-color: var(--accent-violet); }

.claim-text {
    font-size: 0.92rem;
    font-weight: 500;
    color: var(--text-primary);
    line-height: 1.55;
    margin: 0.7rem 0 0.5rem;
}
.claim-explanation {
    font-size: 0.82rem;
    color: var(--text-secondary);
    line-height: 1.6;
    margin: 0;
}

/* ─── BADGE ─── */
.badge {
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    padding: 0.22rem 0.7rem;
    border-radius: 100px;
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}
.bg-verified   { background: rgba(16,185,129,0.12); color: #34d399; border: 1px solid rgba(16,185,129,0.2); }
.bg-inaccurate { background: rgba(245,158,11,0.12); color: #fbbf24; border: 1px solid rgba(245,158,11,0.2); }
.bg-false      { background: rgba(244,63,94,0.12);  color: #fb7185; border: 1px solid rgba(244,63,94,0.2);  }
.bg-unverified { background: rgba(139,92,246,0.12); color: #a78bfa; border: 1px solid rgba(139,92,246,0.2); }

.conf-badge {
    font-size: 0.65rem;
    font-weight: 500;
    padding: 0.15rem 0.55rem;
    border-radius: 100px;
    background: rgba(255,255,255,0.05);
    color: var(--text-muted);
    border: 1px solid rgba(255,255,255,0.06);
}
.cat-badge {
    font-size: 0.62rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--text-muted);
}

/* ─── CORRECT FACT ─── */
.correct-fact {
    display: flex;
    align-items: flex-start;
    gap: 0.5rem;
    font-size: 0.8rem;
    color: #34d399;
    background: rgba(16,185,129,0.06);
    border: 1px solid rgba(16,185,129,0.15);
    padding: 0.6rem 0.9rem;
    border-radius: 8px;
    margin-top: 0.8rem;
    line-height: 1.5;
}

/* ─── SEARCH SNIPPET ─── */
.search-snippet {
    font-size: 0.73rem;
    color: var(--text-muted);
    background: rgba(255,255,255,0.02);
    border: 1px solid var(--border-subtle);
    border-radius: 8px;
    padding: 0.5rem 0.8rem;
    margin-top: 0.6rem;
    font-style: italic;
    line-height: 1.5;
}

/* ─── DIVIDERS & MISC ─── */
.section-header {
    font-family: var(--font-display) !important;
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--text-primary);
    margin: 0 0 0.3rem;
}
.section-sub {
    font-size: 0.82rem;
    color: var(--text-muted);
    margin-bottom: 1.4rem;
}

/* Streamlit widget overrides */
.stProgress > div > div {
    background: linear-gradient(90deg, var(--accent-cyan), var(--accent-violet)) !important;
    border-radius: 100px !important;
}
.stTabs [data-baseweb="tab-list"] {
    gap: 0 !important;
    background: var(--bg-card) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 10px !important;
    padding: 3px !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border-radius: 8px !important;
    color: var(--text-muted) !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    padding: 0.5rem 1rem !important;
}
.stTabs [aria-selected="true"] {
    background: rgba(56,189,248,0.1) !important;
    color: var(--accent-cyan) !important;
}
.stAlert {
    border-radius: 10px !important;
}
</style>
""", unsafe_allow_html=True)

# ============================================
# SIDEBAR
# ============================================
with st.sidebar:
    st.markdown("## System Status")
    st.markdown("---")
    groq_ok = bool(GROQ_API_KEY)
    tavily_ok = bool(TAVILY_API_KEY)
    st.success("✅ **Groq AI** — Active\n`llama-3.3-70b-versatile`") if groq_ok else st.error("❌ Groq API key missing")
    st.success("✅ **Tavily API** — Active\n🔍 AI-Powered Web Search") if tavily_ok else st.error("❌ Tavily API key missing")
    st.markdown("---")
    st.markdown("### Verdict Guide")
    st.markdown("✅ **Verified** — Matches current evidence")
    st.markdown("⚠️ **Inaccurate** — Outdated or numbers off")
    st.markdown("❌ **False** — Completely incorrect / fabricated")
    st.markdown("❓ **Unverified** — Cannot find reliable evidence")
    st.markdown("---")
    st.markdown("### Settings")
    max_claims = st.slider("Max Claims to Check", 5, 20, 12)
    show_snippets = st.checkbox("Show Web Search Snippets", value=False)
    st.markdown("---")
    st.markdown("### Features")
    st.markdown("- PDF Upload & Text Extraction")
    st.markdown("- AI-Powered Claim Identification")
    st.markdown("- Live Web Search (Tavily AI)")
    st.markdown("- Verdict with Correct Facts")
    st.markdown("- Source URLs in report")
    st.markdown("- JSON Report Download")

# ============================================
# API FUNCTIONS
# ============================================

def tavily_search(query, num_results=5):
    try:
        headers = {"Content-Type": "application/json"}
        payload = {
            "api_key": TAVILY_API_KEY,
            "query": query,
            "max_results": num_results,
            "include_answer": True,
            "include_raw_content": False
        }
        response = requests.post(TAVILY_API_URL, headers=headers, json=payload, timeout=30)
        data = response.json()
        results = []
        
        # Add AI-generated answer if available
        if data.get("answer"):
            results.append({
                "title": "AI Summary",
                "snippet": data.get("answer", ""),
                "link": ""
            })
        
        # Add search results
        for item in data.get("results", [])[:num_results]:
            snippet = item.get("content", "") or item.get("snippet", "")
            link = item.get("url", "")
            title = item.get("title", "")
            if snippet:
                results.append({
                    "title": title,
                    "snippet": snippet,
                    "link": link
                })
        
        return results
    except Exception as e:
        print(f"Tavily search error: {e}")
        return []


def format_search_for_prompt(results):
    if not results:
        return "No search results available."
    lines = []
    for i, r in enumerate(results, 1):
        lines.append(f"[{i}] {r['title']}\n{r['snippet']}")
    return "\n\n".join(lines)


def groq_call(system_prompt, user_prompt, max_tokens=2000, retry=0):
    try:
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        body = {
            "model": GROQ_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0,
            "max_tokens": max_tokens
        }
        response = requests.post(GROQ_API_URL, headers=headers, json=body, timeout=90)
        if response.status_code == 429:
            if retry < 4:
                wait_time = (retry + 1) * 6
                time.sleep(wait_time)
                return groq_call(system_prompt, user_prompt, max_tokens, retry + 1)
            return None
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception:
        if retry < 2:
            time.sleep(4)
            return groq_call(system_prompt, user_prompt, max_tokens, retry + 1)
        return None


def extract_pdf_text(file):
    pages_text = []
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                pages_text.append(text)
    return "\n\n".join(pages_text)


def extract_claims_with_llm(text, max_claims=12):
    truncated = text[:6000] if len(text) > 6000 else text
    system = """You are an expert fact-checker. Your job is to identify specific, verifiable factual claims from documents.

Focus on:
- Statistics and numbers (percentages, counts, revenue figures)
- Dates and timelines (founded year, launch date, milestones)
- Rankings and positions ("world's largest", "#1 in...")
- Named facts about companies, countries, people
- Scientific or technical figures
- Market size or share claims
- Growth rates and projections

AVOID extracting:
- Vague opinions or predictions without numbers
- Marketing slogans or subjective claims
- Very obvious/trivially true statements

Respond ONLY with a valid JSON array. No extra text."""

    user = f"""Extract up to {max_claims} specific, verifiable factual claims from this document. Each claim must be a complete sentence that can be independently fact-checked.

DOCUMENT:
{truncated}

Return JSON array:
[
  {{"claim": "The full claim sentence", "category": "statistic|date|ranking|technical|financial|other"}},
  ...
]"""

    response = groq_call(system, user, max_tokens=2000)
    if response:
        clean = re.sub(r"```(?:json)?", "", response).strip().rstrip("`").strip()
        match = re.search(r'\[.*\]', clean, re.DOTALL)
        if match:
            try:
                claims = json.loads(match.group())
                valid = []
                for c in claims:
                    if isinstance(c, dict) and "claim" in c and len(str(c["claim"])) > 15:
                        valid.append({
                            "claim": str(c["claim"]).strip(),
                            "category": str(c.get("category", "statistic")).lower()
                        })
                return valid[:max_claims]
            except json.JSONDecodeError:
                pass
    return extract_claims_regex(text, max_claims)


def extract_claims_regex(text, max_claims=12):
    claims = []
    sentences = re.split(r'(?<=[.!?])\s+', text)
    keywords = [
        'million', 'billion', 'crore', 'lakh', 'trillion',
        'percent', '%', '$', '₹', '€', '£',
        'revenue', 'profit', 'loss', 'earnings', 'valuation',
        'employees', 'workforce', 'subscribers', 'users',
        'founded', 'launched', 'released', 'established',
        'largest', 'biggest', 'fastest', 'first', 'leading',
        'population', 'ranked', 'position', 'market share',
        'growth', 'increase', 'decrease', 'declined', 'rose'
    ]
    for s in sentences:
        s = s.strip()
        if len(s) < 20 or len(s) > 400:
            continue
        has_number = bool(re.search(r'\d+', s))
        has_keyword = any(kw in s.lower() for kw in keywords)
        if has_number or has_keyword:
            s_clean = re.sub(r'^\d+[\.)\s]\s*', '', s)
            claims.append({"claim": s_clean, "category": "statistic"})
        if len(claims) >= max_claims:
            break
    return claims


def build_search_query(claim):
    stop = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'has', 'have', 'had',
            'that', 'this', 'with', 'for', 'and', 'or', 'but', 'in', 'on', 'at'}
    tokens = [t for t in re.findall(r'\b\w+\b', claim) if t.lower() not in stop]
    query = " ".join(tokens[:12])
    return query + " fact check"


def verify_claim(claim_text, show_snippet=False):
    search_query = build_search_query(claim_text)
    search_results = tavily_search(search_query, num_results=5)
    search_text = format_search_for_prompt(search_results)
    current_year = datetime.now().year

    system = """You are a rigorous, unbiased fact-checker. You verify claims against real-world evidence from web search results.

Rules:
- Verified: The claim's core facts match current search evidence
- Inaccurate: The claim has wrong numbers, wrong dates, or is significantly outdated
- False: The claim is completely fabricated or contradicts all evidence
- Unverified: Cannot find sufficient evidence to confirm or deny

Be especially strict about:
- Numbers and statistics (even small differences matter)
- Dates and years
- Superlatives like "world's largest" or "first ever"
- Market share or ranking claims

Always provide the correct fact with specific numbers if the claim is wrong. Respond ONLY with valid JSON."""

    user = f"""Fact-check this claim using the search results below.

CLAIM: "{claim_text}"

WEB SEARCH RESULTS (as of {current_year}):
{search_text}

Respond ONLY with this JSON (no extra text, no markdown):
{{
    "verdict": "Verified|Inaccurate|False|Unverified",
    "confidence": "High|Medium|Low",
    "explanation": "2-3 sentences explaining your verdict citing the search results",
    "correct_fact": "The correct fact with specific numbers if claim is wrong, else null",
    "search_query_used": "{search_query}"
}}"""

    response = groq_call(system, user, max_tokens=800)

    result = {
        "verdict": "Unverified",
        "confidence": "Low",
        "explanation": "Could not verify automatically.",
        "correct_fact": None,
        "search_snippets": search_results[:3] if show_snippet else []
    }

    if response:
        clean = re.sub(r"```(?:json)?", "", response).strip().rstrip("`").strip()
        match = re.search(r'\{.*\}', clean, re.DOTALL)
        if match:
            try:
                parsed = json.loads(match.group())
                result.update(parsed)
                result["search_snippets"] = search_results[:3] if show_snippet else []
            except json.JSONDecodeError:
                pass

    return result


# ============================================
# UI — HERO SECTION
# ============================================
st.markdown("""
<div class="hero">
    <div class="hero-eyebrow">⚡ AI-Powered · Live Web Search · Real-Time Verdicts</div>
    <h1>Fact<span>Check</span> AI</h1>
    <p class="hero-sub">
        Upload any PDF and let AI cross-reference every factual claim against live web sources — in seconds.
    </p>
    <div class="pill-row">
        <span class="pill">🧠 LLaMA 3.3 70B</span>
        <span class="pill">⚡ Groq LPU Inference</span>
        <span class="pill">🔍 Tavily AI Search</span>
        <span class="pill">📊 Confidence Scoring</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Steps
st.markdown("""
<div class="steps">
    <div class="step-card">
        <div class="step-num">01</div>
        <div class="step-title">Upload PDF</div>
        <div class="step-desc">Any text-based document — reports, press releases, research papers</div>
    </div>
    <div class="step-card">
        <div class="step-num">02</div>
        <div class="step-title">AI Extracts Claims</div>
        <div class="step-desc">LLM pinpoints every verifiable statistic, date, and assertion</div>
    </div>
    <div class="step-card">
        <div class="step-num">03</div>
        <div class="step-title">Live Web Verify</div>
        <div class="step-desc">Each claim cross-referenced against real-time Google search results</div>
    </div>
    <div class="step-card">
        <div class="step-num">04</div>
        <div class="step-title">Detailed Report</div>
        <div class="step-desc">Verdicts, confidence scores, correct facts, and downloadable JSON</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Upload + Button
uploaded_file = st.file_uploader(
    "📄 Drop your PDF here or click to browse",
    type=["pdf"],
    help="Upload any text-based PDF. Works great on marketing docs, reports, and press releases."
)

col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    analyze_btn = st.button("🚀 Start Fact-Checking", use_container_width=True, type="primary")

# ============================================
# PROCESSING PIPELINE
# ============================================
if analyze_btn:
    if not uploaded_file:
        st.error("❌ Please upload a PDF file first.")
        st.stop()

    st.info("🌐 **LIVE WEB SEARCH ENABLED** — Cross-referencing claims against real-time Tavily AI search results")

    with st.spinner("📄 Reading PDF and extracting text..."):
        try:
            pdf_text = extract_pdf_text(uploaded_file)
        except Exception as e:
            st.error(f"❌ PDF reading error: {e}")
            st.stop()

    if not pdf_text.strip():
        st.error("⚠️ No text found in this PDF. Please ensure it's a text-based (not scanned/image) PDF.")
        st.stop()

    char_count = len(pdf_text)
    st.success(f"✅ Extracted **{char_count:,} characters** from {uploaded_file.name}")

    with st.spinner("🤖 AI is identifying verifiable claims..."):
        claims = extract_claims_with_llm(pdf_text, max_claims=max_claims)

    if not claims:
        st.error("⚠️ No verifiable claims found. Make sure your PDF contains statistics, numbers, or factual assertions.")
        st.stop()

    st.success(f"✅ Identified **{len(claims)} verifiable claims** — Starting web verification...")

    results = []
    progress_bar = st.progress(0)
    status_text = st.empty()

    for i, claim_obj in enumerate(claims):
        claim_txt = claim_obj["claim"]
        status_text.info(f"🌐 Verifying {i+1}/{len(claims)}: *{claim_txt[:80]}{'...' if len(claim_txt)>80 else ''}*")

        result = verify_claim(claim_txt, show_snippet=show_snippets)
        result["claim"] = claim_txt
        result["category"] = claim_obj.get("category", "statistic")
        results.append(result)

        progress_bar.progress((i + 1) / len(claims))
        time.sleep(1.2)

    status_text.empty()
    progress_bar.empty()

    # ============================================
    # RESULTS HEADER
    # ============================================
    st.markdown("---")
    st.markdown("""
    <div class="section-header">📊 Fact-Check Report</div>
    """, unsafe_allow_html=True)

    col_date, col_file = st.columns(2)
    with col_date:
        st.caption(f"📅 {datetime.now().strftime('%B %d, %Y · %H:%M:%S')}")
    with col_file:
        st.caption(f"📄 {uploaded_file.name}  ·  🌐 Tavily AI Search Enabled")

    # Summary Stats
    counts = {"Verified": 0, "Inaccurate": 0, "False": 0, "Unverified": 0}
    for r in results:
        verdict = r.get("verdict", "Unverified")
        if verdict not in counts:
            verdict = "Unverified"
        counts[verdict] += 1

    total = len(results)
    flag_score = round(((counts["Inaccurate"] + counts["False"]) / total) * 100) if total else 0
    flag_color = "#10b981" if flag_score < 30 else "#f59e0b" if flag_score < 60 else "#f43f5e"

    col1, col2, col3, col4, col5 = st.columns(5)
    cards = [
        (col1, counts["Verified"],   "#10b981", "Verified"),
        (col2, counts["Inaccurate"], "#f59e0b", "Inaccurate"),
        (col3, counts["False"],      "#f43f5e", "False"),
        (col4, counts["Unverified"], "#8b5cf6", "Unverified"),
        (col5, f"{flag_score}%",     flag_color, "Flag Rate"),
    ]
    icons = ["✅", "⚠️", "❌", "❓", "🚩"]
    for (col, val, color, label), icon in zip(cards, icons):
        with col:
            st.markdown(f"""
            <div class="stat-card" style="color:{color};">
                <div class="stat-number" style="color:{color};">{icon} {val}</div>
                <div class="stat-label">{label}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ============================================
    # DETAILED RESULTS TABS
    # ============================================
    st.markdown("""<div class="section-header" style="font-size:1.2rem;">🔎 Detailed Analysis</div>""", unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        f"All ({total})",
        f"✅ Verified ({counts['Verified']})",
        f"⚠️ Inaccurate ({counts['Inaccurate']})",
        f"❌ False ({counts['False']})",
        f"❓ Unverified ({counts['Unverified']})"
    ])

    verdict_icon = {"Verified": "✅", "Inaccurate": "⚠️", "False": "❌", "Unverified": "❓"}

    def render_claim_cards(items):
        if not items:
            st.info("No claims in this category.")
            return
        for item in items:
            v = item.get("verdict", "Unverified")
            if v not in verdict_icon:
                v = "Unverified"
            icon = verdict_icon[v]
            cls = v.lower()
            conf = item.get("confidence", "Low")
            cat = item.get("category", "statistic").upper()

            correct_html = ""
            cf = item.get("correct_fact")
            if cf and str(cf).lower() not in ["none", "null", "", "n/a"]:
                correct_html = f'<div class="correct-fact">💡 <strong>Correct Fact:</strong> {html.escape(str(cf))}</div>'

            snippet_html = ""
            if show_snippets and item.get("search_snippets"):
                snip = item["search_snippets"][0]
                snippet_html = f'<div class="search-snippet">🔍 <strong>{html.escape(snip.get("title",""))}</strong> — {html.escape(snip.get("snippet","")[:200])}</div>'

            st.markdown(f"""
            <div class="claim-card {cls}">
                <div style="display:flex; align-items:center; gap:0.5rem; flex-wrap:wrap;">
                    <span class="badge bg-{cls}">{icon} {v}</span>
                    <span class="conf-badge">{conf} confidence</span>
                    <span class="cat-badge">· {cat}</span>
                </div>
                <p class="claim-text">"{html.escape(str(item['claim']))}"</p>
                <p class="claim-explanation">{html.escape(str(item.get('explanation', 'No explanation provided.')))}</p>
                {correct_html}
                {snippet_html}
            </div>
            """, unsafe_allow_html=True)

    for tab, verdict_filter in zip(
        [tab1, tab2, tab3, tab4, tab5],
        ["All", "Verified", "Inaccurate", "False", "Unverified"]
    ):
        with tab:
            filtered = results if verdict_filter == "All" else [
                r for r in results if r.get("verdict", "Unverified") == verdict_filter
            ]
            render_claim_cards(filtered)

    # ============================================
    # DOWNLOAD REPORT
    # ============================================
    st.markdown("---")
    report_data = {
        "generated_at": datetime.now().isoformat(),
        "file_name": uploaded_file.name,
        "total_claims": total,
        "web_search_enabled": True,
        "summary": {**counts, "flag_rate_percent": flag_score},
        "results": [
            {
                "id": i + 1,
                "claim": r["claim"],
                "category": r.get("category", "statistic"),
                "verdict": r.get("verdict", "Unverified"),
                "confidence": r.get("confidence", "Low"),
                "explanation": r.get("explanation", ""),
                "correct_fact": r.get("correct_fact")
            }
            for i, r in enumerate(results)
        ]
    }

    col_dl1, col_dl2, col_dl3 = st.columns([1, 2, 1])
    with col_dl2:
        st.download_button(
            label="📥 Download Full Report (JSON)",
            data=json.dumps(report_data, indent=2, ensure_ascii=False),
            file_name=f"factcheck_{uploaded_file.name.replace('.pdf','')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )

    st.balloons()
    st.success(f"✅ Fact-checking complete! Flagged **{counts['Inaccurate'] + counts['False']}** problematic claims out of {total} total.")

# ============================================
# FOOTER
# ============================================
st.markdown("---")
st.markdown("""
<div style="text-align:center; font-size:0.72rem; color:#334155; padding:1.2rem 0; letter-spacing:0.04em;">
    FactCheck AI &nbsp;·&nbsp; AI Claim Extraction &nbsp;·&nbsp; Live Web Search via Tavily &nbsp;·&nbsp; Verified · Inaccurate · False Verdicts
</div>
""", unsafe_allow_html=True)
