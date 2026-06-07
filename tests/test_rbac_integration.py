from fastapi.testclient import TestClient
from api.main import app
from api.auth import get_current_active_user
from api.auth import require_permission


class P:
    def __init__(self, code):
        self.code = code

class R:
    def __init__(self, perms):
        self.permissions = perms

class U:
    def __init__(self, role=None):
        self.role = role


# Add a temporary route to test the require_permission dependency
@app.get('/__test_read')
def __test_read(current_user: U = __import__('fastapi').Depends(require_permission('read_product'))):
    return {"ok": True}


client = TestClient(app)


def test_read_allowed():
    perms = [P('read_product')]
    role = R(perms)
    user = U(role)

    app.dependency_overrides[get_current_active_user] = lambda: user
    resp = client.get('/__test_read')
    assert resp.status_code == 200
    assert resp.json() == {"ok": True}
    app.dependency_overrides.clear()


def test_read_forbidden():
    perms = [P('write_product')]
    role = R(perms)
    user = U(role)

    app.dependency_overrides[get_current_active_user] = lambda: user
    resp = client.get('/__test_read')
    assert resp.status_code == 403
    app.dependency_overrides.clear()
