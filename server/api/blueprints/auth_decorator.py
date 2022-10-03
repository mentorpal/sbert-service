#
# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#
from functools import wraps
from flask import request, abort
from os import environ
import logging
import jwt


log = logging.getLogger()
api_keys = set(environ.get("API_SECRET_KEY").split(","))
jwt_secret = set(environ.get("JWT_SECRET_KEY").split(","))


def authenticate(f):
    """Confirms the bearer token matches"""

    @wraps(f)
    def protected_endpoint(*args, **kws):
        bearer_token = request.headers.get("Authorization", "")
        token_authentication = bearer_token.lower().startswith("bearer")
        token_split = bearer_token.split(" ")
        if not token_authentication or len(token_split) == 1:
            log.debug("no authentication token provided")
            abort(401, "no authentication token provided")
        token = token_split[1]
        if token not in api_keys:
            # token not an API key, check if it is a valid JWT access token
            jwt_approved = False
            for secret in jwt_secret:
                try:
                    jwt.decode(token, secret, algorithms=["HS256"])
                    jwt_approved = True
                except:
                    pass
            if not jwt_approved:
                abort(400, "Failed to decode JWT")
        return f(*args, **kws)

    return protected_endpoint
