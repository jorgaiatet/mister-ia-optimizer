"""
Demo data module for Mister IA Optimizer Pro.
Provides realistic sample squad, market, and analysis reports for LaLiga Mister Fantasy.
"""

DEMO_SQUAD = [
    {"name": "Unai Simón", "position": "POR", "team": "Athletic Club", "value": 6850000, "trend": "+120.000€", "points": 84, "status": "Titular", "fitness": "OK"},
    {"name": "Robin Le Normand", "position": "DEF", "team": "Atlético de Madrid", "value": 5400000, "trend": "+50.000€", "points": 72, "status": "Titular", "fitness": "OK"},
    {"name": "Jules Koundé", "position": "DEF", "team": "FC Barcelona", "value": 8100000, "trend": "+90.000€", "points": 95, "status": "Titular", "fitness": "OK"},
    {"name": "Antonio Rüdiger", "position": "DEF", "team": "Real Madrid", "value": 7900000, "trend": "-30.000€", "points": 88, "status": "Titular", "fitness": "Duda (Afectación articular)"},
    {"name": "Dani Vivian", "position": "DEF", "team": "Athletic Club", "value": 4600000, "trend": "+70.000€", "points": 65, "status": "Titular", "fitness": "OK"},
    {"name": "Jude Bellingham", "position": "MED", "team": "Real Madrid", "value": 18200000, "trend": "+250.000€", "points": 145, "status": "Titular", "fitness": "OK"},
    {"name": "Pedri", "position": "MED", "team": "FC Barcelona", "value": 14500000, "trend": "+180.000€", "points": 128, "status": "Titular", "fitness": "OK"},
    {"name": "Álex Baena", "position": "MED", "team": "Villarreal CF", "value": 11200000, "trend": "-110.000€", "points": 110, "status": "Titular", "fitness": "OK"},
    {"name": "Kirian Rodríguez", "position": "MED", "team": "UD Las Palmas", "value": 6300000, "trend": "-90.000€", "points": 78, "status": "Rotación", "fitness": "Baja rendimiento"},
    {"name": "Lamine Yamal", "position": "DEL", "team": "FC Barcelona", "value": 19800000, "trend": "+320.000€", "points": 162, "status": "Titular estrella", "fitness": "OK"},
    {"name": "Antoine Griezmann", "position": "DEL", "team": "Atlético de Madrid", "value": 15400000, "trend": "+40.000€", "points": 134, "status": "Titular", "fitness": "OK"},
    {"name": "Ayoze Pérez", "position": "DEL", "team": "Villarreal CF", "value": 8900000, "trend": "+150.000€", "points": 98, "status": "Titular", "fitness": "OK"},
    {"name": "Cristhian Stuani", "position": "DEL", "team": "Girona FC", "value": 3100000, "trend": "-20.000€", "points": 45, "status": "Suplente habitual", "fitness": "OK"}
]

DEMO_MARKET = [
    {"name": "Robert Lewandowski", "position": "DEL", "team": "FC Barcelona", "value": 17800000, "trend": "+210.000€", "points": 150, "owner": "Mercado"},
    {"name": "Oihan Sancet", "position": "MED", "team": "Athletic Club", "value": 7400000, "trend": "+140.000€", "points": 89, "owner": "Mercado"},
    {"name": "Bryan Zaragoza", "position": "DEL", "team": "CA Osasuna", "value": 5800000, "trend": "+190.000€", "points": 82, "owner": "Mercado"},
    {"name": "Marc Casadó", "position": "MED", "team": "FC Barcelona", "value": 3400000, "trend": "+280.000€", "points": 58, "owner": "Mercado (Chollo al alza)"},
    {"name": "Raúl Asencio", "position": "DEF", "team": "Real Madrid", "value": 1900000, "trend": "+310.000€", "points": 42, "owner": "Mercado (Especulación máxima)"},
    {"name": "Joan García", "position": "POR", "team": "RCD Espanyol", "value": 4100000, "trend": "+80.000€", "points": 74, "owner": "Mercado"}
]

