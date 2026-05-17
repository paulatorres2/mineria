from flask import render_template

from app.nivel_3 import nivel_3_bp
from app.nivel_3.data import NIVEL_DATA


@nivel_3_bp.route("/")
def index() -> str:
    return render_template("nivel_3.html", nivel=NIVEL_DATA)
