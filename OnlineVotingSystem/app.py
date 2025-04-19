import os
import logging
from flask import Flask, jsonify
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_login import LoginManager
from models import db, User, Candidate, Vote
import traceback

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

try:
    # Create the Flask app
    app = Flask(__name__)
    app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)  # needed for url_for to generate with https

    # Configure database
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is not set")
    
    logger.info(f"Using database URL: {database_url[:20]}...")  # Log first 20 chars of URL
    
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
        "pool_size": 5,
        "max_overflow": 10,
        "pool_timeout": 30
    }
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Initialize the app with Flask-SQLAlchemy
    db.init_app(app)
    logger.info("Database initialized successfully")

    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message_category = 'info'
    logger.info("Login manager initialized successfully")

    # Create tables within app context
    with app.app_context():
        try:
            db.create_all()
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating database tables: {str(e)}")
            logger.error(traceback.format_exc())
            raise

        # Initialize user loader for Flask-Login
        @login_manager.user_loader
        def load_user(user_id):
            try:
                return db.session.get(User, int(user_id))
            except Exception as e:
                logger.error(f"Error loading user: {str(e)}")
                logger.error(traceback.format_exc())
                return None

    # Import routes after app context is set up
    from routes import *
    logger.info("Routes imported successfully")

    # Add error handler
    @app.errorhandler(Exception)
    def handle_error(error):
        logger.error(f"Error: {str(error)}")
        logger.error(traceback.format_exc())
        return jsonify({
            "error": str(error),
            "traceback": traceback.format_exc()
        }), 500

except Exception as e:
    logger.error(f"Error during app initialization: {str(e)}")
    logger.error(traceback.format_exc())
    raise

# For Vercel
handler = app

if __name__ == '__main__':
    app.run(debug=True)

