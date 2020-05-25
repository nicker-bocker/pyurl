import pytest

from sugarurl import Url
from sugarurl.core import _UNSET, _Unset


def test_sets():
    string_urls = {'http://localhost?a=1&b=2', 'http://localhost?b=2&a=1', 'http://localhost?b=2&a=1&c=3'}
    assert len(string_urls) == 3
    urls = Url.url_set(string_urls)
    assert len(urls) == 2
    samesies = {'http://localhost?a=1&b=2&c=3', Url('http://localhost?b=2&a=1&c=3')}
    assert len(samesies) == 1


def test_urllike():
    from sugarurl.core import UrlLike
    class URL(UrlLike):
        pass

    with pytest.raises(TypeError):
        x = URL()


def test_sentinel():
    assert type(_UNSET) is _Unset
    assert str(_UNSET) == '_UNSET'
    url = Url('https://docs.python.org/3/library/re.html#module-contents') & {'a': 'b'}
    defrag_control = 'https://docs.python.org/3/library/re.html?a=b'
    depath_control = 'https://docs.python.org?a=b#module-contents'
    depath_deparam_control = 'https://docs.python.org'
    defrag = url(fragment=None)
    depath = url(path=None)
    de_all = url(path=None, fragment=None, params=None, port=None)
    assert defrag == defrag_control
    assert depath == depath_control
    assert de_all == depath_deparam_control
    defrag = url.defrag()
    depath = url.depath()
    de_all = url.depath().defrag().deport().deparam()
    assert defrag == defrag_control
    assert depath == depath_control
    assert de_all == depath_deparam_control
    defrag, _ = url.urldefrag()
    assert defrag == defrag_control


def test_canonical():
    url = Url.as_localhost(params=dict(b=2, a=1))
    assert url.sorted_params() == 'http://localhost?a=1&b=2'


def test_trailing_slash():
    url = Url.as_localhost(trailing_slash=True)
    url2 = url.copy()
    assert url2._trailing_slash is True


def test_equals():
    u1 = Url.as_localhost(port=300) & dict(a=1, b=2)
    u2 = Url.as_localhost(port=300) & dict(b=2, a=1)
    assert u1 == u2
    assert u1 != u2 & dict(a=1, b=3)

    # class FailStr:
    #     def __str__(self):
    #         raise Exception('FAIL')
    #
    # with pytest.raises(Exception):
    #     x = u1 == FailStr()


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
    assert url == 'http://user:pass@localhost'
    url = Url.as_base('https://python-patterns.guide/python/sentinel-object/#the-sentinel-object-pattern')
    assert url == 'https://python-patterns.guide'
    url = url(trailing_slash=True, path='/test')
    assert url == 'https://python-patterns.guide/test/'


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
        assert u == control


def test_modpath_urljoin():
    url = Url.as_localhost(path='/part0/part1/part2')
    template = 'http://localhost/part0/page{}/part2'
    for i in range(33, 36):
        u = url.modpath(1, f'page{i}')
        assert u == template.format(i)
    assert url.modpath(3, 'append') == 'http://localhost/part0/part1/part2/append'
    with pytest.raises(IndexError):
        x = url.modpath(5, 'x')
    x = url.urljoin(Url.as_localhost_ssl(port=3000, path='/file.txt'))
    assert x == 'https://localhost:3000/file.txt'

    u = 'https://www.setlist.fm/search?artist=23de1823&page=1&query=tour%3A%28World+Tour+%E2%80%9819%29'
    x = '/setlist/king-gizzard-and-the-lizard-wizard/2019/fort-canning-park-singapore-singapore-7b9ade18.html'
    r = 'https://www.setlist.fm/setlist/king-gizzard-and-the-lizard-wizard/2019/fort-canning-park-singapore-singapore-7b9ade18.html'
    assert Url(u) + x == r


# def test_urljoin():

def test_netloc_parser():
    url = Url.as_localhost()
    x = url._parse_netloc(*[None] * 5)
    assert x is None


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
    x = url / 'endpoint'
    assert 'page' in url.params


def test_user_pass():
    url = Url('http://user:pass@foo.com:80')
    assert url.username == 'user' and url.password == 'pass' and url.hostname == 'foo.com' and int(url.port) == 80


# def test_validation():
#     import re
#     x = 'http://user:pass@foo.com:80/path?q=help'
#     v = re.compile(r"""
#             ^(?P<scheme>[a-z]+)://
#             (?:(?P<username>\w+):(?P<password>\w+)@)?
#             (?P<hostname>[^:/]+)
#             (?::(?P<port>\d+))?
#             (?P<path>/[^\s?]+)?
#             (?:\?(?P<query>[^\s]+))?
#         """, re.VERBOSE)
#     m = v.match(x)
#     assert m


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