DEMO_SALDO = 4850000

DEMO_REPORT = {
    "economia": """### 💰 Balance Financiero y Estado del Saldo

- **Saldo Disponible**: **4.850.000 €**
- **Valor Total de la Plantilla**: **140.750.000 €** (Tendencia semanal: **+1.120.000 €**)

#### 📈 Jugadores en Fuerte Subida (Mantener o Especular)
- **Lamine Yamal**: +320.000€/día. *Inmune a venta.*
- **Jude Bellingham**: +250.000€/día. *Mantener como pilar central.*
- **Pedri**: +180.000€/día. *En pico de valor y rendimiento.*

#### 📉 Jugadores en Caída / Venta Recomendada
- **Kirian Rodríguez (UD Las Palmas)**: **-90.000€/día** (Valor actual: 6.300.000 €). Ha perdido peso táctico y su valor caerá más. **Recomendación: VENDER YA** para liberar 6.3M€ y juntar un saldo total de **11.15M€**.
- **Álex Baena (Villarreal CF)**: **-110.000€/día**. Aunque da puntos, su valor está ajustando tras la racha. *Mantener solo si no hay sustituto de nivel en mercado.*
- **Cristhian Stuani (Girona FC)**: **-20.000€/día**. Solo juega minutos finales. Vender para sumar 3.1M€ extras a la caja.
""",

    "alineacion": """### 👕 Alineación Ideal Recomendada (Formación 4-3-3)

```
                       Unai Simón (POR)
                                
  Koundé (DEF)   Le Normand (DEF)   Vivian (DEF)   Rüdiger (DEF)
                                
         Bellingham (MED)   Pedri (MED)   Baena (MED)
                                
      Lamine Yamal (DEL)   Griezmann (DEL)   Ayoze (DEL)
```

#### 🛡️ Análisis de Rotaciones y Riesgos de Titularidad

1. **Antonio Rüdiger (DEF - Real Madrid)**: ⚠️ **Riesgo Medio-Alto (60% Titular)**. Arrastra molestias por carga de minutos. *Plan B*: Si no llega a la previa del viernes, pasar a esquema 3-4-3 dando entrada a Kirian o fichando un parche defensivo.
2. **Pedri & Bellingham (MED)**: 🟢 **100% Titulares**. Indiscutibles en sus esquemas.
3. **Ayoze Pérez (DEL - Villarreal)**: 🟢 **90% Titular**. En racha goleadora.
4. **Cristhian Stuani (DEL)**: 🔴 **Suplente (20% Titular)**. Descartar del 11 titular.
""",

    "mercado": """### 🛒 Estrategia Táctica de Mercado

#### 🎯 1. Fichajes de Rendimiento Directo (Puntos Seguros)
- **Oihan Sancet (Athletic Club - 7.400.000 €)**
  - *Razonamiento*: Medio con llegada y gol. Su precio sube +140k/día. Si vendes a Kirian (6.3M) y sumas tu saldo (4.85M), puedes pujar **7.8M€** para asegurar su fichaje sin arriesgar tu economía.

#### 🚀 2. Fichajes Especulativos / Chollos al Alza (Ganancia Rápida)
- **Marc Casadó (FC Barcelona - 3.400.000 €)**
  - *Tendencia*: **+280.000 €/día**.
  - *Estrategia*: Puja precio de coste + 150.000 € (**3.550.000 €**). En 4-5 días habrá ganado +1.2M€ en mercado. Podrás re-venderlo con beneficio neto o mantenerlo como titular chollo.
- **Raúl Asencio (Real Madrid - 1.900.000 €)**
  - *Tendencia*: **+310.000 €/día** (Especulación máxima por bajas en defensa).
  - *Estrategia*: Puja **2.050.000 €**. Riesgo nulo y rentabilidad asegurada de más del 50% de su valor en una semana.
"""
}
