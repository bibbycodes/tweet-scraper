import json
from urllib.parse import urlparse

import base58 as base58
import requests as requests

from src.utils import get_env_var, get_app_with_creds
from PyDictionary import PyDictionary
from spellchecker import SpellChecker
from better_profanity import profanity

dictionary = PyDictionary()

disallowed_words = ['BTC', 'ETH', 'SOL', '$BTC', '$ETH', '$SOL', 'SYMBOL', 'JEET', 'ATH', 'DYOR', 'CTO', 'CA', 'META', 'DCA', 'MC', 'TG', 'UI', 'CA', 'PUMP', 'APED', 'COIN', 'CRYPT', 'BRO', 'BOT', 'TBH', 'KOL', 'RAYDIUM', 'DEX']


def is_solana_public_key(key: str) -> bool:
    try:
        # Decode the Base58 encoded string
        decoded_key = base58.b58decode(key)
        # Check if the decoded key is exactly 32 bytes
        return len(decoded_key) == 32
    except Exception as e:
        # If decoding fails, it's not a valid Solana public key
        return False

def is_url(string: str) -> bool:
    try:
        result = urlparse(string)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

def is_slang(word):
    return profanity.contains_profanity(word)


def is_word_in_dictionary(word):
    spell = SpellChecker()
    return word in spell


def is_word(word):
    return is_word_in_dictionary(word) or is_slang(word)


def get_rld_app():
    rld_username = get_env_var('rld_username')
    rld_password = get_env_var('rld_password')
    return get_app_with_creds(rld_username, rld_password)


def remove_symbols_and_punctuation(text):
    return ''.join(e for e in text if e.isalnum() or e.isspace())


def get_messages(app):
    messages = app.get_inbox(cursor='100')
    return messages


def is_not_word_or_number(word):
    is_not_word = not is_word(word)
    is_not_empty = word != ''
    is_more_than_one_character = len(word) > 2
    is_not_a_number = not word.isdigit()
    return is_not_word and is_not_empty and is_more_than_one_character and is_not_a_number


def normalise_crypto_symbol(symbol):
    if symbol[0] == '$':
        return symbol[1:]
    return symbol


# app = get_rld_app()
# messages = get_messages(app)
# trenches_messages = [(message.text, message.conversation_id, message.time) for message in messages.messages if
#                      message.conversation_id == '1790408334983495951']
# individual_messages = [message[0] for message in trenches_messages]


# messages_as_string = ' '.join(individual_messages)
# print(messages_as_string)
# print(individual_messages)
# individual_words = [remove_symbols_and_punctuation(word) for message in individual_messages for word in message.split()]
# print(individual_words)
# non_english_words = [word for word in individual_words if not is_word(word)]
# print(sorted(non_english_words))

def get_response_from_ollama(message):
    url = "http://localhost:11434/api/chat"
    headers = {"Content-Type": "application/json"}
    data = {
        "model": "llama3",
        "messages": [
            {
                "role": "user",
                "content": message
            }
        ],
        "options": {
            "num_keep": 5,
            "seed": 42,
            "num_predict": 100,
            "typical_p": 0.7,
            "repeat_last_n": 33,
            "temperature": 0.8,
            "repeat_penalty": 1.2,
            "presence_penalty": 1.5,
            "frequency_penalty": 1.0,
            "mirostat": 1,
            "mirostat_tau": 0.8,
            "mirostat_eta": 0.6,
            "penalize_newline": True,
        }
    }

    response = requests.post(url, headers=headers, data=json.dumps(data), stream=True)

    if response.status_code != 200:
        raise Exception(f"Request failed with status code {response.status_code}")

    complete_message = ""
    for line in response.iter_lines():
        if line:
            try:
                decoded_line = json.loads(line.decode('utf-8'))
                if 'message' in decoded_line and 'content' in decoded_line['message']:
                    complete_message += decoded_line['message']['content']
            except json.JSONDecodeError:
                continue

    return complete_message.strip()


def get_crypto_symbol_instructions(message):
    instructions = """
Instructions:
You will be given a message below. From this message, extract any and all potential crypto ticker symbols. These symbols can appear in the forms $SYMBOL, SYMBOL, or symbol. 

Your task is to identify these potential crypto symbols and return them as a JSON array of single strings representing the found symbols. If no symbols are found, return an empty JSON array and nothing else.

Note: The text you return must be parsable as a JSON array.

Where the instructions end, the message begins. The message is enclosed between the delimiters "###". Do not include anything else in your response except for the JSON array.

Instructions end.
Message begins.
###
{}
###
Message ends.
"""
    return instructions.format(message)

def word_contains_numbers(word):
    return any(char.isdigit() for char in word)

def extract_symbols_from_text(message):
    individual_words = [word for word in message.split()]
    return [word[1:] for word in individual_words if word[0] == '$' and not word_contains_numbers(word)]

# symbols = []
# for message in individual_messages:
#     response = get_response_from_ollama(get_crypto_symbol_instructions(message))
#     try:
#         response = json.loads(response)
#         # check if response is a list
#         [symbols.append(symbol) for symbol in response if not isinstance(symbol, list) and symbol.upper() not in disallowed_words]
#         [[symbols.append(symbol) for symbol in sublist if symbol.upper() not in disallowed_words] for sublist in response if isinstance(sublist, list)]
#     except:
#         pass
#     [symbols.append(symbol) for symbol in extract_symbols_from_text(message)]
#     print(symbols)
# 
# symbols_up_cased_set = set([symbol.upper() for symbol in symbols if is_not_word_or_number(symbol)])
# normalised_symbols = [normalise_crypto_symbol(symbol) for symbol in symbols_up_cased_set if len(symbol) > 1]
# print(normalised_symbols)

