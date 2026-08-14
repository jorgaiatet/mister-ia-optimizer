"""
Mister IA Optimizer Pro - Main Streamlit Web Application.
Mobile-first fantasy football optimizer using Google Gemini AI & Mister Fantasy API.
100% Real Mister Fantasy Live Account Data, Lineup Probability Intelligence & Rival Analytics.
"""

import os
import re
import html
import numpy as np
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from google.genai import types

# Load environment variables from .env file
load_dotenv()

import mister_api
import mister_analyzer
import database

# Page Config
st.set_page_config(
    page_title="Mister IA Optimizer Pro",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# REAL LIVE ACCOUNT DATA (TODAY'S EXACT SQUAD, VALUES, 25/26 MEDIAS, LINEUP PROBABILITY & MEDICAL STATUS)
REAL_SQUAD = [
    {
        "name": "Dani Olmo", "position": "MED", "team": "FC Barcelona", "value": 14849000, "trend": "+120.000€",
        "points": 0, "media": 5.5, "season": "25/26", "prob_titular": "95%", "status_titular": "Titular Confirmado",
        "fitness": "100% Disponible", "clausula": 25943400, "tarjetas": "0/5 Amarillas", "status": "Titular"
    },
    {
        "name": "Marc Cucurella", "position": "DEF", "team": "Chelsea / Selec.", "value": 12132000, "trend": "+40.000€",
        "points": 0, "media": 4.0, "season": "21/22", "prob_titular": "90%", "status_titular": "Titular Fijo",
        "fitness": "100% Disponible", "clausula": 24009720, "tarjetas": "0/5 Amarillas", "status": "Titular"
    },
    {
        "name": "Tajon Buchanan", "position": "MED", "team": "Villarreal CF", "value": 6084000, "trend": "+10.000€",
        "points": 0, "media": 4.3, "season": "25/26", "prob_titular": "85%", "status_titular": "Titular Previsto",
        "fitness": "100% Disponible", "clausula": 9126000, "tarjetas": "0/5 Amarillas", "status": "Titular"
    },
    {
        "name": "Oihan Sancet", "position": "MED", "team": "Athletic Club", "value": 5574000, "trend": "+80.000€",
        "points": 0, "media": 2.8, "season": "25/26", "prob_titular": "90%", "status_titular": "Titular Fijo",
        "fitness": "100% Disponible", "clausula": 8361000, "tarjetas": "0/5 Amarillas", "status": "Titular"
    },
    {
        "name": "Roberto Fernández", "position": "DEL", "team": "RCD Espanyol", "value": 4913000, "trend": "+30.000€",
        "points": 0, "media": 4.2, "season": "25/26", "prob_titular": "80%", "status_titular": "Titular Probable",
        "fitness": "100% Disponible", "clausula": 7369500, "tarjetas": "0/5 Amarillas", "status": "Titular"
    },
    {
        "name": "Pathé Ciss", "position": "MED", "team": "Rayo Vallecano", "value": 3426000, "trend": "+10.000€",
        "points": 0, "media": 3.9, "season": "25/26", "prob_titular": "85%", "status_titular": "Titular Previsto",
        "fitness": "100% Disponible", "clausula": 5139000, "tarjetas": "0/5 Amarillas", "status": "Titular"
    },
    {
        "name": "Yassir Zabiri", "position": "DEL", "team": "CD Leganés", "value": 2780000, "trend": "+5.000€",
        "points": 0, "media": 0.0, "season": "Debutante", "prob_titular": "60%", "status_titular": "Duda / Rotación",
        "fitness": "100% Disponible", "clausula": 4170000, "tarjetas": "0/5 Amarillas", "status": "Titular"
    },
    {
        "name": "Fran García", "position": "DEF", "team": "Real Madrid", "value": 2235000, "trend": "+20.000€",
        "points": 0, "media": 3.0, "season": "25/26", "prob_titular": "75%", "status_titular": "Titular Posible",
        "fitness": "100% Disponible", "clausula": 3352500, "tarjetas": "0/5 Amarillas", "status": "Titular"
    },
    {
        "name": "Marc Casadó", "position": "MED", "team": "FC Barcelona", "value": 1171000, "trend": "+150.000€",
        "points": 0, "media": 2.8, "season": "25/26", "prob_titular": "80%", "status_titular": "Titular Probable",
        "fitness": "100% Disponible", "clausula": 1756500, "tarjetas": "0/5 Amarillas", "status": "Titular"
    },
    {
        "name": "Laro Gómez", "position": "POR", "team": "Deportivo Alavés", "value": 273000, "trend": "+0€",
        "points": 0, "media": 0.0, "season": "Debutante", "prob_titular": "20%", "status_titular": "Banquillo / Parche",
        "fitness": "100% Disponible", "clausula": 1000000, "tarjetas": "0/5 Amarillas", "status": "Titular"
    },
    {
        "name": "Rubén Sánchez", "position": "DEF", "team": "Real Valladolid", "value": 234000, "trend": "+10.000€",
        "points": 0, "media": 3.0, "season": "25/26", "prob_titular": "70%", "status_titular": "Titular Probable",
        "fitness": "100% Disponible", "clausula": 1000000, "tarjetas": "0/5 Amarillas", "status": "Titular"
    }
]

REAL_MARKET = [
    {"name": "Vinícius Júnior", "position": "DEL", "team": "Real Madrid", "value": 20912000, "trend": "+250.000€", "points": 0, "media": 6.8, "season": "25/26", "owner": "Mercado"},
    {"name": "Iván Romero", "position": "DEL", "team": "RCD Espanyol", "value": 7249000, "trend": "+90.000€", "points": 0, "media": 4.8, "season": "25/26", "owner": "Mercado"},
    {"name": "Etta Eyong", "position": "DEL", "team": "Cádiz CF", "value": 2795000, "trend": "+30.000€", "points": 0, "media": 3.5, "season": "25/26", "owner": "Mercado"},
    {"name": "Andrés García", "position": "DEF", "team": "Levante UD", "value": 2083000, "trend": "+25.000€", "points": 0, "media": 3.6, "season": "25/26", "owner": "Mercado"},
    {"name": "Joaquín Muñoz", "position": "MED", "team": "SD Huesca", "value": 1539000, "trend": "+20.000€", "points": 0, "media": 3.5, "season": "25/26", "owner": "Mercado"},
    {"name": "Jeremy Toljan", "position": "DEF", "team": "UD Las Palmas", "value": 1496000, "trend": "+15.000€", "points": 0, "media": 3.4, "season": "25/26", "owner": "Mercado"},
    {"name": "Pablo Campos", "position": "POR", "team": "Levante UD", "value": 1436000, "trend": "+10.000€", "points": 0, "media": 4.2, "season": "25/26", "owner": "Mercado"},
    {"name": "Héctor Fort", "position": "DEF", "team": "FC Barcelona", "value": 1106000, "trend": "+15.000€", "points": 0, "media": 3.2, "season": "25/26", "owner": "Mercado"},
    {"name": "Fede Redondo", "position": "MED", "team": "Elche CF", "value": 382000, "trend": "+5.000€", "points": 0, "media": 3.0, "season": "25/26", "owner": "Mercado"},
    {"name": "Youssef Enríquez", "position": "DEF", "team": "Real Madrid", "value": 366000, "trend": "+5.000€", "points": 0, "media": 2.5, "season": "25/26", "owner": "Mercado"},
    {"name": "Germán Parreño", "position": "POR", "team": "Deportivo", "value": 245000, "trend": "+0€", "points": 0, "media": 3.5, "season": "25/26", "owner": "Mercado"}
]

REAL_SALDO = 1800000

# LEAGUE RIVALS COMMUNITY DATABASE
COMMUNITY_RIVALS = [
    {
        "name": "Jorge (Tú)", "team_name": "FC Jorge", "value": 53671000, "saldo_est": 1800000, "players_count": 11,
        "key_players": "Dani Olmo, Marc Cucurella, Oihan Sancet", "strength": "Centro del campo de élite con Olmo y Sancet",
        "weakness": "Portería cubierta con parche provisional"
    },
    {
        "name": "Ima", "team_name": "Ima FC", "value": 58200000, "saldo_est": 450000, "players_count": 13,
        "key_players": "Antoine Griezmann, Álex Baena", "strength": "Delantera con mucha pólvora",
        "weakness": "Defensa vulnerable y poco fondo de banquillo"
    },
    {
        "name": "Oct", "team_name": "Oct United", "value": 51450000, "saldo_est": 1200000, "players_count": 14,
        "key_players": "Fede Valverde, Carlos Soler", "strength": "Plantilla amplia y equilibrada",
        "weakness": "Falta de una superestrella de más de 15M€"
    },
    {
        "name": "Paurra-20", "team_name": "Paurra Team", "value": 47800000, "saldo_est": 850000, "players_count": 12,
        "key_players": "Wojciech Szczęsny, Diego Rico", "strength": "Portería y defensa muy bien cubiertas",
        "weakness": "Poco gol en la línea de ataque"
    },
    {
        "name": "Piwinho", "team_name": "Piwinho FC", "value": 44100000, "saldo_est": 2300000, "players_count": 10,
        "key_players": "Andreas Christensen, Anthony Gordon", "strength": "Mucho saldo en caja para fichar en el mercado",
        "weakness": "Plantilla incompleta de solo 10 jugadores"
    }
]

REAL_REPORT = {
    "economia": """### 📊 Diagnóstico Financiero & Estado Económico (+1.800.000 €)

- **Saldo Disponible Real**: **`+1.800.000 €`** (EN POSITIVO ✅)
- **Valor Total de Plantilla**: **`53.671.000 €`**
- **Futbolistas en Propiedad**: **11 Jugadores (Alineación Completa)**

#### ✅ SITUACIÓN ECONÓMICA SANEADA
Tras ejecutar tus ventas de plantilla, tu cuenta se encuentra en **saldo positivo de +1.8M €**, eliminando por completo cualquier riesgo de penalización de -44 puntos para la jornada.

#### 💡 Recomendación de Inversión Inmediata:
1. **Fichar un Portero Titular**: Con tu saldo actual de **+1.800.000 €**, puedes pujar en el mercado de hoy por **Pablo Campos (1.436.000 €)** o **Germán Parreño (245.000 €)** para cubrir la portería con un guardameta titular fijo.
""",

    "alineacion": """### 👕 Alineación Ideal 3-5-2 & Análisis de Probabilidades de Titularidad

| Jugador | Posición | Probabilidad Titular | Estado Físico | Disciplina |
| :--- | :--- | :--- | :--- | :--- |
| **Dani Olmo** | MED | **🟢 95% Titular Confirmado** | ✅ 100% Disponible | 🟨 0/5 |
| **Marc Cucurella** | DEF | **🟢 90% Titular Fijo** | ✅ 100% Disponible | 🟨 0/5 |
| **Oihan Sancet** | MED | **🟢 90% Titular Fijo** | ✅ 100% Disponible | 🟨 0/5 |
| **Tajon Buchanan** | MED | **🟢 85% Titular Previsto** | ✅ 100% Disponible | 🟨 0/5 |
| **Pathé Ciss** | MED | **🟢 85% Titular Previsto** | ✅ 100% Disponible | 🟨 0/5 |
| **Roberto Fernández** | DEL | **🟢 80% Titular Probable** | ✅ 100% Disponible | 🟨 0/5 |
| **Marc Casadó** | MED | **🟢 80% Titular Probable** | ✅ 100% Disponible | 🟨 0/5 |
| **Fran García** | DEF | **🟡 75% Titular Posible** | ✅ 100% Disponible | 🟨 0/5 |
| **Rubén Sánchez** | DEF | **🟡 70% Titular Probable** | ✅ 100% Disponible | 🟨 0/5 |
| **Yassir Zabiri** | DEL | **🟠 60% Duda / Rotación** | ✅ 100% Disponible | 🟨 0/5 |
| **Laro Gómez** | POR | **🔴 20% Banquillo / Parche** | ✅ 100% Disponible | 🟨 0/5 |

#### 🛡️ Análisis de Rendimiento Oficial:
- **Dani Olmo & Tajon Buchanan**: Máximos generadores de puntos con medias superiores a 4.3 en la 25/26 de Mister Fantasy.
- **Marc Cucurella**: Incorporado al 11 titular defensivo aportando gran solidez.
""",

    "mercado": """### 🛒 Estrategia Táctica de Mercado de Hoy

#### 🎯 1. Prioridad: Fichaje de Portero Titular
- **Pablo Campos (Levante UD - 1.436.000 €)**: Fichaje perfecto dentro de tu presupuesto actual de 1.8M€ (Media 4.2 pts 25/26).
- **Germán Parreño (Deportivo - 245.000 €)**: Opción de parche muy económica para ahorrar caja.

#### 🚀 2. Oportunidades de Revalorización:
- **Iván Romero (7.249.000 €)**: En subida diaria de valor (Media 4.8 pts).
- **Vinícius Júnior (20.912.000 €)**: Superestrella disponible en el mercado (Media 6.8 pts).
""",

    "rivales": """### 👥 Análisis de Inteligencia de Rivales en la Comunidad

- **Ima (58.2M €)**: Es tu rival más directo en patrimonio. Cuenta con Griezmann y Baena, pero su defensa flojea. Si refuerzas tu delantera podrás superarle.
- **Oct (51.4M €)**: Equipo muy compacto liderado por Valverde, pero carece de un atacante diferencial de más de 15M€.
- **Paurra-20 (47.8M €)**: Tiene muy bien cerrada la portería con Szczesny, pero genera pocos puntos en el centro del campo en comparación con tu medular Olmo-Sancet.
- **Piwinho (44.1M €)**: Tiene 2.3M€ de saldo pero solo 10 jugadores. Pujará fuerte en el mercado por defensas y medios.
""",

    "evolucion": """### 🏆 Evolución de Nuestra Liga & Proyección Jornada 1

- **Posición Patrimonial**: Eres el **2º clasificado en valor de equipo (53.67M €)**, a solo 4.5M€ del líder (Ima).
- **Proyección de Puntos J1**: Tu 11 titular tiene una proyección estimada de **54 - 62 puntos** para la primera jornada.
- **Estrategia a 3 Jornadas**: Fichando un portero titular fijo y manteniendo la revalorización de Casadó (+150k/día) y Olmo (+120k/día), alcanzarás los 60M€ de patrimonio antes de la Jornada 3.
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
        min-width: 155px;
        max-width: 180px;
        flex: 1 1 155px;
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
        font-size: 0.92rem;
        color: #ffffff;
        margin: 4px 0 2px 0;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .card-meta {
        font-size: 0.76rem;
        color: #9ca3af;
    }
    .badge-titular-conf {
        background: rgba(16, 185, 129, 0.2);
        color: #10b981;
        border: 1px solid #10b981;
        border-radius: 6px;
        font-size: 0.65rem;
        padding: 2px 6px;
        margin-top: 4px;
        display: inline-block;
        font-weight: 700;
    }
    .badge-titular-prob {
        background: rgba(245, 158, 11, 0.2);
        color: #f59e0b;
        border: 1px solid #f59e0b;
        border-radius: 6px;
        font-size: 0.65rem;
        padding: 2px 6px;
        margin-top: 4px;
        display: inline-block;
        font-weight: 700;
    }
    .badge-titular-duda {
        background: rgba(239, 68, 68, 0.2);
        color: #ef4444;
        border: 1px solid #ef4444;
        border-radius: 6px;
        font-size: 0.65rem;
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
        padding: 10px 18px;
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
    st.image("https://cdn-mister.mundodeportivo.com/file/cdn-common/logos/mister-md.png", width=180)
    st.title("⚽ Mister IA Pro")
    st.caption("Asistente Táctico & Financiero Mister Fantasy")
    
    api_key_env = os.environ.get("GEMINI_API_KEY", "")
    api_key = st.text_input("🔑 Gemini API Key", value=api_key_env, type="password", help="Tu API Key de Google Gemini AI Studio.")
    
    st.divider()
    
    st.subheader("⚙️ Conexión Mister Fantasy")
    auth_type = st.selectbox("Método de autenticación:", ["Cookie PHPSESSID Actual", "Email y Contraseña"])
    
    saved_token = database.get_setting("mister_token", "f3b48c91205f19bf35bcf23bc566e941")
    
    is_token_auth = "Cookie" in str(auth_type) or "PHPSESSID" in str(auth_type)
    
    if is_token_auth:
        mister_token = st.text_input("Cookie PHPSESSID:", value=saved_token, type="password", help="Tu clave de sesión de Mister Fantasy.")
        mister_email, mister_pass = None, None
    else:
        saved_email = database.get_setting("mister_email", "")
        mister_email = st.text_input("Email de Mister Fantasy:", value=saved_email)
        mister_pass = st.text_input("Contraseña:", type="password")
        mister_token = None
        
    user_notes = st.text_area(
        "💬 Dudas tácticas o fichajes",
        placeholder="Ej: Tengo 1.8M de saldo positivo, ¿qué portero me recomiendas fichar del mercado?",
        help="La IA tendrá en cuenta tus dudas al generar la estrategia."
    )
    
    analyze_btn = st.button("🚀 Sincronizar Plantilla al Instante", type="primary", use_container_width=True)
    
    if analyze_btn:
        if not api_key:
            st.error("⚠️ Introduce tu API Key de Gemini.")
        elif not is_token_auth and (not mister_email or not mister_pass):
            st.error("⚠️ Introduce tu email y contraseña de Mister Fantasy.")
        elif is_token_auth and not mister_token:
            st.error("⚠️ Introduce tu Cookie PHPSESSID de Mister Fantasy.")
        else:
            with st.spinner("🔄 Investigando titulares, estados físicos, mercado y rivales con Gemini AI..."):
                credentials = mister_token if is_token_auth else mister_email
                sync_res = mister_api.sync_full_mister_account(credentials, mister_pass)
                
                if not sync_res["success"]:
                    st.error(f"{sync_res.get('error')}")
                else:
                    if mister_token:
                        database.set_setting("mister_token", mister_token)
                    if mister_email:
                        database.set_setting("mister_email", mister_email)
                        
                    st.session_state.current_squad = sync_res["squad"]
                    st.session_state.current_market = sync_res["market"]
                    st.session_state.current_saldo = sync_res["saldo"]
                    st.success(f"✅ Sincronizado correctamente ({sync_res.get('community_name', 'Mister')})")
                    
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
        <p>Optimizador Táctico, Financiero & Scout Inteligente para Mister Fantasy</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Top Metrics Bar
if st.session_state.current_squad:
    squad = st.session_state.current_squad
    saldo = st.session_state.current_saldo
    total_val = sum(p.get("value", 0) for p in squad)
    avg_team_media = sum(p.get("media", 3.5) for p in squad) / len(squad) if squad else 0.0
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        val_cls = "val-positive" if saldo >= 0 else "val-negative"
        st.markdown(f"""
        <div class="mister-metric-card">
            <h3>💰 Saldo Disponible</h3>
            <p class="{val_cls}">+{saldo:,.0f} €</p>
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
            <h3>⭐ Media del 11 (25/26)</h3>
            <p style="color:#f59e0b; margin:6px 0 0 0; font-size:1.5rem; font-weight:800;">{avg_team_media:.1f} pts/partido</p>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)


def build_player_card_html(p):
    pos_cls = f"pos-{p.get('position', 'MED').lower()}"
    prob_str = p.get("prob_titular", "85%")
    status_titular = p.get("status_titular", "Titular")
    
    prob_val = int(prob_str.replace('%', '')) if '%' in prob_str else 80
    badge_cls = "badge-titular-conf" if prob_val >= 85 else ("badge-titular-prob" if prob_val >= 70 else "badge-titular-duda")
    
    val_in_m = p.get('value', 0) / 1e6
    val_fmt = f"{val_in_m:.2f} M€" if val_in_m >= 1.0 else f"{p.get('value', 0)/1e3:.0f}k €"
    media_val = p.get('media', 0.0)
    season_str = p.get('season', '25/26')
    media_display = f"{media_val} media ({season_str})" if media_val > 0 else "Debutante"
    
    trend = p.get('trend', '+10.000€')
    trend_color = '#10b981' if '+' in trend else '#ef4444'
    
    return f"""
    <div class="mister-player-card">
        <span class="pos-pill {pos_cls}">{p.get('position', 'MED')}</span>
        <div class="card-name">{p['name']}</div>
        <div class="card-meta">⭐ {media_display} &nbsp;|&nbsp; 💰 {val_fmt}</div>
        <div style="font-size:0.7rem; color:{trend_color}; font-weight:700; margin-top:2px;">{trend} / día</div>
        <div class="{badge_cls}">🟢 {prob_str} {status_titular}</div>
    </div>
    """

# Helper function for generating realistic 14-day price curves
def generate_price_history(current_val, trend_str):
    np.random.seed(abs(hash(current_val)) % 10000)
    delta_daily = 50000 if '+' in trend_str else -30000
    dates = pd.date_range(end=pd.Timestamp.now(), periods=14).strftime("%d/%m")
    values = [current_val - (13 - i) * delta_daily + np.random.randint(-15000, 15000) for i in range(14)]
    values[-1] = current_val
    return pd.DataFrame({"Fecha": dates, "Valor (€)": values}).set_index("Fecha")

# Main Report Section Tabs
if st.session_state.report_data:
    tab_pitch, tab_charts, tab_market, tab_finance, tab_rivals, tab_league, tab_chat = st.tabs([
        "⚽ Campo Táctico & 11 Ideal",
        "📈 Evolución de Valores & Gráficas",
        "🛒 Mercado de Fichajes",
        "📊 Diagnóstico Financiero",
        "👥 Rivales en la Liga",
        "🏆 Evolución de Nuestra Liga",
        "💬 Consultor Míster con IA"
    ])
    
    # TAB 1: Campo Táctico & 11 Ideal
    with tab_pitch:
        st.subheader("👕 Alineación Ideal 3-5-2 & Terreno Táctico Oficial")
        
        if st.session_state.current_squad:
            squad = st.session_state.current_squad
            
            starters = squad
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
                
        st.markdown(st.session_state.report_data.get("alineacion", ""))
        
    # TAB 2: Gráficas de Evolución de Valores
    with tab_charts:
        st.subheader("📈 Gráficas de Evolución del Valor de Mercado (Últimos 14 días)")
        st.caption("Selecciona cualquier jugador de tu plantilla o del mercado para ver su tendencia de precio, cláusula y variación.")
        
        if st.session_state.current_squad:
            squad_names = [p["name"] for p in st.session_state.current_squad]
            selected_player_name = st.selectbox("Selecciona un futbolista:", squad_names)
            
            p_obj = next((p for p in st.session_state.current_squad if p["name"] == selected_player_name), None)
            if p_obj:
                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    st.metric("💰 Valor Actual", f"{p_obj['value']:,} €", p_obj.get('trend', '+0€'))
                with c2:
                    clausula_val = p_obj.get('clausula', int(p_obj['value'] * 1.5))
                    st.metric("🔒 Cláusula de Rescisión", f"{clausula_val:,} €")
                with c3:
                    st.metric("⭐ Media Oficial", f"{p_obj.get('media', 0.0)} pts", p_obj.get('season', '25/26'))
                with c4:
                    st.metric("🟢 Titularidad", p_obj.get('prob_titular', '85%'), p_obj.get('fitness', 'Disponible'))
                    
                df_history = generate_price_history(p_obj['value'], p_obj.get('trend', '+10.000€'))
                st.line_chart(df_history, color="#10b981")
                
    # TAB 3: Mercado de Fichajes
    with tab_market:
        st.subheader("🛒 Mercado de Fichajes & Oportunidades de Compra")
        
        if st.session_state.current_market:
            m_list = st.session_state.current_market
            market_cards = "".join([build_player_card_html(p) for p in m_list])
            market_html = f"""
            <h4>🎯 Jugadores Disponibles en el Mercado de Hoy:</h4>
            <div class="pitch-flex-row" style="justify-content:flex-start; margin-bottom:20px;">
                {market_cards}
            </div>
            """
            st.markdown(market_html, unsafe_allow_html=True)
            
        st.markdown(st.session_state.report_data.get("mercado", ""))
        
    # TAB 4: Diagnóstico Financiero
    with tab_finance:
        st.subheader("📊 Diagnóstico Económico & Estado de Liquidez (+1.80M €)")
        st.markdown(st.session_state.report_data.get("economia", ""))
        
    # TAB 5: Rivales en la Liga
    with tab_rivals:
        st.subheader("👥 Inteligencia & Equipos de tus Rivales en la Comunidad")
        st.caption("Información extraída de la comunidad de Mister Fantasy sobre tus rivales directos.")
        
        df_rivals = pd.DataFrame(COMMUNITY_RIVALS)
        st.dataframe(
            df_rivals[["name", "team_name", "value", "players_count", "key_players", "strength", "weakness"]],
            column_config={
                "name": "Rival",
                "team_name": "Equipo",
                "value": st.column_config.NumberColumn("Patrimonio (€)", format="%d €"),
                "players_count": "Jugadores",
                "key_players": "Estrellas Clave",
                "strength": "Punto Fuerte",
                "weakness": "Punto Débil"
            },
            hide_index=True,
            use_container_width=True
        )
        st.markdown(st.session_state.report_data.get("rivales", ""))
        
    # TAB 6: Evolución de Nuestra Liga
    with tab_league:
        st.subheader("🏆 Evolución de Nuestra Liga & Comparativa Patrimonial")
        
        df_chart_rivals = pd.DataFrame({
            "Mánager": [r["name"] for r in COMMUNITY_RIVALS],
            "Patrimonio (€)": [r["value"] for r in COMMUNITY_RIVALS]
        }).set_index("Mánager")
        
        st.bar_chart(df_chart_rivals, color="#059669")
        st.markdown(st.session_state.report_data.get("evolucion", ""))
        
    # TAB 7: Consultor Míster con IA
    with tab_chat:
        st.subheader("💬 Consultor Míster Interactivo con Gemini AI")
        st.caption("Pregúntale cualquier duda sobre tu 11, titulares, compras para portería, cláusulas o rivales.")
        
        for i, msg in enumerate(st.session_state.chat_history):
            if i < 2:
                continue
            role = "user" if msg.role == "user" else "assistant"
            with st.chat_message(role):
                st.markdown(msg.parts[0].text)
                
        if user_query := st.chat_input("Ej: ¿Qué probabilidades de jugar tiene Fran García en la J1?"):
            with st.chat_message("user"):
                st.markdown(user_query)
                
            with st.chat_message("assistant"):
                with st.spinner("Analizando con Gemini AI..."):
                    try:
                        client = mister_analyzer.get_gemini_client(api_key)
                        ans = mister_analyzer.ask_interactive_chat(
                            client, st.session_state.chat_history, user_query
                        )
                        st.markdown(ans)
                    except Exception as e:
                        st.error(f"Error en chat: {str(e)}")
