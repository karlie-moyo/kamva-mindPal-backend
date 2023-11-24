#!/usr/bin/env python3
"""Basemodel Module"""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Column, String, DateTime
)
from datetime import datetime, date
from uuid import uuid4
from typing import Dict
import models

Base = declarative_base()


class BaseModel:
    """BaseModel"""
    id = Column(String(60), default=lambda: str(uuid4()), primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow,
                        nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow,
                        nullable=False)

    def save(self):
        """Create and save `obj` to storage"""
        self.updated_at = datetime.utcnow()

        # Set Index for Objects with index attribute
        if hasattr(self, 'index'):
            if getattr(self, 'index', None) is None:
                # optimize this to use mysql native count method to improve performance
                objs = list(models.storage.all(self.__class__).values())
                if len(objs) == 0:
                    setattr(self, 'index', 1)
                else:
                    sorted_objs = sorted(objs, key=lambda x: x.index)
                    setattr(self, 'index', sorted_objs[-1].index + 1)

        # Set custome serial number
        if all([
            hasattr(self, 'serial_number'),
            hasattr(self, 'Z_FILL'),
            hasattr(self, 'SN_PREFIX'),
        ]):
            self.serial_number = self.SN_PREFIX + \
                str(self.index).zfill(self.Z_FILL)

        models.storage.new(self)
        models.storage.save()

    def delete(self):
        """Delete `obj` from storgae"""
        models.storage.delete(self)
        models.storage.save()

    def to_dict(self, detailed=False) -> Dict[str, str]:
        """Returns a dictionary representation of an obj"""
        obj = {}
        obj.update(self.__dict__)

        # Format datetime objects
        for key, value in obj.items():
            if isinstance(value, datetime):
                obj.update({key: value.isoformat() + '+0000'})
            elif isinstance(value, date):
                obj.update({key: value.isoformat() + 'T00:00+0000'})

        # Held back attributes
        attrs = ['_sa_instance_state']
        for attr in attrs:
            if obj.get(attr):
                obj.pop(attr)
        return obj
