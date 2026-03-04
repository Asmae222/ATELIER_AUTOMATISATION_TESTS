from flask import Flask, render_template, jsonify, redirect, url_for, Response
from flask import json
from urllib.request import urlopen
from werkzeug.utils import secure_filename
import sqlite3

from tester.runner import run_all
from storage import init_db, save_run, list_runs, get_last_run

app = Flask(__name__)
init_db()  # Crée la base SQLite au démarrage


# ─── Route du prof (consignes) ────────────────────────────────────────────────
@app.get("/")
def consignes():
    return render_template('consignes.html')


# ─── /run — Déclenche un run de tests ────────────────────────────────────────
@app.route("/run", methods=["GET", "POST"])
def run():
    result = run_all()
    save_run(result)
    return redirect(url_for("dashboard"))


# ─── /dashboard — Tableau de résultats + historique ──────────────────────────
@app.route("/dashboard")
def dashboard():
    last    = get_last_run()
    history = list_runs(limit=20)
    return render_template("dashboard.html", last=last, history=history)


# ─── /health — État de santé de la solution (bonus) ──────────────────────────
@app.route("/health")
def health():
    last = get_last_run()
    if not last:
        return jsonify({"status": "no_data", "message": "Aucun run effectué"}), 200
    avail  = last["summary"]["availability"]
    status = "healthy" if avail >= 80 else "degraded" if avail >= 50 else "down"
    return jsonify({
        "status":          status,
        "api":             last["api"],
        "last_run":        last["timestamp"],
        "availability":    avail,
        "passed":          last["summary"]["passed"],
        "failed":          last["summary"]["failed"],
        "latency_ms_avg":  last["summary"]["latency_ms_avg"],
        "latency_ms_p95":  last["summary"]["latency_ms_p95"],
    })


# ─── /export — Export JSON téléchargeable (bonus) ────────────────────────────
@app.route("/export")
def export():
    runs = list_runs(limit=100)
    data = json.dumps(runs, indent=2, ensure_ascii=False)
    return Response(
        data,
        mimetype="application/json",
        headers={"Content-Disposition": "attachment; filename=runs_export.json"}
    )


if __name__ == "__main__":
    # utile en local uniquement
    app.run(host="0.0.0.0", port=5000, debug=True)
