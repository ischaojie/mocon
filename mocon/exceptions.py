# -*- coding: utf-8 -*-


class MoconException(Exception):
    pass


class InvalidModelException(MoconException):
    pass


class InvalidKeyException(MoconException):
    pass
