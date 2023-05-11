#
# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#
from os import path
from typing import Dict, List
from gensim.models import KeyedVectors
from gensim.models.keyedvectors import Word2VecKeyedVectors
from numpy import ndarray
from datetime import datetime

WORD2VEC_MODELS: Dict[str, Word2VecKeyedVectors] = {}

WORD2VEC_MODEL_NAME = "word2vec"
WORD2VEC_SLIM_MODEL_NAME = "word2vec_slim"


def find_or_load_word2vec(file_path: str) -> Word2VecKeyedVectors:
    print(f"{datetime.now()} loading {file_path}", flush=True)
    abs_path = path.abspath(file_path)
    if abs_path not in WORD2VEC_MODELS:
        WORD2VEC_MODELS[abs_path] = KeyedVectors.load(file_path)
    return WORD2VEC_MODELS[abs_path]


def load_word2vec_model(path: str) -> Word2VecKeyedVectors:
    return KeyedVectors.load_word2vec_format(path, binary=True)


class Word2VecTransformer:
    w2v_model: Word2VecKeyedVectors
    w2v_slim_model: Word2VecKeyedVectors

    def __init__(self, shared_root: str):
        print(f"{datetime.now()} before word2vec.bin", flush=True)
        self.w2v_model = find_or_load_word2vec(
            path.abspath(path.join(shared_root, "word_2_vec_saved_keyed_vectors"))
        )
        print(f"{datetime.now()} after word2vec.bin", flush=True)
        print(f"{datetime.now()} before word2vec_slim.bin", flush=True)

        self.w2v_slim_model = find_or_load_word2vec(
            path.abspath(path.join(shared_root, "word_2_vec_slim_saved_keyed_vectors"))
        )
        print(f"{datetime.now()} after word2vec_slim.bin", flush=True)

    def get_feature_vectors(self, words: List[str], model: str) -> Dict[str, ndarray]:
        result: Dict[str, ndarray] = dict()
        for word in words:
            if model == WORD2VEC_MODEL_NAME:
                if word in self.w2v_model:
                    result[word] = self.w2v_model[word].tolist()
            elif model == WORD2VEC_SLIM_MODEL_NAME and word in self.w2v_slim_model:
                result[word] = self.w2v_slim_model[word].tolist()
        return result

    def get_index_to_key(self, model: str):
        if model == WORD2VEC_MODEL_NAME:
            return self.w2v_model.index_to_key
        elif model == WORD2VEC_SLIM_MODEL_NAME:
            return self.w2v_slim_model.index_to_key
        else:
            return None
