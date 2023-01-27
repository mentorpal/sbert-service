#
# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#
import pickle
import torch
import sys
import logging
from os import path
from typing import List, Union, Dict
from sentence_transformers import SentenceTransformer

SENTENCE_TRANSFORMER_MODELS: Dict[str, SentenceTransformer] = {}


class CustomUnpickler(pickle.Unpickler):
    def find_class(self, module, name):
        try:
            return super().find_class(__name__, name)
        except AttributeError:
            return super().find_class(module, name)


def find_or_load_sentence_transformer(file_path: str) -> SentenceTransformer:
    abs_path = path.abspath(file_path)
    if abs_path not in SENTENCE_TRANSFORMER_MODELS:
        SENTENCE_TRANSFORMER_MODELS[abs_path] = SentenceTransformer(
            path.join(file_path, "distilbert-base-nli-mean-tokens"), device="cpu"
        )
    model = SENTENCE_TRANSFORMER_MODELS[abs_path]
    quantized = torch.quantization.quantize_dynamic(
        model,
        {
            torch.nn.Embedding: torch.quantization.qconfig.float_qparams_weight_only_qconfig
        },
        dtype=torch.qint8,
    )
    return quantized


class TransformerEmbeddings:
    def __init__(self, shared_root: str):
        self.transformer: SentenceTransformer = find_or_load_sentence_transformer(
            path.join(shared_root, "sentence-transformer")
        )

    def get_embeddings(
        self,
        data: Union[str, List[str]],
        batch_size=32,
        show_progress_bar=False,
        convert_to_numpy=True,
        convert_to_tensor=False,
    ):
        embeddings = self.transformer.encode(
            data,
            show_progress_bar=show_progress_bar,
            batch_size=batch_size,
            convert_to_numpy=convert_to_numpy,
            convert_to_tensor=convert_to_tensor,
        )
        return embeddings


def _generate(dst_folder):
    pkl = path.join(dst_folder, "transformer.pkl")
    if path.exists(pkl):
        print(f"{pkl} exists, skipping")
    else:
        print(f"generating {pkl}")
        transformer = TransformerEmbeddings(dst_folder)
        with open(pkl, "wb") as f:
            pickle.dump(transformer, f)
        print(f"{pkl} created")


def load_transformer(dst_folder):
    logging.info("unpickling transformers")
    return CustomUnpickler(open(path.join(dst_folder, "transformer.pkl"), "rb")).load()


if __name__ == "__main__":
    _generate(sys.argv[-1])
