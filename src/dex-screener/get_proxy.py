import requests


def make_request_with_proxy(url, headers = {}):
    response = requests.get(
        url='https://proxy.scrapeops.io/v1/',
        params={
            'api_key': 'ee6a03f0-b361-450c-b38f-c861c198624d',
            'url': url,
            'residential': 'true',
            'country': 'us',
        },
        headers=headers
    )
    return response
