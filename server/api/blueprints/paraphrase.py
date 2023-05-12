#
# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#
from flask import Blueprint, jsonify, request
from .auth_decorator import authenticate
from .encode import find_or_load_encoder
import logging

paraphrase_blueprint = Blueprint("paraphrase_mining", __name__)


@paraphrase_blueprint.route("", methods=["POST"])
@authenticate
def paraphrase():
    if not request.content_type.lower().startswith("application/json"):
        return (jsonify({"error": ["invalid content type, only json accepted"]}), 400)
    logging.info(request.data)
    if "sentences" not in request.json:
        return (jsonify({"sentences": ["required field"]}), 400)

    sentences = request.json["sentences"]
    encoder = find_or_load_encoder()
    result = encoder.paraphrase_mining(sentences)
    logging.info("input length: %s, results: %s", len(sentences), len(result))

    return (
        jsonify(
            {
                # "sentences": sentences, # might be large
                "pairs": result,
            }
        ),
        200,
    )
