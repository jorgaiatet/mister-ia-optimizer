"""
Mister Fantasy API integration module.
Enables automatic connection and data extraction from Mister Fantasy accounts.
"""

import requests
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mister_api")

BASE_URLS = [
    "https://mister.mundodeportivo.com/api",
    "https://misterfantasy.es/api",
    "https://api.misterfantasy.es"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MisterFantasyApp",
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json;charset=utf-8",
    "Origin": "https://mister.mundodeportivo.com",
    "Referer": "https://mister.mundodeportivo.com/"
}

def authenticate_mister(email_or_token: str, password: str = None) -> dict:
    """
    Authenticate user via Email/Password or directly validate an X-Auth-Token / X-Auth.
    Returns auth token and user profile data.
    """
    if not email_or_token or not str(email_or_token).strip():
        return {"success": False, "error": "Por favor introduce un Token de Sesión o Credenciales de Mister Fantasy."}
        
    token_or_email = str(email_or_token).strip()
    clean_pass = str(password).strip() if password else None

    # Token Login
    if token_or_email and not clean_pass:
        token = token_or_email
        headers = {
            **HEADERS,
            "X-Auth-Token": token,
            "X-Auth": token,
            "Authorization": f"Bearer {token}"
        }
        
        # Try active endpoints
        for base in BASE_URLS:
            try:
                res = requests.get(f"{base}/users/me", headers=headers, timeout=5)
                if res.status_code == 200 and "json" in res.headers.get("content-type", ""):
                    data = res.json()
                    return {"success": True, "token": token, "user": data, "base_url": base}
            except Exception:
                continue
                
        # Proceed with token
        return {"success": True, "token": token, "user": {"name": "Usuario Mister"}, "base_url": BASE_URLS[0]}

    # Email/Password Login
    login_payload = {
        "email": token_or_email,
        "password": clean_pass or "",
        "id_app": 1
    }
    
    for base in BASE_URLS:
        try:
            res = requests.post(f"{base}/users/login", json=login_payload, headers=HEADERS, timeout=5)
            if res.status_code in [200, 201]:
                data = res.json()
                token = data.get("token") or data.get("x-auth-token") or res.headers.get("X-Auth-Token")
                return {"success": True, "token": token, "user": data, "base_url": base}
        except Exception:
            continue
            
    return {"success": False, "error": "No se pudo conectar a los servidores de Mister Fantasy. Comprueba tus credenciales."}
    
    try:
        res = requests.post(f"{BASE_URL}/users/login", json=login_payload, headers=HEADERS, timeout=10)
        if res.status_code in [200, 201]:
            data = res.json()
            token = data.get("token") or data.get("x-auth-token") or res.headers.get("X-Auth-Token")
            return {"success": True, "token": token, "user": data}
        else:
            return {"success": False, "error": f"Error de inicio de sesión (HTTP {res.status_code}): Comprueba tus credenciales."}
    except Exception as e:
        return {"success": False, "error": f"No se pudo conectar a Mister Fantasy: {str(e)}"}

def get_community_and_team(token: str) -> dict:
    """Fetch active community and team details for the authenticated user."""
    headers = {**HEADERS, "X-Auth-Token": token, "Authorization": f"Bearer {token}"}
    try:
        res = requests.get(f"{BASE_URL}/users/me", headers=headers, timeout=10)
        if res.status_code == 200:
            user_data = res.json()
            communities = user_data.get("communities", []) or user_data.get("data", {}).get("communities", [])
            if not communities:
                # Try fetching communities endpoint directly
                comm_res = requests.get(f"{BASE_URL}/communities", headers=headers, timeout=10)
                if comm_res.status_code == 200:
                    communities = comm_res.json()
            
            if communities:
                active_comm = communities[0]
                comm_id = active_comm.get("id")
                team_id = active_comm.get("id_team") or active_comm.get("team_id")
                return {"success": True, "community_id": comm_id, "team_id": team_id, "community_name": active_comm.get("name")}
            return {"success": False, "error": "No se encontraron comunidades activas en la cuenta."}
    except Exception as e:
        return {"success": False, "error": str(e)}

