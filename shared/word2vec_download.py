#
# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#
import os
import shutil
from zipfile import ZipFile

from utils import download

from datetime import datetime
from gensim.models import KeyedVectors

from gensim.models.keyedvectors import Word2VecKeyedVectors


def load_and_save_word2vec_keyed_vectors(wor2vec_vectors_path: str, path_to_file: str):
    abs_path = os.path.abspath(path_to_file)
    model_keyed_vectors: Word2VecKeyedVectors = KeyedVectors.load_word2vec_format(
        abs_path, binary=True
    )
    model_keyed_vectors.save(wor2vec_vectors_path)


def word2vec_download(to_path="installed", replace_existing=False) -> str:
    word2vec_path = os.path.abspath(os.path.join(to_path, "word2vec.bin"))
    wor2vec_vectors_path = os.path.abspath(
        os.path.join(to_path, "word_2_vec_saved_keyed_vectors")
    )
    if os.path.isfile(wor2vec_vectors_path) and not replace_existing:
        print(f"already are files!{wor2vec_vectors_path}")
        return word2vec_path
    word2vec_zip = os.path.join(to_path, "word2vec.zip")
    download("http://vectors.nlpl.eu/repository/20/6.zip", word2vec_zip)
    with ZipFile(word2vec_zip, "r") as z:
        z.extract("model.bin")

    load_and_save_word2vec_keyed_vectors(wor2vec_vectors_path, "model.bin")

    os.remove("model.bin")
    os.remove(word2vec_zip)
    return word2vec_path


if __name__ == "__main__":
    word2vec_download()
