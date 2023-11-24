#!/usr/bin/env python3
"""User Role Module"""
from models.base_enum import BaseEnum


class Role(BaseEnum):
    """User Role Enum Class"""

    administrator = 'administrator'
    professional = 'professional'
    user = 'user'
