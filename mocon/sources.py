# -*- coding: utf-8 -*-
from typing import Any, Union, Optional
from urllib.parse import SplitResult, urlsplit, unquote, parse_qsl

from pymongo import MongoClient as Mongo
from redis import Redis

from mocon.exceptions import NotSupportedSource


class Backend:
    def get(self, key: str) -> Any:
        raise NotImplementedError

    def set(self, key: str, value: Any) -> bool:
        raise NotImplementedError

    def delete(self, key: str) -> bool:
        raise NotImplementedError


class RedisBackend(Backend):
    def __init__(self, url: Union[str, "SourceURL"], **options: Any) -> None:
        self._url = SourceURL(url)
        self._options = options

    def connection(self) -> "Redis":
        client = Redis(
            host=self._url.hostname,
            port=self._url.port,
            db=int(self._url.database),
            password=self._url.password,
            **self._options,
        )
        return client

    def get(self, key: str) -> Any:
        return self.connection().get(key)

    def set(self, key: str, value: Any) -> bool:
        return self.connection().set(key, value)

    def delete(self, key: str) -> bool:
        pass


class MongoBackend(Backend):
    pass


class Source:
    SUPPORTED_SOURCE = {
        "redis": RedisBackend,
        "mongodb": MongoBackend,
    }

    def __init__(self, url: Union[str, "SourceURL"], **options):
        self.url = SourceURL(url)
        self.options = options
        self._backend = self.switch_source()

    def switch_source(self):
        Client = self.SUPPORTED_SOURCE.get(self.url.dialect)
        if not Client:
            raise NotSupportedSource(f"{self.url.dialect} is not supported")
        return Client(self.url, **self.options)

    def get(self, key: str) -> Any:
        return self._backend.get(key)

    def set(self, key: str, value: Any) -> bool:
        return self._backend.set(key, value)

    def delete(self, key: str) -> bool:
        return self._backend.delete(key)


def _EmptyNetloc():
    def __bool__(self) -> bool:
        return True


class SourceURL:
    def __init__(self, url: Union[str, "SourceURL"]):
        if isinstance(url, SourceURL):
            self._url: str = url._url
        elif isinstance(url, str):
            self._url = url
        else:
            raise TypeError(
                f"Invalid type for DatabaseURL. Expected str or DatabaseURL, got {type(url)}"
            )

    @property
    def components(self) -> SplitResult:
        if not hasattr(self, "_components"):
            self._components = urlsplit(self._url)
        return self._components

    @property
    def scheme(self) -> str:
        return self.components.scheme

    @property
    def dialect(self) -> str:
        return self.components.scheme.split("+")[0]

    @property
    def driver(self) -> str:
        if "+" not in self.components.scheme:
            return ""
        return self.components.scheme.split("+", 1)[1]

    @property
    def userinfo(self) -> Optional[bytes]:
        if self.components.username:
            info = self.components.username
            if self.components.password:
                info += ":" + self.components.password
            return info.encode("utf-8")
        return None

    @property
    def username(self) -> Optional[str]:
        if self.components.username is None:
            return None
        return unquote(self.components.username)

    @property
    def password(self) -> Optional[str]:
        if self.components.password is None:
            return None
        return unquote(self.components.password)

    @property
    def hostname(self) -> Optional[str]:
        return (
            self.components.hostname
            or self.options.get("host")
            or self.options.get("unix_sock")
        )

    @property
    def port(self) -> Optional[int]:
        return self.components.port

    @property
    def netloc(self) -> Optional[str]:
        return self.components.netloc

    @property
    def database(self) -> str:
        path = self.components.path
        if path.startswith("/"):
            path = path[1:]
        return unquote(path)

    @property
    def options(self) -> dict:
        if not hasattr(self, "_options"):
            self._options = dict(parse_qsl(self.components.query))
        return self._options

    def replace(self, **kwargs: Any) -> "SourceURL":
        if (
            "username" in kwargs
            or "password" in kwargs
            or "hostname" in kwargs
            or "port" in kwargs
        ):
            hostname = kwargs.pop("hostname", self.hostname)
            port = kwargs.pop("port", self.port)
            username = kwargs.pop("username", self.components.username)
            password = kwargs.pop("password", self.components.password)

            netloc = hostname
            if port is not None:
                netloc += f":{port}"
            if username is not None:
                userpass = username
                if password is not None:
                    userpass += f":{password}"
                netloc = f"{userpass}@{netloc}"

            kwargs["netloc"] = netloc

        if "database" in kwargs:
            kwargs["path"] = "/" + kwargs.pop("database")

        if "dialect" in kwargs or "driver" in kwargs:
            dialect = kwargs.pop("dialect", self.dialect)
            driver = kwargs.pop("driver", self.driver)
            kwargs["scheme"] = f"{dialect}+{driver}" if driver else dialect

        if not kwargs.get("netloc", self.netloc):
            # Using an empty string that evaluates as True means we end up
            # with URLs like `sqlite:///database` instead of `sqlite:/database`
            kwargs["netloc"] = _EmptyNetloc()

        components = self.components._replace(**kwargs)
        return self.__class__(components.geturl())

    @property
    def obscure_password(self) -> str:
        if self.password:
            return self.replace(password="********")._url
        return self._url

    def __str__(self) -> str:
        return self._url

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({repr(self.obscure_password)})"

    def __eq__(self, other: Any) -> bool:
        return str(self) == str(other)
