import requests, time, sys

BASE = "http://127.0.0.1:8000"

def wait_for_up(timeout=20):
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            r = requests.get(f"{BASE}/")
            if r.status_code == 200:
                return
        except Exception:
            pass
        time.sleep(0.5)
    raise RuntimeError("service not up")

def must(status, expected, msg):
    assert status == expected, f"{msg}: ожидали {expected}, получили {status}"

def main():
    wait_for_up()

    # admin login
    r = requests.post(f"{BASE}/auth/login", json={"email":"admin@example.com","password":"admin123"})
    must(r.status_code, 200, "admin login")
    A = {"Authorization": f"Bearer {r.json()['token']}"}

    # resources & perms & role
    for res in ["project","report"]:
        requests.post(f"{BASE}/admin/resources", headers=A, json={"code": res})
    for perm in [
        {"resource_code":"project","action":"read"},
        {"resource_code":"project","action":"create"},
        {"resource_code":"report","action":"read"},
    ]:
        requests.post(f"{BASE}/admin/permissions", headers=A, json=perm)
    requests.post(f"{BASE}/admin/roles", headers=A, json={"name":"manager"})
    for rp in [
        {"role_name":"manager","resource_code":"project","action":"read"},
        {"role_name":"manager","resource_code":"project","action":"create"},
    ]:
        requests.post(f"{BASE}/admin/role-permissions", headers=A, json=rp)

    # register user
    requests.post(f"{BASE}/auth/register", json={
        "first_name":"Иван","last_name":"Иванов","patronymic":"",
        "email":"ivan@example.com","password":"qwerty1","password_repeat":"qwerty1"
    })
    # attach role
    r = requests.post(f"{BASE}/admin/user-roles", headers=A,
                      json={"user_email":"ivan@example.com","role_name":"manager"})
    must(r.status_code, 200, "attach role to user")

    # user login
    r = requests.post(f"{BASE}/auth/login", json={"email":"ivan@example.com","password":"qwerty1"})
    must(r.status_code, 200, "user login")
    U = {"Authorization": f"Bearer {r.json()['token']}"}

    # access checks
    r = requests.get(f"{BASE}/projects", headers=U); must(r.status_code, 200, "projects read")
    r = requests.post(f"{BASE}/projects", headers=U); must(r.status_code, 200, "projects create")
    r = requests.get(f"{BASE}/reports", headers=U); must(r.status_code, 403, "reports read forbidden")

    print("OK: e2e тесты прошли")
    return 0

if __name__ == "__main__":
    sys.exit(main())
