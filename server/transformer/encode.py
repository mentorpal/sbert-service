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

    def paraphrase_mining(
        self,
        sentences: List[str],
        batch_size: int = 32,
        query_chunk_size: int = 5000,
        corpus_chunk_size: int = 100000,
        max_pairs: int = 500000,
        top_k: int = 100,
    ):
        """
        Given a list of sentences / texts, this function performs paraphrase mining. It compares all sentences against all
        other sentences and returns a list with the pairs that have the highest cosine similarity score.

        :param model: SentenceTransformer model for embedding computation
        :param sentences: A list of strings (texts or sentences)
        :param batch_size: Number of texts that are encoded simultaneously by the model
        :param query_chunk_size: Search for most similar pairs for #query_chunk_size at the same time. Decrease, to lower memory footprint (increases run-time).
        :param corpus_chunk_size: Compare a sentence simultaneously against #corpus_chunk_size other sentences. Decrease, to lower memory footprint (increases run-time).
        :param max_pairs: Maximal number of text pairs returned.
        :param top_k: For each sentence, we retrieve up to top_k other sentences
        :return: Returns a list of triplets with the format [score, id1, id2]
        """

        # Compute embedding for the sentences
        embeddings = self.transformer.get_embeddings(
            sentences,
            batch_size=batch_size,
            convert_to_tensor=True,
            convert_to_numpy=False,
        )

        top_k += 1  # A sentence has the highest similarity to itself. Increase +1 as we are interest in distinct pairs

        # Mine for duplicates
        pairs = queue.PriorityQueue()
        min_score = -1
        num_added = 0

        for corpus_start_idx in range(0, len(embeddings), corpus_chunk_size):
            for query_start_idx in range(0, len(embeddings), query_chunk_size):
                scores = cos_sim(
                    embeddings[query_start_idx : query_start_idx + query_chunk_size],
                    embeddings[corpus_start_idx : corpus_start_idx + corpus_chunk_size],
                )

                scores_top_k_values, scores_top_k_idx = topk(
                    scores,
                    min(top_k, len(scores[0])),
                    dim=1,
                    largest=True,
                    sorted=False,
                )
                scores_top_k_values = scores_top_k_values.cpu().tolist()
                scores_top_k_idx = scores_top_k_idx.cpu().tolist()

                for query_itr in range(len(scores)):
                    for top_k_idx, corpus_itr in enumerate(scores_top_k_idx[query_itr]):
                        i = query_start_idx + query_itr
                        j = corpus_start_idx + corpus_itr

                        if (
                            i != j
                            and scores_top_k_values[query_itr][top_k_idx] > min_score
                        ):
                            pairs.put((scores_top_k_values[query_itr][top_k_idx], i, j))
                            num_added += 1

                            if num_added >= max_pairs:
                                entry = pairs.get()
                                min_score = entry[0]

        # Get the pairs
        added_pairs = set()  # Used for duplicate detection
        pairs_list = []
        while not pairs.empty():
            score, i, j = pairs.get()
            sorted_i, sorted_j = sorted([i, j])

            if sorted_i != sorted_j and (sorted_i, sorted_j) not in added_pairs:
                added_pairs.add((sorted_i, sorted_j))
                pairs_list.append([score, i, j])

        # Highest scores first
        pairs_list = sorted(pairs_list, key=lambda x: x[0], reverse=True)
        return pairs_list
