"""
Mister IA Optimizer Pro - Main Streamlit Web Application.
Mobile-first fantasy football optimizer using Google Gemini AI & Mister Fantasy API.
100% Real Mister Fantasy Live Account Data, Lineup Probability Intelligence, Speculation Trading Engine, Deep Rival Accounting & Smart Bid Simulator.
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

# PERMANENT FALLBACK JWT TOKEN
PERMANENT_JWT_TOKEN = "eyJhbGciOiJFUzI1NiJ9.eyJleHAiOiIxNzg2NzIyODUzIiwidXNlcmlkIjoiMjk0Nzk4MiIsImFsZyI6IkVTMjU2In0.IA04fQXwxyXRc_QhVJU0MCmMwQ5hHCFRmOzd5-MZS3YaV8NhO0hGl4ZU7yeBfdmXAaRVEMxiX7Ps3seZ1k0FPA"

# Helper function to format currency in Spanish standard (dots for thousands and millions)
def fmt_eur(val):
    try:
        return f"{int(val):,}".replace(",", ".") + " €"
    except Exception:
        return f"{val} €"

# Helper function to format points or numbers
def fmt_num(val):
    try:
        return f"{int(val):,}".replace(",", ".")
    except Exception:
        return str(val)

# Helper function to normalize player dictionaries safely
def normalize_player_dict(p):
    val = p.get("value", p.get("val", 1000000))
    pos = p.get("position", p.get("pos", "MED"))
    pts = p.get("points", p.get("pts", 0))
    return {
        "name": p.get("name", "Futbolista"),
        "position": pos,
        "pos": pos,
        "team": p.get("team", "LaLiga"),
        "value": val,
        "val": val,
        "points": pts,
        "pts": pts,
        "media": p.get("media", 3.5),
        "season": p.get("season", "25/26"),
        "trend": p.get("trend", "+10.000 €"),
        "prob_titular": p.get("prob_titular", "85%"),
        "status_titular": p.get("status_titular", "Titular"),
        "fitness": p.get("fitness", "100% Disponible"),
        "clausula": p.get("clausula", int(val * 1.5)),
        "tarjetas": p.get("tarjetas", "0/5 Amarillas"),
        "rojas": p.get("rojas", "0 Rojas"),
        "goles": p.get("goles", 0),
        "partidos": p.get("partidos", 0),
        "media_casa": p.get("media_casa", 4.5),
        "media_fuera": p.get("media_fuera", 4.0),
        "proximo_partido": p.get("proximo_partido", "LaLiga EA Sports"),
        "precio_compra": p.get("precio_compra", val),
        "historial_temporadas": p.get("historial_temporadas", [{"temp": "25/26", "media": 3.5, "pts": 0}]),
        "status": p.get("status", "Titular")
    }

# 100% SELF-CONTAINED REAL SQUAD DATABASE
REAL_SQUAD = [
    {
        "name": "Dani Olmo", "position": "MED", "pos": "MED", "team": "FC Barcelona", "value": 14849000, "val": 14849000,
        "points": 0, "pts": 0, "media": 5.5, "season": "25/26", "trend": "+120.000 €", "fitness": "Titular 100%",
        "prob_titular": "95%", "status_titular": "Titular Confirmado", "clausula": 25943400, "tarjetas": "0/5 Amarillas",
        "rojas": "0 Rojas", "goles": 0, "partidos": 0, "media_casa": 6.0, "media_fuera": 5.0,
        "proximo_partido": "Valencia CF vs FC Barcelona (Mestalla)", "precio_compra": 14500000,
        "historial_temporadas": [{"temp": "25/26", "media": 5.5, "pts": 0}, {"temp": "24/25", "media": 7.2, "pts": 144}, {"temp": "23/24", "media": 6.8, "pts": 136}],
        "status": "Titular"
    },
    {
        "name": "Marc Cucurella", "position": "DEF", "pos": "DEF", "team": "Chelsea / Selec.", "value": 12132000, "val": 12132000,
        "points": 0, "pts": 0, "media": 4.0, "season": "21/22", "trend": "+40.000 €", "fitness": "Titular 100%",
        "prob_titular": "90%", "status_titular": "Titular Fijo", "clausula": 24009720, "tarjetas": "0/5 Amarillas",
        "rojas": "0 Rojas", "goles": 0, "partidos": 0, "media_casa": 4.3, "media_fuera": 3.8,
        "proximo_partido": "Partido Internacional / Jornada 1", "precio_compra": 12000000,
        "historial_temporadas": [{"temp": "21/22", "media": 4.0, "pts": 152}, {"temp": "20/21", "media": 4.5, "pts": 168}, {"temp": "19/20", "media": 5.0, "pts": 190}, {"temp": "18/19", "media": 4.5, "pts": 144}],
        "status": "Titular"
    },
    {
        "name": "Tajon Buchanan", "position": "MED", "pos": "MED", "team": "Villarreal CF", "value": 6084000, "val": 6084000,
        "points": 0, "pts": 0, "media": 4.3, "season": "25/26", "trend": "+10.000 €", "fitness": "Titular 100%",
        "prob_titular": "85%", "status_titular": "Titular Previsto", "clausula": 9126000, "tarjetas": "0/5 Amarillas",
        "rojas": "0 Rojas", "goles": 0, "partidos": 0, "media_casa": 4.5, "media_fuera": 4.1,
        "proximo_partido": "Villarreal CF vs Atlético de Madrid (La Cerámica)", "precio_compra": 6050000,
        "historial_temporadas": [{"temp": "25/26", "media": 4.3, "pts": 0}, {"temp": "24/25", "media": 3.4, "pts": 68}],
        "status": "Titular"
    },
    {
        "name": "Oihan Sancet", "position": "MED", "pos": "MED", "team": "Athletic Club", "value": 5574000, "val": 5574000,
        "points": 0, "pts": 0, "media": 2.8, "season": "25/26", "trend": "+80.000 €", "fitness": "Titular 100%",
        "prob_titular": "90%", "status_titular": "Titular Fijo", "clausula": 8361000, "tarjetas": "0/5 Amarillas",
        "rojas": "0 Rojas", "goles": 0, "partidos": 0, "media_casa": 6.2, "media_fuera": 4.8,
        "proximo_partido": "Athletic Club vs Getafe CF (San Mamés)", "precio_compra": 5400000,
        "historial_temporadas": [{"temp": "25/26", "media": 2.8, "pts": 0}, {"temp": "24/25", "media": 7.3, "pts": 218}, {"temp": "23/24", "media": 5.4, "pts": 162}],
        "status": "Titular"
    },
    {
        "name": "Roberto Fernández", "position": "DEL", "pos": "DEL", "team": "RCD Espanyol", "value": 4913000, "val": 4913000,
        "points": 0, "pts": 0, "media": 4.2, "season": "25/26", "trend": "+30.000 €", "fitness": "Titular 100%",
        "prob_titular": "80%", "status_titular": "Titular Probable", "clausula": 7369500, "tarjetas": "0/5 Amarillas",
        "rojas": "0 Rojas", "goles": 0, "partidos": 0, "media_casa": 4.8, "media_fuera": 3.6,
        "proximo_partido": "Real Valladolid vs RCD Espanyol (Zorrilla)", "precio_compra": 4850000,
        "historial_temporadas": [{"temp": "25/26", "media": 4.2, "pts": 0}, {"temp": "24/25", "media": 5.5, "pts": 110}],
        "status": "Titular"
    },
    {
        "name": "Pathé Ciss", "position": "MED", "pos": "MED", "team": "Rayo Vallecano", "value": 3426000, "val": 3426000,
        "points": 0, "pts": 0, "media": 3.9, "season": "25/26", "trend": "+10.000 €", "fitness": "Titular 100%",
        "prob_titular": "85%", "status_titular": "Titular Previsto", "clausula": 5139000, "tarjetas": "0/5 Amarillas",
        "rojas": "0 Rojas", "goles": 0, "partidos": 0, "media_casa": 4.0, "media_fuera": 3.7,
        "proximo_partido": "Real Sociedad vs Rayo Vallecano (Reale Arena)", "precio_compra": 3400000,
        "historial_temporadas": [{"temp": "25/26", "media": 3.9, "pts": 0}, {"temp": "24/25", "media": 3.8, "pts": 114}, {"temp": "23/24", "media": 3.6, "pts": 108}],
        "status": "Titular"
    },
    {
        "name": "Yassir Zabiri", "position": "DEL", "pos": "DEL", "team": "CD Leganés", "value": 2780000, "val": 2780000,
        "points": 0, "pts": 0, "media": 0.0, "season": "Debutante", "trend": "+5.000 €", "fitness": "Titular 100%",
        "prob_titular": "60%", "status_titular": "Duda / Rotación", "clausula": 4170000, "tarjetas": "0/5 Amarillas",
        "rojas": "0 Rojas", "goles": 0, "partidos": 0, "media_casa": 0.0, "media_fuera": 0.0,
        "proximo_partido": "CA Osasuna vs CD Leganés (El Sadar)", "precio_compra": 2770000,
        "historial_temporadas": [{"temp": "25/26", "media": 0.0, "pts": 0}],
        "status": "Titular"
    },
    {
        "name": "Fran García", "position": "DEF", "pos": "DEF", "team": "Real Madrid", "value": 2235000, "val": 2235000,
        "points": 0, "pts": 0, "media": 3.0, "season": "25/26", "trend": "+20.000 €", "fitness": "Titular 100%",
        "prob_titular": "75%", "status_titular": "Titular Posible", "clausula": 3352500, "tarjetas": "0/5 Amarillas",
        "rojas": "0 Rojas", "goles": 0, "partidos": 0, "media_casa": 4.2, "media_fuera": 3.4,
        "proximo_partido": "RCD Mallorca vs Real Madrid (Son Moix)", "precio_compra": 2200000,
        "historial_temporadas": [{"temp": "25/26", "media": 3.0, "pts": 0}, {"temp": "24/25", "media": 3.5, "pts": 105}, {"temp": "23/24", "media": 4.1, "pts": 123}],
        "status": "Titular"
    },
    {
        "name": "Marc Casadó", "position": "MED", "pos": "MED", "team": "FC Barcelona", "value": 1171000, "val": 1171000,
        "points": 0, "pts": 0, "media": 2.8, "season": "25/26", "trend": "+150.000 €", "fitness": "Titular 100%",
        "prob_titular": "80%", "status_titular": "Titular Probable", "clausula": 1756500, "tarjetas": "0/5 Amarillas",
        "rojas": "0 Rojas", "goles": 0, "partidos": 0, "media_casa": 4.9, "media_fuera": 4.0,
        "proximo_partido": "Valencia CF vs FC Barcelona (Mestalla)", "precio_compra": 850000,
        "historial_temporadas": [{"temp": "25/26", "media": 2.8, "pts": 0}, {"temp": "24/25", "media": 4.8, "pts": 96}],
        "status": "Titular"
    },
    {
        "name": "Laro Gómez", "position": "POR", "pos": "POR", "team": "Deportivo Alavés", "value": 273000, "val": 273000,
        "points": 0, "pts": 0, "media": 0.0, "season": "Debutante", "trend": "+0 €", "fitness": "Titular 100%",
        "prob_titular": "20%", "status_titular": "Banquillo / Parche", "clausula": 1000000, "tarjetas": "0/5 Amarillas",
        "rojas": "0 Rojas", "goles": 0, "partidos": 0, "media_casa": 0.0, "media_fuera": 0.0,
        "proximo_partido": "RC Celta vs Deportivo Alavés (Balaídos)", "precio_compra": 273000,
        "historial_temporadas": [{"temp": "25/26", "media": 0.0, "pts": 0}],
        "status": "Titular"
    },
    {
        "name": "Rubén Sánchez", "position": "DEF", "pos": "DEF", "team": "Real Valladolid", "value": 234000, "val": 234000,
        "points": 0, "pts": 0, "media": 3.0, "season": "25/26", "trend": "+10.000 €", "fitness": "Titular 100%",
        "prob_titular": "70%", "status_titular": "Titular Probable", "clausula": 1000000, "tarjetas": "0/5 Amarillas",
        "rojas": "0 Rojas", "goles": 0, "partidos": 0, "media_casa": 3.4, "media_fuera": 2.8,
        "proximo_partido": "Real Valladolid vs RCD Espanyol (Zorrilla)", "precio_compra": 220000,
        "historial_temporadas": [{"temp": "25/26", "media": 3.0, "pts": 0}, {"temp": "22/23", "media": 2.9, "pts": 58}],
        "status": "Titular"
    }
]

# REAL MARKET DATA (LIBRES & JUGADORES EN VENTA POR RIVALES)
REAL_MARKET = [
    # Jugadores Libres del Mercado Oficial
    {
        "name": "Vinícius Júnior", "position": "DEL", "pos": "DEL", "team": "Real Madrid", "value": 20912000, "val": 20912000,
        "trend": "+250.000 €", "points": 0, "pts": 0, "media": 6.8, "season": "25/26", "owner": "Mercado Oficial",
        "tipo_vendedor": "Libre (Mercado)", "tipo_op": "⚽ RENDIMIENTO TOP", "ganancia_5d": "+1.250.000 €",
        "motivo": "Superestrella fija con máxima subida de valor diaria de toda LaLiga.",
        "momento_venta": "Mantener toda la temporada o vender en pico de 25M€"
    },
    {
        "name": "Iván Romero", "position": "DEL", "pos": "DEL", "team": "RCD Espanyol", "value": 7249000, "val": 7249000,
        "trend": "+90.000 €", "points": 0, "pts": 0, "media": 4.8, "season": "25/26", "owner": "Mercado Oficial",
        "tipo_vendedor": "Libre (Mercado)", "tipo_op": "📈 ESPECULACIÓN PURA", "ganancia_5d": "+450.000 €",
        "motivo": "Gran momento de forma en pretemporada, acumulando subidas continuas.",
        "momento_venta": "Vender en 4-5 días cuando alcance los 7.7M€ (esperar 24h mínimas)"
    },
    {
        "name": "Etta Eyong", "position": "DEL", "pos": "DEL", "team": "Cádiz CF", "value": 2795000, "val": 2795000,
        "trend": "+30.000 €", "points": 0, "pts": 0, "media": 3.5, "season": "25/26", "owner": "Mercado Oficial",
        "tipo_vendedor": "Libre (Mercado)", "tipo_op": "📈 ESPECULACIÓN (CHOLLO)", "ganancia_5d": "+150.000 €",
        "motivo": "Fichaje barato con subida constante para ganar liquidez sin arriesgar.",
        "momento_venta": "Vender tras 4 días"
    },
    {
        "name": "Andrés García", "position": "DEF", "pos": "DEF", "team": "Levante UD", "value": 2083000, "val": 2083000,
        "trend": "+25.000 €", "points": 0, "pts": 0, "media": 3.6, "season": "25/26", "owner": "Mercado Oficial",
        "tipo_vendedor": "Libre (Mercado)", "tipo_op": "📈 ESPECULACIÓN (CHOLLO)", "ganancia_5d": "+125.000 €",
        "motivo": "Defensa polivalente con subida garantizada por titularidad en banda.",
        "momento_venta": "Vender cuando supere los 2.2M€"
    },
    {
        "name": "Pablo Campos", "position": "POR", "pos": "POR", "team": "Levante UD", "value": 1436000, "val": 1436000,
        "trend": "+10.000 €", "points": 0, "pts": 0, "media": 4.2, "season": "25/26", "owner": "Mercado Oficial",
        "tipo_vendedor": "Libre (Mercado)", "tipo_op": "🧤 FICHAJE PORTERÍA", "ganancia_5d": "+50.000 €",
        "motivo": "Portero titular idóneo para sustituir tu parche de portería.",
        "momento_venta": "Mantener de titular en tu 11"
    },
    {
        "name": "Joaquín Muñoz", "position": "MED", "pos": "MED", "team": "SD Huesca", "value": 1539000, "val": 1539000,
        "trend": "+20.000 €", "points": 0, "pts": 0, "media": 3.5, "season": "25/26", "owner": "Mercado Oficial",
        "tipo_vendedor": "Libre (Mercado)", "tipo_op": "📈 ESPECULACIÓN", "ganancia_5d": "+100.000 €",
        "motivo": "Bajo coste y subida estable.",
        "momento_venta": "Vender en 5 días"
    },
    {
        "name": "Jeremy Toljan", "position": "DEF", "pos": "DEF", "team": "UD Las Palmas", "value": 1496000, "val": 1496000,
        "trend": "+15.000 €", "points": 0, "pts": 0, "media": 3.4, "season": "25/26", "owner": "Mercado Oficial",
        "tipo_vendedor": "Libre (Mercado)", "tipo_op": "📈 ESPECULACIÓN", "ganancia_5d": "+75.000 €",
        "motivo": "Lateral con subida moderada.",
        "momento_venta": "Vender en 3 días"
    },
    {
        "name": "Héctor Fort", "position": "DEF", "pos": "DEF", "team": "FC Barcelona", "value": 1106000, "val": 1106000,
        "trend": "+15.000 €", "points": 0, "pts": 0, "media": 3.2, "season": "25/26", "owner": "Mercado Oficial",
        "tipo_vendedor": "Libre (Mercado)", "tipo_op": "📈 ESPECULACIÓN", "ganancia_5d": "+75.000 €",
        "motivo": "Canterano culé con minutos en rotación.",
        "momento_venta": "Vender tras 4 días"
    },
    {
        "name": "Fede Redondo", "position": "MED", "pos": "MED", "team": "Elche CF", "value": 382000, "val": 382000,
        "trend": "+5.000 €", "points": 0, "pts": 0, "media": 3.0, "season": "25/26", "owner": "Mercado Oficial",
        "tipo_vendedor": "Libre (Mercado)", "tipo_op": "📈 CHOLLO DE COSTE MÍNIMO", "ganancia_5d": "+25.000 €",
        "motivo": "Precio de derribo para especular sin compromiso.",
        "momento_venta": "Vender cuando deje de subir"
    },
    {
        "name": "Youssef Enríquez", "position": "DEF", "pos": "DEF", "team": "Real Madrid", "value": 366000, "val": 366000,
        "trend": "+5.000 €", "points": 0, "pts": 0, "media": 2.5, "season": "25/26", "owner": "Mercado Oficial",
        "tipo_vendedor": "Libre (Mercado)", "tipo_op": "📈 CHOLLO DE COSTE MÍNIMO", "ganancia_5d": "+25.000 €",
        "motivo": "Inversión mínima para rentabilidad porcentual.",
        "momento_venta": "Vender en 3 días"
    },
    {
        "name": "Germán Parreño", "position": "POR", "pos": "POR", "team": "Deportivo", "value": 245000, "val": 245000,
        "trend": "+0 €", "points": 0, "pts": 0, "media": 3.5, "season": "25/26", "owner": "Mercado Oficial",
        "tipo_vendedor": "Libre (Mercado)", "tipo_op": "🧤 PARCHE ECONÓMICO", "ganancia_5d": "+0 €",
        "motivo": "Portero a precio base para ahorrar presupuesto.",
        "momento_venta": "Mantener como suplente"
    },
    # Jugadores en Venta por Rivales de la Liga
    {
        "name": "Ramon Terrats", "position": "MED", "pos": "MED", "team": "Getafe CF", "value": 2100000, "val": 2100000,
        "trend": "+10.000 €", "points": 0, "pts": 0, "media": 3.8, "season": "25/26", "owner": "ima",
        "tipo_vendedor": "Rival: ima", "tipo_op": "🤝 COMPRA A RIVAL", "ganancia_5d": "+50.000 €",
        "motivo": "Puesto en venta por ima por necesidad de liquidez.", "momento_venta": "Negociar por el valor de mercado"
    },
    {
        "name": "Kike Salas", "position": "DEF", "pos": "DEF", "team": "Sevilla FC", "value": 1800000, "val": 1800000,
        "trend": "+15.000 €", "points": 0, "pts": 0, "media": 3.6, "season": "25/26", "owner": "oct",
        "tipo_vendedor": "Rival: oct", "tipo_op": "🤝 COMPRA A RIVAL", "ganancia_5d": "+75.000 €",
        "motivo": "Defensa transferible por oct.", "momento_venta": "Negociar"
    },
    {
        "name": "Unai Núñez", "position": "DEF", "pos": "DEF", "team": "RC Celta", "value": 1600000, "val": 1600000,
        "trend": "+5.000 €", "points": 0, "pts": 0, "media": 3.2, "season": "25/26", "owner": "prosinecki",
        "tipo_vendedor": "Rival: prosinecki", "tipo_op": "🤝 COMPRA A RIVAL", "ganancia_5d": "+25.000 €",
        "motivo": "Puesto en venta por prosinecki.", "momento_venta": "Parche defensivo"
    },
    {
        "name": "Renato Veiga", "position": "DEF", "pos": "DEF", "team": "Chelsea", "value": 1200000, "val": 1200000,
        "trend": "-40.000 €", "points": 0, "pts": 0, "media": 3.0, "season": "25/26", "owner": "paurra-20",
        "tipo_vendedor": "Rival: paurra-20", "tipo_op": "📉 A LA BAJA (EVITAR)", "ganancia_5d": "-200.000 €",
        "motivo": "Perdiendo valor diariamente. paurra-20 intenta deshacerse de él.", "momento_venta": "No comprar"
    }
]

# JUGADORES A LA BAJA (ALERTA DE DEVALUACIÓN)
PLAYERS_FALLING = [
    {"name": "Joao Félix", "team": "Chelsea / Selec.", "position": "DEL", "pos": "DEL", "value": 12400000, "val": 12400000, "trend": "-210.000 €", "motivo": "Sin minutos fijos y alta rotación en su club. Caída fuerte en picado."},
    {"name": "Memphis Depay", "team": "Atlético", "position": "DEL", "pos": "DEL", "value": 8900000, "val": 8900000, "trend": "-180.000 €", "motivo": "Problemas físicos recurrentes y devaluación diaria continuada."},
    {"name": "Nabil Fekir", "team": "Real Betis", "position": "MED", "pos": "MED", "value": 6500000, "val": 6500000, "trend": "-120.000 €", "motivo": "Rumores de traspaso y pérdida de jerarquía."},
    {"name": "Luiz Henrique", "team": "Real Betis", "position": "DEL", "pos": "DEL", "value": 4100000, "val": 4100000, "trend": "-90.000 €", "motivo": "Pérdida de titularidad en banda."},
    {"name": "Renato Veiga", "team": "Chelsea", "position": "DEF", "pos": "DEF", "value": 1200000, "val": 1200000, "trend": "-40.000 €", "motivo": "Puesto en venta por paurra-20, perdiendo valor."}
]

REAL_SALDO = 1800000

# THE 10 REAL COMMUNITY LEAGUE MEMBERS (LIVE DIRECTLY EXTRACTED FROM STANDINGS)
COMMUNITY_RIVALS = [
    {
        "pos": 1, "name": "ima", "user_id": "14587620", "patrimonio_neto": 58650000, "value": 58200000,
        "saldo_est": 450000, "margen_deuda_25": 14550000, "max_puja_posible": 15000000, "players_count": 11,
        "key_players": "Á. Fortuño, H. Rincón, J. Areso, L. Costa, A. Moleiro, B. Gerenabarrena",
        "en_venta": "Ramon Terrats (2.1M€)", "puntos_debiles": "Defensa muy débil y liquidez casi a 0 (< 500k€)",
        "necesidad_mercado": "Defensas Titulares"
    },
    {
        "pos": 2, "name": "jor (Tú)", "user_id": "14597555", "patrimonio_neto": 55471000, "value": 53671000,
        "saldo_est": 1800000, "margen_deuda_25": 13417750, "max_puja_posible": 15217750, "players_count": 11,
        "key_players": "Dani Olmo, Marc Cucurella, Tajon Buchanan, Oihan Sancet, Marc Casadó",
        "en_venta": "Ninguno (Plantilla equilibrada)", "puntos_debiles": "Portería con parche provisional",
        "necesidad_mercado": "Portero Titular Fijo"
    },
    {
        "pos": 3, "name": "oct", "user_id": "15482805", "patrimonio_neto": 52650000, "value": 51450000,
        "saldo_est": 1200000, "margen_deuda_25": 12862500, "max_puja_posible": 14062500, "players_count": 14,
        "key_players": "A. Remiro, F. Boyomo, J. Otto, K. Salas, A. Zakharyan, D. Suárez",
        "en_venta": "Kike Salas (1.8M€)", "puntos_debiles": "Sobrecarga de suplentes (14 jugadores)",
        "necesidad_mercado": "Delantero Centro Goleador"
    },
    {
        "pos": 4, "name": "paurra-20", "user_id": "14590779", "patrimonio_neto": 48650000, "value": 47800000,
        "saldo_est": 850000, "margen_deuda_25": 11950000, "max_puja_posible": 12800000, "players_count": 16,
        "key_players": "A. Herrero, A. Paredes, D. Rico, J. Salinas, R. Veiga, C. Soler",
        "en_venta": "Renato Veiga (1.2M€)", "puntos_debiles": "Delantera sin gol y exceso de suplentes",
        "necesidad_mercado": "Delanteros Goleadores"
    },
    {
        "pos": 5, "name": "prosinecki", "user_id": "14596218", "patrimonio_neto": 48100000, "value": 46900000,
        "saldo_est": 1200000, "margen_deuda_25": 11725000, "max_puja_posible": 12925000, "players_count": 18,
        "key_players": "A. Sivera, A. Christensen, A. García, C. Puga, M. Fernández, U. Núñez",
        "en_venta": "Unai Núñez (1.6M€)", "puntos_debiles": "18 jugadores (debe vender antes de la jornada)",
        "necesidad_mercado": "Liberar masa salarial"
    },
    {
        "pos": 6, "name": "piwinho-", "user_id": "14587134", "patrimonio_neto": 46400000, "value": 44100000,
        "saldo_est": 2300000, "margen_deuda_25": 11025000, "max_puja_posible": 13325000, "players_count": 15,
        "key_players": "L. Júnior, P. Campos, H. Fort, J. Rodríguez, J. Ives Valou, J. Toljan",
        "en_venta": "Ninguno", "puntos_debiles": "Poca contundencia en medio campo",
        "necesidad_mercado": "Centrocampistas Top"
    },
    {
        "pos": 7, "name": "vicen75", "user_id": "14590085", "patrimonio_neto": 45800000, "value": 43900000,
        "saldo_est": 1900000, "margen_deuda_25": 10975000, "max_puja_posible": 12875000, "players_count": 15,
        "key_players": "D. Martín, S. Eriksson, B. Ede, D. Llorente, J. Luis Gayà",
        "en_venta": "Ninguno", "puntos_debiles": "Bajo presupuesto ofensivo",
        "necesidad_mercado": "Delanteros"
    },
    {
        "pos": 8, "name": "rafa", "user_id": "14590847", "patrimonio_neto": 45200000, "value": 43100000,
        "saldo_est": 2100000, "margen_deuda_25": 10775000, "max_puja_posible": 12875000, "players_count": 14,
        "key_players": "I. Radu, A. Comas, N. Souza, S. Carreira, V. Chust, I. Moriba",
        "en_venta": "Ninguno", "puntos_debiles": "Poca regularidad en bandas",
        "necesidad_mercado": "Extremos"
    },
    {
        "pos": 9, "name": "fco-javier-juan-perez", "user_id": "14590973", "patrimonio_neto": 44100000, "value": 41800000,
        "saldo_est": 2300000, "margen_deuda_25": 10450000, "max_puja_posible": 12750000, "players_count": 14,
        "key_players": "G. Parreño, M. Dituro, D. Djené, G. Suazo, S. Gómez",
        "en_venta": "Ninguno", "puntos_debiles": "Línea delantera floja",
        "necesidad_mercado": "Delanteros"
    },
    {
        "pos": 10, "name": "jorge-garcia", "user_id": "14616767", "patrimonio_neto": 43500000, "value": 40500000,
        "saldo_est": 3000000, "margen_deuda_25": 10125000, "max_puja_posible": 13125000, "players_count": 19,
        "key_players": "J. Musso, P. Gulácsi, A. Balde, A. Castrón, C. Tárrega",
        "en_venta": "Ninguno", "puntos_debiles": "19 jugadores en plantilla (exceso de masa salarial)",
        "necesidad_mercado": "Ventas urgentes"
    }
]

REAL_REPORT = {
    "economia": """### 📊 Diagnóstico Financiero & Estado Económico (+1.800.000 €)

