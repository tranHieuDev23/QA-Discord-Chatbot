from keras.models import Model
from keras.layers import Input, GRU, Bidirectional, Dense, Dropout, TimeDistributed


def get_slot_model(vocab_size, slot_type_cnt):
    input_layer = Input(shape=(None, vocab_size))
    a1 = Bidirectional(GRU(128, return_sequences=True))(input_layer)
    a2 = Bidirectional(GRU(128, return_sequences=True))(a1)
    a3 = Bidirectional(GRU(128, return_sequences=True))(a2)
    a4 = TimeDistributed(Dense(128, activation='relu'))(a3)
    a5 = TimeDistributed(Dropout(0.2))(a4)
    output_layer = TimeDistributed(
        Dense(slot_type_cnt, activation='softmax'))(a5)
    return Model(inputs=input_layer, outputs=output_layer)
