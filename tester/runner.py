"""
runner.py — Exécute tous les tests et calcule les métriques QoS
"""
import datetime
from tester.tests import ALL_TESTS


def compute_p95(values: list) -> float | None:
    """Calcule le percentile 95 d'une liste de nombres."""
    if not values:
        return None
    sorted_v = sorted(values)
    idx = max(0, int(len(sorted_v) * 0.95) - 1)
    return round(sorted_v[idx], 2)


def run_all() -> dict:
    """
    Exécute tous les tests et retourne un dict de run complet :
    {
      "api": "Frankfurter",
      "timestamp": "...",
      "summary": { passed, failed, error_rate, latency_ms_avg, latency_ms_p95 },
      "tests": [ {name, status, latency_ms, details}, ... ]
    }
    """
    results = []
    for test_fn in ALL_TESTS:
        try:
            result = test_fn()
        except Exception as e:
            result = {
                "name": test_fn.__name__,
                "status": "FAIL",
                "latency_ms": None,
                "details": f"Exception inattendue: {e}"
            }
        results.append(result)

    passed  = sum(1 for r in results if r["status"] == "PASS")
    failed  = len(results) - passed
    latencies = [r["latency_ms"] for r in results if r["latency_ms"] is not None]
    avg_lat = round(sum(latencies) / len(latencies), 2) if latencies else None
    p95_lat = compute_p95(latencies)

    return {
        "api": "Frankfurter",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "summary": {
            "passed": passed,
            "failed": failed,
            "total": len(results),
            "error_rate": round(failed / len(results), 3) if results else 0,
            "latency_ms_avg": avg_lat,
            "latency_ms_p95": p95_lat,
            "availability": round(passed / len(results) * 100, 1) if results else 0
        },
        "tests": results
    }
