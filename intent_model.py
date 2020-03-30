from keras.models import Model
from keras.layers import Input, Conv1D, GlobalMaxPool1D, Dense, Dropout


def get_intent_model(max_len, vocab_size, intent_cnt):
    input_layer = Input(shape=(max_len, vocab_size))
    a1 = Conv1D(
        filters=32,
        kernel_size=3,
        activation='relu')(input_layer)
    a2 = GlobalMaxPool1D()(a1)
    a3 = Dense(256, activation='relu')(a2)
    a4 = Dropout(0.2)(a3)
    a5 = Dense(256, activation='relu')(a4)
    a6 = Dropout(0.2)(a5)
    output_layer = Dense(intent_cnt, activation='softmax')(a6)
    return Model(inputs=input_layer, outputs=output_layer)
