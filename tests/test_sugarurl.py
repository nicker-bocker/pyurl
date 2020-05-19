import pytest

from sugarurl import Url


def test_sentinel_str():
    url = Url('https://docs.python.org/3/library/re.html#module-contents')
    defrag_control = 'https://docs.python.org/3/library/re.html'
    depath_control = 'https://docs.python.org/#module-contents'
    assert url.defrag() == defrag_control
    assert url.depath() == depath_control


def test_equals():
    u1 = Url.as_localhost(port=300) & dict(a=1, b=2)
    u2 = Url.as_localhost(port=300) & dict(b=2, a=1)
    assert u1 != u2
    assert u1 == Url.as_localhost(port=300) & dict(a=1, b=2)


def test_url():
    url = Url('http://localhost:3333')
    assert url.port == 3333
    assert url.scheme == 'http'
    assert url.hostname == 'localhost'
    assert url.netloc == 'localhost:3333'
    assert url.username == None
    assert url.password == None
    base = url.base_url
    assert isinstance(base, Url)
    assert base.url == url.url
    assert base == url
    assert hash(base) == hash(url)
    ep_x1 = base(path='/x')
    ep_x2 = base / 'x'
    assert ep_x1 == ep_x2
    url = Url.as_localhost(username='user', password='pass')
    print(url)


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
        u = url.modparams(page=i)
        assert hash(u) == hash(control)


def test_pathmod():
    url = Url.as_localhost(path='/part0/part1/part2').base_url / 'weather/radio'
    for i in range(33, 36):
        u = url.modpath(2, f'page{i}.csv')
        print(u)


def test_immutability_and_hashing():
    from typing import Hashable
    control = Url.as_localhost()
    assert isinstance(control, Hashable)
    url = control.copy()
    d = {url: True}
    url.modpath(0, 'new')
    url.params['messing with mutable, but alas, this is a copy!'] = 10
    assert d[url] is True and hash(control) == hash(url)


def test_fragments():
    import requests
    url = Url(
        base_url='https://docs.python.org',
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


def test_bare_caller():
    with pytest.raises(ValueError):
        url = Url()
        x = str(url)
        print(x)


def test_params_copy_over():
    url = Url.as_localhost_ssl(port=3000) / '/api/v2' / ('ep1', 'ep2') & {'page': 1}
    print(url)
    x = url / 'endpoint'
    print(x)


def test_user_pass():
    url = Url('http://user:pass@foo.com:80')
    print(url)
    print(url.username)
    print(url.password)
    print(url.port)


def test_validation():
    import re
    x = 'http://user:pass@foo.com:80/path?q=help'
    v = re.compile(r"""
            ^(?P<scheme>[a-z]+)://
            (?:(?P<username>\w+):(?P<password>\w+)@)?
            (?P<hostname>[^:/]+)
            (?::(?P<port>\d+))?
            (?P<path>/[^\s?]+)?
            (?:\?(?P<query>[^\s]+))?
        """, re.VERBOSE)
    m = v.match(x)
    print(m.groupdict())


def test_netloc_creation():
    Url.default_scheme = 'http'
    try:
        url = Url(netloc='u:p@web.com:80')
        url_str = str(url)
    except:
        pytest.fail()
        raise
    assert url.scheme == 'http'
    assert url.username == 'u'
    assert url.password == 'p'
    assert url.hostname == 'web.com'
    assert url.port == '80'
    url = url(password='new_pass')
    assert url.username == 'u'
    assert url.password == 'new_pass'


def test_url_schemes():
    u = 'dns:example?TYPE=A;CLASS=IN'
    x = Url.parse.urlsplit(u)
    print(x)
    try:
        url = Url(u)
        str_url = str(url)
    except Exception:
        pytest.fail()
        raise

def test_construct_from_args():
    url = Url.as_localhost(username='user', password='hunter2', path='/api/v2', params=dict(q='{job="test"}'))
    print(url.query_unquote)


if __name__ == '__main__':
    pass
