import logging
from flask import Flask, jsonify
from werkzeug.middleware.proxy_fix import ProxyFix
import os
import sys
import traceback

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

try:
    # Add the parent directory to the Python path
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    logger.info("Added parent directory to Python path")

    # Import the app from OnlineVotingSystem
    from OnlineVotingSystem.app import app
    logger.info("Successfully imported app")

    # Configure the app for Vercel
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    logger.info("Configured WSGI app")

    # Add error handler
    @app.errorhandler(Exception)
    def handle_error(error):
        logger.error(f"Error: {str(error)}")
        logger.error(traceback.format_exc())
        return jsonify({
            "error": str(error),
            "traceback": traceback.format_exc()
        }), 500

    # Export the app for Vercel
    handler = app
    logger.info("Handler set successfully")

except Exception as e:
    logger.error(f"Error during initialization: {str(e)}")
    logger.error(traceback.format_exc())
    raise 