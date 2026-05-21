"""Tema visual inspirado em Saros (PS5 / Housemarque) para o X GAMES."""

import streamlit as st

_SAROS_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Exo+2:wght@300;400;600;700&family=Rajdhani:wght@500;600;700&display=swap');

.stApp {
    background:
        radial-gradient(ellipse 80% 50% at 20% -10%, rgba(192,38,211,0.18) 0%, transparent 55%),
        radial-gradient(ellipse 60% 40% at 90% 10%, rgba(0,229,255,0.12) 0%, transparent 50%),
        radial-gradient(ellipse 50% 30% at 50% 100%, rgba(255,69,0,0.08) 0%, transparent 45%),
        linear-gradient(175deg, #050508 0%, #0a0812 35%, #120a18 70%, #0d0d14 100%);
}

@keyframes saros-glow-pulse {
    0%, 100% { box-shadow: 0 0 20px rgba(0,229,255,0.3), 0 0 60px rgba(192,38,211,0.15); }
    50% { box-shadow: 0 0 35px rgba(0,229,255,0.5), 0 0 80px rgba(255,69,0,0.2); }
}

.saros-header {
    position: relative;
    overflow: hidden;
    background: linear-gradient(135deg, rgba(13,8,20,0.95) 0%, rgba(26,18,24,0.92) 40%, rgba(10,10,20,0.95) 100%);
    border: 1px solid rgba(0,229,255,0.35);
    border-radius: 4px;
    padding: 1.6rem 2rem 1.4rem;
    margin-bottom: 1.2rem;
    text-align: center;
    animation: saros-glow-pulse 4s ease-in-out infinite;
}
.saros-header::before {
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, #00e5ff, #c026d3, #ff4500, #fbbf24, transparent);
}
.saros-badge {
    display: inline-block;
    font-family: 'Exo 2', sans-serif;
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.35em;
    text-transform: uppercase;
    color: #fbbf24;
    background: rgba(251,191,36,0.08);
    border: 1px solid rgba(251,191,36,0.35);
    padding: 0.25rem 0.9rem;
    margin-bottom: 0.6rem;
    border-radius: 2px;
}
.saros-header h1 {
    font-family: 'Orbitron', sans-serif;
    font-weight: 900;
    font-size: 2.6rem;
    letter-spacing: 0.12em;
    margin: 0;
    background: linear-gradient(90deg, #fff 0%, #00e5ff 40%, #a78bfa 70%, #fff 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    filter: drop-shadow(0 0 20px rgba(0,229,255,0.5));
}
.saros-subtitle {
    font-family: 'Exo 2', sans-serif;
    color: #8b7f9e;
    font-size: 0.95rem;
    margin: 0.5rem 0 0;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}
.saros-tagline {
    font-family: 'Rajdhani', sans-serif;
    color: #00e5ff;
    font-size: 1.15rem;
    font-weight: 600;
    margin: 0.35rem 0 0;
    text-shadow: 0 0 15px rgba(0,229,255,0.4);
}

.saros-section {
    font-family: 'Orbitron', sans-serif !important;
    font-size: 0.75rem !important;
    font-weight: 700;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #00e5ff !important;
    border-left: 3px solid #ff4500;
    padding: 0.4rem 0 0.4rem 0.8rem;
    margin: 1.2rem 0 0.6rem;
    background: linear-gradient(90deg, rgba(0,229,255,0.06) 0%, transparent 100%);
}

.stTabs [data-baseweb="tab-list"] {
    gap: 6px;
    background: transparent;
    border-bottom: 1px solid rgba(0,229,255,0.15);
}
.stTabs [data-baseweb="tab"] {
    font-family: 'Exo 2', sans-serif;
    font-size: 0.9rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    background: rgba(13,8,20,0.8);
    border-radius: 2px 2px 0 0;
    color: #8b7f9e;
    padding: 10px 18px;
    border: 1px solid rgba(139,127,158,0.25);
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(180deg, rgba(192,38,211,0.35) 0%, rgba(10,8,20,0.95) 100%) !important;
    color: #00e5ff !important;
    border-color: #00e5ff !important;
    box-shadow: 0 -2px 15px rgba(0,229,255,0.25);
    text-shadow: 0 0 10px rgba(0,229,255,0.6);
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #06060c 0%, #0d0814 50%, #0a0a12 100%) !important;
    border-right: 1px solid rgba(0,229,255,0.12);
}
[data-testid="stSidebar"] h3 {
    font-family: 'Orbitron', sans-serif !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.15em;
    color: #00e5ff !important;
    text-transform: uppercase;
}
.saros-sidebar-brand {
    font-family: 'Orbitron', sans-serif;
    font-size: 0.7rem;
    letter-spacing: 0.25em;
    color: #fbbf24;
    text-align: center;
    padding: 0.5rem;
    border: 1px solid rgba(251,191,36,0.2);
    margin-bottom: 0.8rem;
    background: rgba(251,191,36,0.04);
}

div[data-testid="stMetric"] {
    background: linear-gradient(145deg, rgba(26,18,24,0.9), rgba(10,10,20,0.95));
    border: 1px solid rgba(0,229,255,0.2);
    border-radius: 2px;
    padding: 0.6rem;
}
div[data-testid="stMetric"] label {
    font-family: 'Exo 2', sans-serif !important;
    font-size: 0.7rem !important;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #8b7f9e !important;
}
div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
    font-family: 'Orbitron', sans-serif !important;
    color: #ff6b00 !important;
    text-shadow: 0 0 12px rgba(255,107,0,0.5);
}

.stButton > button[kind="primary"] {
    background: linear-gradient(90deg, rgba(192,38,211,0.9), rgba(0,229,255,0.85), rgba(255,69,0,0.8)) !important;
    border: 1px solid rgba(0,229,255,0.5) !important;
    font-family: 'Exo 2', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    border-radius: 2px !important;
    box-shadow: 0 0 20px rgba(0,229,255,0.3) !important;
}
.stButton > button {
    font-family: 'Exo 2', sans-serif !important;
    font-weight: 600;
    border-radius: 2px !important;
    background: rgba(13,8,20,0.8) !important;
    border: 1px solid rgba(139,127,158,0.3) !important;
    color: #e8e4f0 !important;
}
.stButton > button:hover {
    border-color: #00e5ff !important;
    color: #00e5ff !important;
}

.stTextInput input, .stNumberInput input, .stTextArea textarea {
    background: rgba(10,8,16,0.9) !important;
    border-color: rgba(0,229,255,0.2) !important;
    border-radius: 2px !important;
    color: #e8e4f0 !important;
    font-family: 'Rajdhani', sans-serif !important;
}
label, .stRadio label, .stCheckbox label {
    font-family: 'Exo 2', sans-serif !important;
    font-size: 0.78rem !important;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: #8b7f9e !important;
}

h3, h4, h5 {
    font-family: 'Orbitron', sans-serif !important;
    color: #00e5ff !important;
    letter-spacing: 0.05em;
}

[data-testid="stDataFrame"] {
    border: 1px solid rgba(0,229,255,0.15);
    border-radius: 2px;
}

hr {
    border-color: rgba(0,229,255,0.12) !important;
}

.saros-footer {
    text-align: center;
    font-family: 'Exo 2', sans-serif;
    font-size: 0.65rem;
    letter-spacing: 0.2em;
    color: rgba(139,127,158,0.5);
    margin-top: 2rem;
    padding: 1rem;
    border-top: 1px solid rgba(0,229,255,0.08);
    text-transform: uppercase;
}
</style>
"""

_SAROS_HEADER = """
<div class="saros-header">
    <h1>X GAMES</h1>
    <p class="saros-tagline">Assistência Técnica de Video Games</p>
    <p class="saros-subtitle">Ordens de Serviço & Orçamentos</p>
</div>
"""

def aplicar_tema_saros():
    """Injeta CSS e cabeçalho no estilo Saros PS5."""
    st.markdown(_SAROS_CSS, unsafe_allow_html=True)
    st.markdown(_SAROS_HEADER, unsafe_allow_html=True)


def secao(titulo: str):
    """Renderiza um título de seção estilo HUD Saros."""
    st.markdown(f'<p class="saros-section">{titulo}</p>', unsafe_allow_html=True)


def rodape_saros():
    st.markdown(
        '<div class="saros-footer">X GAMES · Planet Carcosa · Soltari Shield Active</div>',
        unsafe_allow_html=True,
    )
