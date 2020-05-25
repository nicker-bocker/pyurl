import pytest

from sugarurl import Url

import requests

def test_local():
    url = Url.as_localhost_ssl(port=8443) / 'hello-world' & {'a': 1}
    headers = {
        'host'            : 'localhost:8443',
        'user-agent'    : 'curl/7.69.1',
        'accept'          : '*/*',
        'arbitrary'       : 'Header',
        'content-length': '7',
        'content-type'  : 'application/x-www-form-urlencoded'
    }
    print(url)
    r = requests.put(url, headers=headers)
    print(r.status_code)