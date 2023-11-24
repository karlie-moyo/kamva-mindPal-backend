#!/usr/bin/env python3
"""Defines User class"""

from typing import Dict
from models.base_model import Base, BaseModel
from sqlalchemy import (
    Column, String, Enum, Text
)
from models.user.auth import UserAuth
from .role import Role
from .status import Status


class User(BaseModel, Base, UserAuth):
    """User class"""
    __tablename__ = "users"

    firstname = Column(String(255))
    lastname = Column(String(255))
    email = Column(String(255), nullable=False, unique=True)
    image = Column(Text)

    # Enum classes
    role = Column(Enum(Role), default=Role.user, nullable=False)
    status = Column(Enum(Status), default=Status.inactive, nullable=False)

    def to_dict(self, detailed=False) -> Dict[str, str]:
        """Overrides parent's defualt"""
        obj = super().to_dict()

        # attributes from relationships and properties
        attrs = []
        for attr in attrs:
            if hasattr(self, attr):
                obj.update({attr: getattr(self, attr)})

        # sensitive attributes
        attrs = ['_password', 'reset_token']
        for attr in attrs:
            if attr in obj:
                obj.pop(attr)

        # detailed attributes
        attrs = ['created_at', 'updated_at', 'email', 'last_session']
        if detailed is not True:
            for attr in attrs:
                if attr in obj:
                    obj.pop(attr)

        # convert objects to dict
        for key, value in obj.items():
            if isinstance(value, list):
                sub_list = []
                for item in value:
                    if not hasattr(item, 'to_dict'):
                        break
                    sub_list.append(item.to_dict())
                if len(sub_list) != 0:
                    obj.update({key: sub_list})
            else:
                if hasattr(value, 'to_dict'):
                    obj.update({key: value.to_dict()})

        return obj
