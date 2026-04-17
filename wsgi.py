import os

from app import create_app
from config import config

app = create_app(config.get(os.environ.get(
    "FLASK_ENV", "default"), config["default"]))

if __name__ == "__main__":
    app.run()
