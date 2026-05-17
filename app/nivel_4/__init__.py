from flask import Blueprint

nivel_4_bp = Blueprint("nivel_4", __name__, url_prefix="/nivel-4")

from app.nivel_4 import routes  # noqa: F401, E402
