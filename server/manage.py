#
# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#
import logging
import time
from flask import g, request
from .api import create_app

try:
    logging.info("creating app")
    app = create_app()
    # logger configured in create_app()
    log = logging.getLogger()
    log.info("app started")
except Exception as x:
    logging.exception(x)
    raise x


@app.before_request
def before_request():
    if request.blueprint != "ping":
        # do not log pings
        log.info("%s", request.full_path)
    g.start = time.time_ns()


@app.after_request
def after_request(response):
    """Logging after every request."""
    if (
        response.response
        and request.blueprint == "encode"
        and (response.status_code < 500)
    ):  # 5xx should be logged in error handler
        now = time.time_ns()
        g.response_time = (now - g.start) // 1_000_000  # in milliseconds
        log.info(
            "%s",
            {
                "status": response.status_code,
                "response-time": g.response_time,
                "endpoint": request.endpoint,
                "method": request.method,
                "full_path": request.full_path,
                "url": request.url,
            },
        )

    return response
