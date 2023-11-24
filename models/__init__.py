#!/usr/bin/env python3
"""Models"""
from models.engine.db_storage import DBStorage
from mail import MailFactory
from mail.config import SMTPConfig
from dotenv import load_dotenv
from os import getenv
import redis

load_dotenv()

redis = redis.from_url(getenv('REDIS_URL', 'redis://localhost:6379/0'))

storage = DBStorage()
storage.reload()

# Application's Own Mail Setup
SMTP_USERNAME = getenv('SMTP_USERNAME')
SMTP_PASSWORD = getenv('SMTP_PASSWORD')
SMTP_SERVER = getenv('SMTP_SERVER')
SMTP_PORT = getenv('SMTP_PORT')
NOTIFY_EMAIL = getenv('NOTIFY_EMAIL')

config = SMTPConfig(server=SMTP_SERVER, port=SMTP_PORT,
                    username=SMTP_USERNAME, password=SMTP_PASSWORD)

mail = MailFactory(config=config.to_dict())

cloud = None