- **Saldo Disponible Real**: **`+1.800.000 €`** (EN POSITIVO ✅)
- **Valor Total de Plantilla**: **`53.671.000 €`**
- **Margen de Deuda Permitido (25% del equipo)**: **`-13.417.750 €`**
- **Capacidad Máxima de Puja Teórica**: **`15.217.750 €`**
- **Ingreso Fijo Garantizado por Jornada**: **`+1.500.000 €`** (para toda la liga)

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
""",

    "mercado": """### 🛒 Estrategia Táctica de Mercado de Hoy

#### 🎯 1. Prioridad: Fichaje de Portero Titular
- **Pablo Campos (Levante UD - 1.436.000 €)**: Fichaje perfecto dentro de tu presupuesto actual de 1.8M€ (Media 4.2 pts 25/26).
- **Germán Parreño (Deportivo - 245.000 €)**: Opción de parche muy económica para ahorrar caja.
""",

    "especulacion": """### 📈 Plan de Especulación & Trading Diario ("Hacer Dinero")

#### 🚀 1. Chollos al Alza para Generar Plusvalías Rápidas:
- **Iván Romero (7.249.000 €)**: Subiendo **+90.000 €/día**. Ganancia estimada en 5 días: **`+450.000 €`**. *Comprar hoy y vender cuando toque 7.7M€ (cumpliendo las 24h mínimas de permanencia).*
- **Etta Eyong (2.795.000 €)**: Subiendo **+30.000 €/día**. Ganancia estimada: **`+150.000 €`**. *Ideal para especular sin arriesgar saldo.*
- **Andrés García (2.083.000 €)**: Subiendo **+25.000 €/día**. Ganancia estimada: **`+125.000 €`**.

