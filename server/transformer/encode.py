#
# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#
import logging
from .utils import sanitize_string
from typing import Union, Tuple, List
from .embeddings import TransformerEmbeddings, load_transformer
from torch import Tensor
from numpy import ndarray

logging.info("encoder init")


class TransformersEncoder:
    transformer: TransformerEmbeddings  # shared

    def __init__(self, shared_root: str):
        self.transformer = self.__load_transformer(shared_root)

    def __load_transformer(self, shared_root):
        if getattr(TransformersEncoder, "transformer", None) is None:
            # class variable, load just once
            logging.info(f"loading transformers from {shared_root}")
            transformer = load_transformer(shared_root)
            setattr(TransformersEncoder, "transformer", transformer)
        return TransformersEncoder.transformer

    def encode(self, question: str) -> Union[List[Tensor], ndarray, Tensor]:
        logging.info(question)
        # sanitized_question = sanitize_string(question)
        embedded_question = self.transformer.get_embeddings(question)
        return embedded_question.tolist()
