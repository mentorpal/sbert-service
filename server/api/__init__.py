#
# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#
# from logging.config import dictConfig
import logging
from flask import Flask
from flask_cors import CORS
from os import environ
from .blueprints.encode import encode_blueprint
from .blueprints.ping import ping_blueprint
from .blueprints.health import health_blueprint


def create_app():
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
    app = Flask(__name__)

    if environ.get("IS_SENTRY_ENABLED", "") == "true":
        import sentry_sdk  # NOQA E402
        from sentry_sdk.integrations.flask import FlaskIntegration  # NOQA E402

        logging.info("SENTRY enabled, calling init")
        sentry_sdk.init(
            dsn=environ.get("SENTRY_DSN_MENTOR_SBERT_SERVICE"),
            # include project so issues can be filtered in sentry:
            environment=environ.get("STAGE", "qa"),
            integrations=[FlaskIntegration()],
            # Set traces_sample_rate to 1.0 to capture 100%
            # of transactions for performance monitoring.
            # We recommend adjusting this value in production.
            traces_sample_rate=0.20,
            debug=environ.get("SENTRY_DEBUG_SBERT_SERVICE", "") == "true",
        )

    CORS(app)

    app.register_blueprint(health_blueprint, url_prefix="/")
    app.register_blueprint(ping_blueprint, url_prefix="/v1/ping")
    app.register_blueprint(encode_blueprint, url_prefix="/v1/encode")

    return app
