# hard-coded list of keywords to look for
import re
from collections import defaultdict

KEYWORD_LIST = [
    # general
    "machine learning",
    "deep learning",
    ["neural network", "neural net", "neural networks", "neural nets"],
    # techniques
    ["transformer", "transformers"],
    ["embedding", "embeddings"],
    ["cnn", "convolutional neural network", "cnns", "convolutional neural networks"],
    ["rnn", "recurrent neural network", "rnns", "recurrent neural networks"],
    ["vae", "variational autoencoder", "vaes", "variational autoencoders"],
    [
        "gan",
        "generative adversarial network",
        "gans",
        "generative adversarial networks",
    ],
    ["lstm", "long short term memory", "lstms"],
    # domain terms
    ["backpropagation"],
    ["gradient descent"],
    ["activation function"],
    "clustering",
    "training",
    "overfitting",
    "underfitting",
    ["loss function", "cost function", "loss functions", "cost functions"],
    "fine tuning",
    ["dataset", "datasets"],
    "classification",
    "regression",
    "segmentation",
]


def build_keyword_to_id_dict():
    kw_dict = {}
    for i, kw in enumerate(KEYWORD_LIST):
        if isinstance(kw, list):
            for k in kw:
                kw_dict[k] = i
        else:
            kw_dict[kw] = i
    return kw_dict


# map from keyword 'values' to ids
KEYWORD_TO_ID_DICT = build_keyword_to_id_dict()


def count_keyword_occurrences(text: str) -> dict[int, int]:
    """
    Counts the occurrences of terms from the KEYWORD list in the source text.
    Does simple punctuation stripping.

    Outputs a map from keyword ids to counts
    """
    # strip punctuation and tokenize text
    text = text.lower()
    text = re.sub(r"[^a-zA-Z]+", " ", text)
    text_tokens = text.split()

    # iterater through id matching dict
    matches = defaultdict(int)
    for kw, id_ in KEYWORD_TO_ID_DICT.items():
        kw_tokens = tuple(kw.split())
        kw_len = len(kw_tokens)

        # sliding window
        for i in range(len(text_tokens) + 1 - kw_len):
            window = tuple(text_tokens[i : i + kw_len])
            if window == kw_tokens:
                matches[id_] += 1

    return matches
