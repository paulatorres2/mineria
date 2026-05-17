from flask import render_template, current_app

from app.nivel_2 import nivel_2_bp
from app.nivel_2.data import NIVEL_DATA
from app.nivel_2 import db as nivel2_db


@nivel_2_bp.route("/")
def index() -> str:
    try:
        nivel2_db.ensure_db()
        resultados = {
            "por_departamento_anio": nivel2_db.query_por_departamento_anio(),
            "arma_zona_top10":       nivel2_db.query_arma_zona_top10(),
            "tendencia_mensual":     nivel2_db.query_tendencia_mensual(),
            "sexo_modalidad_top15":  nivel2_db.query_sexo_modalidad_top15(),
        }
    except Exception as exc:
        current_app.logger.error("Nivel 2 DB error: %s", exc)
        resultados = {
            "por_departamento_anio": [],
            "arma_zona_top10":       [],
            "tendencia_mensual":     [],
            "sexo_modalidad_top15":  [],
        }

    return render_template("nivel_2.html", nivel=NIVEL_DATA, resultados=resultados)
