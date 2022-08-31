#
# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#
import logging
from flask import Blueprint, jsonify, request
from . import encoder
from .auth_decorator import authenticate

encode_blueprint = Blueprint("encode", __name__)


@encode_blueprint.route("/", methods=["GET", "POST"])
@encode_blueprint.route("", methods=["GET", "POST"])
@authenticate
def encode():
    if "query" not in request.args:
        return (jsonify({"query": ["required field"]}), 400)
    sentence = request.args["query"].strip()
    result = encoder.encode(sentence)
    return (
        jsonify(
            {
                "query": sentence,
                "encoding": result,
            }
        ),
        200,
    )


@encode_blueprint.route("cos_sim_weight", methods=["POST"])
@authenticate
def cos_sim_weight():
    """
    Computes the cosine similarity cos_sim(a[i], b[j]) for all i and j.
    :return: Matrix with res[i][j]  = cos_sim(a[i], b[j])
    """
    if not request.content_type.lower().startswith("application/json"):
        return (jsonify({"error": ["invalid content type, only json accepted"]}), 400)
    logging.info(request.data)

    if "a" not in request.json or "b" not in request.json:
        return (jsonify({"a and b sentences": ["required field"]}), 400)
    result = encoder.cos_sim_weight(request.json["a"], request.json["b"])
    return (
        jsonify(
            {
                # "a": request.json["a"],
                # "b": request.json["b"],
                "cos_sim_weight": result,
            }
        ),
        200,
    )
