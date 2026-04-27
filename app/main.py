"""
Secure Flask microservice — health, echo, and item endpoints.
DevSecOps demonstration artefact — Iteration 2.
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
logger = logging.getLogger(__name__)


def create_app() -> Flask:
    app = Flask(__name__)

    MAX_MESSAGE_LENGTH = 280
    ITEM_NAME_PATTERN = re.compile(r"^[A-Za-z0-9 _-]{1,64}$")

    @app.get("/health")
    def health() -> tuple:
        return jsonify({"status": "ok"}), HTTPStatus.OK

    @app.post("/echo")
    def echo() -> tuple:
        body = request.get_json(silent=True)
        if not body or "message" not in body:
            return jsonify({"error": "Request body must contain a 'message' key."}), HTTPStatus.BAD_REQUEST

        message = body["message"]
        if not isinstance(message, str) or not message.strip():
            return jsonify({"error": "'message' must be a non-empty string."}), HTTPStatus.BAD_REQUEST

        if len(message) > MAX_MESSAGE_LENGTH:
            return jsonify({"error": f"'message' exceeds the {MAX_MESSAGE_LENGTH}-character limit."}), HTTPStatus.BAD_REQUEST

        logger.info("Echo request (length=%d)", len(message))
        return jsonify({"echo": message}), HTTPStatus.OK

    @app.post("/items")
    def create_item() -> tuple:
        body = request.get_json(silent=True)
        if not body or "name" not in body:
            return jsonify({"error": "Request body must contain a 'name' key."}), HTTPStatus.BAD_REQUEST

        name = body["name"]
        if not isinstance(name, str) or not ITEM_NAME_PATTERN.match(name):
            return jsonify({"error": "'name' must be 1–64 chars: letters, digits, spaces, underscores, hyphens."}), HTTPStatus.BAD_REQUEST

        logger.info("Item created: %s", name)
        return jsonify({"name": name, "status": "created"}), HTTPStatus.CREATED

    @app.errorhandler(HTTPStatus.NOT_FOUND)
    def not_found(_e) -> tuple:
        return jsonify({"error": "Resource not found."}), HTTPStatus.NOT_FOUND

    @app.errorhandler(HTTPStatus.METHOD_NOT_ALLOWED)
    def method_not_allowed(_e) -> tuple:
        return jsonify({"error": "Method not allowed."}), HTTPStatus.METHOD_NOT_ALLOWED

    @app.errorhandler(HTTPStatus.INTERNAL_SERVER_ERROR)
    def internal_error(_e) -> tuple:
        logger.exception("Unhandled exception")
        return jsonify({"error": "Internal server error."}), HTTPStatus.INTERNAL_SERVER_ERROR

    return app


if __name__ == "__main__":
    create_app().run(host="0.0.0.0", port=8080, debug=False)
