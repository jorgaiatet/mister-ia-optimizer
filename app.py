"""
Mister IA Optimizer Pro - Main Streamlit Web Application.
Mobile-first fantasy football optimizer using Google Gemini AI & Mister Fantasy API.
"""

import os
import streamlit as st
from dotenv import load_dotenv
from google.genai import types

# Load environment variables from .env file
load_dotenv()

import mister_api
import mister_analyzer
from demo_data import DEMO_SQUAD, DEMO_MARKET, DEMO_SALDO, DEMO_REPORT

# Page Config
st.set_page_config(
    page_title="Mister IA Optimizer Pro",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (Dark Emerald Sports Aesthetic & Mobile Responsive)
st.markdown("""
<style>
    /* Main Background & Text */
    .stApp {
        background-color: #0d1117;
        color: #e6edf3;
    }
    
    /* Card Container Styling */
    .metric-card {
        background: linear-gradient(135deg, #161b22 0%, #21262d 100%);
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }
    .metric-card h3 {
        margin: 0;
        font-size: 0.9rem;
        color: #8b949e;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .metric-card p {
        margin: 8px 0 0 0;
        font-size: 1.6rem;
        font-weight: 700;
        color: #2ea043;
    }
    
    /* Header Accent */
    .header-banner {
        background: linear-gradient(90deg, #1f6feb 0%, #238636 100%);
        padding: 18px 24px;
        border-radius: 12px;
        margin-bottom: 24px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .header-banner h1 {
        color: #ffffff;
        margin: 0;
        font-size: 1.8rem;
        font-weight: 800;
    }
    
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 10px 18px;
        background-color: #161b22;
        border: 1px solid #30363d;
        color: #c9d1d9;
    }
    .stTabs [aria-selected="true"] {
        background-color: #238636 !important;
        color: #ffffff !important;
        border-color: #2ea043 !important;
    }
</style>
""", unsafe_allow_html=True)

# Session State Initialization
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "report_data" not in st.session_state:
    st.session_state.report_data = None
if "current_squad" not in st.session_state:
    st.session_state.current_squad = []
if "current_market" not in st.session_state:
    st.session_state.current_market = []
if "current_saldo" not in st.session_state:
    st.session_state.current_saldo = 0

# Sidebar Section
with st.sidebar:
    st.title("⚽ Mister IA Pro")
    st.caption("Optimización Táctica y Financiera con IA")
    
    # API Key Input
    default_key = os.environ.get("GEMINI_API_KEY", "")
    api_key = st.text_input(
        "🔑 Gemini API Key",
        value=default_key,
        type="password",
        help="Consíguela gratis en Google AI Studio (ai.google.dev)"
    )
    
    st.divider()
    
    # Mode Selector
    st.subheader("⚙️ Modo de Análisis")
    mode = st.radio(
        "Elige cómo obtener tus datos:",
        ["🔄 Auto-Sincronización Mister API", "📹 Subir Vídeo / Fotos (Visión IA)", "🎲 Modo Demo (Prueba Rápida)"],
        index=0
    )
    
    st.divider()
    
    user_notes = st.text_area(
        "💬 Dudas o consideraciones tácticas",
        placeholder="Ej: Tengo dudas entre poner a Rüdiger o Baena en el 11, o si debo pujar fuerte por Sancet...",
        help="La IA tendrá en cuenta tus preferencias al generar la estrategia."
    )
    
    # Mode 1: Auto-Sync API
    if mode == "🔄 Auto-Sincronización Mister API":
        st.subheader("1. Conexión a Mister Fantasy")
        auth_type = st.selectbox("Método de autenticación:", ["Email y Contraseña", "Token de Sesión (X-Auth-Token)"])
        
        if auth_type == "Email y Contraseña":
            mister_email = st.text_input("Email de Mister Fantasy:")
            mister_pass = st.text_input("Contraseña:", type="password")
            mister_token = None
        else:
            mister_token = st.text_input("X-Auth-Token de Mister:", type="password")
            mister_email, mister_pass = None, None
            
        analyze_btn = st.button("🚀 Sincronizar y Analizar", type="primary", use_container_width=True)
        
        if analyze_btn:
            if not api_key:
                st.error("⚠️ Introduce tu API Key de Gemini.")
            elif auth_type == "Email y Contraseña" and (not mister_email or not mister_pass):
                st.error("⚠️ Introduce tu email y contraseña de Mister Fantasy.")
            elif auth_type == "Token de Sesión" and not mister_token:
                st.error("⚠️ Introduce tu Token de sesión de Mister Fantasy.")
            else:
                with st.spinner("🔄 Conectando a Mister Fantasy y extrayendo datos de tu cuenta..."):
                    credentials = mister_token if auth_type == "Token de Sesión" else mister_email
                    sync_res = mister_api.sync_full_mister_account(credentials, mister_pass)
                    
                    if not sync_res["success"]:
                        st.error(f"❌ Error en sincronización: {sync_res.get('error')}")
                    else:
                        st.session_state.current_squad = sync_res["squad"]
                        st.session_state.current_market = sync_res["market"]
                        st.session_state.current_saldo = sync_res["saldo"]
                        st.success(f"✅ Sincronizado correctamente ({sync_res.get('community_name', 'Mister')})")
                        
                        with st.spinner("🧠 Analizando estrategia con Gemini AI..."):
                            try:
                                client = mister_analyzer.get_gemini_client(api_key)
                                report = mister_analyzer.analyze_structured_data(
                                    client, sync_res["squad"], sync_res["market"], sync_res["saldo"], user_notes
                                )
                                st.session_state.report_data = report
                                
                                # Set initial chat history context
                                context_text = f"Contexto de la plantilla:\nEconomía: {report['economia']}\nAlineación: {report['alineacion']}\nMercado: {report['mercado']}"
                                st.session_state.chat_history = [
                                    types.Content(role="user", parts=[types.Part.from_text(text=context_text)]),
                                    types.Content(role="model", parts=[types.Part.from_text(text="¡Entendido! He analizado tu plantilla y mercado. ¿Qué dudas tienes?")])
                                ]
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error de análisis IA: {str(e)}")

    # Mode 2: Media Upload
    elif mode == "📹 Subir Vídeo / Fotos (Visión IA)":
        st.subheader("1. Tu Plantilla y Mercado")
        media_files = st.file_uploader(
            "Sube vídeos (.mp4, .mov) o fotos (.jpg, .png) de tu equipo y mercado:",
            type=["mp4", "mov", "jpg", "jpeg", "png"],
            accept_multiple_files=True
        )
        
        analyze_btn = st.button("🚀 Analizar con Visión IA", type="primary", use_container_width=True)
        
        if analyze_btn:
            if not api_key:
                st.error("⚠️ Introduce tu API Key de Gemini.")
            elif not media_files:
                st.error("⚠️ Sube al menos un vídeo o imagen de tu plantilla.")
            else:
                try:
                    client = mister_analyzer.get_gemini_client(api_key)
                    uploaded_gemini = []
                    
                    with st.spinner("📤 Subiendo archivos a los servidores de Gemini AI..."):
                        for f in media_files:
                            g_file = mister_analyzer.upload_file_to_gemini(client, f.getvalue(), f.name)
                            uploaded_gemini.append(g_file)
                            
                    with st.spinner("🧠 Procesando imágenes/vídeo con Visión de Gemini AI... (esto puede tardar 15-30s)"):
                        report = mister_analyzer.analyze_media_files(client, uploaded_gemini, user_notes)
                        st.session_state.report_data = report
                        
                        context_text = f"Contexto:\nEconomía: {report['economia']}\nAlineación: {report['alineacion']}\nMercado: {report['mercado']}"
                        st.session_state.chat_history = [
                            types.Content(role="user", parts=[types.Part.from_text(text=context_text)]),
                            types.Content(role="model", parts=[types.Part.from_text(text="¡Procesado con éxito por Visión IA! ¿En qué te ayudo con tu estrategia?")])
                        ]
                        st.rerun()
                except Exception as e:
                    st.error(f"Error de procesamiento: {str(e)}")

    # Mode 3: Demo Mode
    else:
        st.subheader("1. Datos de Demostración")
        st.info("Utilizará una plantilla y mercado de prueba realistas de LaLiga para testear la app.")
        
        analyze_btn = st.button("🚀 Cargar Informe Demo", type="primary", use_container_width=True)
        
        if analyze_btn:
            st.session_state.current_squad = DEMO_SQUAD
            st.session_state.current_market = DEMO_MARKET
            st.session_state.current_saldo = DEMO_SALDO
            st.session_state.report_data = DEMO_REPORT
            
            context_text = f"Contexto Demo:\nEconomía: {DEMO_REPORT['economia']}\nAlineación: {DEMO_REPORT['alineacion']}\nMercado: {DEMO_REPORT['mercado']}"
            st.session_state.chat_history = [
                types.Content(role="user", parts=[types.Part.from_text(text=context_text)]),
                types.Content(role="model", parts=[types.Part.from_text(text="Modo Demo cargado. Puedes hacerme cualquier consulta táctica sobre esta plantilla de demostración.")])
            ]
            st.rerun()


# Main Application Interface
st.markdown("""
<div class="header-banner">
    <div>
        <h1>⚽ Mister IA Optimizer Pro</h1>
        <p style="margin:4px 0 0 0; color:#c9d1d9; font-size:0.95rem;">Asistente Táctico & Financiero Inteligente para Mister Fantasy</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Top Metrics Banner if squad data is loaded
if st.session_state.current_squad:
    squad = st.session_state.current_squad
    saldo = st.session_state.current_saldo
    total_val = sum(p.get("value", 0) for p in squad)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>💰 Saldo Disponible</h3>
            <p>{saldo:,.0f} €</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>🛡️ Valor Plantilla</h3>
            <p>{total_val:,.0f} €</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>👥 Jugadores en Propiedad</h3>
            <p style="color:#58a6ff;">{len(squad)}</p>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h3>🛒 Jugadores en Mercado</h3>
            <p style="color:#d29922;">{len(st.session_state.current_market)}</p>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

# Report Section Tabs
if st.session_state.report_data:
    st.header("📊 Informe Estratégico del Míster")
    
    tab_eco, tab_ali, tab_mer = st.tabs([
        "💰 Economía & Saldos",
        "👕 Alineación Ideal & Rotaciones",
        "🛒 Mercado & Especulación"
    ])
    
    with tab_eco:
        st.markdown(st.session_state.report_data.get("economia", ""))
        
    with tab_ali:
        st.markdown(st.session_state.report_data.get("alineacion", ""))
        
    with tab_mer:
        st.markdown(st.session_state.report_data.get("mercado", ""))
        
    st.divider()
    
    # Interactive Chat Assistant Section
    st.header("💬 Consultor Míster Interactivo")
    st.caption("Pregúntale cualquier duda sobre tu 11, parches de última hora, ofertas de rivales o pujas máximas.")
    
    # Render Chat Messages (Skip first context injection message)
    for i, msg in enumerate(st.session_state.chat_history):
        if i < 2:
            continue
        role = "user" if msg.role == "user" else "assistant"
        with st.chat_message(role):
            st.markdown(msg.parts[0].text)
            
    # Chat Input
    if user_query := st.chat_input("Ej: Se me lesionó un defensa, ¿a quién pongo de sustituto?"):
        with st.chat_message("user"):
            st.markdown(user_query)
            
        with st.chat_message("assistant"):
            with st.spinner("Pensando respuesta táctica..."):
                try:
                    client = mister_analyzer.get_gemini_client(api_key)
                    ans = mister_analyzer.ask_interactive_chat(
                        client, st.session_state.chat_history, user_query
                    )
                    st.markdown(ans)
                except Exception as e:
                    st.error(f"Error al responder: {str(e)}")

else:
    # Empty State Instructions
    st.info("👈 Para comenzar, elige un **Modo de Análisis** en la barra lateral y pulsa el botón de analizar.")
    
    st.markdown("""
    ### 🌟 Características Principales de la Aplicación:
    
    1. **🔄 Sincronización Directa Mister Fantasy**: Conéctate a tu cuenta y extrae automáticamente tu saldo, plantilla y mercado de hoy sin subir nada manualmente.
    2. **📹 Visión con IA (Gemini Vision)**: Sube capturas o vídeos haciendo scroll desde tu smartphone.
    3. **👕 Algoritmo de Rotaciones & Titularidad**: Evaluación rigurosa de titularidades probables para no cometer "ceros".
    4. **💰 Especulación & Chollos**: Identificación inmediata de jugadores a precio de coste en fuerte alza para ganar saldo gratis.
    5. **💬 Chat Interactivo Contextual**: Resuelve dudas tácticas específicas en tiempo real.
    """)

# Mobile Deployment & Usage Guide
with st.expander("📱 ¿Cómo usar esta aplicación desde tu móvil?"):
    st.markdown("""
    #### 1. Opción 1: En tu casa (Misma red WiFi)
    - Cuando ejecutas la app en tu PC, verás en la terminal dos direcciones:
      - **Local URL**: `http://localhost:8501`
      - **Network URL**: `http://192.168.X.X:8501`
    - Abre **Chrome** o **Safari** en tu móvil y escribe la dirección de **Network URL**.

    #### 2. Opción 2: Desde cualquier lugar (Despliegue Gratis en la Nube)
    - Sube este proyecto a tu repositorio de GitHub.
    - Entra en [Streamlit Community Cloud](https://streamlit.io/cloud) y conecta tu repositorio (100% Gratis).
    - Te dará un enlace web privado (ej. `https://mi-mister-ia.streamlit.app`).

    #### 📱 Consejo PWA (Instalar en Pantalla de Inicio):
    - En tu móvil (iOS/Android), pulsa en el botón **Compartir / Menú de opciones** de Safari/Chrome y selecciona **"Añadir a la pantalla de inicio"**.
    - ¡Se abrirá como una App nativa con icono propio!
    """)
