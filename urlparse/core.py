import abc
import copy
import re

from typing import Any
from typing import Dict
from typing import Union
from urllib import parse


class UrlLike(abc.ABC):
    @abc.abstractmethod
    def __str__(self):
        pass


class Url(UrlLike):
    # TODO methods from ulrlib parse
    # TODO Pathib like poverloaded operators
    # TODO add docstrings

    _re_path_validator = re.compile(r'^(/\S+)+$')

    @classmethod
    def as_localhost(cls, **kwargs):
        return cls('http://localhost', **kwargs)

    @classmethod
    def as_localhost_ssl(cls, **kwargs):
        return cls('https://localhost', **kwargs)

    @classmethod
    def as_base(cls, url, **kwargs):
        return cls(url).base_url(**kwargs)

    def __init__(self,
                 base_url: Union[UrlLike, str] = None, *,
                 scheme: str = None,
                 netloc: str = None,
                 path: str = None,
                 params: Dict[str, Any] = None,
                 port: Union[int, str] = None,
                 fragment: str = None,
                 trailing_slash: bool = False,
                 **kwargs
                 ):

        split = {}
        if base_url:
            if isinstance(base_url, str):
                split = parse.urlsplit(base_url, allow_fragments=True)._asdict()
            elif isinstance(base_url, UrlLike):
                split = {k[1:]: v for k, v in vars(base_url).items()}
                # trailing_slash = vars(base_url).get('_trailing_slash', trailing_slash)
        self._path = path or split.get('path') or ''
        self._params = params or dict(parse.parse_qsl(split.get('query') or ''))
        self._scheme = scheme or split.get('scheme')
        self._netloc = netloc or split.get('netloc')
        self._port = port or split.get('port')
        self._fragment = fragment or split.get('fragment')
        self._trailing_slash = trailing_slash or split.get('trailing_slash')

        if not self._netloc:
            raise ValueError(f'"{base_url}" is not a valid url')
        if self._path:
            if not self._path.startswith('/'):
                self._path = f"/{path}"
            if trailing_slash and not path.endswith('/'):
                self._path = f"{path}/"
            if not self._re_path_validator.match(self._path):
                raise ValueError('Invalid url path')
        if ':' in self._netloc:
            self._netloc, _, self._port = self._netloc.partition(':')
        if self._port:
            try:
                self._port = int(self._port)
            except ValueError:
                raise ValueError(f'{self._port} is an invalid port')

    def __str__(self):
        url_string = parse.urlunsplit((self.scheme, self.netloc_port, self.path, self.query, self.fragment))
        return url_string

    def __call__(self, **kwargs) -> 'Url':
        new_url = Url(self, **kwargs)
        return new_url

    def __hash__(self):
        try:
            return self._hash
        except AttributeError:
            self._hash = hash(self.url)
            return self._hash

    def __eq__(self, other):
        try:
            return self.url == other.url
        except Exception:
            return False

    def __and__(self, other):
        new_url = Url(self, params=other)
        return new_url

    def __truediv__(self, other):
        if not isinstance(other, str):
            raise NotImplementedError('Only strings can be used with overloaded truediv operator')
        new_url = Url(self, path=other)
        return new_url

    @property
    def scheme(self) -> str:
        return self._scheme

    @property
    def netloc(self) -> str:
        return self._netloc

    @property
    def params(self) -> dict:
        return self._params.copy()


    @property
    def port(self) -> int:
        return self._port

    @property
    def path(self) -> str:
        return self._path

    @property
    def fragment(self):
        return self._fragment

    @property
    def base_url(self):
        try:
            return self._base_url
        except AttributeError:
            self._base_url = Url(scheme=self.scheme, netloc=self.netloc, port=self.port)
            return self._base_url

    @property
    def netloc_port(self) -> str:
        if self.port is None:
            return self.netloc
        return f"{self.netloc}:{self.port}"

    @property
    def query(self) -> str:
        return parse.urlencode(self.params)

    @property
    def query_unquote(self) -> str:
        return parse.unquote(self.query)

    @property
    def url(self) -> str:
        return str(self)

    def copy(self) -> 'Url':
        return copy.copy(self)

    def urlsplit(self) -> parse.SplitResult:
        return parse.urlsplit(self.url)


    def paramsmod(self, __dict=None, /, **params):
        __dict = __dict or {}
        new_url = Url(self, params={**self.params, **__dict, **params})
        return new_url

    def pathmod(self, index, value):
        old_path = self.path
        parts = [p for p in old_path.split('/') if p]
        if index < 0 or index > len(parts):
            raise ValueError(f'{index} is out of range')
        if index == len(parts):
            parts = parts + [str(value)]
        else:
            parts[index] = str(value)
        new_path = f"/{'/'.join(parts)}{'/' if self._trailing_slash else ''}"
        new_url = Url(self, path=new_path)
        return new_url

    def geturl(self):
        return self.url

    def parse_qsl(self):
        return self.params

    def urljoin(self, url, allow_fragments=True):
        new_url = Url(parse.urljoin(self.url, url, allow_fragments))
        return new_url

    def urldefrag(self):
        #TODO imp
        pass

