from functools import wraps
from flask import session, redirect, url_for


def login_required(function):

    @wraps(function)
    def wrapper(*args, **kwargs):

        if "user_id" not in session:
            return redirect(url_for("login"))

        return function(*args, **kwargs)

    return wrapper


def role_required(required_role):

    def decorator(function):

        @wraps(function)
        def wrapper(*args, **kwargs):

            if "user_id" not in session:
                return redirect(url_for("login"))

            if session.get("role") != required_role:
                return "Access denied", 403

            return function(*args, **kwargs)

        return wrapper

    return decorator


def roles_required(*required_roles):

    def decorator(function):

        @wraps(function)
        def wrapper(*args, **kwargs):

            if "user_id" not in session:
                return redirect(url_for("login"))

            if session.get("role") not in required_roles:
                return "Access denied", 403

            return function(*args, **kwargs)

        return wrapper

    return decorator