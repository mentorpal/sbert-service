#
# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#
import logging
import queue
from typing import Union, List
from torch import Tensor, tensor, topk, mm, nn
from numpy import ndarray
from .embeddings import TransformerEmbeddings, load_transformer

logging.info("encoder init")


def cos_sim(a: Tensor, b: Tensor):
    """
    Computes the cosine similarity cos_sim(a[i], b[j]) for all i and j.
    :return: Matrix with res[i][j]  = cos_sim(a[i], b[j])
    """
    if not isinstance(a, Tensor):
        a = tensor(a)

    if not isinstance(b, Tensor):
        b = tensor(b)

    if len(a.shape) == 1:
        a = a.unsqueeze(0)

    if len(b.shape) == 1:
        b = b.unsqueeze(0)

    a_norm = nn.functional.normalize(a, p=2, dim=1)
    b_norm = nn.functional.normalize(b, p=2, dim=1)
    return mm(a_norm, b_norm.transpose(0, 1))


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
        embedded_question = self.transformer.get_embeddings(question)
        return embedded_question.tolist()

    def cos_sim_weight(self, a: List[str], b: List[str]):
        return float(
            cos_sim(
                self.transformer.get_embeddings(a, convert_to_tensor=True),
                self.transformer.get_embeddings(b, convert_to_tensor=True),
            )
        )
