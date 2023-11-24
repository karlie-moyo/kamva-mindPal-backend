#!/usr/bin/env python3
"""User Status Module"""
from models.base_enum import BaseEnum


class Status(BaseEnum):
    """User Status Enum Class"""

    active = 'active'
    inactive = 'inactive'
    suspended = 'suspended'
    banned = 'banned'
