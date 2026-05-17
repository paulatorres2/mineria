from flask import render_template

from app.nivel_1 import nivel_1_bp
from app.nivel_1.data import NIVEL_DATA


@nivel_1_bp.route("/")
def index() -> str:
    return render_template("nivel_1.html", nivel=NIVEL_DATA)


@nivel_1_bp.route("/dashboard")
def dashboard() -> str:
    return render_template("dashboard.html", nivel=NIVEL_DATA)