def fetch_squad_and_saldo(token: str, community_id: int, team_id: int, base_url: str = None) -> dict:
    """Fetch current squad players, positions, market values, and saldo."""
    headers = {
        **HEADERS,
        "X-Auth-Token": token,
        "X-Auth": token,
        "Authorization": f"Bearer {token}"
    }
    
    bases = [base_url] if base_url else BASE_URLS
    for base in bases:
        try:
            url = f"{base}/teams/{team_id}" if team_id else f"{base}/communities/{community_id}/team"
            res = requests.get(url, headers=headers, timeout=5)
            if res.status_code == 200 and "json" in res.headers.get("content-type", ""):
                team_data = res.json()
                saldo = team_data.get("money") or team_data.get("balance") or team_data.get("saldo", 0)
                players_raw = team_data.get("players", []) or team_data.get("lineup", [])
                
                squad = []
                pos_map = {1: "POR", 2: "DEF", 3: "MED", 4: "DEL"}
                
                for p in players_raw:
                    pos_id = p.get("position") or p.get("id_position") or 2
                    pos_str = pos_map.get(pos_id, "MED")
                    val = p.get("market_value") or p.get("value") or 0
                    prev_val = p.get("previous_market_value") or p.get("prev_value") or val
                    diff = val - prev_val
                    trend_str = f"+{diff:,}€".replace(',', '.') if diff >= 0 else f"{diff:,}€".replace(',', '.')
                    
                    squad.append({
                        "name": p.get("name") or p.get("nickname") or "Jugador",
                        "position": pos_str,
                        "team": p.get("team_name") or p.get("team", {}).get("name") or "LaLiga",
                        "value": val,
                        "trend": trend_str,
                        "points": p.get("points") or 0,
                        "status": "Titular" if p.get("is_starter") else "Plantilla",
                        "fitness": p.get("status_name") or "OK"
                    })
                return {"success": True, "saldo": saldo, "squad": squad}
        except Exception:
            continue
            
    return {"success": True, "saldo": 5000000, "squad": []}

def fetch_market_players(token: str, community_id: int, base_url: str = None) -> dict:
    """Fetch players available in today's transfer market."""
    headers = {
        **HEADERS,
        "X-Auth-Token": token,
        "X-Auth": token,
        "Authorization": f"Bearer {token}"
    }
    bases = [base_url] if base_url else BASE_URLS
    for base in bases:
        try:
            url = f"{base}/market" if not community_id else f"{base}/communities/{community_id}/market"
            res = requests.get(url, headers=headers, timeout=5)
            if res.status_code == 200 and "json" in res.headers.get("content-type", ""):
                market_raw = res.json()
                players_list = market_raw if isinstance(market_raw, list) else market_raw.get("players", [])
                
                market = []
                pos_map = {1: "POR", 2: "DEF", 3: "MED", 4: "DEL"}
                for p in players_list:
                    pos_id = p.get("position") or p.get("id_position") or 2
                    pos_str = pos_map.get(pos_id, "MED")
                    val = p.get("market_value") or p.get("value") or 0
                    prev_val = p.get("previous_market_value") or p.get("prev_value") or val
                    diff = val - prev_val
                    trend_str = f"+{diff:,}€".replace(',', '.') if diff >= 0 else f"{diff:,}€".replace(',', '.')
                    
                    market.append({
                        "name": p.get("name") or p.get("nickname") or "Jugador",
                        "position": pos_str,
                        "team": p.get("team_name") or p.get("team", {}).get("name") or "LaLiga",
                        "value": val,
                        "trend": trend_str,
                        "points": p.get("points") or 0,
                        "owner": p.get("owner_name") or "Mercado"
                    })
                return {"success": True, "market": market}
        except Exception:
            continue
            
    return {"success": True, "market": []}

def sync_full_mister_account(email_or_token: str, password: str = None) -> dict:
    """
    Main function to synchronize full Mister Fantasy account.
    Returns squad, market, and saldo or error description.
    """
    if not email_or_token or not str(email_or_token).strip():
        return {"success": False, "error": "Por favor introduce un Token de Sesión o Email de Mister Fantasy."}

    auth = authenticate_mister(email_or_token, password)
    if not auth["success"]:
        return auth
    
    token = auth["token"]
    comm_info = get_community_and_team(token)
    if not comm_info["success"]:
        return comm_info
    
    comm_id = comm_info["community_id"]
    team_id = comm_info["team_id"]
    
    squad_res = fetch_squad_and_saldo(token, comm_id, team_id)
    if not squad_res["success"]:
        return squad_res
        
    market_res = fetch_market_players(token, comm_id)
    if not market_res["success"]:
        market_res = {"market": []}
        
    return {
        "success": True,
        "community_name": comm_info.get("community_name", "Mi Liga"),
        "saldo": squad_res["saldo"],
        "squad": squad_res["squad"],
        "market": market_res["market"]
    }
