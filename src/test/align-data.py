import random
import time
import json
import csv
import requests
import os


class CoinGeckoClient:
    BASE_URL = "https://api.coingecko.com/api/v3"

    def get_token_details(self, token_id):
        time.sleep(random.uniform(30, 60))
        url = f"{self.BASE_URL}/coins/{token_id}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()

        else:
            print(f"Failed to fetch token details for {token_id}. Status code: {response.status_code}")
            return None

def read_csv(file_path):
    data = []
    with open(file_path, 'r', newline='') as csvfile:
        csv_reader = csv.DictReader(csvfile)
        for row in csv_reader:
            data.append(row)
    return data


def read_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def select_fields(data):
    return {
        'symbol': data['symbol'],
        'tweet_count': data['tweet_count'],
        'user_count': data['user_count'],
        'coin_gecko_id': data['coin_gecko_id'],
        'Marketcap': data['Marketcap'],
        'FDV': data['FDV']
    }

def get_extra_coin_gecko_data(symbol):
    details = cgClient.get_token_details(symbol['coin_gecko_id'])
    if details:
        symbol['contract_addresses'] = extract_values_from_dict_and_return_list(details.get('platforms', {}))
        symbol['contract_address'] = details.get('contract_address', None)
        symbol['ath'] = details['market_data'].get('ath', {}).get('usd', None)
        symbol['twitter_followers'] = details['community_data'].get('twitter_followers', None)
        symbol['reddit_subscribers'] = details['community_data'].get('reddit_subscribers', None)
        symbol['telegram_channel_user_count'] = details['community_data'].get('telegram_channel_user_count', None)
        symbol['homepage'] = details['links'].get('homepage', [None])[0]
        symbol['ath_percentage_change'] = details['market_data'].get('ath_change_percentage', {}).get('usd', None)
        symbol['mcap_to_tvl_ratio'] = details['market_data'].get('mcap_to_tvl_ratio', None)
        symbol['fdv_to_tvl_ratio'] = details['market_data'].get('fdv_to_tvl_ratio', None)
        symbol['ath_date'] = details.get('ath_date', {}).get('usd', None)
        symbol['name'] = details.get('name', None)
        symbol['platform'] = details.get('platform', None)
    return symbol

def save_to_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

def get_and_save_coin_gecko_data_for_symbols(symbols, start_index=0, output_filename='symbol_details.json'):
    if os.path.exists(output_filename):
        with open(output_filename) as f:
            existing_data = json.load(f)
    else:
        existing_data = []

    for i in range(start_index, len(symbols)):
        print(i)
        symbol = symbols[i]
        try:
            with open(output_filename, 'r') as file:
                existing_data = json.load(file)
                existing_symbol = [item for item in existing_data if item['symbol'] == symbol['symbol']][0]
                if existing_symbol.get('contract_address', None) is None:
                    print(f"Symbol '{symbol['symbol']}' already has extra data in '{output_filename}'. Skipping...")
                    continue
                else:
                    print(f"Fetching extra data for symbol '{symbol['symbol']}'")
                    symbol = get_extra_coin_gecko_data(symbol)
                    existing_data.append(symbol)
                    save_to_json(existing_data, output_filename)
        except Exception as e:
            print(f"Error occurred while processing symbol '{symbol['coin_gecko_id']}': {str(e)}")
            continue


def find_by_symbol(symbol, data):
    for item in data:
        if item.get('symbol', None) == symbol:
            return item
    return None


def find_by_coin_gecko_id(coin_market_id, data):
    for item in data:
        if item.get('gecko_id', None) == coin_market_id:
            return item
    return None


def find_by_name(name, data):
    for item in data:
        if item.get('name', None) == name:
            return item
    return None

def find_by_contract_address(contract_address, data):
    for item in data:
        if item.get('address', None) == contract_address:
            return item
    return None


def find_by_contract_addresses(contract_addresses, data):
    for item in data:
        if item.get('contract_addresses', None) == contract_addresses:
            return item
    return None

def extract_values_from_dict_and_return_list(data):
    return [value for key, value in data.items()]

def extract_keys_from_dict_and_return_list(data):
    return [key for key, value in data.items()]


def find_item_in_defilama(item, data):
    found_by_coin_gecko_id = find_by_coin_gecko_id(item.get('coin_gecko_id', None), data)
    if found_by_coin_gecko_id:
        print("found by coin gecko id")
        return found_by_coin_gecko_id
    found_by_contract_address = find_by_contract_address(item.get('contract_address', None), data)
    if found_by_contract_address:
        print("found by contract address")
        return found_by_contract_address
    found_by_contract_addresses = find_by_contract_addresses(item.get('contract_addresses', None), data)
    if found_by_contract_addresses:
        print("found by contract addresses")
        return found_by_contract_addresses
    found_by_name = find_by_name(item.get('name', None), data)
    if found_by_name:
        print("found by name")
        return found_by_name
    found_by_symbol = find_by_symbol(item.get('symbol', None), data)
    if found_by_symbol:
        print("found by symbol")
        return found_by_symbol
    print(f"Could not find item in defilama data: {item['symbol']}")
    return None


# cgClient = CoinGeckoClient()
symbols = read_csv('./syms.csv')
defi_llama_data = read_json('./tvl.json')
symbols_with_extra_data = read_json('./symbol_details.json')

def dedupe_array(arr, key):
    seen = set()
    deduped = []
    for item in arr:
        if item[key] not in seen:
            deduped.append(item)
            seen.add(item[key])
    return deduped

# Example usage:

deduped = dedupe_array(symbols_with_extra_data, 'symbol')

# symbols_data_parsed = [select_fields(symbol) for symbol in symbols if symbol['coin_gecko_id'] != '']
# get_and_save_coin_gecko_data_for_symbols(symbols_data_parsed, 0, 'symbol_details.json')

def join_data(manual_data, defillama_data):
    for item in manual_data:
        found = find_item_in_defilama(item, defillama_data)
        if found:
            item['tvl'] = found.get('tvl', None)
            item['listed_at'] = found.get('listedAt', None)
            item['slug'] = found.get('slug', None)
            item['cmc_id'] = found.get('cmcId', None)
            item['market_cap'] = found.get('mcap', None)
            item['twitter'] = found.get('twitter', None)
            item['chains'] = found.get('chains', None)
            item['description'] = found.get('description', None)
            item['category'] = found.get('category', None)
            item['defi_llama_id'] = found.get('id', None)
    return manual_data

joined_data = join_data(deduped, defi_llama_data)

with open('joined_data.json', 'w') as f:
    json.dump(joined_data, f, indent=4)
