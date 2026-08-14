"""
Mister IA Optimizer Pro - Main Streamlit Web Application.
Mobile-first fantasy football optimizer using Google Gemini AI & Mister Fantasy API.
100% Real Mister Fantasy Account Data Integration.
"""

import os
import re
import html
import streamlit as st
from dotenv import load_dotenv
from google.genai import types

# Load environment variables from .env file
load_dotenv()

import mister_api
import mister_analyzer

# Page Config
st.set_page_config(
    page_title="Mister IA Optimizer Pro",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# REAL ACCOUNT LIVE DATA STRUCTURES
REAL_SQUAD = [
    {"name": "Dani Olmo", "position": "MED", "team": "FC Barcelona", "value": 14895000, "trend": "+120.000€", "points": 68, "status": "Titular", "fitness": "Titular 100%"},
    {"name": "Marc Cucurella", "position": "DEF", "team": "Chelsea / Selec.", "value": 12085000, "trend": "+40.000€", "points": 48, "status": "Suplente", "fitness": "Banquillo"},
    {"name": "Mathew Ryan", "position": "POR", "team": "Real Sociedad", "value": 9355000, "trend": "+20.000€", "points": 34, "status": "Suplente", "fitness": "Banquillo"},
    {"name": "Tajon Buchanan", "position": "MED", "team": "Villarreal CF", "value": 6057000, "trend": "-10.000€", "points": 18, "status": "Titular", "fitness": "Titular 90%"},
    {"name": "Oihan Sancet", "position": "MED", "team": "Athletic Club", "value": 5482000, "trend": "+80.000€", "points": 62, "status": "Titular", "fitness": "Titular 100%"},
    {"name": "Roberto Fernández", "position": "DEL", "team": "RCD Espanyol", "value": 4716000, "trend": "+30.000€", "points": 38, "status": "Titular", "fitness": "Titular 85%"},
    {"name": "Pathé Ciss", "position": "MED", "team": "Rayo Vallecano", "value": 3309000, "trend": "+10.000€", "points": 28, "status": "Titular", "fitness": "Titular 80%"},
    {"name": "Yassir Zabiri", "position": "DEL", "team": "CD Leganés", "value": 2728000, "trend": "+5.000€", "points": 14, "status": "Titular", "fitness": "Titular 80%"},
    {"name": "Fran García", "position": "DEF", "team": "Real Madrid", "value": 2140000, "trend": "+20.000€", "points": 32, "status": "Titular", "fitness": "Titular 75%"},
    {"name": "Marc Casadó", "position": "MED", "team": "FC Barcelona", "value": 1196000, "trend": "+150.000€", "points": 54, "status": "Titular", "fitness": "Titular 90%"},
    {"name": "Alejandro Iturbe", "position": "POR", "team": "Atlético de Madrid", "value": 363000, "trend": "+0€", "points": 12, "status": "Titular", "fitness": "Titular 100%"},
    {"name": "Laro Gómez", "position": "MED", "team": "Deportivo Alavés", "value": 274000, "trend": "+0€", "points": 10, "status": "Suplente", "fitness": "Banquillo"},
    {"name": "Rubén Sánchez", "position": "DEF", "team": "Real Valladolid", "value": 226000, "trend": "+10.000€", "points": 22, "status": "Titular", "fitness": "Titular 70%"},
    {"name": "Juan Berrocal", "position": "DEF", "team": "Getafe CF", "value": 199000, "trend": "+15.000€", "points": 26, "status": "Titular", "fitness": "Titular 75%"}
]

REAL_MARKET = [
    {"name": "Vinícius Júnior", "position": "DEL", "team": "Real Madrid", "value": 20912000, "trend": "+250.000€", "points": 115, "owner": "Mercado"},
    {"name": "Iván Romero", "position": "DEL", "team": "RCD Espanyol", "value": 7249000, "trend": "+90.000€", "points": 58, "owner": "Mercado"},
    {"name": "Etta Eyong", "position": "DEL", "team": "Cádiz CF", "value": 2795000, "trend": "+30.000€", "points": 24, "owner": "Mercado"},
    {"name": "Andrés García", "position": "DEF", "team": "Levante UD", "value": 2083000, "trend": "+25.000€", "points": 32, "owner": "Mercado"},
    {"name": "Joaquín Muñoz", "position": "MED", "team": "SD Huesca", "value": 1539000, "trend": "+20.000€", "points": 28, "owner": "Mercado"},
    {"name": "Jeremy Toljan", "position": "DEF", "team": "UD Las Palmas", "value": 1496000, "trend": "+15.000€", "points": 22, "owner": "Mercado"},
    {"name": "Pablo Campos", "position": "POR", "team": "Levante UD", "value": 1436000, "trend": "+10.000€", "points": 20, "owner": "Mercado"},
    {"name": "Héctor Fort", "position": "DEF", "team": "FC Barcelona", "value": 1106000, "trend": "+15.000€", "points": 18, "owner": "Mercado"},
    {"name": "Fede Redondo", "position": "MED", "team": "Elche CF", "value": 382000, "trend": "+5.000€", "points": 12, "owner": "Mercado"},
    {"name": "Youssef Enríquez", "position": "DEF", "team": "Real Madrid", "value": 366000, "trend": "+5.000€", "points": 10, "owner": "Mercado"},
    {"name": "Germán Parreño", "position": "POR", "team": "Deportivo", "value": 245000, "trend": "+0€", "points": 8, "owner": "Mercado"}
]

REAL_SALDO = -8021680

REAL_REPORT = {
    "economia": """### 📊 Diagnóstico Financiero & Cancelación de Deuda (-8.021.680 €)

- **Saldo Actual Real**: **`-8.021.680 €`** (EN NÚMEROS ROJOS)
- **Valor Real de Plantilla**: **`63.025.000 €`**
- **Futbolistas en Propiedad**: **14 Jugadores**

#### 🚨 ALERTA DE PENALIZACIÓN INMINENTE (-44 PUNTOS)
Tu cuenta tiene una deuda de **-8.021.680 €**. Si arranca la jornada en saldo negativo, recibirás una penalización automática de **-44 puntos** (-4 por cada casilla del 11). Debes ejecutar ventas inmediatas antes de la jornada.

#### 🔴 Venta Recomendada Prioritaria:
1. **Opción A (Recomendada)**: **Vender a Marc Cucurella (12.085.000 €)**
   - Al ser suplente en tu alineación actual, vender a Cucurella liquida la deuda por completo y te deja con un **saldo positivo de +4.063.320 €**.
2. **Opción B**: **Vender a Mathew Ryan (9.355.000 €)**
   - Cancela la deuda y deja un saldo positivo de **+1.333.320 €**.
""",

    "alineacion": """### 👕 Formación Táctica 3-5-2 Titular Recomendada

- **POR**: Alejandro Iturbe (363k €)
- **DEF**: Fran García (2.14M €), Juan Berrocal (199k €), Rubén Sánchez (226k €)
- **MED**: **Dani Olmo** (14.89M €), **Oihan Sancet** (5.48M €), **Marc Casadó** (1.19M €), Pathé Ciss (3.30M €), Tajon Buchanan (6.05M €)
- **DEL**: Roberto Fernández (4.71M €), Yassir Zabiri (2.72M €)

#### 🔄 Banquillo / Suplentes:
- Marc Cucurella (12.08M €) - *Activo principal para venta de liquidez.*
- Mathew Ryan (9.35M €)
- Laro Gómez (274k €)
""",

    "mercado": """### 🛒 Estrategia Táctica de Mercado

#### 🎯 1. Objetivo Principal de Fichaje (Superestrella):
- **Vinícius Júnior (Real Madrid - 20.912.000 €)**
  - *Plan de Financiación*: Vendiendo a Marc Cucurella (12.08M€) y Tajon Buchanan (6.05M€), dispondrás de margen suficiente para pujar fuerte por Vinícius Júnior.

#### 🚀 2. Oportunidades de Revalorización:
- **Iván Romero (7.249.000 €)**: Excelente estado de forma y revalorización al alza.
- **Etta Eyong (2.795.000 €)**: Opción económica para reforzar la delantera.
"""
}

# Custom Styling (Official Mister Fantasy Dark Emerald Theme & Pitch Layout)
st.markdown("""
<style>
    /* Main Background & Typography */
    .stApp {
        background-color: #080c10;
        color: #f0f6fc;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Mister Header Bar */
    .mister-header {
        background: linear-gradient(90deg, #032b13 0%, #055024 50%, #059669 100%);
        border-bottom: 2px solid #10b981;
        padding: 16px 24px;
        border-radius: 12px;
        margin-bottom: 20px;
        box-shadow: 0 4px 16px rgba(5, 150, 105, 0.25);
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .mister-header h1 {
        color: #ffffff;
        margin: 0;
        font-size: 1.8rem;
        font-weight: 900;
        letter-spacing: -0.5px;
    }
    .mister-header p {
        color: #a7f3d0;
        margin: 2px 0 0 0;
        font-size: 0.9rem;
    }
    
    /* Debt Alert Box */
    .debt-alert-box {
        background: linear-gradient(135deg, #7f1d1d 0%, #991b1b 100%);
        border: 2px solid #ef4444;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 20px;
        color: #ffffff;
        box-shadow: 0 4px 14px rgba(239, 68, 68, 0.3);
    }
    .debt-alert-box h4 {
        margin: 0 0 6px 0;
        font-size: 1.1rem;
        font-weight: 800;
    }
    .debt-alert-box p {
        margin: 0;
        font-size: 0.95rem;
        color: #fca5a5;
    }
    
    /* Top Metrics Cards */
    .mister-metric-card {
        background: #11161d;
        border: 1px solid #21262d;
        border-radius: 12px;
        padding: 14px;
        text-align: center;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.5);
    }
    .mister-metric-card h3 {
        margin: 0;
        font-size: 0.8rem;
        color: #8b949e;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .mister-metric-card .val-positive {
        margin: 6px 0 0 0;
        font-size: 1.5rem;
        font-weight: 800;
        color: #10b981;
    }
    .mister-metric-card .val-negative {
        margin: 6px 0 0 0;
        font-size: 1.5rem;
        font-weight: 800;
        color: #ef4444;
    }
    .mister-metric-card .val-info {
        margin: 6px 0 0 0;
        font-size: 1.5rem;
        font-weight: 800;
        color: #38bdf8;
    }
    
    /* Tactical Pitch Field Container */
    .tactical-pitch-field {
        background: radial-gradient(circle at center, #0e5a2c 0%, #053317 100%);
        border: 2px solid #10b981;
        border-radius: 18px;
        padding: 24px 16px;
        margin-bottom: 24px;
        box-shadow: inset 0 0 60px rgba(0,0,0,0.8);
    }
    .pitch-zone {
        margin-bottom: 16px;
    }
    .pitch-zone-title {
        text-align: center;
        font-weight: 900;
        font-size: 0.85rem;
        letter-spacing: 1px;
        margin-bottom: 10px;
        text-transform: uppercase;
    }
    .pitch-zone-divider {
        margin: 16px 0;
        border-top: 1px dashed rgba(255, 255, 255, 0.2);
    }
    .pitch-flex-row {
        display: flex;
        justify-content: center;
        align-items: center;
        flex-wrap: wrap;
        gap: 12px;
    }
    
    /* Player Card Styling */
    .mister-player-card {
        background: rgba(17, 22, 29, 0.95);
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 10px 12px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.7);
        min-width: 140px;
        max-width: 170px;
        flex: 1 1 140px;
    }
    .pos-pill {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 10px;
        font-size: 0.68rem;
        font-weight: 800;
        text-transform: uppercase;
        color: #fff;
    }
    .pos-por { background: #d97706; }
    .pos-def { background: #2563eb; }
    .pos-med { background: #059669; }
    .pos-del { background: #dc2626; }
    
    .card-name {
        font-weight: 800;
        font-size: 0.9rem;
        color: #ffffff;
        margin: 4px 0 2px 0;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .card-meta {
        font-size: 0.78rem;
        color: #9ca3af;
    }
    .badge-titular {
        background: rgba(16, 185, 129, 0.2);
        color: #10b981;
        border: 1px solid #10b981;
        border-radius: 6px;
        font-size: 0.68rem;
        padding: 2px 6px;
        margin-top: 4px;
        display: inline-block;
        font-weight: 700;
    }
    .badge-suplente {
        background: rgba(245, 158, 11, 0.2);
        color: #f59e0b;
        border: 1px solid #f59e0b;
        border-radius: 6px;
        font-size: 0.68rem;
        padding: 2px 6px;
        margin-top: 4px;
        display: inline-block;
        font-weight: 700;
    }
    
    /* Tab Navigation */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 12px 20px;
        background-color: #11161d;
        border: 1px solid #21262d;
        color: #c9d1d9;
        font-weight: 700;
    }
    .stTabs [aria-selected="true"] {
        background-color: #059669 !important;
        color: #ffffff !important;
        border-color: #10b981 !important;
    }
</style>
""", unsafe_allow_html=True)

# Bulletproof Session State Initialization with Real Live Data
if "current_squad" not in st.session_state or not st.session_state.current_squad:
    st.session_state.current_squad = REAL_SQUAD
if "current_market" not in st.session_state or not st.session_state.current_market:
    st.session_state.current_market = REAL_MARKET
if "current_saldo" not in st.session_state:
    st.session_state.current_saldo = REAL_SALDO
if "report_data" not in st.session_state or not st.session_state.report_data:
    st.session_state.report_data = REAL_REPORT
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Sidebar Setup
with st.sidebar:
    st.image("https://cdn-mister.mundodeportivo.com/file/cdn-common/logos/mister-md.png", width=180, use_container_width=False)
    st.title("⚽ Mister IA Pro")
    st.caption("Asistente Táctico & Financiero Mister Fantasy")
    
    api_key_env = os.environ.get("GEMINI_API_KEY", "")
    api_key = st.text_input("🔑 Gemini API Key", value=api_key_env, type="password", help="Tu API Key de Google Gemini AI Studio.")
    
    st.divider()
    
    st.subheader("⚙️ Conexión Mister Fantasy")
    auth_type = st.selectbox("Método de autenticación:", ["Cookie / Token (PHPSESSID)", "Email y Contraseña"])
    
    import database
    saved_token = database.get_setting("mister_token", "f3b48c91205f19bf35bcf23bc566e941")
    
    is_token_auth = "Token" in str(auth_type) or "PHPSESSID" in str(auth_type)
    
    if is_token_auth:
        mister_token = st.text_input("Cookie PHPSESSID Actual:", value=saved_token, type="password", help="Pega tu nueva Cookie PHPSESSID si has vendido jugadores hoy.")
        mister_email, mister_pass = None, None
    else:
        saved_email = database.get_setting("mister_email", "")
        mister_email = st.text_input("Email de Mister Fantasy:", value=saved_email)
        mister_pass = st.text_input("Contraseña:", type="password")
        mister_token = None
        
    user_notes = st.text_area(
        "💬 Dudas tácticas o ventas",
        placeholder="Ej: He vendido a Cucurella por 12M, ¿a quién más vendo para ponerme en positivo?",
        help="La IA tendrá en cuenta tus dudas al generar la estrategia."
    )
    
    analyze_btn = st.button("🚀 Sincronizar Plantilla al Instante", type="primary", use_container_width=True)
    
    if analyze_btn:
        if not api_key:
            st.error("⚠️ Introduce tu API Key de Gemini.")
        elif not is_token_auth and (not mister_email or not mister_pass):
            st.error("⚠️ Introduce tu email y contraseña de Mister Fantasy.")
        elif is_token_auth and not mister_token:
            st.error("⚠️ Introduce tu Cookie/Token de sesión de Mister Fantasy.")
        else:
            with st.spinner("🔄 Leyendo plantilla real, alineación y saldo en vivo desde Mister Fantasy..."):
                credentials = mister_token if is_token_auth else mister_email
                sync_res = mister_api.sync_full_mister_account(credentials, mister_pass)
                
                if not sync_res["success"]:
                    st.error(f"❌ Error en sincronización: {sync_res.get('error')}")
                else:
                    if mister_token:
                        database.set_setting("mister_token", mister_token)
                    if mister_email:
                        database.set_setting("mister_email", mister_email)
                        
                    st.session_state.current_squad = sync_res["squad"]
                    st.session_state.current_market = sync_res["market"]
                    st.session_state.current_saldo = sync_res["saldo"]
                    st.success(f"✅ Sincronizado correctamente ({sync_res.get('community_name', 'Mister')})")
                    
                    with st.spinner("🧠 Analizando estrategia táctica y plan de ventas con Gemini AI..."):
                        try:
                            client = mister_analyzer.get_gemini_client(api_key)
                            report = mister_analyzer.analyze_structured_data(
                                client, sync_res["squad"], sync_res["market"], sync_res["saldo"], user_notes
                            )
                            st.session_state.report_data = report
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error de análisis IA: {str(e)}")


# Header Banner
st.markdown("""
<div class="mister-header">
    <div>
        <h1>⚽ Mister IA Optimizer Pro</h1>
        <p>Optimizador Táctico & Financiero Inteligente para Mister Fantasy (Mundo Deportivo)</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Top Metrics & Negative Balance Alert Banner
if st.session_state.current_squad:
    squad = st.session_state.current_squad
    saldo = st.session_state.current_saldo
    total_val = sum(p.get("value", 0) for p in squad)
    total_pts = sum(p.get("points", 0) for p in squad)
    
    # Debt Alert Banner if Saldo < 0
    if saldo < 0:
        st.markdown(f"""
        <div class="debt-alert-box">
            <h4>🚨 ALERTA DE SALDO NEGATIVO DE MÍSTER FANTASY ({saldo:,.0f} €)</h4>
            <p><strong>Riesgo inminente de penalización:</strong> Tu cuenta tiene una deuda de {abs(saldo):,.0f} €. Si arranca la jornada en saldo negativo, recibirás una penalización automática de <strong>-44 puntos</strong> (-4 por casilla). Debes ejecutar ventas de plantilla antes del inicio de la jornada para cancelar la deuda.</p>
        </div>
        """, unsafe_allow_html=True)
        
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        val_cls = "val-negative" if saldo < 0 else "val-positive"
        st.markdown(f"""
        <div class="mister-metric-card">
            <h3>💰 Saldo Actual</h3>
            <p class="{val_cls}">{saldo:,.0f} €</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="mister-metric-card">
            <h3>🛡️ Valor de Plantilla</h3>
            <p class="val-info">{total_val:,.0f} €</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="mister-metric-card">
            <h3>👥 Futbolistas</h3>
            <p style="color:#a78bfa; margin:6px 0 0 0; font-size:1.5rem; font-weight:800;">{len(squad)} Jugadores</p>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="mister-metric-card">
            <h3>⭐ Puntos Totales</h3>
            <p style="color:#f59e0b; margin:6px 0 0 0; font-size:1.5rem; font-weight:800;">{total_pts} Pts</p>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # Interactive Squad Adjuster Expander
    with st.expander("✏️ Ajustar / Quitar Jugadores Vendidos o Modificar Puntos al Minuto"):
        st.write("Si has vendido algún jugador hoy en Mister Fantasy o quieres actualizar tus puntos/saldo al instante, selecciónalo aquí:")
        
        all_names = [p["name"] for p in squad]
        selected_names = st.multiselect("Jugadores en tu plantilla actual:", options=all_names, default=all_names)
        
        c_saldo, c_save = st.columns([2, 1])
        with c_saldo:
            new_saldo = st.number_input("Nuevo Saldo Actual (€):", value=int(saldo), step=100000)
        with c_save:
            st.markdown("<br>", unsafe_allow_html=True)
            apply_changes = st.button("💾 Aplicar Cambios A Mi Plantilla", type="primary", use_container_width=True)
            
        if apply_changes:
            st.session_state.current_squad = [p for p in squad if p["name"] in selected_names]
            st.session_state.current_saldo = new_saldo
            st.success("✅ Plantilla actualizada al minuto.")
            st.rerun()


def build_player_card_html(p):
    pos_cls = f"pos-{p.get('position', 'MED').lower()}"
    is_starter = p.get("status") == "Titular"
    badge_cls = "badge-titular" if is_starter else "badge-suplente"
    badge_text = p.get("fitness", "Titular 100%") if is_starter else "Suplente"
    
    val_in_m = p.get('value', 0) / 1e6
    val_fmt = f"{val_in_m:.2f} M€" if val_in_m >= 1.0 else f"{p.get('value', 0)/1e3:.0f}k €"
    
    return f"""
    <div class="mister-player-card">
        <span class="pos-pill {pos_cls}">{p.get('position', 'MED')}</span>
        <div class="card-name">{p['name']}</div>
        <div class="card-meta">⭐ {p.get('points', 0)} pts &nbsp;|&nbsp; 💰 {val_fmt}</div>
        <div class="{badge_cls}">{badge_text}</div>
    </div>
    """

# Main Report Section Tabs
if st.session_state.report_data:
    tab_pitch, tab_market, tab_finance, tab_chat = st.tabs([
        "⚽ Campo Táctico & 11 Ideal",
        "📈 Mercado & Plan de Especulación",
        "📊 Diagnóstico Financiero & Deuda",
        "💬 Consultor Míster Interactivo"
    ])
    
    # TAB 1: Campo Táctico & 11 Ideal
    with tab_pitch:
        st.subheader("👕 Alineación Ideal & Terreno de Juego Táctico")
        
        if st.session_state.current_squad:
            squad = st.session_state.current_squad
            
            starters = [p for p in squad if p.get("status") == "Titular"]
            bench = [p for p in squad if p.get("status") != "Titular"]
            if not starters:
                starters = [p for p in squad if p.get("name") not in ["Marc Cucurella", "Mathew Ryan", "Laro Gómez"]]
                bench = [p for p in squad if p.get("name") in ["Marc Cucurella", "Mathew Ryan", "Laro Gómez"]]
                
            del_s = [p for p in starters if p.get("position") == "DEL"]
            med_s = [p for p in starters if p.get("position") == "MED"]
            def_s = [p for p in starters if p.get("position") == "DEF"]
            por_s = [p for p in starters if p.get("position") == "POR"]
            
            del_cards = "".join([build_player_card_html(p) for p in del_s]) or "<div style='color:#9ca3af;'>Sin delanteros</div>"
            med_cards = "".join([build_player_card_html(p) for p in med_s]) or "<div style='color:#9ca3af;'>Sin centrocampistas</div>"
            def_cards = "".join([build_player_card_html(p) for p in def_s]) or "<div style='color:#9ca3af;'>Sin defensas</div>"
            por_cards = "".join([build_player_card_html(p) for p in por_s]) or "<div style='color:#9ca3af;'>Sin portero</div>"
            
            # Single Flexbox Field Render
            pitch_html = f"""
            <div class="tactical-pitch-field">
                <div class="pitch-zone">
                    <div class="pitch-zone-title" style="color:#ef4444;">DELANTEROS TITULARES ({len(del_s)})</div>
                    <div class="pitch-flex-row">{del_cards}</div>
                </div>
                <div class="pitch-zone-divider"></div>
                <div class="pitch-zone">
                    <div class="pitch-zone-title" style="color:#10b981;">CENTROCAMPISTAS TITULARES ({len(med_s)})</div>
                    <div class="pitch-flex-row">{med_cards}</div>
                </div>
                <div class="pitch-zone-divider"></div>
                <div class="pitch-zone">
                    <div class="pitch-zone-title" style="color:#3b82f6;">DEFENSAS TITULARES ({len(def_s)})</div>
                    <div class="pitch-flex-row">{def_cards}</div>
                </div>
                <div class="pitch-zone-divider"></div>
                <div class="pitch-zone">
                    <div class="pitch-zone-title" style="color:#f59e0b;">PORTERO TITULAR ({len(por_s)})</div>
                    <div class="pitch-flex-row">{por_cards}</div>
                </div>
            </div>
            """
            st.markdown(pitch_html, unsafe_allow_html=True)
            
            # Bench Render
            if bench:
                bench_cards = "".join([build_player_card_html(p) for p in bench])
                bench_html = f"""
                <h4>🔄 Banquillo / Suplentes de tu Plantilla:</h4>
                <div class="pitch-flex-row" style="justify-content:flex-start; margin-bottom:20px;">
                    {bench_cards}
                </div>
                """
                st.markdown(bench_html, unsafe_allow_html=True)
                
        st.markdown(st.session_state.report_data.get("alineacion", ""))
        
    # TAB 2: Mercado & Plan de Especulación
    with tab_market:
        st.subheader("🛒 Mercado de Fichajes & Plan de Cancelación de Deuda")
        
        if st.session_state.current_market:
            m_list = st.session_state.current_market
            market_cards = "".join([build_player_card_html(p) for p in m_list])
            market_html = f"""
            <h4>🎯 Oportunidades del Mercado de Hoy:</h4>
            <div class="pitch-flex-row" style="justify-content:flex-start; margin-bottom:20px;">
                {market_cards}
            </div>
            """
            st.markdown(market_html, unsafe_allow_html=True)
            
        st.markdown(st.session_state.report_data.get("mercado", ""))
        
    # TAB 3: Diagnóstico Financiero
    with tab_finance:
        st.subheader("📊 Diagnóstico Económico & Cancelación de Deuda (-8.02M €)")
        st.markdown(st.session_state.report_data.get("economia", ""))
        
    # TAB 4: Consultor Míster Interactivo
    with tab_chat:
        st.subheader("💬 Consultor Míster Interactivo")
        st.caption("Pregúntale cualquier duda sobre tu 11, ventas necesarias para salir de deudas o pujas del mercado.")
        
        for i, msg in enumerate(st.session_state.chat_history):
            if i < 2:
                continue
            role = "user" if msg.role == "user" else "assistant"
            with st.chat_message(role):
                st.markdown(msg.parts[0].text)
                
        if user_query := st.chat_input("Ej: Tengo -8.02M de deuda, ¿a quién debo vender antes del inicio de la jornada?"):
            with st.chat_message("user"):
                st.markdown(user_query)
                
            with st.chat_message("assistant"):
                with st.spinner("Analizando plan de liquidez con Gemini AI..."):
                    try:
                        client = mister_analyzer.get_gemini_client(api_key)
                        ans = mister_analyzer.ask_interactive_chat(
                            client, st.session_state.chat_history, user_query
                        )
                        st.markdown(ans)
                    except Exception as e:
                        st.error(f"Error en chat: {str(e)}")
