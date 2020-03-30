import requests
import discord
import io
import aiohttp

GREETINGS = [
    'Hello there!',
    'How can I help you?',
    'Beep boop?',
    'It\'s a pleasure to meet you!',
    'Hi there!'
]

BYES = [
    'Farewell',
    'Hope to see you soon!',
    'When you need help, don\'t hesitate to ask!',
    'I will miss you!',
    'Take care!',
]

CONFUSED = [
    'Huh?',
    'I don\'t get it...',
    'What were you saying again?',
    'I have a lot of answer, but not to that question.'
    'Beep boop, boop beep?'
]

NO_RESULT = [
    'That question is 404-ed. Please try another one.',
    'Hmmm, weird, I cannot find anything about that',
    'The database returned empty, but maybe another question would work?'
]

CONFIRMED = [
    'Okay then'
]

__properties__synonyms__ = [
    ('P22', ['father', 'dad']),
    ('P25', ['mother', 'mom']),
    ('P569', ['date of birth', 'DOB', 'birth date', 'birth year',
              'birthdate', 'birthyear', 'year of birth', 'birthday']),
    ('P570', ['date of death', 'DOD', 'death', 'dead', 'death date',
              'died on', 'year of death', 'date of the end', 'deathdate']),
    ('P50', ['author', 'writer', 'creator', 'written by',
             'authors', 'by', 'writers', 'authors', 'writers']),
    ('P57', ['director', 'film director', 'movie director', 'directed by']),
    ('P61', ['discoverer', 'inventor', 'coined', 'inventor', 'developer',
             'created by', 'developer of', 'discoverer', 'first described']),
    ('P580', ['start time', 'introduction', 'from', 'began', 'beginning', 'building date', 'from date',
              'from time', 'introduced', 'since', 'start date', 'started in', 'starting', 'starttime']),
    ('P582', ['end time', 'to', 'ending', 'cease date', 'cease operation', 'cease time', 'closed', 'completed in', 'dissolved',
              'divorced', 'end date', 'enddate', 'ends', 'endtime', 'fall date', 'left office', 'stop time', 'till', 'until']),
    ('P17', ['country', 'host country', 'land', 'state']),
    ('P21', ['sex', 'gender', 'gender identity',
             'gender expression', 'biological sex']),
    ('P106', ['occupation', 'profession', 'job',
              'work', 'career', 'employment', 'craft']),
    ('P27', ['country of citizenship', 'citizenship',
             'nationality', 'citizen of', 'national of']),
    ('P19', ['place of birth', 'birthplace', 'born in', 'POB', 'birth place',
             'location born', 'born at', 'birth location', 'location of birth', 'birth city']),
    ('P421', ['located in time zone', 'timezone', 'time zone', 'time', 'TZ']),
    ('P276', ['location', 'moveable object location', 'located in', 'event location', 'venue', 'is in',
              'location of item', 'place held', 'based in', 'neighborhood', 'region', 'in', 'located']),
    ('P495', ['country of origin', 'place of origin',
              'comes from', 'CoO', 'originates from', 'origin']),
    ('P136', ['genre', 'music genre', 'film genre', 'artistic genre', 'literary genre',
              'kind of music', 'type of film', 'genre of music', 'type of music']),
    ('P112', ['founded by', 'founder', 'co-founder',
              'co-founded by', 'established by', 'founders'])
]


def find_best_property_id(phrase):
    best_p_id = None
    for (p_id, p_vectors) in __properties__synonyms__:
        for v in p_vectors:
            if (phrase == v):
                return p_id
    return None


def get_wikidata_entity_id(title):
    try:
        result = requests.get('https://en.wikipedia.org/w/api.php', params={
            'action': 'query',
            'prop': 'pageprops',
            'ppprop': 'wikibase_item',
            'redirects': 1,
            'titles': title,
            'format': 'json'
        }).json()
        for item in result['query']['pages']:
            pagedata = result['query']['pages'][item]
            if ('pageprops' in pagedata and 'wikibase_item' in pagedata['pageprops']):
                return pagedata['pageprops']['wikibase_item']
        return None
    except RuntimeError as e:
        return None


async def send_image(channel, image_url, image_name):
    async with aiohttp.ClientSession() as session:
        async with session.get(image_url) as resp:
            if resp.status != 200:
                return
            data = io.BytesIO(await resp.read())
            await channel.send(file=discord.File(data, image_name))
