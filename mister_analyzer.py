"""
Gemini AI Analyzer module for Mister IA Optimizer Pro.
Uses google-genai SDK for multimodal video/image analysis and structured report generation.
"""

import os
import json
import tempfile
from typing import List, Dict, Any
from pydantic import BaseModel, Field
from google import genai
from google.genai import types

# Candidate models in order of priority (handles free tier & version updates)
CANDIDATE_MODELS = [
    'gemini-flash-latest',
    'gemini-3-flash-preview',
    'gemini-2.0-flash',
    'gemini-1.5-flash'
]

class MisterReport(BaseModel):
    economia: str = Field(description="Análisis del saldo, valor de plantilla, jugadores en subida/bajada y sugerencias de venta.")
    alineacion: str = Field(description="11 ideal en formación óptima, con desglose detallado de riesgos de rotación y titularidades.")
    mercado: str = Field(description="Oportunidades de mercado divididas en 1) Rendimiento seguro y 2) Especulación/Chollos a precio de coste.")

SYSTEM_PROMPT = """
Eres el analista táctico y financiero número 1 de Mister Fantasy (Mundo Deportivo) para LaLiga Española.
Tu objetivo es ayudar al usuario a ganar su liga maximizando el rendimiento de puntos y el patrimonio de su equipo.

Reglas clave para tu análisis:
1. **Economía**:
   - Analiza el SALDO disponible del usuario y su valor total de equipo.
   - Identifica qué jugadores están SUBIENDO de valor (mantener) y cuáles están BAJANDO (vender inmediatamente).
   - Indica a quién vender YA para liberar saldo fresco.
2. **Alineación**:
   - Propon un 11 titular optimizado en la mejor formación según la plantilla (ej: 4-3-3, 3-4-3, 4-4-2).
   - Analiza rigurosamente el **RIESGO DE ROTACIÓN** y probabilidad de titularidad de cada jugador (Titular 100%, Riesgo Medio 60%, Suplente 20%).
3. **Mercado**:
   - **Rendimiento**: Jugadores del mercado que darán PUNTOS SEGUROS en las próximas jornadas.
   - **Especulación (Chollos al alza)**: Jugadores baratos a precio de coste con alta tasa de revalorización diaria para sacar beneficio económico rápido.

Responde siempre en formato Markdown enriquecido, limpio, profesional y directo al grano con emojis tácticos.
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

def upload_file_to_gemini(client: genai.Client, file_bytes: bytes, filename: str) -> Any:
    """Upload a temporary file (video or image) to Gemini Files API."""
    suffix = f"_{filename}"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    try:
        gemini_file = client.files.upload(file=tmp_path)
        return gemini_file
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

def analyze_structured_data(client: genai.Client, squad: List[Dict], market: List[Dict], saldo: float, user_notes: str = "") -> Dict[str, str]:
    """
    Generate MisterReport from structured JSON data (API Auto-Sync or Demo).
    """
    user_context = f"""
    DATO REAL DE LA PLANTILLA Y MERCADO:
    - Saldo Disponible: {saldo:,.0f} €
    - Plantilla del Míster: {json.dumps(squad, ensure_ascii=False, indent=2)}
    - Mercado de Hoy: {json.dumps(market, ensure_ascii=False, indent=2)}
    
    Notas o dudas adicionales del usuario:
    {user_notes if user_notes else 'Ninguna.'}
    """
    
    prompt = f"{SYSTEM_PROMPT}\n\n{user_context}"
    
    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=MisterReport,
        temperature=0.2
    )
    
    response = generate_with_fallback(client, [prompt], config)
    return json.loads(response.text)

def analyze_media_files(client: genai.Client, gemini_files: List[Any], user_notes: str = "") -> Dict[str, str]:
    """
    Generate MisterReport from uploaded videos/images using Gemini Vision.
    """
    prompt = f"""
    {SYSTEM_PROMPT}
    
    Lee atentamente los vídeos e imágenes adjuntos donde se muestra el scroll por la plantilla y el mercado de Mister Fantasy.
    Extrae los nombres, valores, tendencias de valor y el SALDO exacto.
    
    Notas o preguntas del usuario a tener en cuenta:
    {user_notes if user_notes else 'Ninguna.'}
    """
    
    contents = gemini_files + [prompt]
    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=MisterReport,
        temperature=0.2
    )
    
    response = generate_with_fallback(client, contents, config)
    return json.loads(response.text)

def ask_interactive_chat(client: genai.Client, chat_history: List[types.Content], user_query: str) -> str:
    """
    Send query to interactive chat session with full tactical context history.
    """
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
