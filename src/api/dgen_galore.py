import requests

class DgenGlore:
    def __init__(self, base_url):
        """
        Initialize the API class with a base URL.
        :param base_url: Base URL of the API to which requests will be made.
        """
        self.base_url = base_url

    def get(self, path, params=None):
        """
        Send a GET request to the specified API path.
        :param path: API path as a string.
        :param params: Dictionary of URL parameters.
        :return: Response object or None if an error occurs.
        """
        try:
            response = requests.get(f"{self.base_url}{path}", params=params)
            response.raise_for_status()  # Raises stored HTTPError, if one occurred.
            return response
        except requests.RequestException as e:
            print(f"An error occurred: {e}")
            return None

    def post(self, path, data=None, json=None):
        """
        Send a POST request to the specified API path.
        :param path: API path as a string.
        :param data: Dictionary, bytes, or file-like object to send in the body of the request.
        :param json: A JSON serializable Python object to send in the body of the request.
        :return: Response object or None if an error occurs.
        """
        try:
            response = requests.post(f"{self.base_url}{path}", data=data, json=json)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            print(f"An error occurred: {e}")
            return None

    def post_mentions(self, data):
        """
        Send a POST request specifically to the /mentions endpoint.
        :param data: A JSON serializable Python object to send as the body of the request.
        :return: Response object or None if an error occurs.
        """
        return self.post("/mentions", json=data)
