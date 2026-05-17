from flask import Blueprint

nivel_1_bp = Blueprint("nivel_1", __name__, url_prefix="/nivel-1")

from app.nivel_1 import routes  # noqa: F401, E402
