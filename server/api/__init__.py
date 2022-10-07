#
# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#
import logging.config
import logging
import json
from os import environ
from flask import Flask
from flask_cors import CORS
from werkzeug.exceptions import HTTPException
from .blueprints.encode import encode_blueprint
from .blueprints.ping import ping_blueprint
from .blueprints.health import health_blueprint
from .blueprints.paraphrase import paraphrase_blueprint


def create_app():
    _setup_sentry()
    _setup_logging()
    app = Flask(__name__)
    CORS(app)
    _setup_error_handlers(app)
    _setup_route_handlers(app)

    return app


def _setup_route_handlers(app):
    app.register_blueprint(health_blueprint, url_prefix="/")
    app.register_blueprint(ping_blueprint, url_prefix="/v1/ping")
    app.register_blueprint(encode_blueprint, url_prefix="/v1/encode")
    app.register_blueprint(paraphrase_blueprint, url_prefix="/v1/paraphrase")

    @app.route("/v1/debug-sentry")
    def _error_handler_test():
        raise Exception("Safe to ignore, route for intentional error")


def _setup_error_handlers(app):
    def http_error_handler(e):
        """Return JSON instead of HTML for HTTP errors."""
        # start with the correct headers and status code from the error
        response = e.get_response()
        # replace the body with JSON
        response.data = json.dumps(
            {
                "code": e.code,
                "name": e.name,
                "description": e.description,
            }
        )
        response.content_type = "application/json"
        return response

    def generic_exception_handler(e):
        """Return JSON instead of generic 500 internal error for Exceptions"""
        response = app.response_class(
            response=json.dumps({"error": "Exception", "message": str(e)}),
            status=500,
            content_type="application/json",
        )
        return response

    app.register_error_handler(HTTPException, http_error_handler)
    app.register_error_handler(Exception, generic_exception_handler)


def _setup_sentry():
    if environ.get("IS_SENTRY_ENABLED", "") == "true":
        import sentry_sdk  # NOQA E402
        from sentry_sdk.integrations.flask import FlaskIntegration  # NOQA E402

        def traces_sampler(sampling_context):
            """
            see https://docs.sentry.io/platforms/python/guides/flask/configuration/sampling/
            """
            op = sampling_context["transaction_context"]["op"]
            if op == "http.server":
                if "OPTIONS" == sampling_context["wsgi_environ"]["REQUEST_METHOD"]:
                    return 0.0
                path = sampling_context["wsgi_environ"]["PATH_INFO"]
                if path == "/" or path == "/v1/ping":
                    # Drop this transaction, by setting its sample rate to 0%
                    return 0.0

                # Set traces_sample_rate to 1.0 to capture 100%
                # of transactions for performance monitoring.
                return 0.2

        logging.info("SENTRY enabled, calling init")
        sentry_sdk.init(
            dsn=environ.get("SENTRY_DSN_MENTOR_SBERT_SERVICE"),
            # include project so issues can be filtered in sentry:
            environment=environ.get("STAGE", "qa"),
            integrations=[FlaskIntegration()],
            traces_sampler=traces_sampler,
            debug=environ.get("SENTRY_DEBUG_SBERT_SERVICE", "") == "true",
        )


def _setup_logging():
    logging.config.dictConfig(
        {
            "version": 1,
            "formatters": {
                "default": {
                    "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
                }
            },
            "handlers": {
                "wsgi": {
                    "class": "logging.StreamHandler",
                    "stream": "ext://flask.logging.wsgi_errors_stream",
                    "formatter": "default",
                }
            },
            "root": {"level": "INFO", "handlers": ["wsgi"]},
        }
    )
