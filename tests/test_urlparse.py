import pytest

from .context import urlparse
from urlparse import Url
from requests import PreparedRequest


def test_url():
    url = Url('http://localhost:3333')
    assert url.port == 3333
    assert url.scheme == 'http'
    assert url.netloc == 'localhost'
    base = url.base_url
    assert isinstance(base, Url)
    assert base.url == url.url
    assert base == url
    assert hash(base) == hash(url)
    ep_x1 = base(path='/x')
    ep_x2 = base / 'x'
    assert ep_x1 == ep_x2
    pr = PreparedRequest()
    pr.prepare_url(ep_x1, params={'q': 'hello'})
    req_url = pr.url


def test_op_overloading():
    url = Url('http://localhost:3333')
    x = url / 'x'
    assert x.url == url.url + '/x'
    x = x & {'q': 'help'}
    print(x)


def test_class_method():
    controls = [
        'http://localhost:3000/api/v2?timeout=3000&limit=100&page=1',
        'http://localhost:3000/api/v2?timeout=3000&limit=100&page=2',
        'http://localhost:3000/api/v2?timeout=3000&limit=100&page=3',
    ]
    url = Url.as_localhost(port=3000) / 'api/v2' & dict(timeout=3000, limit=100)
    for i, control in enumerate(controls, 1):
        u = url.paramsmod(page=i)
        assert hash(u) == hash(control)


# http://localhost:3000/api/v2?timeout=3000&limit=100&page=1
# http://localhost:3000/api/v2?timeout=3000&limit=100&page=2
# http://localhost:3000/api/v2?timeout=3000&limit=100&page=3

def test_pathmod():
    url = Url.as_localhost(path='/part0/part1/part2').base_url / 'weather/radio'
    for i in range(33, 36):
        u = url.pathmod(2, f'page{i}.csv')
        print(u)


def test_immutability():
    control = Url.as_localhost()
    url = control.copy()
    d = {url: True}
    url.pathmod(0, 'new')
    url.params['messing with mutable'] = 10
    assert d[url] is True and control == url


def test_fragements():
    import requests
    url = Url(
        'https://docs.python.org',
        path='/3/library/asyncio-eventloop.html',
        fragment='asyncio.loop.run_until_complete')
    r = requests.get(url)
    assert r.status_code == 200
    assert r.url == str(url)


def test_scheme_override():
    url = Url.as_localhost_ssl(scheme='ws', port=3000)
    assert str(url) == 'ws://localhost:3000'
    url = url(port=3001)
    assert str(url) == 'ws://localhost:3001'


def test_path_validation():
    url = Url.as_localhost_ssl()
    with pytest.raises(ValueError):
        url = url(path='/This is an invalid path')


if __name__ == '__main__':
    pass
