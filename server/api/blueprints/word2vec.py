#
# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#
from flask import Blueprint, jsonify, request

from . import w2v_transformer
from .auth_decorator import authenticate

w2v_blueprint = Blueprint("w2v", __name__)


@w2v_blueprint.route("/", methods=["GET", "POST"])
@w2v_blueprint.route("", methods=["GET", "POST"])
@authenticate
def encode():
    if request.get_json(silent=True) is not None and "words" in request.json:
        words = request.json["words"].strip().split(" ")
    elif "words" in request.args:
        words = request.args["words"].strip().split(" ")
    else:
        return (jsonify({"words": ["required field"]}), 400)

    if request.get_json(silent=True) is not None and "model" in request.json:
        model = request.json["model"].strip()
    elif "model" in request.args:
        model = request.args["model"].strip()
    else:
        return (jsonify({"model": ["required field"]}), 400)
    result = w2v_transformer.get_feature_vectors(words, model)
    return (jsonify(result), 200)


@w2v_blueprint.route("/index_to_key", methods=["GET", "POST"])
@w2v_blueprint.route("index_to_key", methods=["GET", "POST"])
@authenticate
def index_to_key():
    if "model" not in request.args:
        return (jsonify({"model": ["required field"]}), 400)
    model_name = request.args["model"].strip()
    result = w2v_transformer.get_index_to_key(model_name)
    return (jsonify(result), 200)
