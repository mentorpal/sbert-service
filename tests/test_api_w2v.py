#
# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#

# @pytest.fixture(autouse=True)
# def python_path_env(monkeypatch, shared_root):
#     monkeypatch.setenv("SHARED_ROOT", shared_root)


import pytest


def test_returns_400_response_when_query_missing(client):
    res = client.post("/v1/w2v/", headers={"Authorization": "bearer dummykey"})
    assert res.status_code == 400


@pytest.mark.parametrize(
    "model",
    [("word2vec"), ("word2vec_slim")],
)
def test_hello_world_query_param(model: str, client):
    res = client.post(
        f"/v1/w2v?words=hello+world&model={model}",
        headers={"Authorization": "bearer dummykey"},
    )
    assert res.status_code == 200


@pytest.mark.parametrize(
    "model",
    [("word2vec"), ("word2vec_slim")],
)
def test_hello_world_json_body(model: str, client):
    res = client.post(
        "/v1/w2v",
        json={"words": "hello world", "model": model},
        headers={"Authorization": "bearer dummykey"},
    )
    assert res.status_code == 200


@pytest.mark.parametrize(
    "model",
    [("word2vec"), ("word2vec_slim")],
)
def test_index_to_key(model: str, client):
    res = client.post(
        f"/v1/w2v/index_to_key?model={model}",
        headers={"Authorization": "bearer dummykey"},
    )
    assert res.status_code == 200
