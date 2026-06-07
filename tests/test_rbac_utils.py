from api.auth import user_has_permission, require_permission
from fastapi import HTTPException

class P:
    def __init__(self, code):
        self.code = code

class R:
    def __init__(self, perms):
        self.permissions = perms

class U:
    def __init__(self, role=None):
        self.role = role


def test_user_has_permission_true():
    perms = [P('read_product'), P('write_product')]
    role = R(perms)
    user = U(role)
    assert user_has_permission(user, 'read_product') is True


def test_user_has_permission_false():
    perms = [P('write_product')]
    role = R(perms)
    user = U(role)
    assert user_has_permission(user, 'read_product') is False


def test_require_permission_allows():
    perms = [P('manage_users')]
    role = R(perms)
    user = U(role)
    dep = require_permission('manage_users')
    # when called directly, it should return the user
    returned = dep(current_user=user)
    assert returned is user


def test_require_permission_forbids():
    perms = [P('read_product')]
    role = R(perms)
    user = U(role)
    dep = require_permission('manage_users')
    try:
        dep(current_user=user)
        assert False, "Expected HTTPException"
    except HTTPException as exc:
        assert exc.status_code == 403
