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

WORD2VEC_MODELS: Dict[str, Word2VecKeyedVectors] = {}

WORD2VEC_MODEL_NAME = "word2vec"
WORD2VEC_SLIM_MODEL_NAME = "word2vec_slim"


def find_or_load_word2vec(file_path: str) -> Word2VecKeyedVectors:
    abs_path = path.abspath(file_path)
    if abs_path not in WORD2VEC_MODELS:
        WORD2VEC_MODELS[abs_path] = KeyedVectors.load_word2vec_format(
            abs_path, binary=True
        )
    return WORD2VEC_MODELS[abs_path]


def load_word2vec_model(path: str) -> Word2VecKeyedVectors:
    return KeyedVectors.load_word2vec_format(path, binary=True)


class Word2VecTransformer:
    w2v_model: Word2VecKeyedVectors
    w2v_slim_model: Word2VecKeyedVectors

    def __init__(self, shared_root: str):
        self.w2v_model = find_or_load_word2vec(path.abspath(path.join(shared_root, "word2vec.bin")))
        self.w2v_slim_model = find_or_load_word2vec(path.abspath(path.join(shared_root, "word2vec_slim.bin")))

    def get_feature_vectors(self, words: List[str], model: str) -> Dict[str, ndarray]:
        result: Dict[str, ndarray] = dict()
        for word in words:
            if model is WORD2VEC_MODEL_NAME:
                if word in self.w2v_model:
                    result[word] = self.w2v_model[word]
            elif model is WORD2VEC_SLIM_MODEL_NAME and word in self.w2v_slim_model:
                result[word] = self.w2v_slim_model[word]
        return result
    
    def get_index_to_key(self, model:str):
        if model is WORD2VEC_MODEL_NAME:
            return self.w2v_model.index_to_key
        elif model is WORD2VEC_SLIM_MODEL_NAME:
            return self.w2v_slim_model.index_to_key
        else:
            return None
