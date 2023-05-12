#
# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#
import os
from server.transformer.word2vec_transformer import Word2VecTransformer
from typing import Dict
from server.transformer.encode import TransformersEncoder
import logging

encoder_holder: Dict[str, TransformersEncoder] = {}


def find_or_load_encoder():
    logging.info(encoder_holder)
    if "encoder" not in encoder_holder:
        logging.info("encoder not in holder, loading in")
        encoder = TransformersEncoder(shared_root)
        encoder_holder["encoder"] = encoder
        return encoder
    logging.info("encoder found")
    return encoder_holder["encoder"]


shared_root = os.environ.get("SHARED_ROOT", "shared")
if not os.path.isdir(shared_root):
    raise Exception("Shared missing.")

# load on init so request handler is fast on first hit
w2v_transformer: Word2VecTransformer = Word2VecTransformer(shared_root)
