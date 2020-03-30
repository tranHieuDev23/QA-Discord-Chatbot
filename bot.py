import discord
import os
from dotenv import load_dotenv
from preprocess import preprocess_input
from predict_intent import guess_intent
from predict_slot import guess_slot
import wikipedia
import random
from bot_data import GREETINGS, BYES, CONFIRMED, CONFUSED, NO_RESULT, find_best_property_id, get_wikidata_entity_id, send_image
from wikidata.client import Client

client = discord.Client()
wdata = Client()


@client.event
async def on_ready():
    print('Bot is ready!')


async def get_response(message):
    content = message.content
    tokenized_content = preprocess_input(content, 16)
    if (len(tokenized_content) > 16):
        await message.channel.send(random.choice(CONFUSED))
        return
    intent = guess_intent(message.content)
    if (intent == 'greet'):
        await message.channel.send(random.choice(GREETINGS))
        return
    if (intent == 'bye'):
        await message.channel.send(random.choice(BYES))
        return
    if (intent == 'affirmative' or intent == 'negative'):
        await message.channel.send(random.choice(CONFUSED))
        return
    slots = guess_slot(message.content)
    if (intent == 'definitionQuestion'):
        if (len(slots) != 1):
            await message.channel.send(random.choice(CONFUSED))
            return
        (subject, _) = slots[0]
        await answer_definition_question(message, subject)
    if (intent == 'propertyQuestion'):
        if (len(slots) != 2):
            await message.channel.send(random.choice(CONFUSED))
            return
        (subject, t1) = slots[0]
        (prop, t2) = slots[1]
        if (t1 == 'property'):
            subject, prop = prop, subject
        await answer_property_question(message, subject, prop)


def __get_better_url__(url1, url2):
    if (url1.endswith('.svg') or url2.endswith('.svg')):
        return url1 if url2.endswith('.svg') else url2
    if (url2.endswith('.png') or url2.endswith('.png')):
        return url1 if url2.endswith('.png') else url2
    return url1


def __get_best_url__(urls):
    result = urls[0]
    for item in urls[1:]:
        if (result.endswith('.svg') and not item.endswith('.svg')):
            result = __get_better_url__(result, item)
    return result


async def answer_definition_question(message, subject):
    channel = message.channel
    author = message.author
    try:
        answer = wikipedia.summary(subject, sentences=2)
        await channel.send(answer)

        answer_page = wikipedia.page(subject)
        if (len(answer_page.images) > 0):
            selected_url = __get_best_url__(answer_page.images)
            dot_id = selected_url.rfind('.')
            extension = selected_url[dot_id:]
            await send_image(channel, selected_url, subject + extension)
        return
    except wikipedia.exceptions.PageError as e:
        await channel.send(random.choice(NO_RESULT))
        return
    except wikipedia.exceptions.DisambiguationError as e:
        selection_message = 'The thing you are asking for may mean one of these things:\n'
        for i in range(min(len(e.options), 5)):
            selection_message += str(i + 1) + ') ' + e.options[i] + '\n'
        selection_message += 'Please send the number of the option you want to ask, or text me "Cancel" to cancel the request.'
        await channel.send(selection_message)

        def checker(new_message):
            if (new_message.author != author):
                return False
            try:
                value = int(new_message.content)
                if (1 <= value and value <= len(e.options)):
                    return True
                return False
            except ValueError:
                return new_message.content.strip().lower() == 'cancel'

        new_message = await client.wait_for('message', check=checker)
        if (new_message.content == 'cancel'):
            await channel.send(random.choice(CONFIRMED))
            return
        option_id = int(new_message.content)
        await answer_definition_question(message, e.options[option_id])


async def answer_property_question(message, subject, prop):
    channel = message.channel
    author = message.author
    try:
        answer_titles = wikipedia.search(subject)
        if (len(answer_titles) == 0):
            await channel.send(random.choice(NO_RESULT))
            return
        title = answer_titles[0]
        entity_id = get_wikidata_entity_id(title)
        if (entity_id == None):
            await channel.send(random.choice(NO_RESULT))
            return
        entity = wdata.get(entity_id, load=True)
        property_id = find_best_property_id(prop)
        prop_obj = wdata.get(property_id)
        try:
            answer = entity[prop_obj]
            await channel.send(answer.label)
        except:
            await channel.send(random.choice(NO_RESULT))
        return
    except wikipedia.exceptions.PageError as e:
        await channel.send(random.choice(NO_RESULT))
        return
    except wikipedia.exceptions.DisambiguationError as e:
        selection_message = 'The thing you are asking for may mean one of these things:\n'
        for i in range(len(e.options)):
            selection_message += str(i + 1) + ') ' + e.options[i] + '\n'
        selection_message += 'Please send the number of the option you want to ask, or text me "Cancel" to cancel the request.'
        await channel.send(selection_message)

        def checker(new_message):
            if (new_message.author != author):
                return False
            try:
                value = int(new_message.content)
                if (1 <= value and value <= len(e.options)):
                    return True
                return False
            except ValueError:
                return new_message.content.strip().lower() == 'cancel'

        new_message = await client.wait_for('message', check=checker)
        if (new_message.content == 'cancel'):
            await channel.send(random.choice(CONFIRMED))
            return
        option_id = int(new_message.content)
        await answer_property_question(message, e.options[option_id], prop)


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    await get_response(message)

load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
client.run(DISCORD_TOKEN)
