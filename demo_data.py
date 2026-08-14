"""
Real live data module for Mister IA Optimizer Pro.
Synchronized with real Mister Fantasy account data & live market prices.
"""

DEMO_SQUAD = [
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

DEMO_MARKET = [
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

DEMO_SALDO = -8021680

DEMO_REPORT = {
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
