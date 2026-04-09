from flask import render_template

from app.main import main_bp
from app.main.data import PROJECT_DATA


@main_bp.route("/")
def index() -> str:
    return render_template("index.html", proyecto=PROJECT_DATA)
