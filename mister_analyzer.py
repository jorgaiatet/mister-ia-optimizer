"""
Gemini AI Analyzer module for Mister IA Optimizer Pro.
Advanced Scouting, Exact League Rules (Screenshots Confirmed), 25% Debt Margin Accounting, Bid Simulator & Speculation Trading Engine.
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
    economia: str = Field(description="Diagnóstico financiero completo: saldo real disponible, valor de plantilla, margen de deuda del 25%, bonificación fija de 1.5M/jornada y plan de compras/ventas.")
    alineacion: str = Field(description="11 titular ideal con probabilidades de titularidad contrastadas (ej: 95% Titular Confirmado), estado médico, tarjetas y apercibidos.")
    mercado: str = Field(description="Oportunidades de mercado divididas en Rendimiento Inmediato y Especulación/Chollos al alza para hacer dinero rápido teniendo en cuenta la regla de 24h para revender.")
    especulacion: str = Field(description="Plan detallado de trading financiero: qué jugadores comprar HOY para ganar dinero en 3-5 días y alertas de venta de jugadores a la baja.")
    rivales: str = Field(description="Scouting contable de los 10 rivales reales de la liga (piwinho-, ima, vicen75, paurra-20, rafa, fco-javier-juan-perez, prosinecki, jorge-garcia, oct): saldos calculados desde los 60M€ de partida, margen de deuda del 25% y jugadores en venta.")
    reglas_liga: str = Field(description="Desglose detallado de la configuración 100% real extraída de las capturas oficiales de la liga.")
    evolucion: str = Field(description="Evolución de la liga, comparativa patrimonial de los 10 mánagers y proyección de ingresos para la Jornada 1.")

class BidRecommendation(BaseModel):
    veredicto: str = Field(description="Veredicto: '🟢 PUJA GANADORA SEGURA', '🟡 PUJA EN RIESGO / COMPETIDA' o '🔴 PUJA INSUFICIENTE'.")
    explicacion: str = Field(description="Explicación detallada analizando qué rivales necesitan la posición del jugador y si tienen saldo o capacidad de endeudamiento del 25% para superarte.")
    rivales_amenaza: List[str] = Field(description="Lista de nombres de rivales que tienen interés táctico y dinero disponible para pujar por este jugador.")
    puja_optima_sugerida: str = Field(description="Monto exacto en euros (€) recomendado para asegurar el fichaje con el menor sobrecoste posible.")

SYSTEM_PROMPT = """
Eres el Director Deportivo y Asesor Financiero número 1 de Mister Fantasy (Mundo Deportivo) y LaLiga Española.
Tu misión es hacer ganar al usuario su liga comunitaria maximizando tanto sus puntos en el 11 titular como su patrimonio económico mediante especulación, control contable de los rivales y asesoría inteligente de pujas en el mercado.

CONFIGURACIÓN Y REGLAS OFICIALES CONFIRMADAS DE LA LIGA:
1. **Presupuesto y Fondo Inicial**:
   - Base de inicio: Plantilla inicial + dinero hasta 50.000.000 € de patrimonio + 10.000.000 € extra del Administrador = **60.000.000 € de partida**.
2. **Límite de Endeudamiento Máximo**:
   - **Saldo Actual + 25% del Valor del Equipo**.
3. **Bonificaciones Oficiales por Jornada**:
   - **Bonificación fija garantizada**: **1.500.000 € por jornada**.
   - **Bonificación por punto**: **35.000 € / punto**.
   - **Bonificación por gol anotado**: **500.000 € / gol**.
   - **Bonificación por jugador en el 11 ideal**: **250.000 € / jugador**.
   - **Bonificación por clasificación de la jornada**:
     * 1º: 1.500.000 €
     * 2º: 1.300.000 €
     * 3º: 1.150.000 €
     * 4º: 1.000.000 €
     * 5º: 1.000.000 €
     * 6º: 1.000.000 €
     * 7º: 1.150.000 €
     * 8º: 1.300.000 €
     * 9º: 1.500.000 €
