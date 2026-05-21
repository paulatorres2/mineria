import json

from flask import Response, render_template, stream_with_context

from app.nivel_4 import nivel_4_bp
from app.nivel_4.data import NIVEL_DATA
from app.nivel_4 import spark as nivel4_spark


@nivel_4_bp.route("/")
def index() -> str:
    return render_template("nivel_4.html", nivel=NIVEL_DATA)


@nivel_4_bp.route("/api/stream")
def api_stream():
    def generate():
        for event in nivel4_spark.stream_pipeline():
            yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
    return Response(
        stream_with_context(generate()),
        content_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
