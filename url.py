import requests
from urllib.parse import urlparse
from dataclasses import dataclass

@dataclass
class Url:
    url: str
    is_running: bool = False

    def __post_init__(self):
        if not self.is_valid():
            raise TypeError(f'Invalid URL: {self.url}')
        self.update()

    def is_valid(self):
        min_attributes = ('scheme', 'netloc')
        tokens = urlparse(self.url)
        return all([getattr(tokens, qualifying_attr)
                    for qualifying_attr in min_attributes])

    def check_url(self) -> bool:
        try:
            #Get Url
            get = requests.get(self.url)
            # if the request succeeds 
            return get.status_code in [200]
        #Exception
        except requests.exceptions.RequestException as e:
            # print URL with Errs
            raise SystemExit(f"{self.url}: is Not reachable \nErr: {e}")

    def update(self):
        self.is_running = self.check_url()

if __name__ == '__main__':
    print(Url('http://www.google.com'))