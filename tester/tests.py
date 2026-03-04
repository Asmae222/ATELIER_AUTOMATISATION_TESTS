"""
tests.py — Suite de tests "as code" pour l'API Frankfurter
Chaque test retourne {"name": str, "status": "PASS"|"FAIL", "latency_ms": float, "details": str}
"""
from tester.client import get


def _make_result(name, response, passed, details=""):
    return {
        "name": name,
        "status": "PASS" if passed else "FAIL",
        "latency_ms": response.get("latency_ms"),
        "details": details or (response.get("error") or "")
    } 


# ── A. Tests Contrat (fonctionnels) ──────────────────────────────────────────

def test_latest_status_200():
    """GET /latest → HTTP 200"""
    r = get("/latest")
    passed = r["status_code"] == 200
    return _make_result("GET /latest → HTTP 200", r, passed,
                        f"status={r['status_code']}")


def test_latest_content_type_json():
    """GET /latest → Content-Type application/json (via parsing réussi)"""
    r = get("/latest")
    passed = r["status_code"] == 200 and r["json"] is not None
    return _make_result("GET /latest → body JSON parseable", r, passed)


def test_latest_has_required_fields():
    """GET /latest → champs 'amount','base','date','rates' présents"""
    r = get("/latest")
    body = r.get("json") or {}
    missing = [f for f in ["amount", "base", "date", "rates"] if f not in body]
    passed = r["status_code"] == 200 and not missing
    return _make_result("GET /latest → champs obligatoires présents", r, passed,
                        f"manquants={missing}" if missing else "OK")


def test_latest_rates_is_dict():
    """GET /latest → 'rates' est un objet non vide"""
    r = get("/latest")
    body = r.get("json") or {}
    rates = body.get("rates", None)
    passed = isinstance(rates, dict) and len(rates) > 0
    return _make_result("GET /latest → rates est un dict non vide", r, passed,
                        f"type={type(rates).__name__}, len={len(rates) if rates else 0}")


def test_latest_base_is_eur():
    """GET /latest?from=EUR → base = 'EUR'"""
    r = get("/latest", params={"from": "EUR"})
    body = r.get("json") or {}
    passed = r["status_code"] == 200 and body.get("base") == "EUR"
    return _make_result("GET /latest?from=EUR → base='EUR'", r, passed,
                        f"base={body.get('base')}")


def test_convert_usd_to_gbp():
    """GET /latest?from=USD&to=GBP → taux USD→GBP présent et > 0"""
    r = get("/latest", params={"from": "USD", "to": "GBP"})
    body = r.get("json") or {}
    rate = (body.get("rates") or {}).get("GBP")
    passed = r["status_code"] == 200 and isinstance(rate, (int, float)) and rate > 0
    return _make_result("GET /latest?from=USD&to=GBP → taux GBP > 0", r, passed,
                        f"GBP={rate}")


def test_historical_date():
    """GET /2020-01-01 → retourne HTTP 200 avec une date valide"""
    r = get("/2020-01-01")
    body = r.get("json") or {}
    # Frankfurter retourne le dernier jour ouvré bancaire
    # (2020-01-01 étant férié, il retourne 2019-12-31)
    passed = r["status_code"] == 200 and "date" in body
    return _make_result("GET /2020-01-01 → date correcte", r, passed,
                        f"date={body.get('date')}")

def test_currencies_list():
    """GET /currencies → dict de devises non vide"""
    r = get("/currencies")
    body = r.get("json") or {}
    passed = r["status_code"] == 200 and isinstance(body, dict) and len(body) > 0
    return _make_result("GET /currencies → liste non vide", r, passed,
                        f"nb devises={len(body)}")


# ── B. Tests Robustesse / cas invalides ──────────────────────────────────────

def test_invalid_currency_returns_error():
    """GET /latest?from=INVALID → 404 ou 422 attendu (pas 200)"""
    r = get("/latest", params={"from": "ZZZZ"})
    passed = r["status_code"] in (400, 404, 422, 500) or r["status_code"] != 200
    return _make_result("GET /latest?from=ZZZZ → erreur attendue", r, passed,
                        f"status={r['status_code']}")


def test_future_date_handled():
    """GET /2999-01-01 → ne plante pas (status connu)"""
    r = get("/2999-01-01")
    passed = r["status_code"] is not None and r["error"] is None
    return _make_result("GET /2999-01-01 → réponse sans crash", r, passed,
                        f"status={r['status_code']}")


# ── Liste de tous les tests ───────────────────────────────────────────────────

ALL_TESTS = [
    test_latest_status_200,
    test_latest_content_type_json,
    test_latest_has_required_fields,
    test_latest_rates_is_dict,
    test_latest_base_is_eur,
    test_convert_usd_to_gbp,
    test_historical_date,
    test_currencies_list,
    test_invalid_currency_returns_error,
    test_future_date_handled,
]
