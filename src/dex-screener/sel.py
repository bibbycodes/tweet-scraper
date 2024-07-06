import json
import random
import time

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.proxy import Proxy, ProxyType


def generate_token_url(pair_address):
    return f'{base_url}/solana/{pair_address}'


headers = {
    'authority': 'dexscreener.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'accept-language': 'en-GB,en;q=0.8',
    'cache-control': 'max-age=0',
    'cookie': '__cuid=9cc5a4b0dc3341eaadeb982446323c24; amp_fef1e8=4563a7db-f1e3-4a9a-856e-895b9c5a3665R...1hljirmqs.1hljiu02l.a.2.c; chakra-ui-color-mode=dark; cf_clearance=0EuAmKxWiaAQfijqBszxwEfTFinCZ6vYE1nqjJwdpNE-1706892355-1-Ab0tfKS+ZZjMx8XnSSnMuOdkLRp+x6Ti795Q2wox3XyIfKeSqbyxN2ECpT4W8fRkzvQIOPo2xLRZ06WEq1Haf1A=; __cf_bm=Sstj3_IrNhqopyVPgkbbsx_V_7EKK0BMd0DGJJ8CYEs-1706899204-1-AR/5PRvE+qvWvjc3TZG79Lwq97TkVhj/NI2fWRl0cijo3V8WffbhM6fVapk/h280OGmBV4pUt4o3so/hXcQMTC4flyCCHJ/9vWb6yt94KMNn',
    'referer': 'dexscreener.com',
    'sec-ch-ua': '"Not A(Brand";v="99", "Brave";v="121", "Chromium";v="121"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-model': '""',
    'sec-ch-ua-platform': 'macOS',
    'sec-ch-ua-platform-version': '13.6.2',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'sec-gpc': '1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
}

base_url = 'https://dexscreener.com'
new_pairs_url = base_url + '/new-pairs?rankBy=pairAge&order=asc&maxAge=1'

def get_new_pairs_links(html_data):
    soup = BeautifulSoup(html_data, 'html.parser')
    elements = soup.find_all('a', class_='ds-dex-table-row ds-dex-table-row-new')
    hrefs = [base_url + element['href'] for element in elements]
    return hrefs


def get_token_details(token_page_soup):
    elements = token_page_soup.find_all('div', class_='chakra-stack custom-i33gp9')
    result = {}
    for element in elements:
        text = element.find('span', class_='chakra-text custom-72rvq0').text
        href = element.find('a', title="Open in block explorer")['href']
        token_address = href.split('/')[-1]
        result[text] = token_address
    return result

def get_time_created(token_page_soup):
    elements = token_page_soup.find_all('span', class_='chakra-text custom-2ygcmq')
    for element in elements:
        if 'ago' in element.text:
            return element.text
    return None

def get_social_links(token_page_soup):
    result = {}
    div_element = token_page_soup.find('div', class_='chakra-wrap custom-1art13b')
    if div_element:
        links = div_element.find_all('a')
        for link in links:
            link_text = link.text
            href = link.get('href')
            result[link_text] = href
    return result

def scrape_and_update():
    print("Scraping and updating...")
    print(new_pairs_url)
    new_links_page = requests.get(new_pairs_url, headers=headers)
    print(new_links_page.text)
    new_pairs_links = get_new_pairs_links(new_links_page.text)
    print(new_pairs_links)
    time.sleep(random.randint(3, 6))

    for link in new_pairs_links:
        pair_address = link.split('/')[-1]
        token_url = generate_token_url(pair_address)
        headers['referer'] = new_pairs_url

        # Check if 'token.json' file exists, and if not, create it with an empty JSON object
        try:
            with open('token.json', 'r') as file:
                data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {}

        # Your code to make requests and update the JSON data goes here
        options = ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-software-rasterizer")
        options.add_argument("--disable-features=VizDisplayCompositor")
        options.add_argument("--disable-features=VizDisplayCompositorAnimatedImageDecode")
        options.add_argument("--disable-features=VizDisplayCompositorSurfaceSynchronization")


        service = ChromeService("chromedriver_path")  # Replace with the path to your chromedriver
        driver = webdriver.Chrome(service=service, options=options)

        driver.get(link)
        time.sleep(random.randint(1, 6))

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        token_details = get_token_details(soup)
        time_created = get_time_created(soup)
        social_links = {}

        try:
            social_links = get_social_links(soup)
            print(social_links, token_url, time_created)
        except AttributeError:
            data[pair_address] = {
                'token_details': token_details,
                'social_links': social_links
            }

        # Save the updated JSON data back to 'token.json'
        with open('token.json', 'w') as file:
            json.dump(data, file)

        driver.quit()

while True:
    scrape_and_update()
    print("Having a little snooze...")
    time.sleep(random.randint(100, 300))
