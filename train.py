from load_data import load_data
from preprocess import preprocess_input, get_token_to_id_dict, get_id_vector, get_slot_id_vector
from intent_model import get_intent_model
from slot_model import get_slot_model
from os import path
from keras.models import load_model
from keras.preprocessing.sequence import pad_sequences
import pickle
import numpy as np

training_path = 'dataset/default_dataset_training.json'
testing_path = 'dataset/default_dataset_testing.json'

sentences, tokenized_sentences, intents, intent_texts, slots, slot_texts = load_data(
    training_path)
sentences_test, tokenized_sentences_test, intents_test, _, slots_test, __ = load_data(
    testing_path)

sentence_max_length = 16
token2id_path = 'token2id.pkl'
processed_sents = list(
    map(lambda x: preprocess_input(x, sentence_max_length), sentences))
processed_sents_test = list(
    map(lambda x: preprocess_input(x, sentence_max_length), sentences_test))
token_2_id = None
if (path.exists(token2id_path)):
    with open(token2id_path, 'rb') as file:
        token_2_id = pickle.load(file)
else:
    token_2_id = get_token_to_id_dict(processed_sents)
    with open(token2id_path, 'wb') as file:
        pickle.dump(token_2_id, file)
sent_ids = list(map(lambda sent: get_id_vector(
    sent, token_2_id), processed_sents))
sent_ids_test = list(map(lambda sent: get_id_vector(
    sent, token_2_id), processed_sents_test))

intent_model_path = 'intent.h5'
intent_model = None
if (path.exists(intent_model_path)):
    intent_model = load_model(intent_model_path)
else:
    intent_model = get_intent_model(
        sentence_max_length, len(token_2_id) + 1, len(intent_texts))

X_train = np.array(sent_ids)
y_train = np.array(intents)
X_test = np.array(sent_ids_test)
y_test = np.array(intents_test)
intent_model.compile(
    optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
intent_model.fit(X_train, y_train, epochs=20, validation_data=(X_test, y_test))
intent_model.save(intent_model_path)

slot_model_path = 'slot.h5'
slot_model = None
if (path.exists(slot_model_path)):
    slot_model = load_model(slot_model_path)
else:
    slot_model = get_slot_model(len(token_2_id) + 1, len(slot_texts))

slots = pad_sequences(slots, sentence_max_length, padding='post')
slots = get_slot_id_vector(slots, len(slot_texts))
slots_test = pad_sequences(slots_test, sentence_max_length, padding='post')
slots_test = get_slot_id_vector(slots_test, len(slot_texts))
y_train = np.array(slots)
y_test = np.array(slots_test)

selected_ids = [i for i in range(len(intents)) if intents[i] >= 4]
X_train = X_train[selected_ids]
y_train = y_train[selected_ids]
selected_ids_test = [i for i in range(len(intents_test)) if intents_test[i] >= 4]
X_test = X_test[selected_ids_test]
y_test = y_test[selected_ids_test]

slot_model.compile(
    optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
slot_model.fit(X_train, y_train, epochs=20, validation_data=(X_test, y_test))
slot_model.save(slot_model_path)