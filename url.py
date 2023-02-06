import requests
from urllib.parse import urlparse
from dataclasses import dataclass

@dataclass
class Url:
    url: str
    is_running: bool = False
    status_code: int = 0

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
        req = requests.get(self.url)
        self.status_code = req.status_code
        return req.status_code in [200]

    def update(self):
        self.is_running = self.check_url()

if __name__ == '__main__':
    print(Url('http://www.google.com'))