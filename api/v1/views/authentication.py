#!/usr/bin/env python3
"""Authentication routes"""

from api.v1.views import app_views, postdata, mail
from flask import jsonify, abort, render_template, g
from flasgger import swag_from
from api.v1.auth import AUTH_TOKEN_NAME_ON_HEADER
from api.v1.auth import Auth
from models.user.status import Status

DOC_PATH = 'docs/auth/'


@app_views.route('/login', methods=['POST'])
@swag_from(DOC_PATH + 'login.yaml')
def user_login():
    """Validates user login and creates a session if exists"""
    auth: Auth = g.auth

    data = postdata()
    if data is None:
        abort(400)

    email = data.get('email', None)
    password = data.get('password', None)
    if not all([password, email]):
        abort(400)

    user = auth.email_for_user(email=email)
    if user is None:
        abort(404)

    if user.status is not Status.active:
        return jsonify({
            "status": "error",
            "message": "Unauthorized: User account status[{}]".
            format(user.status.to_dict())
        }), 401

    if user.is_valid_password(password):
        token = auth.create_session(user_id=user.id)
        resp = {
            "status": "success",
            "message": "Login successful",
            "data": user.to_dict(),
        }

        if token is not None:
            resp.update({AUTH_TOKEN_NAME_ON_HEADER: token})
        return jsonify(resp), 200

    return jsonify({
        "status": "error",
        "message": "Incorrect password",
        "data": None
    }), 401


@app_views.route('/reset', methods=['POST'])
@swag_from(DOC_PATH + 'post_reset.yaml')
def reset_user_password():
    """Generates and send a reset token to User's email"""
    auth: Auth = g.auth

    data = postdata()
    if data is None:
        abort(400)
    if 'email' not in data:
        abort(400)

    user = auth.email_for_user(email=data.get('email'))
    if user is None:
        abort(404)
    encoded_token = user.generate_reset_token()  # set an expiry on the token
    user.save()

    mail.send_mail(user=user, Subject='Password Reset',
                   body=render_template('reset_user_password.html',
                                        user=user,
                                        encoded_token=encoded_token),
                   content_type='html')
    return jsonify({
        "status": "success",
        "message": "Request is being processed",
        "data": None
    }), 200


@app_views.route('/reset/<encoded_token>', methods=['PUT'],
                 strict_slashes=False)
@swag_from(DOC_PATH + 'put_reset.yaml')
def change_user_password(encoded_token):
    """Changes User Password"""
    auth: Auth = g.auth

    data = postdata()
    if data is None:
        abort(400)

    password = data.get('password')
    if password is None:
        abort(400)

    try:
        user = auth.reset_user_password(
            encoded_token=encoded_token,
            new_password=password
        )
        user.save()
    except ValueError as exc:
        return jsonify({
            "status": "error",
            "message": str(exc),
            "data": None
        }), 401

    return jsonify({
        "status": "success",
        "message": "Password change success",
        "data": None
    }), 200


@app_views.route('/logout', methods=['DELETE'], strict_slashes=False)
@swag_from(DOC_PATH + 'logout.yaml')
def logout():
    """Clears active user's session"""
    auth: Auth = g.auth
    try:
        auth.destroy_session()
    except ValueError as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "data": None
        }), 400
    return jsonify({
        "status": "success",
        "message": "Logout success",
        "data": None
    }), 200
