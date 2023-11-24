#!/usr/bin/env python3
"""Users URI Module"""

from flask import abort, g, request
from api.v1.views import (
    app_views, storage, jsonify, postdata,
    login_required, pagination,
)
from models.user import User, Role
from sqlalchemy.exc import IntegrityError
from typing import List, Dict
from flasgger import swag_from

DOC_PATH = 'docs/users/'


@app_views.route('/users', methods=['GET'])
@login_required()
@swag_from(DOC_PATH + 'get_users.yaml')
def get_users():
    """Return all users in storage"""

    detailed = request.args.get('detailed') == 'true'

    users: List[User] = storage.all(User).values()
    return jsonify({
        "status": "success",
        "message": "Users retrieved successfully",
        "data": pagination(
            items=users,
            func=lambda x: x.to_dict(detailed=detailed)
        )
    }), 200


@app_views.route('/users/<user_id>', methods=['GET'])
@login_required()
@swag_from(DOC_PATH + 'get_user.yaml')
def get_user(user_id):
    """Returns a User with a matching user_id"""
    detailed = request.args.get('detailed') == 'true'

    user: User = storage.get(User, user_id)
    if user is None:
        abort(404)
    return jsonify({
        "status": "success",
        "message": "User retrieved successfully",
        "data": user.to_dict(detailed=detailed)
    }), 200


@app_views.route('/users/me', methods=['GET'])
@login_required()
@swag_from(DOC_PATH + 'get_me.yaml')
def get_current_user():
    """Returns a User that is currently logged"""

    detailed = request.args.get('detailed', False) == 'true'
    user: User = g.user
    return jsonify({
        "status": "success",
        "message": "User retrieved successfully",
        "data": user.to_dict(detailed=detailed)
    }), 200