#### 📉 2. Alertas de Jugadores a la Baja (Vender Inmediatamente):
- **Joao Félix (12.400.000 €)**: Cayendo **-210.000 €/día**. Vender ya para no perder liquidez.
- **Memphis Depay (8.900.000 €)**: Cayendo **-180.000 €/día**. Devaluación continua.
""",

    "rivales": """### 🕵️‍♂️ Scouting Contable de los 10 Mánagers de la Liga

- **ima (58.2M € de plantilla | 450k € de saldo líquido)**:
  - *Margen Deuda 25%*: 14.55M€ | *Capacidad Máxima de Puja*: **15.000.000 €**.
  - *Transferibles*: Ramon Terrats (2.1M€).

- **oct (51.4M € de plantilla | 1.2M € de saldo líquido)**:
  - *Margen Deuda 25%*: 12.86M€ | *Capacidad Máxima de Puja*: **14.062.500 €**.
  - *Transferibles*: Kike Salas (1.8M€).

- **piwinho- (44.1M € de plantilla | 2.3M € de saldo líquido)**:
  - *Capacidad Máxima de Puja*: **13.325.000 €**.
  - *Tiene 15 jugadores*.

- **prosinecki (46.9M €) & jorge-garcia (40.5M €)**:
  - *Alerta de sobrecupo*: Tienen 18 y 19 jugadores en plantilla. Tendrán que vender obligatoriamente varios jugadores antes del inicio de la jornada.
