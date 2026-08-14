"""
Gemini AI Analyzer module for Mister IA Optimizer Pro.
Uses google-genai SDK for multimodal analysis, web research on lineups, injuries, suspensions, rival intelligence, and league evolution.
"""

import os
import json
import tempfile
from typing import List, Dict, Any
from pydantic import BaseModel, Field
from google import genai
from google.genai import types

# Candidate models in order of priority
CANDIDATE_MODELS = [
    'gemini-flash-latest',
    'gemini-3-flash-preview',
    'gemini-2.0-flash',
    'gemini-1.5-flash'
]

class MisterReport(BaseModel):
    economia: str = Field(description="Diagnóstico financiero completo: saldo disponible, valor total de plantilla, análisis de liquidez y plan de compras/ventas.")
    alineacion: str = Field(description="11 titular ideal con probabilidades de titularidad contrastadas (ej: 95% Titular Confirmado), estado médico (lesiones/molestias), tarjetas y apercibidos.")
    mercado: str = Field(description="Oportunidades de mercado de hoy divididas en Rendimiento Inmediato y Especulación/Chollos al alza.")
    rivales: str = Field(description="Análisis de inteligencia de rivales de la comunidad (Ima, Oct, Paurra-20, Piwinho), fortalezas, debilidades y comparación patrimonial.")
    evolucion: str = Field(description="Evolución de la liga, comparativa de plantillas, jugadores más cotizados y previsión de puntos para la Jornada 1.")

SYSTEM_PROMPT = """
Eres el analista táctico, deportivo y financiero de élite para Mister Fantasy (Mundo Deportivo) y LaLiga Española.
Tu misión es investigar y optimizar la plantilla del usuario para ganar su liga con la máxima ventaja sobre sus rivales.

INSTRUCCIONES CLAVE POR SECCIÓN:

1. **Economía & Diagnóstico Financiero**:
   - Analiza el Saldo Real y el Valor Total de la plantilla.
   - Recomienda si conviene mantener la liquidez o invertir en posiciones clave (como portería o delantera).

2. **Alineación, Probabilidades de Titularidad & Estado Físico**:
   - Para cada uno de los jugadores del 11 titular y banquillo, evalúa su probabilidad real de jugar según las últimas noticias de los clubes y prensa deportiva:
     * Porcentaje de titularidad: (ej. `95% Titular Confirmado`, `85% Probable Titular`, `60% Duda Táctica / Rotación`, `30% Suplente`).
     * Estado médico y físico: (ej. `100% Disponible`, `Molestias`, `En proceso de recuperación`).
     * Situación disciplinaria: (ej. `Sin sanciones`, `Apercibido 0/5 amarillas`).

3. **Mercado de Fichajes**:
   - Jugadores recomendados para fichar hoy.
   - Jugadores con alta revalorización económica diaria para especular.

4. **Inteligencia de Rivales en la Comunidad**:
   - Analiza a los rivales directos de la liga del usuario (Ima, Oct, Paurra-20, Piwinho).
   - Detecta sus puntos débiles y dónde el usuario tiene ventaja competitiva (ej. centro del campo estelar con Olmo y Sancet).

5. **Evolución de la Liga & Previsión J1**:
   - Proyección estimada de puntos para la Jornada 1.
   - Estrategia para dominar la tabla en las primeras 5 jornadas.

Formatea siempre tu respuesta en Markdown limpio, con tablas y emojis deportivos bien estructurados.
"""

def get_gemini_client(api_key: str = None) -> genai.Client:
    """Initialize and return Google GenAI client."""
    key = api_key or os.environ.get("GEMINI_API_KEY")
    if not key:
        raise ValueError("Se requiere una API Key de Google Gemini válida.")
    return genai.Client(api_key=key)

def generate_with_fallback(client: genai.Client, contents: List[Any], config: types.GenerateContentConfig = None) -> Any:
    """Call Gemini API with model fallback list for maximum reliability."""
    last_exception = None
    for model_name in CANDIDATE_MODELS:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=contents,
                config=config
            )
            return response
        except Exception as e:
            last_exception = e
            continue
    raise last_exception or ValueError("No se pudo conectar a ningún modelo de Gemini disponible.")

def analyze_structured_data(client: genai.Client, squad: List[Dict], market: List[Dict], saldo: float, user_notes: str = "") -> Dict[str, str]:
    """Generate MisterReport from structured JSON data."""
    user_context = f"""
    DATOS ACTUALES DE LA PLANTILLA Y MERCADO:
    - Saldo Disponible: {saldo:,.0f} €
    - Plantilla Actual del Usuario: {json.dumps(squad, ensure_ascii=False, indent=2)}
    - Mercado de Hoy: {json.dumps(market, ensure_ascii=False, indent=2)}
    - Rivales de la Liga Comunitaria: Ima, Oct, Paurra-20, Piwinho
    
    Notas o dudas del usuario:
    {user_notes if user_notes else 'Ninguna.'}
    """
    
    prompt = f"{SYSTEM_PROMPT}\n\n{user_context}"
    
    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=MisterReport,
        temperature=0.3
    )
    
    response = generate_with_fallback(client, [prompt], config)
    return json.loads(response.text)

def ask_interactive_chat(client: genai.Client, chat_history: List[types.Content], user_query: str) -> str:
    """Send query to interactive chat session with full tactical context history."""
    chat_history.append(
        types.Content(role="user", parts=[types.Part.from_text(text=user_query)])
    )
    
    config = types.GenerateContentConfig(
        system_instruction="Eres un asesor experto en Mister Fantasy. Respondes con precisión, tono deportivo táctico y formato Markdown."
    )
    
    response = generate_with_fallback(client, chat_history, config)
    ans_text = response.text
    chat_history.append(
        types.Content(role="model", parts=[types.Part.from_text(text=ans_text)])
    )
    return ans_text
