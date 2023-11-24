#!/usr/bin/env python3
"""Session Auth using Redis key, value store"""
from api.v1.auth import Auth, AUTH_TOKEN_NAME_ON_HEADER, AUTH_TTL
from flask import request
import jwt
from jwt.exceptions import ExpiredSignatureError
from jwt import InvalidTokenError
from datetime import datetime, timedelta


token_name = AUTH_TOKEN_NAME_ON_HEADER


class JWT(Auth):
    """Session Auth Class"""

    def __init__(self, secret_key: str) -> None:
        """Intializes Session Auth instance"""
        self.secret_key = secret_key
        super().__init__()

    def create_session(self, user_id: str = None) -> str:
        """Creates a session for user_id"""
        if user_id is None:
            raise ValueError('Missing user_id')

        payload = {
            "user_id": user_id,
            "exp": datetime.utcnow() + timedelta(seconds=int(AUTH_TTL))
        }

        token = jwt.encode(payload=payload, key=self.secret_key,
                           algorithm='HS256')
        if isinstance(token, bytes):
            token = token.decode('utf-8')

        return token

    def get_user_id(self, token: str = None) -> str:
        """Returns value: user_id of a matching Token"""
        if token is None:
            raise ValueError(
                'Missing {token_name}'.format(token_name=token_name))

        try:
            payload = jwt.decode(jwt=token, key=self.secret_key,
                                 algorithms=['HS256'])
        except ExpiredSignatureError:
            raise ValueError('Expired Signature, please log in again.')
        except InvalidTokenError:
            raise ValueError('Invalid JWT Token')

        user_id = payload.get('user_id')
        if user_id is None:
            return None
        return user_id

    def get_token_from_headers(self, request=request) -> str:
        """Returns a token from request.headers"""
        token = request.headers.get(token_name)
        if token is None:
            raise ValueError(
                'Missing {token_name}'.format(token_name=token_name))
        return token

    def current_user(self, request=request) -> any:
        """Overloads and get the current active user"""
        user_id = self.get_user_id(
            token=self.get_token_from_headers(request=request)
        )
        if user_id is None:
            raise ValueError('user_id not found')
        return self.id_for_user(id=user_id)

    def destroy_session(self):
        """Destroys session if exists"""
        pass
