"""
app_streamlit.py — ვებ-ინტერფეისი (პროფესიონალური დიზაინი).

გაშვება:
    python -m src.ingest
    streamlit run app_streamlit.py
"""
import html
import json

import streamlit as st

from src import config
from src.rag import RAGPipeline

st.set_page_config(
    page_title="IBSU მიღების ასისტენტი",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ── სტილი (Anonymous Pro + Noto Sans Georgian, IBSU-ს ლურჯი პალიტრა) ──────
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Anonymous+Pro:ital,wght@0,400;0,700;1,400;1,700&family=Noto+Sans+Georgian:wght@400;500;600;700&display=swap');

:root{
  --brand:#14487F; --brand-dark:#0C2D52; --brand-light:#E8F0FA;
  --gold:#C8A54B; --bg:#EEF2F7; --card:#FFFFFF;
  --text:#17293D; --muted:#64748B; --border:#DCE4EC;
}

/* ფონტი ტექსტზე (ხატულებს არ ვეხებით) */
html, body, [data-testid="stAppViewContainer"], [data-testid="stSidebar"],
[data-testid="stAppViewContainer"] p, [data-testid="stAppViewContainer"] li,
[data-testid="stAppViewContainer"] label, [data-testid="stAppViewContainer"] h1,
[data-testid="stAppViewContainer"] h2, [data-testid="stAppViewContainer"] h3,
.stMarkdown, .stButton button, .stChatInput textarea, .stTextInput input{
  font-family:'Anonymous Pro','Noto Sans Georgian',monospace !important;
}
/* Streamlit-ის material ხატულების დაცვა */
span[data-testid="stIconMaterial"], .material-icons, .material-symbols-outlined,
[class*="material-symbols"]{ font-family:'Material Symbols Outlined' !important; }

[data-testid="stAppViewContainer"]{ background:var(--bg); }
[data-testid="stHeader"]{ background:transparent; }
#MainMenu, footer{ visibility:hidden; }
.block-container{ padding-top:1.4rem; max-width:820px; }

/* ── ჰედერი ───────────────────────────────────────────── */
.app-header{
  background:linear-gradient(135deg,var(--brand) 0%,var(--brand-dark) 100%);
  color:#fff; padding:22px 26px; border-radius:16px; margin-bottom:18px;
  box-shadow:0 6px 20px rgba(12,45,82,.18);
}
.app-header .title{ font-size:1.55rem; font-weight:700; letter-spacing:.3px; }
.app-header .sub{ font-size:.92rem; opacity:.9; margin-top:6px; }
.app-header .badge{
  display:inline-block; margin-top:12px; padding:4px 12px; font-size:.75rem;
  background:rgba(255,255,255,.15); border:1px solid rgba(255,255,255,.3);
  border-radius:999px;
}

/* ── ჩატის ბუშტები ───────────────────────────────────────── */
.row{ display:flex; gap:10px; margin:14px 0; align-items:flex-end; }
.row.user{ flex-direction:row-reverse; }
.avatar{
  width:38px; height:38px; min-width:38px; border-radius:50%;
  display:flex; align-items:center; justify-content:center; font-size:1.1rem;
  box-shadow:0 2px 6px rgba(0,0,0,.12);
}
.avatar.bot{ background:var(--brand-light); }
.avatar.user{ background:var(--gold); }
.bubble{ padding:12px 16px; border-radius:16px; max-width:76%; line-height:1.55;
  font-size:.95rem; box-shadow:0 2px 8px rgba(23,41,61,.06); }
.user .bubble{ background:var(--brand); color:#fff; border-bottom-right-radius:5px; }
.bot .bubble{ background:var(--card); color:var(--text); border:1px solid var(--border);
  border-left:3px solid var(--brand); border-bottom-left-radius:5px; }
.bot .bubble.fallback{ border-left-color:var(--gold); background:#FFFDF6; }

/* ── წყაროების ჩიპები ────────────────────────────────────── */
.sources{ margin-top:10px; padding-top:9px; border-top:1px dashed var(--border); }
.src-label{ font-size:.72rem; color:var(--muted); margin-right:6px; }
.chip{ display:inline-block; margin:3px 4px 0 0; padding:3px 9px; font-size:.72rem;
  background:var(--brand-light); color:var(--brand); border-radius:999px;
  border:1px solid #d3e0f2; }
.chip b{ color:var(--brand-dark); }

/* ── საიდბარი ─────────────────────────────────────────────── */
[data-testid="stSidebar"]{ background:#fff; border-right:1px solid var(--border); }
.side-title{ font-weight:700; color:var(--brand-dark); font-size:1.05rem; margin-bottom:2px; }
.side-note{ font-size:.8rem; color:var(--muted); line-height:1.5; }
.stat{ display:flex; justify-content:space-between; padding:6px 0;
  border-bottom:1px solid var(--border); font-size:.85rem; }
.stat b{ color:var(--brand); }
[data-testid="stSidebar"] .stButton button{
  background:var(--brand-light); color:var(--brand-dark); border:1px solid #d3e0f2;
  border-radius:10px; text-align:left; font-size:.82rem; font-weight:400;
  transition:all .15s ease;
}
[data-testid="stSidebar"] .stButton button:hover{
  background:var(--brand); color:#fff; border-color:var(--brand);
}

/* ── ჩატის ინფუთი ─────────────────────────────────────────── */
[data-testid="stChatInput"]{ border:1px solid var(--border); border-radius:14px; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


@st.cache_resource(show_spinner="ვტვირთავ მოდელსა და ბაზას...")
def get_pipeline():
    return RAGPipeline()


@st.cache_data
def faq_stats():
    with open(config.DATA_PATH, encoding="utf-8") as f:
        faq = json.load(f)["faq"]
    cats = sorted({x.get("category", "") for x in faq})
    return len(faq), len(cats)


def esc(text: str) -> str:
    return html.escape(text or "").replace("\n", "<br>")


def short(s: str, n: int = 40) -> str:
    s = s or ""
    return s if len(s) <= n else s[: n - 1] + "…"


def render_user(text: str):
    st.markdown(
        f'<div class="row user"><div class="avatar user">🧑‍🎓</div>'
        f'<div class="bubble">{esc(text)}</div></div>',
        unsafe_allow_html=True,
    )


def render_bot(text: str, sources: list):
    is_fb = "ვერ ვიპოვე" in (text or "")
    chips = ""
    if sources and not is_fb:
        chips = '<div class="sources"><span class="src-label">📄 წყაროები:</span>'
        for s in sources[:3]:
            chips += (f'<span class="chip">{esc(short(s["question"]))} '
                      f'<b>{s["similarity"]}</b></span>')
        chips += "</div>"
    cls = "bubble fallback" if is_fb else "bubble"
    st.markdown(
        f'<div class="row bot"><div class="avatar bot">🎓</div>'
        f'<div class="{cls}">{esc(text)}{chips}</div></div>',
        unsafe_allow_html=True,
    )


# ── ჰედერი ───────────────────────────────────────────────────
n_entries, n_cats = faq_stats()
st.markdown(
    f'<div class="app-header">'
    f'<div class="title">🎓 IBSU მიღების ასისტენტი</div>'
    f'<div class="sub">RAG-ზე დაფუძნებული ჩატბოტი — პასუხობს უნივერსიტეტის '
    f'რეალურ მონაცემებზე დაყრდნობით, ქართულ ენაზე.</div>'
    f'<span class="badge">🔒 პასუხობს მხოლოდ ბაზაში არსებულ ინფორმაციაზე</span>'
    f'</div>',
    unsafe_allow_html=True,
)

# ── საიდბარი ──────────────────────────────────────────────────
SAMPLES = [
    ("💻 კომპ. მეცნიერების საფასური", "რა ღირს კომპიუტერული მეცნიერების სწავლა?"),
    ("🏆 შიდა გრანტები", "რა შიდა გრანტები არსებობს IBSU-ში?"),
    ("📝 რეგისტრაცია", "რამდენ ეტაპიანია რეგისტრაცია?"),
    ("🔁 მობილობა", "რა საბუთები მჭირდება გარე მობილობის დროს?"),
    ("🌍 გაცვლითი პროგრამები", "რომელი საერთაშორისო პროგრამები მოქმედებს?"),
    ("📞 კონტაქტი", "როგორ დავუკავშირდე უნივერსიტეტს?"),
]

clicked_q = None
with st.sidebar:
    st.markdown('<div class="side-title">🎓 ასისტენტის შესახებ</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="side-note">ეს ჩატბოტი პასუხობს IBSU-ში ჩაბარების მსურველთა '
        'კითხვებს უნივერსიტეტის ოფიციალურ მონაცემებზე დაყრდნობით.</div>',
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        f'<div class="stat"><span>📚 ცოდნის ბაზა</span><b>{n_entries} ჩანაწერი</b></div>'
        f'<div class="stat"><span>🗂️ კატეგორია</span><b>{n_cats}</b></div>'
        f'<div class="stat"><span>🧠 მოდელი</span><b>{config.OLLAMA_MODEL}</b></div>'
        f'<div class="stat"><span>🔎 top-k</span><b>{config.TOP_K}</b></div>',
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="side-title">💡 სანიმუშო კითხვები</div>', unsafe_allow_html=True)
    for label, q in SAMPLES:
        if st.button(label, use_container_width=True, key=f"s_{label}"):
            clicked_q = q
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🗑️ საუბრის გასუფთავება", use_container_width=True, key="clear"):
        st.session_state.messages = []
        st.rerun()
    st.markdown(
        '<div class="side-note">ℹ️ პირველი პასუხი შეიძლება ~1 წუთი დაგვიანდეს '
        '(მოდელი მეხსიერებაში იტვირთება), შემდეგ სწრაფია.</div>',
        unsafe_allow_html=True,
    )

# ── საუბრის მდგომარეობა და რენდერი ────────────────────────────
rag = get_pipeline()
if "messages" not in st.session_state:
    st.session_state.messages = []

if not st.session_state.messages:
    st.markdown(
        '<div class="row bot"><div class="avatar bot">🎓</div>'
        '<div class="bubble">გამარჯობა! 👋 დამისვით კითხვა IBSU-ში ჩაბარების, '
        'სწავლის საფასურის, გრანტების, რეგისტრაციის ან მობილობის შესახებ — '
        'ან აირჩიეთ სანიმუშო კითხვა მარცხნივ.</div></div>',
        unsafe_allow_html=True,
    )

for m in st.session_state.messages:
    if m["role"] == "user":
        render_user(m["content"])
    else:
        render_bot(m["content"], m.get("sources", []))

# ── შეყვანა (ჩაწერილი ან სანიმუშო ღილაკი) ─────────────────────
typed_q = st.chat_input("დასვით კითხვა მიღების შესახებ...")
user_q = typed_q or clicked_q

if user_q:
    render_user(user_q)
    with st.spinner("ვამუშავებ პასუხს..."):
        out = rag.answer(user_q)
    render_bot(out["answer"], out["sources"])
    st.session_state.messages.append({"role": "user", "content": user_q})
    st.session_state.messages.append(
        {"role": "assistant", "content": out["answer"], "sources": out["sources"]}
    )
