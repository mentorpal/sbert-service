#
# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#
from dataclasses import dataclass
import json
from typing import List
from flask import Blueprint, jsonify, request

from server.transformer import word2vec_transformer
from . import w2v_transformer
from .auth_decorator import authenticate

w2v_blueprint = Blueprint("w2v", __name__)

@dataclass
class requestBody:
    words: List[str]
    model: str

@w2v_blueprint.route("", methods=["GET", "POST"])
@authenticate
def encode():
    if not request.is_json:
        return (jsonify({"error": "missing json body"}), 400) 
    json_body = request.get_json()
    body: requestBody = json.loads(json_body)
    result = w2v_transformer.get_feature_vectors(body.words, body.model)
    return (jsonify(result), 200)
