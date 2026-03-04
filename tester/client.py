"""
client.py — Wrapper HTTP avec timeout, mesure de latence, retry et gestion 429/5xx
"""
import time
import requests

BASE_URL = "https://api.frankfurter.app"
TIMEOUT  = 5   # secondes
MAX_RETRY = 1  # 1 retry maximum


def get(path: str, params: dict = None) -> dict:
    """
    Effectue un GET sur BASE_URL + path.
    Retourne un dict :
      {
        "status_code": int,
        "json": dict | None,
        "latency_ms": float,
        "error": str | None,
        "retried": bool
      }
    Gère : timeout, 429 (backoff 2s), 5xx (1 retry), exceptions réseau.
    """
    url = BASE_URL + path
    retried = False

    for attempt in range(MAX_RETRY + 1):
        try:
            t0 = time.perf_counter()
            resp = requests.get(url, params=params, timeout=TIMEOUT)
            latency_ms = (time.perf_counter() - t0) * 1000

            # 429 — rate limit : backoff puis retry
            if resp.status_code == 429 and attempt < MAX_RETRY:
                retried = True
                time.sleep(2)
                continue

            # 5xx — erreur serveur : 1 retry
            if resp.status_code >= 500 and attempt < MAX_RETRY:
                retried = True
                time.sleep(1)
                continue

            # Tente de parser le JSON
            try:
                body = resp.json()
            except Exception:
                body = None

            return {
                "status_code": resp.status_code,
                "json": body,
                "latency_ms": round(latency_ms, 2),
                "error": None,
                "retried": retried
            }

        except requests.exceptions.Timeout:
            if attempt < MAX_RETRY:
                retried = True
                continue
            return {"status_code": None, "json": None, "latency_ms": None,
                    "error": "Timeout", "retried": retried}

        except requests.exceptions.RequestException as e:
            return {"status_code": None, "json": None, "latency_ms": None,
                    "error": str(e), "retried": retried}
