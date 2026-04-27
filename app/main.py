"""
Secure Flask microservice — health, echo, and item endpoints.
DevSecOps demonstration artefact — Iteration 2 (hardened).
"""

from __future__ import annotations

import logging
import re
from http import HTTPStatus
from flask import Flask, jsonify, request

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

logger = logging.getLogger("secure-app")


def create_app() -> Flask:
    app = Flask(__name__)

    # Security constraints (input boundaries)
    MAX_MESSAGE_LENGTH = 280
    ITEM_NAME_PATTERN = re.compile(r"^[A-Za-z0-9 _-]{1,64}$")

    # -------------------------
    # HEALTH CHECK
    # -------------------------
    @app.get("/health")
    def health():
        return jsonify({"status": "ok"}), HTTPStatus.OK

    # -------------------------
    # ECHO ENDPOINT
    # -------------------------
    @app.post("/echo")
    def echo():
        body = request.get_json(silent=True)

        if not isinstance(body, dict):
            return jsonify({"error": "Invalid JSON body."}), HTTPStatus.BAD_REQUEST

        message = body.get("message")

        if not isinstance(message, str):
            return jsonify({"error": "'message' must be a string."}), HTTPStatus.BAD_REQUEST

        message = message.strip()

        if not message:
            return jsonify({"error": "'message' cannot be empty."}), HTTPStatus.BAD_REQUEST

        if len(message) > MAX_MESSAGE_LENGTH:
            return jsonify({
                "error": f"'message' exceeds {MAX_MESSAGE_LENGTH} characters."
            }), HTTPStatus.BAD_REQUEST

        logger.info("Echo request processed (length=%d)", len(message))

        return jsonify({"echo": message}), HTTPStatus.OK

    # -------------------------
    # ITEM CREATION
    # -------------------------
    @app.post("/items")
    def create_item():
        body = request.get_json(silent=True)

        if not isinstance(body, dict):
            return jsonify({"error": "Invalid JSON body."}), HTTPStatus.BAD_REQUEST

        name = body.get("name")

        if not isinstance(name, str):
            return jsonify({"error": "'name' must be a string."}), HTTPStatus.BAD_REQUEST

        name = name.strip()

        if not ITEM_NAME_PATTERN.fullmatch(name):
            return jsonify({
                "error": "Invalid 'name'. Allowed: 1–64 chars (letters, numbers, space, _ -)."
            }), HTTPStatus.BAD_REQUEST

        logger.info("Item created: %s", name)

        return jsonify({
            "name": name,
            "status": "created"
        }), HTTPStatus.CREATED

    # -------------------------
    # ERROR HANDLERS
    # -------------------------
    @app.errorhandler(HTTPStatus.NOT_FOUND)
    def not_found(_):
        return jsonify({"error": "Resource not found."}), HTTPStatus.NOT_FOUND

    @app.errorhandler(HTTPStatus.METHOD_NOT_ALLOWED)
    def method_not_allowed(_):
        return jsonify({"error": "Method not allowed."}), HTTPStatus.METHOD_NOT_ALLOWED

    @app.errorhandler(Exception)
    def internal_error(e):
        logger.exception("Unhandled exception: %s", str(e))
        return jsonify({"error": "Internal server error."}), HTTPStatus.INTERNAL_SERVER_ERROR

    return app


# -------------------------
# GUNICORN / PRODUCTION ENTRYPOINT SUPPORT
# -------------------------
app = create_app()

if __name__ == "__main__":
    # Explicitly safe for local dev only (never debug in CI/CD)
    app.run(host="0.0.0.0", port=8080, debug=False)
