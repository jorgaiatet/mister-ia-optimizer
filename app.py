"""
Mister IA Optimizer Pro - Main Streamlit Web Application.
Mobile-first fantasy football optimizer using Google Gemini AI & Mister Fantasy API.
"""

import os
import re
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

# Custom Styling (Mister Fantasy Dark Emerald Sports Theme)
st.markdown("""
<style>
    /* Main Background & Text */
    .stApp {
        background-color: #0b0e14;
        color: #e6edf3;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Card Container Styling */
    .metric-card {
        background: linear-gradient(135deg, #161b22 0%, #1c2128 100%);
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
    }
    .metric-card h3 {
        margin: 0;
        font-size: 0.85rem;
        color: #8b949e;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .metric-card p {
        margin: 8px 0 0 0;
        font-size: 1.5rem;
        font-weight: 800;
        color: #10b981;
    }
    
    /* Header Accent Banner */
    .header-banner {
        background: linear-gradient(90deg, #059669 0%, #10b981 100%);
        padding: 20px 28px;
        border-radius: 14px;
        margin-bottom: 24px;
        box-shadow: 0 6px 20px rgba(16, 185, 129, 0.25);
    }
    .header-banner h1 {
        color: #ffffff;
        margin: 0;
        font-size: 1.9rem;
        font-weight: 900;
        letter-spacing: -0.5px;
    }
    
    /* Tactical Football Pitch Container */
    .pitch-field {
        background: radial-gradient(circle, #0e5a2c 0%, #053317 100%);
        border: 2px solid #10b981;
        border-radius: 16px;
        padding: 24px 16px;
        position: relative;
        margin-bottom: 24px;
        box-shadow: inset 0 0 50px rgba(0,0,0,0.7);
    }
    
    /* Player Card on Pitch */
    .mister-player-card {
        background: rgba(22, 27, 34, 0.95);
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 10px 8px;
        text-align: center;
        box-shadow: 0 4px 10px rgba(0,0,0,0.6);
        margin: 6px;
    }
    .pos-pill {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 10px;
        font-size: 0.7rem;
        font-weight: 800;
        text-transform: uppercase;
        color: #fff;
    }
    .pos-por { background: #d97706; }
    .pos-def { background: #2563eb; }
    .pos-med { background: #059669; }
    .pos-del { background: #dc2626; }
    
    .mister-player-name {
        font-weight: 800;
        font-size: 0.88rem;
        color: #ffffff;
        margin: 4px 0 2px 0;
    }
    .mister-player-meta {
        font-size: 0.75rem;
        color: #9ca3af;
    }
    .badge-titular {
        background: rgba(16, 185, 129, 0.2);
        color: #10b981;
        border: 1px solid #10b981;
        border-radius: 6px;
        font-size: 0.7rem;
        padding: 2px 6px;
        margin-top: 4px;
        display: inline-block;
        font-weight: 700;
    }
    .badge-riesgo {
        background: rgba(245, 158, 11, 0.2);
        color: #f59e0b;
        border: 1px solid #f59e0b;
        border-radius: 6px;
        font-size: 0.7rem;
        padding: 2px 6px;
        margin-top: 4px;
        display: inline-block;
        font-weight: 700;
    }
    
    /* Tab Navigation Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 12px 20px;
        background-color: #161b22;
        border: 1px solid #30363d;
        color: #c9d1d9;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #059669 !important;
        color: #ffffff !important;
        border-color: #10b981 !important;
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
    st.session_state.current_saldo = 14500000

# Sidebar Configuration
with st.sidebar:
    st.image("https://cdn-mister.mundodeportivo.com/file/cdn-common/logos/mister-md.png", width=180, use_container_width=False)
    st.title("⚽ Mister IA Pro")
    st.caption("Optimización Táctica y Financiera para Mister Fantasy")
    
    # Gemini API Key configuration
    api_key_env = os.environ.get("GEMINI_API_KEY", "")
    api_key = st.text_input("🔑 Gemini API Key", value=api_key_env, type="password", help="Tu API Key de Google Gemini AI Studio.")
    
    st.divider()
    
    # Analysis Mode Selector
    st.subheader("⚙️ Modo de Análisis")
    mode = st.radio(
        "Elige cómo obtener tus datos:",
        ["🔄 Auto-Sincronización Mister API", "📹 Subir Vídeo / Fotos (Visión IA)", "🎲 Modo Demo (Prueba Rápida)"],
        index=0
    )
    
    st.divider()
    
    user_notes = st.text_area(
        "💬 Dudas o consideraciones tácticas",
        placeholder="Ej: Tengo dudas entre poner a Olmo o Sancet en el 11, o si debo pujar fuerte por Vinícius...",
        help="La IA tendrá en cuenta tus preferencias al generar la estrategia."
    )
    
    # Mode 1: Auto-Sync API
    if mode == "🔄 Auto-Sincronización Mister API":
        st.subheader("1. Conexión a Mister Fantasy")
        auth_type = st.selectbox("Método de autenticación:", ["Token o Cookie de Sesión (PHPSESSID)", "Email y Contraseña"])
        
        import database
        saved_token = database.get_setting("mister_token", "f3b48c91205f19bf35bcf23bc566e941")
        
        is_token_auth = "Token" in str(auth_type) or "PHPSESSID" in str(auth_type)
        
        if is_token_auth:
            mister_token = st.text_input("Cookie / Token de Sesión:", value=saved_token, type="password", help="Tu clave de sesión quedará guardada para vincular la app automáticamente.")
            mister_email, mister_pass = None, None
        else:
            saved_email = database.get_setting("mister_email", "")
            mister_email = st.text_input("Email de Mister Fantasy:", value=saved_email)
            mister_pass = st.text_input("Contraseña:", type="password")
            mister_token = None
            
        saved_squad_text = database.get_setting("custom_squad_text", "")
        custom_squad_text = st.text_area(
            "📝 Ajuste Manual de Jugadores (Opcional):",
            value=saved_squad_text,
            placeholder="Ej: D. Olmo, O. Sancet, M. Casadó, M. Cucurella, F. García, P. Ciss...",
            help="Puedes modificar o añadir nombres de tu plantilla aquí."
        )
        
        analyze_btn = st.button("🚀 Sincronizar y Analizar", type="primary", use_container_width=True)
        
        if analyze_btn:
            if not api_key:
                st.error("⚠️ Introduce tu API Key de Gemini.")
            elif not is_token_auth and (not mister_email or not mister_pass):
                st.error("⚠️ Introduce tu email y contraseña de Mister Fantasy.")
            elif is_token_auth and not mister_token:
                st.error("⚠️ Introduce tu Cookie/Token de sesión de Mister Fantasy.")
            else:
                with st.spinner("🔄 Conectando a Mister Fantasy y extrayendo datos de tu cuenta..."):
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
                        
                        with st.spinner("🧠 Analizando estrategia táctica con Gemini AI..."):
                            try:
                                client = mister_analyzer.get_gemini_client(api_key)
                                report = mister_analyzer.analyze_structured_data(
                                    client, sync_res["squad"], sync_res["market"], sync_res["saldo"], user_notes
                                )
                                st.session_state.report_data = report
                                
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
            "Sube vídeos (.mp4, .mov) o fotos (.jpg, .png) de tu plantilla y mercado:",
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
                            
                    with st.spinner("🧠 Procesando imágenes/vídeo con Visión de Gemini AI..."):
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
        st.info("Carga plantilla y mercado de prueba realistas de LaLiga.")
        
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
        <p style="margin:4px 0 0 0; color:#e2e8f0; font-size:0.95rem;">Asistente Táctico & Financiero Inteligente para Mister Fantasy (Mundo Deportivo)</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Top Metrics Banner if squad data is loaded
if st.session_state.current_squad:
    squad = st.session_state.current_squad
    saldo = st.session_state.current_saldo
    total_val = sum(p.get("value", 0) for p in squad)
    total_pts = sum(p.get("points", 0) for p in squad)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>💰 Saldo Líquido</h3>
            <p>{saldo:,.0f} €</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>🛡️ Valor de Plantilla</h3>
            <p style="color:#38bdf8;">{total_val:,.0f} €</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>👥 Futbolistas</h3>
            <p style="color:#a78bfa;">{len(squad)} Jugadores</p>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h3>⭐ Puntos Totales</h3>
            <p style="color:#f59e0b;">{total_pts} Pts</p>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)


# Main Report Section Tabs
if st.session_state.report_data:
    tab_pitch, tab_market, tab_finance, tab_chat = st.tabs([
        "⚽ Campo Táctico & 11 Ideal",
        "📈 Mercado & Especulación (Chollos)",
        "📊 Diagnóstico Financiero",
        "💬 Consultor Míster Interactivo"
    ])
    
    # TAB 1: Campo Táctico & 11 Ideal
    with tab_pitch:
        st.subheader("👕 Alineación Ideal & Riesgo de Rotaciones (Formación 4-3-3 / 3-4-3)")
        
        if st.session_state.current_squad:
            squad = st.session_state.current_squad
            
            # Group squad by position
            por_list = [p for p in squad if p.get("position") == "POR"]
            def_list = [p for p in squad if p.get("position") == "DEF"]
            med_list = [p for p in squad if p.get("position") == "MED"]
            del_list = [p for p in squad if p.get("position") == "DEL"]
            
            # Tactical Field Render
            st.markdown('<div class="pitch-field">', unsafe_allow_html=True)
            
            # 1. Delanteros Line
            st.markdown("<h5 style='text-align:center; color:#ef4444; margin-bottom:8px;'>DELANTEROS</h5>", unsafe_allow_html=True)
            cols_del = st.columns(max(len(del_list), 1))
            for i, p in enumerate(del_list):
                with cols_del[i % len(cols_del)]:
                    badge_cls = "badge-titular" if p.get("points", 0) > 40 else "badge-riesgo"
                    st.markdown(f"""
                    <div class="mister-player-card">
                        <span class="pos-pill pos-del">DEL</span>
                        <div class="mister-player-name">{p['name']}</div>
                        <div class="mister-player-meta">⭐ {p.get('points', 0)} pts | {p.get('value', 0)/1e6:.1f} M€</div>
                        <div class="{badge_cls}">{p.get('fitness', 'Titular 100%')}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
            st.markdown("<div style='margin: 16px 0; border-top: 1px dashed rgba(255,255,255,0.2);'></div>", unsafe_allow_html=True)
            
            # 2. Centrocampistas Line
            st.markdown("<h5 style='text-align:center; color:#10b981; margin-bottom:8px;'>CENTROCAMPISTAS</h5>", unsafe_allow_html=True)
            cols_med = st.columns(max(len(med_list), 1))
            for i, p in enumerate(med_list):
                with cols_med[i % len(cols_med)]:
                    badge_cls = "badge-titular" if p.get("points", 0) > 40 else "badge-riesgo"
                    st.markdown(f"""
                    <div class="mister-player-card">
                        <span class="pos-pill pos-med">MED</span>
                        <div class="mister-player-name">{p['name']}</div>
                        <div class="mister-player-meta">⭐ {p.get('points', 0)} pts | {p.get('value', 0)/1e6:.1f} M€</div>
                        <div class="{badge_cls}">{p.get('fitness', 'Titular 100%')}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
            st.markdown("<div style='margin: 16px 0; border-top: 1px dashed rgba(255,255,255,0.2);'></div>", unsafe_allow_html=True)
            
            # 3. Defensas Line
            st.markdown("<h5 style='text-align:center; color:#3b82f6; margin-bottom:8px;'>DEFENSAS</h5>", unsafe_allow_html=True)
            cols_def = st.columns(max(len(def_list), 1))
            for i, p in enumerate(def_list):
                with cols_def[i % len(cols_def)]:
                    badge_cls = "badge-titular" if p.get("points", 0) > 40 else "badge-riesgo"
                    st.markdown(f"""
                    <div class="mister-player-card">
                        <span class="pos-pill pos-def">DEF</span>
                        <div class="mister-player-name">{p['name']}</div>
                        <div class="mister-player-meta">⭐ {p.get('points', 0)} pts | {p.get('value', 0)/1e6:.1f} M€</div>
                        <div class="{badge_cls}">{p.get('fitness', 'Titular 100%')}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
            st.markdown("<div style='margin: 16px 0; border-top: 1px dashed rgba(255,255,255,0.2);'></div>", unsafe_allow_html=True)
            
            # 4. Porteros Line
            st.markdown("<h5 style='text-align:center; color:#f59e0b; margin-bottom:8px;'>PORTERO</h5>", unsafe_allow_html=True)
            cols_por = st.columns(max(len(por_list), 1))
            for i, p in enumerate(por_list):
                with cols_por[i % len(cols_por)]:
                    badge_cls = "badge-titular" if p.get("points", 0) > 30 else "badge-riesgo"
                    st.markdown(f"""
                    <div class="mister-player-card">
                        <span class="pos-pill pos-por">POR</span>
                        <div class="mister-player-name">{p['name']}</div>
                        <div class="mister-player-meta">⭐ {p.get('points', 0)} pts | {p.get('value', 0)/1e6:.1f} M€</div>
                        <div class="{badge_cls}">{p.get('fitness', 'Titular 100%')}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
            st.markdown('</div>', unsafe_allow_html=True)
            
        st.markdown(st.session_state.report_data.get("alineacion", ""))
        
    # TAB 2: Mercado & Especulación (Chollos)
    with tab_market:
        st.subheader("🛒 Mercado de Fichajes & Estrategia de Especulación")
        
        if st.session_state.current_market:
            m_list = st.session_state.current_market
            st.markdown("#### 🎯 Oportunidades Destacadas del Mercado de Hoy:")
            m_cols = st.columns(min(len(m_list), 4))
            for i, p in enumerate(m_list[:8]):
                with m_cols[i % 4]:
                    pos_cls = f"pos-{p.get('position', 'MED').lower()}"
                    st.markdown(f"""
                    <div class="mister-player-card">
                        <span class="pos-pill {pos_cls}">{p.get('position', 'MED')}</span>
                        <div class="mister-player-name">{p['name']}</div>
                        <div class="mister-player-meta">💰 {p.get('value', 0)/1e6:.1f} M€ | ⭐ {p.get('points', 0)} pts</div>
                        <div class="badge-titular">📈 Revalorización al alza</div>
                    </div>
                    """, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            
        st.markdown(st.session_state.report_data.get("mercado", ""))
        
    # TAB 3: Diagnóstico Financiero
    with tab_finance:
        st.subheader("📊 Diagnóstico Económico del Patrimonio")
        st.markdown(st.session_state.report_data.get("economia", ""))
        
    # TAB 4: Consultor Míster Interactivo
    with tab_chat:
        st.subheader("💬 Consultor Míster Interactivo")
        st.caption("Pregúntale cualquier duda sobre tu 11, parches de última hora, ofertas de rivales o pujas máximas.")
        
        for i, msg in enumerate(st.session_state.chat_history):
            if i < 2:
                continue
            role = "user" if msg.role == "user" else "assistant"
            with st.chat_message(role):
                st.markdown(msg.parts[0].text)
                
        if user_query := st.chat_input("Ej: Tengo 14.5M, ¿debo pujar por Vinícius o asegurar a Budimir?"):
            with st.chat_message("user"):
                st.markdown(user_query)
                
            with st.chat_message("assistant"):
                with st.spinner("Pensando respuesta táctica con Gemini AI..."):
                    try:
                        client = mister_analyzer.get_gemini_client(api_key)
                        ans = mister_analyzer.ask_interactive_chat(
                            client, st.session_state.chat_history, user_query
                        )
                        st.markdown(ans)
                    except Exception as e:
                        st.error(f"Error en chat: {str(e)}")
