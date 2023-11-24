#!/usr/bin/env python3
"""Authentication"""
from os import getenv
from models.user import User
from models import storage
from models.user.auth import UserAuth


AUTH_TOKEN_NAME_ON_HEADER = getenv('AUTH_TOKEN_NAME_ON_HEADER', 'x-token')
AUTH_TTL = getenv('AUTH_TTL', 259200)
USER_MODELS = [User]


class Auth:
    """A base class for other types of Auth"""

    def email_for_user(self, email: str) -> any:
        """Returns user with a matching email"""
        user = None
        for model in USER_MODELS:
            user = storage.match(model, email=email)
            if user is not None:
                break
        return user

    def id_for_user(self, id: str) -> any:
        """Returns user with a matching id"""
        user = None
        for model in USER_MODELS:
            user = storage.get(model, id)
            if user is not None:
                break
        return user

    def reset_user_password(self, encoded_token: str, new_password: str):
        """Restes user password"""
        user = None
        for model in USER_MODELS:
            try:
                user = UserAuth.update_user_password(
                    encoded_token=encoded_token,
                    new_password=new_password,
                    cls=model
                )
            except ValueError:
                pass
            if user is not None:
                break
        if user is None:
            raise ValueError('Invalid or expired token')
        return user

    def create_session(self, user_id: str = None) -> str:
        pass

    def current_user(self, request=None) -> any:
        pass

    def destroy_session(self):
        pass
