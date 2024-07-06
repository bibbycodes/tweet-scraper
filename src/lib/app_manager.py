from src.utils import get_env_var, get_app_with_creds
from time import sleep


class AppManager:
    def __init__(self, initialise=False):
        if initialise:
            self.apps = self.initialise_apps()
        else:
            self.apps = []
        self.current_index = 0
        self.keys = ['a', 'b', 'c', 'd']

    def get_next(self):
        if not self.apps:
            raise ValueError("The array is empty.")

        item = self.apps[self.current_index]
        print(f"Using current index: {self.current_index}")
        self.current_index = (self.current_index + 1) % len(self.apps)
        return item

    def initialise_user(self, key):
        username = get_env_var(f"username_{key}")
        password = get_env_var(f"password_{key}")
        return get_app_with_creds(username, password)

    def initialise_apps(self):
        apps = []
        for key in self.keys:
            print(f"Logging into {get_env_var(f'username_{key}')}")
            user = self.initialise_user(key)
            apps.append(user)
            sleep(15)
        self.apps = apps
        return apps
    
    def get_apps(self):
        return self.apps
