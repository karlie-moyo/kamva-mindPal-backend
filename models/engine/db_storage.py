#!/usr/bin/env python3
"""SQLAlchemy Storage Engine"""
from sqlalchemy import extract
from typing import List
from datetime import datetime
from math import ceil
from typing import Dict, Callable
from models.user import User
from models.base_model import Base
from sqlalchemy import create_engine, func, and_
from sqlalchemy.orm import scoped_session, sessionmaker
from os import getenv
from dotenv import load_dotenv
import uuid

load_dotenv()

PAGINATION = int(getenv('PAGINATION', 25))


# grouping of models' classes
classes = [
    User
]
DB_USER = getenv('DB_USER')
DB_PWD = getenv('DB_PWD')
DB_HOST = getenv('DB_HOST')
DB_NAME = getenv('DB_NAME')
DB_ENGINE = getenv('DB_ENGINE')

# check if the running instance is a test environment
TEST = getenv('TEST')
if TEST == 'True':
    DB_ENGINE = 'sqlite'
    DB_NAME = 'tests'

# create database connection
engine = None
if DB_ENGINE == 'mysql':
    engine = create_engine(
        'mysql+mysqldb://{}:{}@{}/{}'.format(
            DB_USER, DB_PWD, DB_HOST, DB_NAME
        ),
        # pool_pre_ping=True,
        pool_recycle=3600
    )
else:
    engine = create_engine(
        'sqlite:///{}.sqlite'.format(DB_NAME),
        pool_pre_ping=True
    )


class DBStorage:
    """DBStorage class"""
    __engine = None
    __session = None

    def __init__(self):
        """DBStorage class constructor"""
        self.__engine = engine

    def reload(self):
        """(Re)load data from MySQL database"""
        Base.metadata.create_all(self.__engine)
        factory = sessionmaker(bind=self.__engine, expire_on_commit=False)
        self.__session = scoped_session(factory)

    def new(self, obj):
        """Add `obj` to the current database session"""
        self.__session.add(obj)

    def save(self):
        """Save/commit all changes of the current db session"""
        self.__session.commit()

    def delete(self, obj=None):
        """delete `obj` from database"""
        if obj is not None:
            self.__session.delete(obj)

    def rollback(self):
        """rolls back the current Sqlalchemy session
        after a failed flush occured
        just for testing purposes"""
        self.__session.rollback()

    def all(self, cls=None):
        """
        query-> SELECT * FROM cls.__tablename__
        [Returns a dictionary (key:obj) object for easy indexing]
        """
        objs_dict = {}
        if cls is None:
            for item in classes:
                objs = self.__session.query(item).all()
                for obj in objs:
                    key = obj.__class__.__name__ + '.' + obj.id
                    objs_dict[key] = obj
        else:
            objs = self.__session.query(cls).all()
            for obj in objs:
                key = obj.__class__.__name__ + '.' + obj.id
                objs_dict[key] = obj

        return objs_dict

    def close(self):
        """close the current db session"""
        self.__session.remove()

    def get(self, cls, id=None, attr=None):
        """
        Returns a `obj` of `cls` with a matching `id`,
        or None if not exists.
        """
        # checks if id is None
        if id is None:
            return None

        # gracefully handles uuid for id
        if isinstance(id, uuid.UUID):
            id = str(id)

        if cls not in classes:
            return None
        if attr is not None:
            obj = self.all(cls).get(cls.__name__ + '.' + id, None)
            if obj is None:
                return obj
            return getattr(obj, attr, None)
        return self.all(cls).get(cls.__name__ + '.' + id, None)

    def match(self, cls, all=False, **kwargs):
        """
        Returns a `obj` of `cls` with a matching list
        of attributes
        """
        from sqlalchemy import func
        if cls not in classes or len(kwargs) == 0:
            return None
        results = []
        for key, value in kwargs.items():
            value = value if not isinstance(value, str) else value.lower()
            if all is False:
                obj = self.__session.query(cls).filter(
                    func.lower(getattr(cls, key)) == value).first()
                if obj is not None:
                    return obj
            else:
                obj = self.__session.query(cls).filter(
                    func.lower(getattr(cls, key)) == value).all()
                if obj is not None:
                    results.extend(obj)
                    obj = results[:]
        return obj

    def count(self, cls, **kwargs) -> int:
        """Returns a count of an object with a matching list of attributes"""
        if cls not in classes:
            return None
        for key in kwargs.keys():
            if not hasattr(cls, key):
                kwargs.pop(key)
        result = self.__session.query(
            func.count()
        ).select_from(cls).filter_by(**kwargs)
        return result.scalar()

    def paginated(self, cls, page=1, func: Callable = None,
                  size=None) -> Dict[str, any]:
        """Returned a paginated data of the matching class instances"""
        if cls not in classes:
            return None

        # assert size is integer
        if size is not None:
            try:
                size = int(size)
            except ValueError:
                size = PAGINATION
        else:
            size = PAGINATION

        total_items = self.count(cls)
        total_pages = ceil(total_items / size)
        try:
            page = page or 1
            page = 1 if int(page) <= 0 else int(page)
        except ValueError:
            if page == 'all':
                items = self.all(cls).values()
                return {
                    "page": 1,
                    "page_size": total_items,
                    "total_items": total_items,
                    "total_pages": 1,
                    "items": items if func is None else [func(x) for x in items]
                }
            else:
                page = 1

        items = self.__session.query(cls).offset(
            (page - 1) * size).limit(size).all()
        page_size = len(items)

        return {
            "page": page,
            "page_size": page_size,
            "total_items": total_items,
            "total_pages": total_pages,
            "items": items if func is None else [func(x) for x in items]
        }

    def filter_by_date(self, cls, date_from: datetime,
                       date_to: datetime) -> List[any]:
        """Returns a filtered list of cls instance from storage"""
        if not all([cls in classes, isinstance(date_from, datetime),
                    isinstance(date_to, datetime)]):
            return []
        result = self.__session.query(cls).filter(
            cls.created_at.between(date_from.date(), date_to.date())
        ).all()
        return result

    def filter_by_month(self, cls, date: datetime) -> List[any]:
        """Returns a filtered list of cls instance from storage"""
        if not all([cls in classes, isinstance(date, datetime)]):
            return []
        result = self.__session.query(cls).filter(
            and_(extract('month', cls.created_at) == date.month,
                 extract('year', cls.created_at) == date.year)
        ).all()
        return result
