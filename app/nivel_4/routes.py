from flask import render_template

from app.nivel_4 import nivel_4_bp
from app.nivel_4.data import NIVEL_DATA


@nivel_4_bp.route("/")
def index() -> str:
    return render_template("nivel_4.html", nivel=NIVEL_DATA)