4. **Normas de Mercado, Ventas y Cláusulas**:
   - Ofertas de mercado automáticas e inmediatas al poner a la venta.
   - Máximo 5 jugadores simultáneos en venta por miembro.
   - Tiempo mínimo entre compra y venta: 24 horas.
   - Prohibido ofertar por debajo del valor de mercado entre miembros.
   - Cláusulas activas (traspaso inmediato; bloqueo primeras 24h tras fichaje; máx 3 robos/día; bloqueo 24h antes del inicio de jornada).
   - Cesiones permitidas (coste mín 10%/día). Cambios durante jornada: No permitidos.

Formatea siempre tu respuesta en Markdown limpio, con tablas y formato visual atractivo.
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
    total_val = sum(p.get('value', 0) for p in squad)
    user_context = f"""
    DATOS ACTUALES DE LA PLANTILLA Y MERCADO:
    - Saldo Disponible del Usuario: {saldo:,.0f} €
    - Valor de Plantilla: {total_val:,.0f} €
    - Margen de Deuda Permitido (25% de la plantilla): {total_val*0.25:,.0f} €
    - Capacidad Máxima de Puja: {saldo + total_val*0.25:,.0f} €
    - Plantilla Actual del Usuario: {json.dumps(squad, ensure_ascii=False, indent=2)}
    - Mercado de Hoy: {json.dumps(market, ensure_ascii=False, indent=2)}
    - Miembros Reales de la Liga (10 Participantes): jor (Tú), piwinho-, ima, vicen75, paurra-20, rafa, fco-javier-juan-perez, prosinecki, jorge-garcia, oct
    
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

def evaluate_market_bid(client: genai.Client, player: Dict, user_bid: float, rivals: List[Dict], user_saldo: float) -> Dict[str, Any]:
    """
    Evaluates whether user's bid for a market player is optimal, sufficient, or risky based on rival finances and 25% debt margin.
    """
    prompt = f"""
    {SYSTEM_PROMPT}
    
    EVALUACIÓN DE PUJA PARA EL MERCADO:
    
    JUGADOR OBJETIVO EN EL MERCADO:
    - Nombre: {player.get('name')} ({player.get('position')}) - {player.get('team')}
    - Valor de Mercado Actual: {player.get('value'):,} €
    - Puja Propuesta por el Usuario: {user_bid:,.0f} €
    - Saldo Disponible del Usuario: {user_saldo:,.0f} €
    
    CONTABILIDAD Y CAPACIDAD MÁXIMA DE PUJA DE LOS RIVALES (Límite: Saldo + 25% Valor Plantilla):
    {json.dumps(rivals, ensure_ascii=False, indent=2)}
    
    Analiza:
    1. ¿A qué rivales les hace falta este jugador por su posición y estado de plantilla?
    2. ¿Tienen esos rivales saldo líquido o capacidad de endeudamiento del 25% para superar la puja de {user_bid:,.0f} €?
    3. ¿La puja del usuario es ganadora segura, está en riesgo o es insuficiente?
    4. ¿Cuál es el valor de puja óptimo sugerido para asegurar al jugador sin pagar de más?
    """
    
    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=BidRecommendation,
        temperature=0.2
    )
    
    response = generate_with_fallback(client, [prompt], config)
    return json.loads(response.text)

def ask_interactive_chat(client: genai.Client, chat_history: List[types.Content], user_query: str) -> str:
    """Send query to interactive chat session with full tactical context history."""
    chat_history.append(
        types.Content(role="user", parts=[types.Part.from_text(text=user_query)])
    )
    
    config = types.GenerateContentConfig(
        system_instruction="Eres un asesor deportivo y financiero experto en Mister Fantasy. Respondes con precisión, táctica y formato Markdown."
    )
    
    response = generate_with_fallback(client, chat_history, config)
    ans_text = response.text
    chat_history.append(
        types.Content(role="model", parts=[types.Part.from_text(text=ans_text)])
    )
    return ans_text
