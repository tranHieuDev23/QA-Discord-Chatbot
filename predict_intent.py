from load_data import load_data
from preprocess import get_id_vector, preprocess_input
from keras.models import load_model
import pickle
import numpy as np

sentences, tokenized_sentences, intents, intent_texts, slots, slot_texts = load_data(
    'dataset/default_dataset_testing.json')

token_2_id = None
with open('token2id.pkl', 'rb') as file:
    token_2_id = pickle.load(file)

model = load_model('intent.h5')


def guess_intent(text):
    tokens = preprocess_input(text, 16)
    ids = get_id_vector(tokens, token_2_id)
    X = np.array([ids])
    y = model.predict(X)[0]
    intent_id = np.argmax(y)
    return intent_texts[intent_id]


if __name__ == '__main__':
    while(True):
        text = input('Please input your sentence: ')
        print(guess_intent(text))
