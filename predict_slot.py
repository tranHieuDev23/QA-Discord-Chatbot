from load_data import load_data
from preprocess import get_id_vector, preprocess_input, null_token
from keras.models import load_model
import pickle
import numpy as np

sentences, tokenized_sentences, intents, intent_texts, slots, slot_texts = load_data(
    'dataset/default_dataset_testing.json')

token_2_id = None
with open('token2id.pkl', 'rb') as file:
    token_2_id = pickle.load(file)

model = load_model('slot.h5')


def guess_slot(text):
    tokens = preprocess_input(text, 16)
    ids = get_id_vector(tokens, token_2_id)
    X = np.array([ids])
    y = model.predict(X)[0]
    slots = np.argmax(y, axis=1)
    result = []
    last_token = ''
    last_type = 0
    for i in range(16):
        token = tokens[i]
        slot_type = slots[i]
        if (token != null_token and slot_type != 0):
            if (slot_type == last_type):
                last_token += ' ' + token
            else:
                if (last_type != 0):
                    result.append((last_token, slot_texts[last_type]))
                last_token = token
                last_type = slot_type
        if (i == 15 and last_type != 0):
            result.append((last_token, slot_texts[last_type]))
    return result


if __name__ == '__main__':
    while(True):
        text = input('Please input your sentence: ')
        print(guess_slot(text))
