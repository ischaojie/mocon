# -*- coding: utf-8 -*-


class MoconException(Exception):
    pass


class InvalidModelException(MoconException):
    pass


class InvalidKeyException(MoconException):
    pass


class PrimaryKeyNotFound(MoconException):
    pass


class PrimaryKeyDuplicated(MoconException):
    pass


class NoSourceError(MoconException):
    pass


class NotSupportedSource(MoconException):
    pass
