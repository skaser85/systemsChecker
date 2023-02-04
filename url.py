import requests
from urllib.parse import urlparse

min_attributes = ('scheme', 'netloc')

def is_valid(url, qualifying=min_attributes):
    tokens = urlparse(url)
    return all([getattr(tokens, qualifying_attr)
                for qualifying_attr in qualifying])

def check_url(url: str) -> str:
    if not is_valid(url):
        raise ValueError(f'Invalid URL: {url}')
    try:
        #Get Url
        get = requests.get(url)
        # if the request succeeds 
        if get.status_code in [200]:
            return(f"{url}: is reachable")
        else:
            return(f"{url}: is Not reachable, status_code: {get.status_code}")
    #Exception
    except requests.exceptions.RequestException as e:
        # print URL with Errs
        raise SystemExit(f"{url}: is Not reachable \nErr: {e}")

if __name__ == '__main__':
    print(check_url('http://www.google.com'))