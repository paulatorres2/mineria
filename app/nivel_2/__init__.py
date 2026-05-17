from flask import Blueprint

nivel_2_bp = Blueprint("nivel_2", __name__, url_prefix="/nivel-2")

from app.nivel_2 import routes  # noqa: F401, E402
