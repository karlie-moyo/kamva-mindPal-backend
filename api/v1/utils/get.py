#!/usr/bin/env python3
"""Extracts attributes from a dictionary based what is important"""
from typing import Dict


def attrs(
        attrs: list = [], required: list = [],
        nullable: list = [], silent: bool = False, **kwargs
) -> Dict[str, str]:
    data = {}
    for attr in attrs:
        if attr in kwargs:
            data.update({attr: kwargs.get(attr)})
        elif attr in required:
            raise ValueError("Missing required data: " + attr)
        elif attr not in nullable and silent is not True:
            raise ValueError("Missing required data: " + attr)
    return data
