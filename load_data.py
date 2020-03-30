import json
from nltk.tokenize import word_tokenize


def process_item(item, slot_to_id):
    item_text = ''
    tokenized_text = []
    item_slots = []
    for part in item:
        value = part['value'].strip().lower()
        tokens = word_tokenize(value)
        slot_type = part['slot'] if part['type'] == 'Slot' else None
        if (slot_type not in slot_to_id):
            slot_id = len(slot_to_id)
            slot_to_id[slot_type] = slot_id
        slot_id = slot_to_id[slot_type]

        item_text += ' ' + value
        for token in tokens:
            tokenized_text.append(token)
            item_slots.append(slot_id)
    item_text = item_text[1:]
    return item_text, tokenized_text, item_slots


def load_data(filepath):
    sentences = []
    tokenized_sentences = []
    intents = []
    intent_texts = []
    slot_to_id = {}
    slots = []
    slot_texts = []
    with open(filepath, encoding='utf-8') as file:
        data = json.load(file)
        intent_id = 0
        for intent in data:
            for item in data[intent]:
                item_text, tokenized_text, item_slots = process_item(item, slot_to_id)
                sentences.append(item_text)
                tokenized_sentences.append(tokenized_text)
                slots.append(item_slots)
                intents.append(intent_id)
            intent_texts.append(intent)
            intent_id += 1
    slot_texts = [None] * len(slot_to_id)
    for item in slot_to_id:
        slot_texts[slot_to_id[item]] = item
    return sentences, tokenized_sentences, intents, intent_texts, slots, slot_texts
