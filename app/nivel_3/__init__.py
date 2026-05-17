from flask import Blueprint

nivel_3_bp = Blueprint("nivel_3", __name__, url_prefix="/nivel-3")

from app.nivel_3 import routes  # noqa: F401, E402