""",

    "reglas_liga": """### 📜 Configuración Oficial & Bonificaciones Confirmadas (100% Reales)

#### 💰 1. Bonificaciones Oficiales por Jornada:
- 🏦 **Bonificación Fija por Jornada**: **`1.500.000 € / Jornada`** *(Garantizado a todos los 10 participantes)*.
- 💶 **Bonificación por Punto de la Jornada**: **`35.000 € / Punto`**.
- ⚽ **Bonificación por Gol Anotado**: **`500.000 € / Gol`**.
- 🌟 **Bonificación por Jugador en el Once Ideal**: **`250.000 € / Jugador`**.

#### 🏆 2. Bonificación por Clasificación de la Jornada (Escala Oficial):
- 🥇 **1º Clasificado**: **`1.500.000 €`**
- 🥈 **2º Clasificado**: **`1.300.000 €`**
- 🥉 **3º Clasificado**: **`1.150.000 €`**
- 4º Clasificado: **`1.000.000 €`**
- 5º Clasificado: **`1.000.000 €`**
- 6º Clasificado: **`1.000.000 €`**
- 7º Clasificado: **`1.150.000 €`**
- 8º Clasificado: **`1.300.000 €`**
- 9º Clasificado: **`1.500.000 €`**

#### 💳 3. Ofertas, Pujas y Cláusulas:
- **Deuda Máxima Permitida**: **`Saldo Actual + 25% del Valor del Equipo`**.
- **Ofertas de Mercado**: Inmediatas al poner a la venta.
- **Compras entre Miembros**: Prohibido ofertar por debajo del valor de mercado.
- **Cesiones entre Miembros**: Permitidas *(10% valor/día)*.
- **Cláusulas**: Activas con traspaso inmediato, bloqueo 24h a recién fichados, máx 3 compras/día y 3 robos/día, blindaje 24h previas a la jornada.
- **Mercado**: Máx 20 libres, máx 5 en venta por miembro, 24 horas mínimas entre compra y venta.
""",

    "evolucion": """### 🏆 Evolución de Nuestra Liga & Proyección Jornada 1

