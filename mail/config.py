#!/usr/bin/env python3
"""SMTP Configurations module"""

from typing import Dict


class SMTPConfig():
    """SMTP Configurations"""

    def __init__(self, username, password, server, port=587,
                 rate=50, alias=None):
        """Initializes SMTPConfig"""
        self.username = username
        self.password = password
        self.server = server
        self.port = port
        self.rate = rate
        self.alias = alias

    def to_dict(self, detailed=False) -> Dict[str, str]:
        """Overrides parent's defualt"""
        obj = self.__dict__

        if detailed is True:
            obj.update({'password': self.password})
            return obj

        return obj

    def to_json_serializable(self):
        return self.to_dict(detailed=True)

    @classmethod
    def from_json_serializable(cls, data):
        return cls(**data)
