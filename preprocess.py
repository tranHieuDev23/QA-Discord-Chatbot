import nltk
from nltk.tokenize import word_tokenize
from keras.utils import to_categorical

nltk.download('punkt')
null_token = '<NUL>'


def preprocess_input(text, length_limit):
    text = text.strip().lower()
    tokens = word_tokenize(text)
    if (len(tokens) >= length_limit):
        stemmed = tokens[:length_limit]
    else:
        diff = length_limit - len(tokens)
        for i in range(diff):
            tokens.append(null_token)
    return tokens


def get_token_to_id_dict(X):
    vocab = set()
    vocab.add(null_token)
    for item in X:
        for token in item:
            vocab.add(token)
    token_to_id = {}
    id = 0
    for token in vocab:
        id += 1
        token_to_id[token] = id
    return token_to_id


def get_id_vector(tokens, token_to_id):
    vocab_len = len(token_to_id) + 1
    result = []
    for token in tokens:
        one_hot = [0.0] * vocab_len
        if (token in token_to_id):
            one_hot[token_to_id[token]] = 1.0
        else:
            one_hot[0] = 1.0
        result.append(one_hot)
    return result


def get_slot_id_vector(slots, num_types):
    return to_categorical(slots, num_types)