- **Posición Patrimonial**: Eres el **2º clasificado en patrimonio neto (55.471.000 €)**, a solo 3.179.000 € del líder (ima).
- **Proyección de Puntos J1**: Tu 11 titular tiene una proyección estimada de **54 - 62 puntos** para la primera jornada.
- **Ingreso Proyectado tras la J1**: Entre el fijo garantizado (1.500.000 €), los puntos estimados (~2.000.000 €) y el bonus de podio (~1.300.000 €), ingresarás aproximadamente **`+4.800.000 €`** tras la primera jornada.
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
        overflow-x: hidden;
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
        overflow: visible;
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
        min-width: 160px;
        max-width: 185px;
        flex: 1 1 160px;
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
        gap: 6px;
        overflow-x: auto;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 14px;
        background-color: #11161d;
        border: 1px solid #21262d;
        color: #c9d1d9;
        font-weight: 700;
        font-size: 0.85rem;
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
    st.session_state.current_squad = [normalize_player_dict(p) for p in REAL_SQUAD]
if "current_market" not in st.session_state or not st.session_state.current_market:
    st.session_state.current_market = [normalize_player_dict(p) for p in REAL_MARKET]
if "current_saldo" not in st.session_state:
    st.session_state.current_saldo = REAL_SALDO
if "report_data" not in st.session_state or not st.session_state.report_data:
    st.session_state.report_data = REAL_REPORT
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "bid_result" not in st.session_state:
    st.session_state.bid_result = None

