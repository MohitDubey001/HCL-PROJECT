"""
Application Root
"""

import os
from flask import Flask
from dotenv import load_dotenv

from models.models import db, login_manager
from routes.routes import main as main_blueprint

load_dotenv()


# Env. Vars.
DB_URL = os.getenv("DB_URL")
SECRET_KEY = os.getenv("SECRET_KEY")
PORT = int(os.getenv("PORT", "5000"))


def create_app():
    app = Flask(__name__)
    app.secret_key = SECRET_KEY

    if not DB_URL:
        raise RuntimeError("Set DB_URL environment variable.")

    app.config["SQLALCHEMY_DATABASE_URI"] = DB_URL
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.register_blueprint(main_blueprint)

    # DB Initialisation
    db.init_app(app)

    # Authentication
    login_manager.init_app(app)
    
    return app


if __name__ == "__main__":
    app = create_app()

    with app.app_context():
        db.create_all()

    app.run(host="0.0.0.0", port=PORT, debug=True)