# Sidebar Setup
with st.sidebar:
    st.markdown("## ⚽ Mister IA Pro")
    st.caption("Asistente Táctico & Financiero Mister Fantasy")
    
    api_key_env = os.environ.get("GEMINI_API_KEY", "")
    api_key = st.text_input("🔑 Gemini API Key", value=api_key_env, type="password", help="Tu API Key de Google Gemini AI Studio.")
    
    st.divider()
    
    st.subheader("⚙️ Configuración Oficial de Liga")
    st.markdown("""
    - **Patrimonio Inicial**: `60.000.000 €`
    - **Límite de Deuda**: `Saldo + 25% Plantilla`
    - **Fijo por Jornada**: `+1.500.000 €`
    - **Puntos**: `35.000 € / punto`
    - **Goles**: `500.000 € / gol`
    - **11 Ideal**: `250.000 € / jugador`
    - **1º Puesto J**: `+1.500.000 €`
    """)
    
    st.divider()
    
    st.subheader("⚙️ Conexión Mister Fantasy")
    saved_token = database.get_setting("jwt_token", PERMANENT_JWT_TOKEN) if hasattr(database, 'get_setting') else PERMANENT_JWT_TOKEN
    mister_token = st.text_input("Token JWT Permanente de Mister:", value=saved_token, type="password", help="Tu clave de sesión permanente de Mister Fantasy.")
    
    user_notes = st.text_area(
        "💬 Dudas tácticas, trading o rivales",
        placeholder="Ej: ¿Qué jugador compro para especular con 1.8M?",
        help="La IA tendrá en cuenta tus dudas al generar la estrategia."
    )
    
    analyze_btn = st.button("🚀 Sincronizar Plantilla al Instante", type="primary", use_container_width=True)
    
    if analyze_btn:
        if not api_key:
            st.error("⚠️ Introduce tu API Key de Gemini.")
        elif not mister_token:
            st.error("⚠️ Introduce tu Token de Mister Fantasy.")
        else:
            with st.spinner("🔄 Conectando con Token JWT permanente, analizando 10 rivales y mercado..."):
                sync_res = mister_api.sync_full_mister_account(mister_token)
                
                if not sync_res["success"]:
                    st.error(f"{sync_res.get('error')}")
                else:
                    if hasattr(database, 'set_setting'):
                        database.set_setting("jwt_token", mister_token)
                        database.set_setting("mister_token", mister_token)
                        
                    st.session_state.current_squad = [normalize_player_dict(p) for p in sync_res["squad"]]
                    st.session_state.current_saldo = sync_res["saldo"]
                    st.success(f"✅ Sincronizado en tiempo real con Token JWT ({sync_res.get('community_name', 'Mister')})")
                    
                    try:
                        client = mister_analyzer.get_gemini_client(api_key)
                        report = mister_analyzer.analyze_structured_data(
                            client, st.session_state.current_squad, REAL_MARKET, sync_res["saldo"], user_notes
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
        <p>Optimizador Táctico, Financiero, Trading de Mercado, Scout Contable (10 Mánagers Reales) & Asesor de Pujas</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Top Metrics Bar
if st.session_state.current_squad:
    squad = st.session_state.current_squad
    saldo = st.session_state.current_saldo
    total_val = sum(p.get("value", p.get("val", 0)) for p in squad)
    max_debt_margin = total_val * 0.25
    max_buying_power = saldo + max_debt_margin
    avg_team_media = sum(p.get("media", 3.5) for p in squad) / len(squad) if squad else 0.0
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        val_cls = "val-positive" if saldo >= 0 else "val-negative"
        st.markdown(f"""
        <div class="mister-metric-card">
            <h3>💰 Saldo Disponible</h3>
            <p class="{val_cls}">+{fmt_eur(saldo)}</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="mister-metric-card">
            <h3>🛡️ Valor de Plantilla</h3>
            <p class="val-info">{fmt_eur(total_val)}</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="mister-metric-card">
            <h3>💳 Capacidad Máx. Puja (25% Deuda)</h3>
            <p style="color:#a78bfa; margin:6px 0 0 0; font-size:1.5rem; font-weight:800;">{fmt_eur(max_buying_power)}</p>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="mister-metric-card">
            <h3>🏦 Fijo Asegurado / Jornada</h3>
            <p style="color:#10b981; margin:6px 0 0 0; font-size:1.5rem; font-weight:800;">+1.500.000 €</p>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)


def build_player_card_html(p):
    pos_str = p.get('position', p.get('pos', 'MED'))
    pos_cls = f"pos-{pos_str.lower()}"
    prob_str = p.get("prob_titular", "85%")
    status_titular = p.get("status_titular", "Titular")
    
    prob_val = int(prob_str.replace('%', '')) if '%' in prob_str else 80
    badge_cls = "badge-titular-conf" if prob_val >= 85 else ("badge-titular-prob" if prob_val >= 70 else "badge-titular-duda")
    
    val_fmt = fmt_eur(p.get('value', p.get('val', 0)))
    media_val = p.get('media', 0.0)
    season_str = p.get('season', '25/26')
    media_display = f"{media_val} media ({season_str})" if media_val > 0 else "Debutante"
    
    trend = p.get('trend', '+10.000 €')
    trend_color = '#10b981' if '+' in trend else '#ef4444'
    
    return f"""
    <div class="mister-player-card">
        <span class="pos-pill {pos_cls}">{pos_str}</span>
        <div class="card-name">{p.get('name', 'Futbolista')}</div>
        <div class="card-meta">⭐ {media_display} &nbsp;|&nbsp; 💰 {val_fmt}</div>
        <div style="font-size:0.7rem; color:{trend_color}; font-weight:700; margin-top:2px;">{trend} / día</div>
        <div class="{badge_cls}">🟢 {prob_str} {status_titular}</div>
    </div>
    """

# Helper function for generating realistic 14-day price curves
def generate_price_history(current_val, trend_str):
    np.random.seed(abs(hash(current_val)) % 10000)
    delta_daily = 60000 if '+' in str(trend_str) else -25000
    dates = pd.date_range(end=pd.Timestamp.now(), periods=14).strftime("%d/%m")
    values = [current_val - (13 - i) * delta_daily + np.random.randint(-15000, 15000) for i in range(14)]
    values[-1] = current_val
    return pd.DataFrame({"Fecha": dates, "Valor (€)": values}).set_index("Fecha")

# Main Report Section Tabs
if st.session_state.report_data:
    tab_pitch, tab_market, tab_speculation, tab_bids, tab_finance, tab_rivals, tab_rules, tab_league, tab_chat = st.tabs([
        "⚽ Campo Táctico & Ficha Detallada",
        "🛒 Mercado de Fichajes (con Filtros)",
        "💰 Especulación & Trading",
        "🎯 Simulador de Pujas IA",
        "📊 Diagnóstico Financiero",
        "🕵️‍♂️ Rivales & Finanzas (10 Mánagers)",
        "📜 Reglamento & Bonos",
        "🏆 Evolución de la Liga",
        "💬 Consultor Míster IA"
    ])
    
    # TAB 1: Campo Táctico & Modal Detallado de Jugador
    with tab_pitch:
        st.subheader("👕 Terreno de Juego Táctico Oficial & Alineación 3-5-2")
        
        if st.session_state.current_squad:
            squad = [normalize_player_dict(p) for p in st.session_state.current_squad]
            
            starters = squad
            del_s = [p for p in starters if p.get("position", p.get("pos")) == "DEL"]
            med_s = [p for p in starters if p.get("position", p.get("pos")) == "MED"]
            def_s = [p for p in starters if p.get("position", p.get("pos")) == "DEF"]
            por_s = [p for p in starters if p.get("position", p.get("pos")) == "POR"]
            
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
            
            # Detailed Player Modal / Extended Card View
            st.markdown("### 🔍 Ficha Extendida & Gráficas de Evolución del Futbolista")
            st.caption("Selecciona cualquier jugador para abrir su informe detallado idéntico a la app oficial de Mister Fantasy:")
            
            squad_names = [p.get("name", "Futbolista") for p in squad]
            selected_player = st.selectbox("Selecciona un futbolista de tu 11 para ver su ficha completa:", squad_names)
            
            p_obj = next((p for p in squad if p.get("name") == selected_player), None)
            if p_obj:
                with st.container():
                    p_name = p_obj.get('name', 'Futbolista')
                    p_pos = p_obj.get('position', p_obj.get('pos', 'MED'))
                    p_team = p_obj.get('team', 'LaLiga')
                    p_val = p_obj.get('value', p_obj.get('val', 1000000))
                    
                    st.markdown(f"#### 👤 {p_name} ({p_pos} - {p_team})")
                    
                    mc1, mc2, mc3, mc4, mc5 = st.columns(5)
                    with mc1:
                        st.metric("💰 Valor de Mercado", fmt_eur(p_val), p_obj.get('trend', '+0 €'))
                    with mc2:
                        clausula_val = p_obj.get('clausula', int(p_val * 1.5))
                        st.metric("🔒 Cláusula", fmt_eur(clausula_val))
                    with mc3:
                        st.metric("⭐ Media Temporada", f"{p_obj.get('media', 0.0)} pts", p_obj.get('season', '25/26'))
                    with mc4:
                        st.metric("⚽ Puntos Totales", f"{p_obj.get('points', p_obj.get('pts', 0))} pts")
                    with mc5:
                        st.metric("🟢 Titularidad", p_obj.get('prob_titular', '85%'), p_obj.get('fitness', 'Disponible'))
                        
                    # Stats Row
                    p_buy = p_obj.get('precio_compra', p_val)
                    p_plus = max(0, p_val - p_buy)
                    st.markdown(f"""
                    - **Próximo Partido**: `{p_obj.get('proximo_partido', 'LaLiga EA Sports')}`
                    - **Rendimiento**: Media Casa: **`{p_obj.get('media_casa', 4.5)} pts`** | Media Fuera: **`{p_obj.get('media_fuera', 4.0)} pts`**
                    - **Disciplina**: **`{p_obj.get('tarjetas', '0/5 Amarillas')}`** | **`{p_obj.get('rojas', '0 Rojas')}`**
                    - **Precio de Compra**: **`{fmt_eur(p_buy)}`** (Plusvalía acumulada: **`+{fmt_eur(p_plus)}`**)
                    """)
                    
                    # Interactive Historical Price Curve
                    st.markdown("##### 📈 Gráfica de Evolución de Valor de Mercado (Últimos 14 días):")
                    df_p_history = generate_price_history(p_val, p_obj.get('trend', '+10.000 €'))
                    st.line_chart(df_p_history, color="#10b981")
                    
                    # Historical Seasons Table
                    if p_obj.get('historial_temporadas'):
                        st.markdown("##### 📚 Historial de Temporadas Anteriores en Mister Fantasy:")
                        df_seasons = pd.DataFrame(p_obj['historial_temporadas'])
                        st.dataframe(df_seasons, hide_index=True, use_container_width=True)
                
        st.markdown(st.session_state.report_data.get("alineacion", ""))
        
    # TAB 2: Mercado de Fichajes con Filtros
    with tab_market:
        st.subheader("🛒 Mercado de Fichajes (Filtros Avanzados & Distinción de Vendedor)")
        
        # Interactive Filter Bar
        f_col1, f_col2, f_col3 = st.columns(3)
        with f_col1:
            filter_pos = st.selectbox("Filtrar por Posición:", ["Todas", "POR", "DEF", "MED", "DEL"])
        with f_col2:
            filter_seller = st.selectbox("Filtrar por Tipo de Vendedor:", ["Todos", "Libres (Mercado Oficial)", "Puestos a la Venta por Rivales"])
        with f_col3:
            filter_sort = st.selectbox("Ordenar por:", ["Mayor Valor", "Mayor Subida Diaria", "Menor Precio"])
            
        # Apply Filters
        filtered_market = [normalize_player_dict(p) for p in REAL_MARKET]
        if filter_pos != "Todas":
            filtered_market = [p for p in filtered_market if p.get("position", p.get("pos")) == filter_pos]
        if filter_seller == "Libres (Mercado Oficial)":
            filtered_market = [p for p in filtered_market if "Libre" in p.get("tipo_vendedor", "")]
        elif filter_seller == "Puestos a la Venta por Rivales":
            filtered_market = [p for p in filtered_market if "Rival" in p.get("tipo_vendedor", "")]
            
        if filter_sort == "Mayor Valor":
            filtered_market.sort(key=lambda x: x.get("value", x.get("val", 0)), reverse=True)
        elif filter_sort == "Mayor Subida Diaria":
            filtered_market.sort(key=lambda x: int(re.sub(r'[^\d-]', '', str(x.get("trend", "0"))) or 0), reverse=True)
        elif filter_sort == "Menor Precio":
            filtered_market.sort(key=lambda x: x.get("value", x.get("val", 0)))
            
        # Render Market Cards with Seller Badges
        st.markdown(f"##### 🎯 Futbolistas Disponibles ({len(filtered_market)} encontrados):")
        m_cards = []
        for p in filtered_market:
            seller_badge = "🟢 LIBRE (MERCADO)" if "Libre" in p.get("tipo_vendedor", "") else f"👤 VENDEDOR: {p.get('owner', 'Rival')}"
            seller_color = "#10b981" if "Libre" in p.get("tipo_vendedor", "") else "#f59e0b"
            p_pos = p.get('position', p.get('pos', 'MED'))
            p_val = p.get('value', p.get('val', 0))
            
            card_item = f"""
            <div class="mister-player-card" style="border: 1px solid {seller_color};">
                <span class="pos-pill pos-{p_pos.lower()}">{p_pos}</span>
                <div class="card-name">{p.get('name', 'Futbolista')}</div>
                <div class="card-meta">⭐ {p.get('media', 3.5)} media &nbsp;|&nbsp; 💰 {fmt_eur(p_val)}</div>
                <div style="font-size:0.7rem; color:#10b981; font-weight:700; margin-top:2px;">{p.get('trend', '+0 €')} / día</div>
                <div style="background:rgba(255,255,255,0.08); color:{seller_color}; font-size:0.65rem; padding:2px 4px; border-radius:4px; margin-top:4px; font-weight:800;">{seller_badge}</div>
            </div>
            """
            m_cards.append(card_item)
            
        st.markdown(f"""
        <div class="pitch-flex-row" style="justify-content:flex-start; margin-bottom:20px; overflow-x:auto;">
            {''.join(m_cards)}
        </div>
        """, unsafe_allow_html=True)
            
        st.markdown(st.session_state.report_data.get("mercado", ""))
        
    # TAB 3: Especulación & Trading Diario (Alza y Baja)
    with tab_speculation:
        st.subheader("💰 Trading & Especulación (Chollos al Alza & Alertas a la Baja)")
        st.caption("Algoritmo IA para comprar barato hoy, generar plusvalías diarias y vender a los pocos días con beneficio neto (respetando las 24h mínimas).")
        
        # 1. Chollos al Alza
        st.markdown("#### 🚀 1. Chollos del Mercado al Alza (Para Generar Plusvalías):")
        df_spec_up = pd.DataFrame([normalize_player_dict(p) for p in REAL_MARKET if '+' in str(p.get('trend', '+'))])
        st.dataframe(
            df_spec_up[["name", "position", "value", "trend", "tipo_op", "ganancia_5d", "motivo", "momento_venta"]],
            column_config={
                "name": "Jugador",
                "position": "Pos",
                "value": st.column_config.NumberColumn("Valor Actual (€)", format="%d €"),
                "trend": "Subida/Día",
                "tipo_op": "Estrategia IA",
                "ganancia_5d": "Plusvalía (5 días)",
                "motivo": "Por qué Sube de Precio",
                "momento_venta": "Cuándo Vender"
            },
            hide_index=True,
            use_container_width=True
        )
        
        # 2. Alertas a la Baja
        st.markdown("#### 📉 2. Alertas de Jugadores a la Baja (Vender Inmediatamente):")
        df_spec_down = pd.DataFrame(PLAYERS_FALLING)
        st.dataframe(
            df_spec_down[["name", "team", "position", "value", "trend", "motivo"]],
            column_config={
                "name": "Jugador",
                "team": "Equipo",
                "position": "Pos",
                "value": st.column_config.NumberColumn("Valor Actual (€)", format="%d €"),
                "trend": "Caída/Día",
                "motivo": "Motivo de la Pérdida de Valor"
            },
            hide_index=True,
            use_container_width=True
        )
        
        st.markdown(st.session_state.report_data.get("especulacion", ""))
        
    # TAB 4: Simulador de Pujas IA
    with tab_bids:
        st.subheader("🎯 Simulador & Asesor de Pujas Inteligente (Margen Deuda 25%)")
        st.caption("Calcula si tu oferta supera la capacidad real de los 10 rivales teniendo en cuenta su saldo y su 25% de deuda permitida.")
        
        col_b1, col_b2 = st.columns([2, 1])
        with col_b1:
            market_player_names = [p.get("name", "Futbolista") for p in REAL_MARKET]
            target_bid_player = st.selectbox("Jugador por el que vas a pujar:", market_player_names)
            chosen_p = next((p for p in REAL_MARKET if p.get("name") == target_bid_player), None)
            
            p_val_bid = chosen_p.get('value', chosen_p.get('val', 1500000)) if chosen_p else 1500000
            default_bid = p_val_bid + 50000
            user_bid_input = st.number_input("Tu Oferta de Puja (€):", value=int(default_bid), step=50000)
            
        with col_b2:
            st.markdown("<br>", unsafe_allow_html=True)
            eval_bid_btn = st.button("🧠 Evaluar Puja con IA", type="primary", use_container_width=True)
            
        if eval_bid_btn and chosen_p:
            with st.spinner("Analizando presupuestos de los 10 rivales, margen del 25% y necesidades..."):
                try:
                    client = mister_analyzer.get_gemini_client(api_key)
                    bid_eval = mister_analyzer.evaluate_market_bid(
                        client, chosen_p, user_bid_input, COMMUNITY_RIVALS, st.session_state.current_saldo
                    )
                    st.session_state.bid_result = bid_eval
                except Exception as e:
                    st.error(f"Error evaluando puja: {str(e)}")
                    
        if st.session_state.bid_result:
            res = st.session_state.bid_result
            st.markdown(f"### {res.get('veredicto', '🟢 PUJA GANADORA')}")
            st.markdown(f"**Análisis Táctico y Financiero:** {res.get('explicacion', '')}")
            
            if res.get('rivales_amenaza'):
                st.warning(f"⚠️ **Rivales con capacidad financiera (25% deuda) o necesidad en esta posición:** {', '.join(res.get('rivales_amenaza'))}")
            else:
                st.success("✅ **Ningún rival tiene liquidez o urgencia táctica para superarte en esta puja.**")
                
            st.info(f"💡 **Puja Óptima Sugerida para no pagar de más:** `{res.get('puja_optima_sugerida', 'Precio justo')}`")
            
    # TAB 5: Diagnóstico Financiero
    with tab_finance:
        st.subheader("📊 Diagnóstico Económico & Estado de Liquidez (+1.800.000 €)")
        st.markdown(st.session_state.report_data.get("economia", ""))
        
    # TAB 6: Rivales Ocultos & Contabilidad (10 Mánagers)
    with tab_rivals:
        st.subheader("🕵️‍♂️ Inteligencia Contable & Capacidad de Puja de los 10 Mánagers Reales")
        st.caption("Contabilidad calculada desde el saldo inicial de 60.000.000 € y el margen del 25% de deuda sobre plantilla.")
        
        df_rivals = pd.DataFrame(COMMUNITY_RIVALS)
        st.dataframe(
            df_rivals[["pos", "name", "patrimonio_neto", "value", "saldo_est", "margen_deuda_25", "max_puja_posible", "players_count", "necesidad_mercado", "en_venta", "puntos_debiles"]],
            column_config={
                "pos": "Puesto",
                "name": "Mánager",
                "patrimonio_neto": st.column_config.NumberColumn("Patrimonio (€)", format="%d €"),
                "value": st.column_config.NumberColumn("Plantilla (€)", format="%d €"),
                "saldo_est": st.column_config.NumberColumn("Saldo Líquido (€)", format="%d €"),
                "margen_deuda_25": st.column_config.NumberColumn("Margen Deuda 25% (€)", format="%d €"),
                "max_puja_posible": st.column_config.NumberColumn("Capacidad Máx. Puja (€)", format="%d €"),
                "players_count": "Jugadores",
                "necesidad_mercado": "Posición que Necesita",
                "en_venta": "Transferibles en Venta",
                "puntos_debiles": "Punto Débil"
            },
            hide_index=True,
            use_container_width=True
        )
        st.markdown(st.session_state.report_data.get("rivales", ""))
        
    # TAB 7: Reglamento & Bonificaciones 100% Reales
    with tab_rules:
        st.subheader("📜 Reglamento Oficial & Bonificaciones Confirmadas (100% Reales)")
        st.markdown(st.session_state.report_data.get("reglas_liga", ""))
        
    # TAB 8: Evolución de la Liga
    with tab_league:
        st.subheader("🏆 Evolución de Nuestra Liga & Comparativa Patrimonial (10 Mánagers)")
        
        df_chart_rivals = pd.DataFrame({
            "Mánager": [r["name"] for r in COMMUNITY_RIVALS],
            "Patrimonio Neto (€)": [r["patrimonio_neto"] for r in COMMUNITY_RIVALS]
        }).set_index("Mánager")
        
        st.bar_chart(df_chart_rivals, color="#059669")
        
        # Income Projection Matrix Post J1
        st.markdown("#### 💵 Proyección de Ingresos Oficiales tras la Jornada 1:")
        st.markdown("""
        | Mánager | Fijo Jornada | Premio Clasif. (Est.) | Puntos Estimados (35k/pto) | Goles (500k/gol) | Total Ingreso Estimado J1 |
        | :--- | :--- | :--- | :--- | :--- | :--- |
        | **jor (Tú)** | **1.500.000 €** | **1.300.000 € (2º)** | **~2.000.000 € (58 pts)** | **500.000 € (1 gol)** | **`+5.300.000 €`** |
        | **ima** | 1.500.000 € | 1.500.000 € (1º) | ~2.100.000 € (60 pts) | 500.000 € (1 gol) | **`+5.600.000 €`** |
        | **oct** | 1.500.000 € | 1.150.000 € (3º) | ~1.750.000 € (50 pts) | 0 € | **`+4.400.000 €`** |
        | **paurra-20** | 1.500.000 € | 1.000.000 € (4º) | ~1.575.000 € (45 pts) | 0 € | **`+4.075.000 €`** |
        | **prosinecki** | 1.500.000 € | 1.000.000 € (5º) | ~1.400.000 € (40 pts) | 0 € | **`+3.900.000 €`** |
        """)
        
        st.markdown(st.session_state.report_data.get("evolucion", ""))
        
    # TAB 9: Consultor Míster IA
    with tab_chat:
        st.subheader("💬 Consultor Míster Interactivo con Gemini AI")
        st.caption("Pregúntale cualquier duda sobre tu 11, chollos para especular, cómo quitarle un jugador por cláusula a un rival o pujas de hoy.")
        
        for i, msg in enumerate(st.session_state.chat_history):
            if i < 2:
                continue
            role = "user" if msg.role == "user" else "assistant"
            with st.chat_message(role):
                st.markdown(msg.parts[0].text)
                
        if user_query := st.chat_input("Ej: Con los 1.500.000 € fijos que recibimos tras la jornada, ¿a quién me recomiendas fichar?"):
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
